# PS v2.0 compatible
# PS v3.0 and later: Get-CimInstance replaces Get-WmiObject

$dyle_endpoint = "https://us-central1-charade-ca63f.cloudfunctions.net/rawLogins"

# Get the Data
$c_bios = Get-WmiObject Win32_Bios
$c_os = Get-WmiObject Win32_OperatingSystem
$c_system = Get-WmiObject Win32_ComputerSystem
$c_volume = Get-WmiObject Win32_Volume -Filter "BootVolume = True"
$c_netset = Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled = True"

# Build the Report
$user_info_source = ([ADSI]"LDAP://<SID=$([System.Security.Principal.WindowsIdentity]::GetCurrent().User)>")
$report = [PSCustomObject]@{
    user = $user_info_source.Name.Value # full name 
    email = $user_info_source.mail.Value
    upn = $user_info_source.UserPrincipalName.Value

    # These are the same with different endianness 
    user_objectGUID = [System.Guid]::new($user_info_source.objectGUID.Value)
    user_NativeGUID = $user_info_source.NativeGuid

    serial = $c_bios.SerialNumber
    os_version = $c_os.Version
    os_sku = $c_os.OperatingSystemSKU
    os_arch = $c_os.OSArchitecture
    manufacturer = $c_system.Manufacturer
    model = $c_system.Model
    name = $c_system.Name
    system_type = $c_system.PCSystemType
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

# -ContentType is necessary because otherwise 
# it will be interpreted as multipart form data
Invoke-WebRequest -Uri $dyle_endpoint -Method POST -ContentType application/json -Body $(ConvertTo-Json -Depth 4 $report)
