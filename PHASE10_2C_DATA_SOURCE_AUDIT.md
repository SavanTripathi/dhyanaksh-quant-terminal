# 📊 PHASE 10.2C — DATA SOURCE AUDIT & FRESHNESS SPECIFICATION

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Subsystem:** Daily Prospective Paper Data Ingestion

---

## 1. PRIMARY DATA SOURCE ARCHITECTURE

- **Provider:** `yfinance` Python client querying Yahoo Finance Indian Equity API endpoints (`.NS` tickers, e.g. `RELIANCE.NS`, `TCS.NS`, `INFY.NS`).
- **Adjustment Mechanics:** `auto_adjust=True` explicitly enabled to account for dividend, bonus, and split events.
- **Anomaly Filter:** 3x 20-day rolling median range filter actively strips anomalous spike candles (e.g. unadjusted demerger gap bars).
- **Timezone & Resolution:** Indian Standard Time (IST / UTC+5:30) EOD daily bars timestamped at EOD market close (15:30 IST / 10:00 UTC).

---

## 2. STALE DATA & FALLBACK PREVENTION FOR PROSPECTIVE EVALUATION

- **Offline Fallback Guard:** While `app.engine.data_feed` contains a fallback generator for offline UI preview, **the prospective runner strictly disallows synthetic fallback data**.
- **Data Freshness Assertion:** If `yfinance` is unreachable or returns historical dates without today's closed session, the runner logs `STALE_FEED_ABORT` and terminates cleanly without modifying the prospective ledger.
- **Zero Backfill Enforcement:** If a calendar trading day is missed due to machine downtime or network outage, the prospective runner **never backfills or simulates the missed session**. It simply resumes evaluation from the next live observed trading session.
