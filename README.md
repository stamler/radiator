# radiator
A script for Windows computers to record their properties to a server.

## grooming
Early versions of radiator.vbs (v2 and prior) logged data with ambiguous dates. For example mm/dd/yyyy vs dd/mm/yyyy. The grooming process accounts for these discrepancies using the inference module.

### radiator.vbs

- network configuration is stored as JSON for each adapter (up to 5)
  https://msdn.microsoft.com/en-us/library/aa394217(v=vs.85).aspx
