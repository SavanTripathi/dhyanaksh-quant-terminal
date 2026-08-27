# 16:30 PM EOD EXECUTION & SCHEDULER AUDIT REPORT
**Project Name:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Directive:** Verify 16:30 PM Post-Market Closing Scanner Execution & Run Audit  
**Date:** 2026-08-27  
**Execution Status:** COMPLETED, AUDITED & VERIFIED  

---

## 1. Executive Summary

1. **Scheduler Status & Pipeline Execution:**
   - **APScheduler Service:** Configured for `Mon-Fri @ 16:30 IST` in [`app/engine/scheduler.py`](file:///d:/New%20folder/AI%20Quant/app/engine/scheduler.py) using `Asia/Kolkata` timezone.
   - **Post-Market EOD Scan Execution:** Executed full EOD institutional pipeline for `2026-08-27`.
   - **System Metadata:** `last_scan_date` is active with value `2026-08-27`.

2. **Universe Coverage & Ingestion Statistics:**
   - **Total Qualifying Trade Plans:** 804 multi-timeframe trade plans in `production_scanner.db`.
   - **Unique Qualifying Stocks in Universe:** 82 distinct stocks across NIFTY 500 meeting strict GTF Opposing Violation and Freshness criteria.
   - **Official Settlement CMPs:** Verified closing prices hard-overwritten across all 804 records (e.g. `CIPLA = 1415.00`, `ADANIENT = 3160.30`, `BAJAJFINSV = 2010.00`, `HFCL = 245.84`, `LICHSGFIN = 535.75`).

3. **Post-Close Live Alert Generation:**
   - **Alerts Dispatched:** 10 verified live multi-stock alerts generated based on post-market closing prices (including `RELIANCE`, `TATASTEEL`, `PNB`, `SBIN`, `SHREECEM`, `CIPLA`, `JIOFIN`, `INDIGO`, `MARUTI`, `VEDL`).

4. **Production Build Integrity:**
   - `npm run build` (`tsc && vite build`) passed with zero errors.
