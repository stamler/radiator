import re
from enum import IntEnum, auto

class Version(IntEnum):
    v1 = auto()
    v2 = auto()
    v3 = auto()
    v3_2 = auto()

# original v1
# datetime,username,manufacturer,serial,name,macaddress
full_line_v1 = re.compile('^([^,]+),([^,]+),(.*),([\- A-Za-z0-9]*),'
                                            '([^,]+),([:A-Fa-f0-9]{17})$')

# v2
# "datetime","username","manufacturer","serial","name","macaddress",
# "ram","osversion","ossku","osarchitecture","hdd"
# Another solution is a regex that matches every field and then findall(),
# But this can't be used to validate the format of the first line unless we
# do a findall and then count the number of results
# 11 instances of "(\[.*\]|{.*}|[^"]*)"
full_line_v2 = re.compile('^"([^"]*)",?"([^"]*)",?"([^"]*)",?"([^"]*)",?'
                           '"([^"]*)",?"([^"]*)",?"([^"]*)",?"([^"]*)",?'
                           '"([^"]*)",?"([^"]*)",?"([^"]*)",?$')

# v3.0, v3.1
# "datetime(YMDHMS)","username","manufacturer","serial","name","macaddress",
# "ram","osversion","ossku","osarchitecture","hdd","ipaddresses"
# 12 instances of "(\[.*\]|{.*}|[^"]*)"
full_line_v3 = re.compile('^"([^"]*)",?"([^"]*)",?"([^"]*)",?"([^"]*)",?'
                           '"([^"]*)",?"([^"]*)",?"([^"]*)",?"([^"]*)",?'
                           '"([^"]*)",?"([^"]*)",?"([^"]*)",?"([^"]*)",?$')

# v3.2, v3.3
# "datetime(YMDHMS)","username","manufacturer","serial","name",
# "networkconfig(JSON)", "ram","osversion","ossku","osarchitecture","hdd"
# 11 instances of "(\[.*\]|{.*}|[^"]*)",?
full_line_v3_2 = re.compile('^"(\[.*\]|{.*}|[^"]*)",?"(\[.*\]|{.*}|[^"]*)",?'
                             '"(\[.*\]|{.*}|[^"]*)",?"(\[.*\]|{.*}|[^"]*)",?'
                             '"(\[.*\]|{.*}|[^"]*)",?"(\[.*\]|{.*}|[^"]*)",?'
                             '"(\[.*\]|{.*}|[^"]*)",?"(\[.*\]|{.*}|[^"]*)",?'
                             '"(\[.*\]|{.*}|[^"]*)",?"(\[.*\]|{.*}|[^"]*)",?'
                             '"(\[.*\]|{.*}|[^"]*)",?$')

# values are tuples of format (regex,strp_format_string)
date_formats = {
    "ambiguous_date":(re.compile('(0?[1-9]|1[012])/(0?[1-9]|1[012])/(20\d\d)'),),
    "unambiguous_dmy":(re.compile('(1[3-9]|2[0-9]|3[01])/(0?[1-9]|1[012])/(20\d\d)'),'%d/%m/%Y %I:%M:%S %p'),
    "unambiguous_mdy":(re.compile('(0?[1-9]|1[012])/(1[3-9]|2[0-9]|3[01])/(20\d\d)'),'%m/%d/%Y %I:%M:%S %p'),
    "assumed_ymd":(re.compile('(20\d\d)[/-](0?[1-9]|1[012])[/-]([0-2]?[0-9]|3[01])'),'%Y-%m-%d %I:%M:%S %p')
}

manufacturer_subs = {
                        "":"",
                        "American Megatrends Inc.":"American Megatrends",
                        "American Megatrends, Inc.":"American Megatrends",
                        "TOSHIBA":"TOSHIBA",
                        "Award Software International, Inc.":"eMachines",
                        "Phoenix Technologies LTD":"VMWARE-PHOENIX",
                        "Dell Computer Corporation":"DELL",
                        "LENOVO":"LENOVO",
                        "Dell Inc.":"DELL",
                        "Seabios":"KVM-SEABIOS",
                        "Dell Inc.                ":"DELL",
                        "Hewlett-Packard":"HP",
                        "Acer":"ACER",
                        "HP":"HP",
                        "Acer      ":"ACER",
                        "Intel Corp.":"INTEL",
                        "Dell Inc.         ":"DELL",
                        "Phoenix Technologies, LTD":"PHOENIX"
                    }

osVersion_subs = {
                        "6.0":"WinVista",
                        "6.1":"Win7",
                        "6.2":"Win8",
                        "6.3":"Win8.1",
                        "10.0":"Win10"
                    }

osSku_subs = {
                        # Translated from https://msdn.microsoft.com/en-us/library/aa394239(v=vs.85).aspx
                        # ^(.+) \((\d+)\)\n(.+)$
                        "0":"An unknown product",
                        "1":"Ultimate",
                        "2":"Home Basic",
                        "3":"Home Premium",
                        "4":"Enterprise",
                        "5":"Home Basic N",
                        "6":"Business",
                        "7":"Server Standard",
                        "8":"Server Datacenter (full installation)",
                        "9":"Windows Small Business Server",
                        "10":"Server Enterprise (full installation)",
                        "11":"Starter",
                        "12":"Server Datacenter (core installation)",
                        "13":"Server Standard (core installation)",
                        "14":"Server Enterprise (core installation)",
                        "15":"Server Enterprise for Itanium-based Systems",
                        "16":"Business N",
                        "17":"Web Server (full installation)",
                        "18":"HPC Edition",
                        "19":"Windows Storage Server 2008 R2 Essentials",
                        "20":"Storage Server Express",
                        "21":"Storage Server Standard",
                        "22":"Storage Server Workgroup",
                        "23":"Storage Server Enterprise",
                        "24":"Windows Server 2008 for Windows Essential Server Solutions",
                        "25":"Small Business Server Premium",
                        "26":"Home Premium N",
                        "27":"Enterprise N",
                        "28":"Ultimate N",
                        "29":"Web Server (core installation)",
                        "30":"Windows Essential Business Server Management Server",
                        "31":"Windows Essential Business Server Security Server",
                        "32":"Windows Essential Business Server Messaging Server",
                        "33":"Server Foundation",
                        "34":"Windows Home Server 2011",
                        "35":"Windows Server 2008 without Hyper-V for Windows Essential Server Solutions",
                        "36":"Server Standard without Hyper-V",
                        "37":"Server Datacenter without Hyper-V (full installation)",
                        "38":"Server Enterprise without Hyper-V (full installation)",
                        "39":"Server Datacenter without Hyper-V (core installation)",
                        "40":"Server Standard without Hyper-V (core installation)",
                        "41":"Server Enterprise without Hyper-V (core installation)",
                        "42":"Microsoft Hyper-V Server",
                        "43":"Storage Server Express (core installation)",
                        "44":"Storage Server Standard (core installation)",
                        "45":"Storage Server Workgroup (core installation)",
                        "46":"Storage Server Enterprise (core installation)",
                        "47":"Starter N",
                        "48":"Professional",
                        "49":"Professional N",
                        "50":"Windows Small Business Server 2011 Essentials",
                        "51":"Server For SB Solutions",
                        "52":"Server Solutions Premium",
                        "53":"Server Solutions Premium (core installation)",
                        "54":"Server For SB Solutions EM",
                        "55":"Server For SB Solutions EM",
                        "56":"Windows MultiPoint Server",
                        "59":"Windows Essential Server Solution Management",
                        "60":"Windows Essential Server Solution Additional",
                        "61":"Windows Essential Server Solution Management SVC",
                        "62":"Windows Essential Server Solution Additional SVC",
                        "63":"Small Business Server Premium (core installation)",
                        "64":"Server Hyper Core V",
                        "66":"Starter E",
                        "67":"Home Basic E",
                        "68":"Home Premium E",
                        "69":"Professional E",
                        "70":"Enterprise E",
                        "71":"Ultimate E",
                        "72":"Server Enterprise (evaluation installation)",
                        "76":"Windows MultiPoint Server Standard (full installation)",
                        "77":"Windows MultiPoint Server Premium (full installation)",
                        "79":"Server Standard (evaluation installation)",
                        "80":"Server Datacenter (evaluation installation)",
                        "84":"Enterprise N (evaluation installation)",
                        "95":"Storage Server Workgroup (evaluation installation)",
                        "96":"Storage Server Standard (evaluation installation)",
                        "97":"Windows RT",
                        "98":"Windows 8 N",
                        "99":"Windows 8 China",
                        "100":"Windows 8 Single Language",
                        "101":"Windows Home",
                        "103":"Professional with Media Center",
                        "104":"MOBILE_CORE",
                        "123":"IOTUAP",
                        "143":"Windows Server Datacenter Edition (nano installation)",
                        "144":"Windows Server Standard Edition (nano installation)",
                        "147":"Windows Server Datacenter Edition (core installation)",
                        "148":"Windows Server Standard Edition (core installation)"
                    }
