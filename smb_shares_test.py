import wmi

c = wmi.WMI()

smb_share = ''
print("Available SMB Client Shares:")
for s in c.Win32_PerfFormattedData_Counters_SMBClientShares():
    print(repr(s.Name))
    if s.Name.__contains__("performance_test_monitored"):
        smb_share = s.Name


print(smb_share)