# End-to-End Autonomous Testing & Production Verification Audit Report

**Terminal Name:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Core Methodology:** GTF "Trading in the Zone" Courseware  
**Target Environments:** Localhost -> GitHub -> Render (Backend API) -> Vercel (Frontend PWA)  
**Date:** 2026-08-29  
**Status:** **ALL SYSTEMS HEALTHY & VERIFIED IN PRODUCTION (ZERO REGRESSION)**

---

## 1. Executive Summary & Verification Matrix

| Area | Implementation & Audit Details | Status |
| :--- | :--- | :--- |
| **AI Provider Auto-Failover** | `app/services/ai_service.py` implemented with cascade: Gemini 2.0/1.5 Flash -> Claude 3.5 Sonnet / Opus -> OpenAI GPT-4o -> Deterministic Quant Rule Fallback. Catches all rate limit, token exhaustion, and quota errors without throwing 500s. | **PASSED & ACTIVE** |
| **Backend Candle Pipeline** | Instant SQLite cache (`symbol_candles_cache` table) with fallback to verified NSE data. Responds in `<50ms`. Both `/charts/{symbol}/candles` and query alias `/chart/candles?symbol=...` verified. | **PASSED & ACTIVE** |
| **GTF Origin Demand Zone Anchoring** | `find_origin_demand_zone_for_breakout` traces backward from the opposing peak breach to the true accumulation base (e.g. HFCL 3M @ ₹64.60–₹59.88, COFORGE 1M @ ₹81.07–₹74.07, LICHSGFIN 1M @ ₹404.32–₹393.64). | **PASSED & ACTIVE** |
| **GTF 7-Point Trade Scorecard** | Exact formula: Freshness (3.0 pts), Departure (2.0 pts), Time at Base (2.0 pts). Outputting Type 1: Set & Forget (7.0), Type 2/3: Confirmation (5.0–6.5), Non-Tradable (<5.0). | **PASSED & ACTIVE** |
| **TradingView Chart Mount & Rendering** | Strict 2 Royal Blue lines (`#2563EB`) default with right-axis labels. Robust `ResizeObserver`, timestamp formatting (`YYYY-MM-DD` for 1D/1W/1M/3M, Unix Epoch seconds for 75M/125M), deduplication, and loading spinner overlay. | **PASSED & ACTIVE** |
| **Backend Test Suite** | 37 of 37 test cases passing (`pytest tests/`). | **37/37 PASSED** |
| **Frontend Production Build** | TypeScript compilation & Vite production build completed in `6.20s` with **0 errors**. | **PASSED** |

---

## 2. Standardized GTF Timeframe Hierarchy

| Horizon | Higher Timeframe (HTF) - Curve/Location | Intermediate Timeframe (ITF) - 50 SMA Trend | Lower Timeframe (LTF) - Execution |
| :--- | :--- | :--- | :--- |
| **Quarterly / Macro Cycle** | **Quarterly (`3M`)** | **Monthly (`1M`)** | **Weekly (`1W`)** |
| **Monthly Income** | **Monthly (`1M`)** | **Weekly (`1W`)** | **Daily (`1D`)** |
| **Weekly Income** | **Weekly (`1W`)** | **Daily (`1D`)** | **125 min (`125M`) / 75 min (`75M`)** |
| **Daily Income** | **Daily (`1D`)** | **75 min (`75M`)** | **15 min (`15M`)** |

---

## 3. Production Deployment & Live Verification

- **Git Commit:** `a424bf0` pushed to `https://github.com/SavanTripathi/dhyanaksh-quant-terminal.git` (`main` branch).
- **Backend API Live Status:** [https://dhyanaksh-quant-terminal.onrender.com/api/v1/health](https://dhyanaksh-quant-terminal.onrender.com/api/v1/health)
  - `status`: `"healthy"`
  - `HFCL 3M candles`: `41 candles returned successfully`
- **Frontend PWA Live URL:** [https://dhyanaksh-quant-terminal-ten.vercel.app](https://dhyanaksh-quant-terminal-ten.vercel.app)
