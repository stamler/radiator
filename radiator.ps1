# PS v2.0 compatible
# PS v3.0 and later: Get-CimInstance replaces Get-WmiObject

$dyle_endpoint = "https://firestore.googleapis.com/v1beta1/projects/<PROJECT_ID>/databases/(default)/documents/<COLLECTION_NAME>"

$report = New-Object -TypeName PSObject

# Build the Body
$report | Add-Member -MemberType NoteProperty -Name timestamp -Value $(Get-Date -Format "o")

# [System.Security.Principal.WindowsIdentity]::GetCurrent().Name returns domain prefix too
$report | Add-Member -MemberType NoteProperty -Name user -Value $env:UserName 

$c_bios = Get-WmiObject Win32_Bios
$report | Add-Member -MemberType NoteProperty -Name serial -Value $c_bios.SerialNumber

$c_os = Get-WmiObject Win32_OperatingSystem
$report | Add-Member -MemberType NoteProperty -Name os_version -Value $c_os.Version
$report | Add-Member -MemberType NoteProperty -Name os_sku -Value $c_os.OperatingSystemSKU
$report | Add-Member -MemberType NoteProperty -Name os_arch -Value $c_os.OSArchitecture

$c_system = Get-WmiObject Win32_ComputerSystem
$report | Add-Member -MemberType NoteProperty -Name mfg -Value $c_system.Manufacturer
$report | Add-Member -MemberType NoteProperty -Name model -Value $c_system.Model
$report | Add-Member -MemberType NoteProperty -Name name -Value $c_system.Name
$report | Add-Member -MemberType NoteProperty -Name ram -Value $c_system.TotalPhysicalMemory

$c_volume = Get-WmiObject Win32_Volume -Filter "BootVolume = True"
$report | Add-Member -MemberType NoteProperty -Name boot_drive -Value $c_volume.DriveLetter
$report | Add-Member -MemberType NoteProperty -Name boot_drive_fs -Value $c_volume.FileSystem
$report | Add-Member -MemberType NoteProperty -Name boot_drive_cap -Value $c_volume.Capacity
$report | Add-Member -MemberType NoteProperty -Name boot_drive_free -Value $c_volume.FreeSpace

$c_netset = Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled = True"
$network_configs = @()
ForEach ($c_net in $c_netset) {
    $network_config = New-Object -TypeName PSObject
    $network_config | Add-Member -MemberType NoteProperty -Name mac -Value $c_net.MACAddress
    $network_config | Add-Member -MemberType NoteProperty -Name dhcp_enabled -Value $c_net.DHCPEnabled
    $network_config | Add-Member -MemberType NoteProperty -Name dhcp_server -Value $c_net.DHCPServer
    $network_config | Add-Member -MemberType NoteProperty -Name dns_hostname -Value $c_net.DNSHostName

    #NB These next 5 are arrays of strings
    $network_config | Add-Member -MemberType NoteProperty -Name ips -Value $c_net.IPAddress
    $network_config | Add-Member -MemberType NoteProperty -Name subnets -Value $c_net.IPSubnet
    $network_config | Add-Member -MemberType NoteProperty -Name gateways -Value $c_net.DefaultIPGateway
    $network_config | Add-Member -MemberType NoteProperty -Name dns_order -Value $c_net.DNSServerSearchOrder    

    $network_configs += $network_config
}
$report | Add-Member -MemberType NoteProperty -Name network_config -Value $network_configs

# Upload the body 
$body = New-Object -TypeName PSObject 
$body | Add-Member -MemberType NoteProperty -Name fields -Value $report

Invoke-WebRequest -Uri $dyle_endpoint -Method POST -Body $(ConvertTo-Json $body)
