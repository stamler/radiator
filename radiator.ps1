# PS v2.0 and prior: Get-WmiObject
$dyle_endpoint = "https://firestore.googleapis.com/v1beta1/projects/<PROJECT_ID>/databases/(default)/documents/<COLLECTION_NAME>"

# Build the Body
$timestamp = Get-Date -Format "o"
$env:UserName 
# [System.Security.Principal.WindowsIdentity]::GetCurrent().Name returns domain prefix too

$c_system = Get-WmiObject Win32_ComputerSystem
$c_system.Manufacturer
$c_system.Model
$c_system.Name
$c_system.TotalPhysicalMemory

$c_bios = Get-WmiObject Win32_Bios
$c_bios.SerialNumber

$c_os = Get-WmiObject Win32_OperatingSystem
$c_os.Version 
$c_os.OperatingSystemSKU
$c_os.OSArchitecture

$c_volume = Get-WmiObject Win32_Volume -Filter "BootVolume = True"
$c_volume.DriveLetter
$c_volume.FileSystem
$c_volume.Capacity
$c_volume.FreeSpace

$c_netset = Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled = True"
ForEach ($c_net in $c_netset) {
    $c_net.MACAddress
    $c_net.IPAddress
    $c_net.IPSubnet
    $c_net.DefaultIPGateway
    $c_net.DHCPEnabled
    $c_net.DHCPServer
    $c_net.DNSServerSearchOrder    
}

# Upload the body 
Invoke-WebRequest -Uri $dyle_endpoint -Method POST -Body $json_to_push


# PS v3.0 and later: Get-CimInstance win32_bios
