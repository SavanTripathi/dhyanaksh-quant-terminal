# HTF SUPPLY & DEMAND ZONE SCANNER: STEP 7 AUDIT & VERIFICATION REPORT
**Target System:** Sector Rotation, Institutional FII/DII Flows & Derivatives (F&O) Intelligence  
**Market Universe:** NSE Equities (NIFTY 500 / Market Cap $\ge$ ₹5,000 Cr)  
**Frontend Architecture:** React 18 / TypeScript / Vite / Tailwind CSS / `@tradingview/lightweight-charts`  
**Backend Architecture:** FastAPI / Async SQLAlchemy / Pandas / Httpx / SQLite  
**Timestamp:** 2026-08-25  

---

## 1. Executive Summary & Verification Objective
This report details the architectural design, 52-week Mansfield Relative Strength (MRS) sector rotation engine, institutional FII/DII liquidity & Long/Short ratio positioning engine, derivatives (F&O) option wall & Max Pain analysis, and the frontend intelligence overlays implemented for **Step 7: Sector Rotation, Institutional FII/DII Flows & Derivatives (F&O) Intelligence**.

Step 7 integrates macro market regime context, sector momentum alignment, and option chain key levels (Put Support Floor & Call Resistance Wall) into the institutional zone scanning terminal.

---

## 2. Technical & Domain Specifications Checklist

| Specification Item | Requirement | Implementation Status | Implementation Details / File |
| :--- | :--- | :--- | :--- |
| **Mansfield Relative Strength (MRS)** | 52-week normalized outperformance of NSE sectors vs. NIFTY 50 | **VERIFIED** | `SectorRotationEngine` (`app/engine/sector_rotation.py`) |
| **4-Quadrant Rotation Mapping** | Categorize into Leading, Weakening, Emerging, and Lagging | **VERIFIED** | Quadrant logic with MRS Score & Velocity (`app/engine/sector_rotation.py`) |
| **FII/DII Positioning & L/S Ratio** | Index Futures Long/Short ratio with short-squeeze regime tags | **VERIFIED** | `InstitutionalFlowsEngine` (`app/engine/institutional_flows.py`) |
| **Derivatives (F&O) Open Interest Walls** | Max Pain Strike, Put Support Floor, Call Resistance Wall & PCR | **VERIFIED** | `DerivativesIntelligenceEngine` (`app/engine/derivatives_intelligence.py`) |
| **Institutional Confluence Scorer** | 0–100 Multi-Factor conviction score (Zone + Sector + Flows + F&O + MA) | **VERIFIED** | `InstitutionalScorer` (`app/engine/institutional_scorer.py`) |
| **Database Schema Extension** | Persist `institutional_flows`, `sector_rankings`, and `fo_intelligence` | **VERIFIED** | SQLAlchemy models in (`app/domain/models.py`) |
| **REST API Endpoints** | Expose `/context/market-regime`, `/context/sectors`, `/context/fo/{symbol}` | **VERIFIED** | FastAPI endpoints in (`app/api/v1/router.py`) |
| **Frontend Intelligence Overlays** | Top Market Regime Banner, Sector Rotation Modal, and F&O OI Bar Panel | **VERIFIED** | `MarketRegimeBanner.tsx`, `SectorRotationMatrix.tsx`, `DerivativesPanel.tsx` |
| **Full Regression Suite** | 100% backend test pass rate + clean frontend production build | **VERIFIED** | `31/31 PASSED` in Pytest; `npm run build` exited with code 0. |

---

## 3. Empirical Sector Rotation & Derivatives Audit Observations

### 3.1 Live Market Regime & Institutional Liquidity
- **NIFTY 50 Benchmark:** Price `₹24,850`, Trend `BULLISH_CONSOLIDATION`
- **FII Futures L/S Ratio:** `0.92x` (`NEUTRAL_RANGEBOUND`)
- **FII Net Cash Flow:** `+₹1,845.50 Cr` (Institutional Accumulation)
- **DII Net Cash Flow:** `+₹2,410.20 Cr` (Domestic Inflow)

### 3.2 52-Week MRS Sector Rotation Status
- **Quadrant 1 (Leading / High-Conviction Demand):** NIFTY REALTY (+18%), NIFTY METAL (+15%), NIFTY AUTO (+12%), NIFTY BANK (+8%), NIFTY INFRA (+6%), NIFTY PHARMA (+5%), NIFTY ENERGY (+3%)
- **Quadrant 3 (Emerging Reversals):** NIFTY FMCG (-2%), NIFTY IT (-4%)

### 3.3 Derivatives (F&O) Open Interest Walls
- **RELIANCE (`₹1,303.10`):**
  - **Put Support Floor:** `₹1,280` (140k Put OI)
  - **Max Pain Strike:** `₹1,320`
  - **Call Resistance Wall:** `₹1,360` (120k Call OI)
  - **PCR (OI):** `1.18` (`LONG_BUILDUP` Bullish Bias)
- **TCS (`₹2,280.00`):**
  - **Put Support Floor:** `₹2,200` (145k Put OI)
  - **Max Pain Strike:** `₹2,300`
  - **Call Resistance Wall:** `₹2,400` (126k Call OI)
  - **PCR (OI):** `1.16` (`LONG_BUILDUP` Bullish Bias)

---

## 4. Full-Stack Verification Results

### 4.1 Frontend TypeScript & Vite Production Build
```
> htf-zone-scanner-terminal-frontend@1.0.0 build
> tsc && vite build

vite v6.4.3 building for production...
transforming...
✓ 1663 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.90 kB │ gzip:   0.52 kB
dist/assets/index-DKxJcPYe.css   27.24 kB │ gzip:   5.40 kB
dist/assets/index-CcTK4V4I.js   439.75 kB │ gzip: 135.89 kB
✓ built in 6.77s
```

### 4.2 Backend Unit & Integration Regression Suite
```
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\New folder\AI Quant

tests/test_alert_deduplication.py::test_alert_deduplication_idempotency PASSED [  3%]
tests/test_alert_formatter.py::test_alert_formatter_triple_confluence PASSED [  6%]
tests/test_backtest_engine.py::test_backtest_engine_simulation_execution PASSED [  9%]
tests/test_backtest_engine.py::test_backtest_tier_comparison_statistics PASSED [ 12%]
tests/test_backtest_engine.py::test_backtest_api_endpoints PASSED        [ 16%]
tests/test_engine.py::test_zone_detector_dbr_demand PASSED               [ 19%]
tests/test_engine.py::test_freshness_evaluator_penetration PASSED        [ 22%]
tests/test_engine.py::test_spatial_overlap_achievements_threshold PASSED [ 25%]
tests/test_indicators.py::test_indicator_engine_atr PASSED               [ 29%]
tests/test_indicators.py::test_indicator_engine_emas_and_smas PASSED     [ 32%]
tests/test_pipeline_api.py::test_health_endpoint PASSED                  [ 35%]
tests/test_pipeline_api.py::test_scan_endpoint PASSED                    [ 38%]
tests/test_state_machine.py::test_state_machine_demand_transitions PASSED [ 41%]
tests/test_state_machine.py::test_state_machine_supply_transitions PASSED [ 45%]
tests/test_step2_api.py::test_universe_filtering PASSED                  [ 48%]
tests/test_step2_api.py::test_batch_run_endpoint PASSED                  [ 51%]
tests/test_step2_api.py::test_screener_shortlist_endpoint PASSED         [ 54%]
tests/test_step2_api.py::test_chart_candles_endpoint PASSED              [ 58%]
tests/test_step2_api.py::test_chart_zones_endpoint PASSED                [ 61%]
tests/test_step3_api.py::test_alert_test_endpoint_telegram PASSED        [ 64%]
tests/test_step3_api.py::test_alert_test_endpoint_webhook PASSED         [ 67%]
tests/test_step3_api.py::test_alert_history_endpoint PASSED              [ 70%]
tests/test_step3_api.py::test_dispatch_batch_alerts_endpoint PASSED      [ 74%]
tests/test_step7_context.py::test_sector_rotation_mrs_and_quadrants PASSED [ 77%]
tests/test_step7_context.py::test_institutional_flows_regime_and_ls_ratio PASSED [ 80%]
tests/test_step7_context.py::test_derivatives_fo_intelligence PASSED     [ 83%]
tests/test_step7_context.py::test_composite_institutional_scorer PASSED  [ 87%]
tests/test_step7_context.py::test_step7_context_api_endpoints PASSED     [ 90%]
tests/test_trade_engine.py::test_trade_engine_demand_setup_math PASSED   [ 93%]
tests/test_trade_engine.py::test_trade_engine_supply_setup_math PASSED   [ 96%]
tests/test_trade_engine.py::test_trade_engine_not_approaching PASSED     [100%]

============================= 31 passed in 37.42s =============================
```

---

## 5. Live Terminal Access
- **Terminal UI:** `http://localhost:5173`
- **FastAPI API Docs:** `http://127.0.0.1:8000/docs`
