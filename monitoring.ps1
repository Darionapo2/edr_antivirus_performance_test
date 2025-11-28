$outputFile = ".\monitoring\metrics.csv"

$folder = Split-Path $outputFile
if (!(Test-Path $folder)) {
    New-Item -ItemType Directory -Path $folder | Out-Null
}

$intervalSeconds = 1

# SMB share instance EXACTLY as shown in your PerfMon
$share = "\T14G4-PF4RA1BE\performance_test_monitored"

if (!(Test-Path $outputFile)) {
    $headers = "Timestamp,% Processor Time,% Idle Time,CPU0,CPU1,CPU2,CPU3,CPU4,CPU5,CPU6,CPU7,CPU8,CPU9,CPU10,CPU11,Available MBytes,Copy Read Hits %, % Disk Time,FileSystem Bytes Read,FileSystem Bytes Written,Disk Read Bytes/sec,Disk Write Bytes/sec,Disk Reads/sec,Disk Writes/sec,Avg. Disk sec/Read,Avg. Disk sec/Write,Current Disk Queue Length,SMB Avg. Bytes/Read,SMB Avg. Bytes/Write,SMB Avg. sec/Data Request,SMB Avg. sec/Read,SMB Avg. sec/Write,SMB Avg. Read Queue Length,SMB Avg. Write Queue Length,SMB Avg. Data Queue Length,SMB Avg. Data Bytes/Request,SMB Data Bytes/sec,SMB Read Bytes/sec,SMB Write Bytes/sec"

    $headers | Out-File $outputFile

    Write-Host $headers

}

Write-Host "Monitoring started... press CTRL+C to stop"

while ($true) {

    # CPU
    $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
    $cpu_idle = (Get-Counter '\Processor(_Total)\% Idle Time').CounterSamples.CookedValue

    $cpu0 = (Get-Counter '\Processor(0)\% Processor Time').CounterSamples.CookedValue
    $cpu1 = (Get-Counter '\Processor(1)\% Processor Time').CounterSamples.CookedValue
    $cpu2 = (Get-Counter '\Processor(2)\% Processor Time').CounterSamples.CookedValue
    $cpu3 = (Get-Counter '\Processor(3)\% Processor Time').CounterSamples.CookedValue
    $cpu4 = (Get-Counter '\Processor(4)\% Processor Time').CounterSamples.CookedValue
    $cpu5 = (Get-Counter '\Processor(5)\% Processor Time').CounterSamples.CookedValue
    $cpu6 = (Get-Counter '\Processor(6)\% Processor Time').CounterSamples.CookedValue
    $cpu7 = (Get-Counter '\Processor(7)\% Processor Time').CounterSamples.CookedValue
    $cpu8 = (Get-Counter '\Processor(8)\% Processor Time').CounterSamples.CookedValue
    $cpu9 = (Get-Counter '\Processor(9)\% Processor Time').CounterSamples.CookedValue
    $cpu10 = (Get-Counter '\Processor(10)\% Processor Time').CounterSamples.CookedValue
    $cpu11 = (Get-Counter '\Processor(11)\% Processor Time').CounterSamples.CookedValue

    # Memory
    $mem = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue
    $cache_copy_read_hits_perc = (Get-Counter '\Cache\Copy Read Hits %').CounterSamples.CookedValue

    # Disk
    $disk = (Get-Counter '\PhysicalDisk(_Total)\% Disk Time').CounterSamples.CookedValue

    $fs_readB  = (Get-Counter '\FileSystem Disk Activity(_Total)\FileSystem Bytes Read').CounterSamples.CookedValue
    $fs_writeB = (Get-Counter '\FileSystem Disk Activity(_Total)\FileSystem Bytes Written').CounterSamples.CookedValue

    $readB  = (Get-Counter '\PhysicalDisk(_Total)\Disk Read Bytes/sec').CounterSamples.CookedValue
    $writeB = (Get-Counter '\PhysicalDisk(_Total)\Disk Write Bytes/sec').CounterSamples.CookedValue

    $reads  = (Get-Counter '\PhysicalDisk(_Total)\Disk Reads/sec').CounterSamples.CookedValue
    $writes = (Get-Counter '\PhysicalDisk(_Total)\Disk Writes/sec').CounterSamples.CookedValue

    $latR   = (Get-Counter '\PhysicalDisk(_Total)\Avg. Disk sec/Read').CounterSamples.CookedValue
    $latW   = (Get-Counter '\PhysicalDisk(_Total)\Avg. Disk sec/Write').CounterSamples.CookedValue

    $queue  = (Get-Counter '\PhysicalDisk(_Total)\Current Disk Queue Length').CounterSamples.CookedValue

    # SMB CLIENT SHARES (EXACT from your screenshot)
    $smb_avg_bytes_read     = (Get-Counter "\SMB Client Shares($share)\Avg. Bytes/Read").CounterSamples.CookedValue
    $smb_avg_bytes_write    = (Get-Counter "\SMB Client Shares($share)\Avg. Bytes/Write").CounterSamples.CookedValue
    $smb_avg_sec_data_req   = (Get-Counter "\SMB Client Shares($share)\Avg. sec/Data Request").CounterSamples.CookedValue
    $smb_avg_sec_read       = (Get-Counter "\SMB Client Shares($share)\Avg. sec/Read").CounterSamples.CookedValue
    $smb_avg_sec_write      = (Get-Counter "\SMB Client Shares($share)\Avg. sec/Write").CounterSamples.CookedValue
    $smb_avg_read_queue     = (Get-Counter "\SMB Client Shares($share)\Avg. Read Queue Length").CounterSamples.CookedValue
    $smb_avg_write_queue    = (Get-Counter "\SMB Client Shares($share)\Avg. Write Queue Length").CounterSamples.CookedValue
    $smb_avg_data_queue     = (Get-Counter "\SMB Client Shares($share)\Avg. Data Queue Length").CounterSamples.CookedValue
    $smb_avg_data_bytes_req = (Get-Counter "\SMB Client Shares($share)\Avg. Data Bytes/Request").CounterSamples.CookedValue
    $smb_data_bytes_sec     = (Get-Counter "\SMB Client Shares($share)\Data Bytes/sec").CounterSamples.CookedValue
    $smb_read_bytes_sec     = (Get-Counter "\SMB Client Shares($share)\Read Bytes/sec").CounterSamples.CookedValue
    $smb_write_bytes_sec    = (Get-Counter "\SMB Client Shares($share)\Write Bytes/sec").CounterSamples.CookedValue

    # Timestamp
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")

    $values = @(
        $timestamp,
        [Math]::Round($cpu,3),
        [Math]::Round($cpu_idle,3),
        [Math]::Round($cpu0,3),
        [Math]::Round($cpu1,3),
        [Math]::Round($cpu2,3),
        [Math]::Round($cpu3,3),
        [Math]::Round($cpu4,3),
        [Math]::Round($cpu5,3),
        [Math]::Round($cpu6,3),
        [Math]::Round($cpu7,3),
        [Math]::Round($cpu8,3),
        [Math]::Round($cpu9,3),
        [Math]::Round($cpu10,3),
        [Math]::Round($cpu11,3),
        [Math]::Round($mem,3),
        [Math]::Round($cache_copy_read_hits_perc,3),
        [Math]::Round($disk,3),
        [Math]::Round($fs_readB,3),
        [Math]::Round($fs_writeB,3),
        [Math]::Round($readB,3),
        [Math]::Round($writeB,3),
        [Math]::Round($reads,3),
        [Math]::Round($writes,3),
        [Math]::Round($latR,3),
        [Math]::Round($latW,3),
        [Math]::Round($queue,3),

        # SMB values
        [Math]::Round($smb_avg_bytes_read,3),
        [Math]::Round($smb_avg_bytes_write,3),
        [Math]::Round($smb_avg_sec_data_req,3),
        [Math]::Round($smb_avg_sec_read,3),
        [Math]::Round($smb_avg_sec_write,3),
        [Math]::Round($smb_avg_read_queue,3),
        [Math]::Round($smb_avg_write_queue,3),
        [Math]::Round($smb_avg_data_queue,3),
        [Math]::Round($smb_avg_data_bytes_req,3),
        [Math]::Round($smb_data_bytes_sec,3),
        [Math]::Round($smb_read_bytes_sec,3),
        [Math]::Round($smb_write_bytes_sec,3)
    )

    $line = $values -join ","

    Write-Host $line

    Add-Content -Path $outputFile -Value $line

    Start-Sleep -Seconds $intervalSeconds
}
