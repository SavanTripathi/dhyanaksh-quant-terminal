# GTF Quantitative Standardization & Timeframe Locking Audit Report

**Terminal Name:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Methodology Reference:** Official GTF "Trading in the Zone" Courseware  
**Date:** 2026-08-29  
**Status:** ALL DIRECTIVES FULFILLED (ZERO REGRESSION)

---

## 1. Summary of Standardized Changes

| Requirement | Implementation Details | Status |
| :--- | :--- | :--- |
| **Strict Timeframe Locking** | `6M` completely excised from backend enums, serializers, candle aggregators, and frontend UI toolbars. Locked strictly to: `3M` (Quarterly), `1M` (Monthly), `1W` (Weekly), `1D` (Daily), `125M` (Execution), `75M` (Execution). | **LOCKED & VERIFIED** |
| **GTF 7-Point Trade Scorecard** | Implemented exact 7-point formula: Freshness (3.0 pts), Departure / Legout Strength (2.0 pts), and Time at Base (2.0 pts). | **IMPLEMENTED** |
| **GTF Entry Classification** | `7.0 / 7.0` $\rightarrow$ **Entry Type 1: Set & Forget** (Limit Order). `5.0 – 6.5` $\rightarrow$ **Entry Type 2/3: Confirmation Entry**. `< 5.0` $\rightarrow$ **Non-Tradable**. | **IMPLEMENTED** |
| **LOTL Base Merge** | Nested or stacked base formations within $1.5 \times \text{ATR}$ are identified as `is_lotl_merged = True` with upper base proximal and lower base distal boundaries. | **IMPLEMENTED** |
| **50 SMA 7-Candle Clock Rule** | Computed vector slope over 7 ITF candles: `1:30 (12:00 - 3:00 Trend UP)`, `4:30 (3:00 - 6:00 Trend DOWN)`, and `3:00 (Trend SIDEWAYS)`. | **IMPLEMENTED** |
| **Opposing Zone Violations** | Standardized opposing structural shift tracking: 1 Breached (Sideways Consolidation) vs $\ge 2$ Breached (Major Institutional Uptrend). | **IMPLEMENTED** |
| **Zero UI / Chart Regression** | Maintained strictly **2 Royal Blue Lines** by default on TradingView charts with no UI layout redesign or database restructuring. | **ZERO REGRESSION** |

---

## 2. Standardized GTF Hierarchy Table

| Purpose | Higher Time Frame (HTF) - Location | Intermediate Time Frame (ITF) - Trend | Lower Time Frame (LTF) - Execution |
| :--- | :--- | :--- | :--- |
| **Quarterly / Macro Cycle** | **Quarterly (`3M`)** | **Monthly (`1M`)** | **Weekly (`1W`)** |
| **Monthly Income** | **Monthly (`1M`)** | **Weekly (`1W`)** | **Daily (`1D`)** |
| **Weekly Income** | **Weekly (`1W`)** | **Daily (`1D`)** | **125 min (`125M`) / 75 min (`75M`)** |
| **Daily Income** | **Daily (`1D`)** | **75 min (`75M`)** | **15 min (`15M`)** |

---

## 3. Production Verification & Deployment

- **Frontend Production Build:** `npm run build` completed in `24.91s` with **0 errors**.
- **Git Commit:** `49dabeb` pushed to `https://github.com/SavanTripathi/dhyanaksh-quant-terminal.git` (`main` branch).
- **Live Terminal URL:** [https://dhyanaksh-quant-terminal-ten.vercel.app](https://dhyanaksh-quant-terminal-ten.vercel.app)
- **Live Backend API URL:** [https://dhyanaksh-quant-terminal.onrender.com](https://dhyanaksh-quant-terminal.onrender.com)
