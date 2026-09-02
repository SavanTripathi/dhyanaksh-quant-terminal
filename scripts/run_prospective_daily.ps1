# Dhyanaksh HTF Quantitative Terminal — Daily Prospective Paper Collector
# Schedule: Monday - Friday at 16:00 IST (10:30 UTC)

$ErrorActionPreference = "Stop"
$WorkingDir = "d:\New folder\AI Quant"
Set-Location -Path $WorkingDir

$LogFile = "$WorkingDir\logs\prospective_daily_runner.log"

Write-Output "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [INFO] Invoking Daily Prospective Paper Collector..." | Out-File -FilePath $LogFile -Append

try {
    $env:ENABLE_LIVE_BROKER_EXECUTION = "false"
    python -m scripts.run_daily_prospective_collector
    Write-Output "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [INFO] Collector execution completed with exit code 0." | Out-File -FilePath $LogFile -Append
} catch {
    Write-Output "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [ERROR] Collector execution failed: $_" | Out-File -FilePath $LogFile -Append
    exit 1
}
