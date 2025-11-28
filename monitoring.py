import wmi
import time
import csv
from datetime import datetime

def start_monitoring():

    # WMI init
    c = wmi.WMI()

    interval = 1 # seconds
    output_file = "./monitoring/metrics.csv"

    # 1) Discover the SMB share object once
    target_share = None
    print("Available SMB Client Shares:")
    for s in c.Win32_PerfFormattedData_Counters_SMBClientShares():
        print("FOUND:", repr(s.Name))
        if "performance_test_monitored" in s.Name:
            target_share = s
            print(target_share)

    if target_share is None:
        raise RuntimeError("Non ho trovato nessuna SMB Client Share che contenga 'performance_test_monitored'")

    # CSV header
    headers = [
        "Timestamp", "% Processor Time", "% Idle Time",
        "CPU0", "CPU1", "CPU2", "CPU3", "CPU4", "CPU5", "CPU6", "CPU7", "CPU8", "CPU9", "CPU10", "CPU11",
        "Available MBytes", "Copy Read Hits %", "% Disk Time",
        "Disk Read Bytes/sec", "Disk Write Bytes/sec",
        "Disk Reads/sec", "Disk Writes/sec",
        "Avg. Disk sec/Read", "Avg. Disk sec/Write", "Current Disk Queue Length",
        "SMB Avg. Bytes/Read", "SMB Avg. Bytes/Write", "SMB Avg. sec/Data Request",
        "SMB Avg. sec/Read", "SMB Avg. sec/Write",
        "SMB Avg. Read Queue Length", "SMB Avg. Write Queue Length",
        "SMB Avg. Data Queue Length", "SMB Avg. Data Bytes/Request",
        "SMB Data Bytes/sec", "SMB Read Bytes/sec", "SMB Write Bytes/sec"
    ]

    # Create file and write header
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

    print("Monitoring started... CTRL+C to stop")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # CPU (total)
        cpu_total = c.Win32_PerfFormattedData_PerfOS_Processor(Name="_Total")[0]

        # Per-core CPU
        cpu_cores = [c.Win32_PerfFormattedData_PerfOS_Processor(Name=str(i))[0] for i in range(12)]

        # Memory
        mem = c.Win32_PerfFormattedData_PerfOS_Memory()[0]

        # Cache
        cache = c.Win32_PerfFormattedData_PerfOS_Cache()[0]

        # Physical Disk
        disk = c.Win32_PerfFormattedData_PerfDisk_PhysicalDisk(Name="_Total")[0]

        # SMB Client Shares
        target_share.Refresh_()
        smb = target_share

        row = [
            timestamp,
            cpu_total.PercentProcessorTime,
            cpu_total.PercentIdleTime,

            # Per-core CPU
            *[core.PercentProcessorTime for core in cpu_cores],

            mem.AvailableMBytes,
            cache.CopyReadHitsPercent,
            disk.PercentDiskTime,

            disk.DiskReadBytesPersec,
            disk.DiskWriteBytesPersec,

            disk.DiskReadsPersec,
            disk.DiskWritesPersec,

            disk.AvgDiskSecPerRead,
            disk.AvgDiskSecPerWrite,
            disk.CurrentDiskQueueLength,

            smb.AvgBytesPerRead,
            smb.AvgBytesPerWrite,
            smb.AvgsecPerDataRequest,

            smb.AvgsecPerRead,
            smb.AvgsecPerWrite,

            smb.AvgReadQueueLength,
            smb.AvgWriteQueueLength,
            smb.AvgDataQueueLength,
            smb.AvgDataBytesPerRequest,

            smb.DataBytesPersec,
            smb.ReadBytesPersec,
            smb.WriteBytesPersec
        ]

        # Print to console
        print(",".join(str(v) for v in row))

        # Append to CSV
        with open(output_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        time.sleep(interval)


if __name__ == '__main__':
    start_monitoring()