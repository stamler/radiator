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
$report = [PSCustomObject]@{
    datetime = @{"timestampValue" = $(Get-Date -Format "o")}
    # [System.Security.Principal.WindowsIdentity]::GetCurrent().Name returns domain prefix too
    username = @{ "stringValue" = $env:UserName }
    serial = @{ "stringValue" = $c_bios.SerialNumber }
    os_version = @{"stringValue" = $c_os.Version }
    os_sku = @{"integerValue" = $c_os.OperatingSystemSKU }
    os_arch = @{"stringValue" = $c_os.OSArchitecture }
    manufacturer = @{"stringValue" = $c_system.Manufacturer }
    model = @{"stringValue" = $c_system.Model }
    name = @{"stringValue" = $c_system.Name }
    ram = @{"integerValue" = $c_system.TotalPhysicalMemory }
    boot_drive = @{"stringValue" = $c_volume.DriveLetter }
    boot_drive_fs = @{"stringValue" = $c_volume.FileSystem }
    boot_drive_cap = @{"integerValue" = $c_volume.Capacity }
    boot_drive_free = @{"integerValue" = $c_volume.FreeSpace }
}

$network_configs = @()
ForEach ($c_net in $c_netset) {
    $network_config = @{
        mac = @{"stringValue" = $c_net.MACAddress }
        dhcp_enabled = @{"booleanValue" = $c_net.DHCPEnabled }
        dhcp_server = @{"stringValue" = $c_net.DHCPServer }
        dns_hostname = @{"stringValue" = $c_net.DNSHostName }
        ips = @{"arrayValue" = $c_net.IPAddress }
        subnets = @{"arrayValue" = $c_net.IPSubnet }
        gateways = @{"arrayValue" = $c_net.DefaultIPGateway }
        dns_order = @{"arrayValue" = $c_net.DNSServerSearchOrder }
    }

    $network_configs += $network_config
}
$report | Add-Member -MemberType NoteProperty -Name network_config -Value @{"arrayValue" = @{"values" = $network_configs } } 

# Upload the body 
$body = [PSCustomObject]@{
    fields = $report
}

Invoke-WebRequest -Uri $dyle_endpoint -Method POST -Body $(ConvertTo-Json $body)
