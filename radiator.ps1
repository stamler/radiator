# PS v2.0 compatible
# PS v3.0 and later: Get-CimInstance replaces Get-WmiObject

$dyle_endpoint = "https://firestore.googleapis.com/v1beta1/projects/<PROJECT_ID>/databases/(default)/documents/<COLLECTION_NAME>"

# Get the Data
$c_bios = Get-WmiObject Win32_Bios
$c_os = Get-WmiObject Win32_OperatingSystem
$c_system = Get-WmiObject Win32_ComputerSystem
$c_volume = Get-WmiObject Win32_Volume -Filter "BootVolume = True"
$c_netset = Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled = True"

# Build the Report
# TODO: figure out why 400 error occurs on post where an entry is 'null'
$report = [PSCustomObject]@{
    datetime = $(Get-Date -Format "o")
    # [System.Security.Principal.WindowsIdentity]::GetCurrent().Name returns domain prefix too
    username = $env:UserName
    serial = $c_bios.SerialNumber
    os_version = $c_os.Version
    os_sku = $c_os.OperatingSystemSKU
    os_arch = $c_os.OSArchitecture
    manufacturer = $c_system.Manufacturer
    model = $c_system.Model
    name = $c_system.Name
    ram = $c_system.TotalPhysicalMemory
    boot_drive = $c_volume.DriveLetter
    boot_drive_fs = $c_volume.FileSystem
    boot_drive_cap = $c_volume.Capacity
    boot_drive_free = $c_volume.FreeSpace
}

$network_configs = @()
ForEach ($c_net in $c_netset) {
    # Iterate over array elements and assign type stringValue
    ForEach ($t in $c_net.IPAddress) {
        [array]$ip_list += $t
    }
    ForEach ($t in $c_net.IPSubnet) {
        [array]$subnet_list += $t
    }
    ForEach ($t in $c_net.DefaultIPGateway) {
        [array]$gateway_list += $t
    }
    ForEach ($t in $c_net.DNSServerSearchOrder) {
        [array]$dns_list += $t
    }

    $network_config = @{
        mac = $c_net.MACAddress
        dhcp_enabled = $c_net.DHCPEnabled
        dhcp_server = $c_net.DHCPServer
        dns_hostname = $c_net.DNSHostName
        ips = $ip_list
        subnets = $subnet_list
        gateways = $gateway_list
        dns_order = $dns_list
    }

    $network_configs += $network_config
}
$report | Add-Member -MemberType NoteProperty -Name network_config -Value $network_configs 

Invoke-WebRequest -Uri $dyle_endpoint -Method POST -Body $(ConvertTo-Json -Depth 4 $report)
