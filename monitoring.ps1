# ===============================
# Monitoraggio Server Windows
# CPU, Memoria, Disco → CSV
# ===============================

# Percorso file CSV di output
$outputFile = ".\monitoring\metrics.csv"

# Crea cartella se non esiste
$folder = Split-Path $outputFile
if (!(Test-Path $folder)) {
    New-Item -ItemType Directory -Path $folder | Out-Null
}

# Intervallo tra campioni (secondi)
$intervalSeconds = 5

# Scrive l’intestazione del CSV se non esiste
if (!(Test-Path $outputFile)) {
    "Timestamp,CPU_Percent,Memory_AvailableMB,Disk_UsagePercent" | Out-File $outputFile
}

Write-Host "Monitoraggio iniziato... (CTRL + C per interrompere)"
while ($true) {

    # CPU: % Processor Time
    $cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue

    # Memoria disponibile (MB)
    $mem = (Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue

    # Disco: % Disk Time
    $disk = (Get-Counter '\PhysicalDisk(_Total)\% Disk Time').CounterSamples.CookedValue

    # Timestamp ISO
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")

    # Riga CSV
    $line = "$timestamp,$([Math]::Round($cpu,2)),$([Math]::Round($mem,2)),$([Math]::Round($disk,2))"

    # Aggiungi al file
    Add-Content -Path $outputFile -Value $line

    # Attendi intervallo
    Start-Sleep -Seconds $intervalSeconds
}
