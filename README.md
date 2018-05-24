# radiator
Radiator is a system to store information about computers in a Windows domain environment in a corporate database. It has two components. The first, `radiator.vbs`, is a logon script which records properties about a Windows computer into a log file stored on an SMB file share. The second, `radiator-push.py` (and dependencies), is a system to read the log files created by `radiator.vbs`, form them into JSON, and push them to an API. The target API is an instance of the companion project, [charade](https://github.com/stamler/charade).

The `radiator.py` component is being written for deployment in a docker container run on a cron job. Development targets Synology NAS devices running DSM 6.0+.

## grooming
Early versions of radiator.vbs (v2 and prior) logged data with ambiguous dates. For example mm/dd/yyyy vs dd/mm/yyyy. The grooming process accounts for these discrepancies using the included inference module.

### radiator.vbs
- network configuration is stored as JSON for each adapter (up to 5)
  https://msdn.microsoft.com/en-us/library/aa394217(v=vs.85).aspx
