# 🔍 PHASE 10.2K — MARKET DATA & EOD INGESTION FORENSIC AUDIT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Primary Feed:** `yfinance` Indian Equity Client (`.NS` tickers)

---

## 1. INGESTION SPECIFICATION & SAFETY AUDIT

- **API Endpoint:** Yahoo Finance official adjusted quote stream (`auto_adjust=True`).
- **Candle Formation:** Daily EOD bars consolidate final official 15:30 IST NSE settlement closes.
- **Corporate Actions:** Splits, bonuses, and rights adjustments are automatically folded into adjusted historical bars.
- **Anomaly Filter:** 3x 20-day rolling median range threshold dynamically strips spurious unadjusted demerger gap bars.
- **Incomplete Candle Prevention:** The 15:45 IST hard gate combined with the EOD timestamp checker guarantees that mid-day continuous trading bars can never be ingested as completed daily candles.
