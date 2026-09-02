# ⚙️ PHASE 10.2C — OPERATIONAL READINESS & SCHEDULER SPECIFICATION

**Job Identifier:** `Dhyanaksh_Prospective_Daily_Collector`  
**Execution Frequency:** Monday – Friday at 16:00 IST (10:30 UTC)  
**Execution Command:** `powershell.exe -ExecutionPolicy Bypass -File d:\New folder\AI Quant\scripts\run_prospective_daily.ps1`  
**Working Directory:** `d:\New folder\AI Quant`

---

## 1. MANUAL OR SCHEDULED TRIGGER OPTIONS

### Option A: Manual CLI Run (Anytime post-market close)
```powershell
python -m scripts.run_daily_prospective_collector
```

### Option B: Windows Task Scheduler Registration Command
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File ""d:\New folder\AI Quant\scripts\run_prospective_daily.ps1"""
$trigger = New-ScheduledTaskTrigger -Daily -At 4:00PM
Register-ScheduledTask -TaskName "Dhyanaksh_Prospective_Daily_Collector" -Action $action -Trigger $trigger -Description "Daily Headless Prospective Paper Trading Collector for Dhyanaksh Quant Terminal"
```
