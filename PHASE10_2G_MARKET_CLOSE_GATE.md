# 🔒 PHASE 10.2G — MARKET-CLOSE HARD GATE & EXECUTION MODE SPECIFICATION

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Timezone Reference:** `Asia/Kolkata (IST / UTC+5:30)`

---

## 1. MANDATORY TIME-OF-DAY SAFETY GATE

```python
# Hard EOD Timing Gate: Execution before 15:45 IST (10:15 UTC) is strictly forbidden for prospective ledger writes
current_ist_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
if current_ist_time.hour < 15 or (current_ist_time.hour == 15 and current_ist_time.minute < 45):
    if not dry_run:
        logging.critical("PROSPECTIVE EOD WRITE FORBIDDEN BEFORE 15:45 IST! ABORTING.")
        sys.exit(1)
```

---

## 2. EXPLICIT EXECUTION MODES

1. **`DRY_RUN` (`--dry-run` or default interactive invocation without flag):** Read-only evaluation against live/historical feeds. Mutates zero files.
2. **`REPLAY` (`--mode replay`):** Writes strictly to `PAPER_TRADING_V1_1_REPLAY_TEST_EVENTS.csv`.
3. **`PROSPECTIVE` (`--mode prospective`):** Only callable post-15:45 IST with full EOD candle verification, writing to `PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv`.
