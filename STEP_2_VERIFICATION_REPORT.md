# HTF SUPPLY & DEMAND ZONE SCANNER: STEP 2 AUDIT & VERIFICATION REPORT
**Target System:** NIFTY 500 Batch Scanner & Deterministic Trade Engine  
**Market Universe:** NSE Equities (NIFTY 500 / Market Cap $\ge$ ₹5,000 Cr)  
**Architecture:** Modular Backend Monolith (FastAPI / SQLAlchemy Async Core / Pandas / SQLite)  
**Timestamp:** 2026-08-25  

---

## 1. Executive Summary & Verification Objective
This report details the architectural design, mathematical formulations, algorithmic implementation, and automated test suite results for **Step 2: NIFTY 500 Batch Scanner & Deterministic Trade Engine**.

The system automates the EOD scanning pipeline across the NIFTY 500 universe (filtered for Market Cap $\ge$ ₹5,000 Cr), identifies multi-timeframe strictly fresh zones with **Achievements > 1** (Tier 2 and Tier 3 setups), formulates deterministic trade plans with exact Entry, Stop Loss (with $0.20 \times \text{ATR}_{1\text{D}}(14)$ buffer), Targets (T1=2.0R, T2=3.5R, T3=5.0R), calculates proximity distance % and approaching flag ($\le 2.5\%$), and assesses Moving Average trend confluences (20/50 EMA, 200 SMA).

---

## 2. Technical & Domain Specifications Checklist

| Specification Item | Requirement | Implementation Status | Implementation Details / File |
| :--- | :--- | :--- | :--- |
| **Universe Filtering** | Active NSE Equities with $\text{Market Cap} \ge \text{₹5,000 Cr}$ | **VERIFIED** | Filter repository rejecting small caps (`app/engine/universe.py`) |
| **MTF Aggregation** | 3M, 1M, 1W, 1D, 125M, 75M | **VERIFIED** | Indian session-aware (09:15-15:30 IST) continuous resampler (`app/engine/aggregator.py`) |
| **Strict Freshness & Spatial Overlap** | Zero subsequent penetrations & Achievements > 1 | **VERIFIED** | Strict freshness filter & 1D interval overlap engine (`app/engine/freshness.py`, `app/engine/spatial_overlap.py`) |
| **Demand Trade Plan Formulas** | Entry=$H$, $\text{SL}=L - 0.20\text{ATR}$, $T_1=E+2R$, $T_2=E+3.5R$, $T_3=E+5R$ | **VERIFIED** | Deterministic trade engine (`app/engine/trade_engine.py`) |
| **Supply Trade Plan Formulas** | Entry=$L$, $\text{SL}=H + 0.20\text{ATR}$, $T_1=E-2R$, $T_2=E-3.5R$, $T_3=E-5R$ | **VERIFIED** | Deterministic trade engine (`app/engine/trade_engine.py`) |
| **Approaching Flag** | $\text{True if } 0.0\% \le \text{Distance \%} \le 2.5\%$ | **VERIFIED** | Exact proximity mathematical calculation (`app/engine/trade_engine.py`) |
| **MA Confluence Layer** | 20 EMA, 50 EMA, 200 SMA; flag if 50 EMA / 200 SMA is in zone | **VERIFIED** | Vectorized indicator calculations and zone overlap test (`app/engine/indicators.py`, `app/engine/trade_engine.py`) |
| **Database Schema** | `trade_plans` & `batch_scan_runs` tables | **VERIFIED** | Async SQLAlchemy ORM models (`app/domain/models.py`) |
| **REST API - Screener** | `GET /api/v1/screener/shortlist` | **VERIFIED** | Filter by `min_achievements`, `direction`, `approaching_only`, `has_ma_confluence` (`app/api/v1/router.py`) |
| **REST API - Candles** | `GET /api/v1/charts/{symbol}/candles` | **VERIFIED** | OHLCV feed for 3M, 1M, 1W, 1D, 125M, 75M (`app/api/v1/router.py`) |
| **REST API - Zones** | `GET /api/v1/charts/{symbol}/zones` | **VERIFIED** | Active fresh zones & cluster coordinates (`app/api/v1/router.py`) |
| **REST API - Batch Run** | `POST /api/v1/batch/run` | **VERIFIED** | On-demand EOD batch execution (`app/api/v1/router.py`) |

---

## 3. Mathematical Formulations

### 3.1 Indicator Formulations
For daily candle series with high $H_t$, low $L_t$, close $C_t$:
- **True Range ($TR_t$):**
  $$TR_t = \max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)$$
- **Average True Range ($\text{ATR}_{1\text{D}}(14)$):**
  $$\text{ATR}_t = \frac{\text{ATR}_{t-1} \times 13 + TR_t}{14}$$
- **ATR Buffer:**
  $$\text{Buffer} = 0.20 \times \text{ATR}_{1\text{D}}(14)$$
- **Exponential Moving Average ($\text{EMA}_n$):**
  $$\alpha = \frac{2}{n + 1}, \quad \text{EMA}_t = \alpha C_t + (1 - \alpha)\text{EMA}_{t-1} \quad (n = 20, 50)$$
- **Simple Moving Average ($\text{SMA}_{200}$):**
  $$\text{SMA}_{200, t} = \frac{1}{200}\sum_{i=0}^{199} C_{t-i}$$

---

### 3.2 Demand Setup Formulation
Given a spatial overlap cluster $[L_{\text{common}}, H_{\text{common}}]$ where direction is `DEMAND`:
1. **Entry Price:**
   $$\text{Entry} = H_{\text{common}} \quad (\text{Proximal Line})$$
2. **Stop Loss (SL):**
   $$\text{SL} = L_{\text{common}} - (0.20 \times \text{ATR}_{1\text{D}}(14)) \quad (\text{Distal Line minus ATR Buffer})$$
3. **Risk per Share ($R$):**
   $$R = \text{Entry} - \text{SL}$$
4. **Target Multiples:**
   $$T_1 = \text{Entry} + 2.0 \times R$$
   $$T_2 = \text{Entry} + 3.5 \times R$$
   $$T_3 = \text{Entry} + 5.0 \times R$$
5. **Distance %:**
   $$\text{Distance \%} = \left(\frac{\text{Current Price} - \text{Entry}}{\text{Current Price}}\right) \times 100$$
6. **Approaching Flag:**
   $$\text{is\_approaching} = \begin{cases} \text{True}, & \text{if } 0.0\% \le \text{Distance \%} \le 2.5\% \\ \text{False}, & \text{otherwise} \end{cases}$$

---

### 3.3 Supply Setup Formulation
Given a spatial overlap cluster $[L_{\text{common}}, H_{\text{common}}]$ where direction is `SUPPLY`:
1. **Entry Price:**
   $$\text{Entry} = L_{\text{common}} \quad (\text{Proximal Line})$$
2. **Stop Loss (SL):**
   $$\text{SL} = H_{\text{common}} + (0.20 \times \text{ATR}_{1\text{D}}(14)) \quad (\text{Distal Line plus ATR Buffer})$$
3. **Risk per Share ($R$):**
   $$R = \text{SL} - \text{Entry}$$
4. **Target Multiples:**
   $$T_1 = \text{Entry} - 2.0 \times R$$
   $$T_2 = \text{Entry} - 3.5 \times R$$
   $$T_3 = \text{Entry} - 5.0 \times R$$
5. **Distance %:**
   $$\text{Distance \%} = \left(\frac{\text{Entry} - \text{Current Price}}{\text{Current Price}}\right) \times 100$$
6. **Approaching Flag:**
   $$\text{is\_approaching} = \begin{cases} \text{True}, & \text{if } 0.0\% \le \text{Distance \%} \le 2.5\% \\ \text{False}, & \text{otherwise} \end{cases}$$

---

### 3.4 Moving Average Confluence Rule
$$\text{has\_ma\_confluence} = \text{True} \iff (L_{\text{common}} - \text{Buffer} \le \text{EMA}_{50} \le H_{\text{common}} + \text{Buffer}) \lor (L_{\text{common}} - \text{Buffer} \le \text{SMA}_{200} \le H_{\text{common}} + \text{Buffer})$$

---

## 4. Codebase Architecture

```
d:\New folder\AI Quant\
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── router.py             # FastAPI routes (/screener/shortlist, /charts/..., /batch/run)
│   ├── core/
│   │   ├── config.py                 # Pydantic Settings
│   │   └── database.py               # Async SQLAlchemy engine & session factory
│   ├── domain/
│   │   ├── enums.py                  # Timeframe, ZoneDirection, FreshnessStatus, ZoneStructure
│   │   ├── models.py                 # ORM Models (TradePlanModel, BatchScanRunModel, etc.)
│   │   └── schemas.py                # Pydantic Schemas for Trade Plans, Screener, Charts
│   ├── engine/
│   │   ├── aggregator.py             # MTF Candle Aggregator (75M, 125M, 1D, 1W, 1M, 3M)
│   │   ├── zone_detector.py          # Institutional zone detector
│   │   ├── freshness.py              # Strict freshness penetration evaluator
│   │   ├── spatial_overlap.py        # Achievements > 1 spatial overlap clusterer
│   │   ├── indicators.py             # Vectorized ATR(14), 20/50 EMA, 200 SMA
│   │   ├── trade_engine.py           # Deterministic Trade Plan generator (Demand/Supply math)
│   │   ├── universe.py               # NIFTY 500 universe repository (Market Cap >= 5,000 Cr)
│   │   ├── data_feed.py              # Session-aligned candle generator for testing
│   │   ├── batch_scanner.py          # EOD Batch Scanner Orchestrator
│   │   └── pipeline.py               # Real-time scan pipeline
│   └── main.py                       # FastAPI application factory & lifespan
├── tests/
│   ├── conftest.py                   # Pytest async DB fixtures
│   ├── test_engine.py                # Unit tests for ZoneDetector, Freshness, SpatialOverlap
│   ├── test_indicators.py            # Unit tests for ATR, EMA, SMA
│   ├── test_trade_engine.py          # Mathematical verification of Trade Engine formulas
│   ├── test_pipeline_api.py          # Integration tests for Pipeline & Health
│   └── test_step2_api.py             # Integration tests for Universe, Batch Scanner, Screener, Charts
├── README.md                         # Project documentation
├── STEP_1_VERIFICATION_REPORT.md     # Step 1 Verification Report
├── STEP_2_VERIFICATION_REPORT.md     # This comprehensive Step 2 Audit Report
└── requirements.txt
```

---

## 5. Automated Verification & Test Results

The test suite executes 15 comprehensive unit and integration tests covering mathematical formulas, universe filtering, batch scanning, indicators, and REST endpoints.

### Pytest Execution Summary:
```
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\New folder\AI Quant
plugins: anyio-4.14.2, asyncio-1.4.0

tests/test_engine.py::test_zone_detector_dbr_demand PASSED               [  6%]
tests/test_engine.py::test_freshness_evaluator_penetration PASSED        [ 13%]
tests/test_engine.py::test_spatial_overlap_achievements_threshold PASSED [ 20%]
tests/test_indicators.py::test_indicator_engine_atr PASSED               [ 26%]
tests/test_indicators.py::test_indicator_engine_emas_and_smas PASSED     [ 33%]
tests/test_pipeline_api.py::test_health_endpoint PASSED                  [ 40%]
tests/test_pipeline_api.py::test_scan_endpoint PASSED                    [ 46%]
tests/test_step2_api.py::test_universe_filtering PASSED                  [ 53%]
tests/test_step2_api.py::test_batch_run_endpoint PASSED                  [ 60%]
tests/test_step2_api.py::test_screener_shortlist_endpoint PASSED         [ 66%]
tests/test_step2_api.py::test_chart_candles_endpoint PASSED              [ 73%]
tests/test_step2_api.py::test_chart_zones_endpoint PASSED                [ 80%]
tests/test_trade_engine.py::test_trade_engine_demand_setup_math PASSED   [ 86%]
tests/test_trade_engine.py::test_trade_engine_supply_setup_math PASSED   [ 93%]
tests/test_trade_engine.py::test_trade_engine_not_approaching PASSED     [100%]

============================= 15 passed in 5.61s ==============================
```

### Mathematical Unit Test Assertions Verified:
1. **Demand Setup (`test_trade_engine_demand_setup_math`):**
   - Cluster: $[1000.0, 1050.0]$, ATR=25.0, Buffer=5.0, Current=1060.0.
   - Entry = $1050.0$, $\text{SL} = 995.0$, $R = 55.0$, $T_1 = 1160.0$, $T_2 = 1242.5$, $T_3 = 1325.0$.
   - $\text{Distance \%} = 0.94\%$, $\text{is\_approaching} = \text{True}$, $\text{has\_ma\_confluence} = \text{True}$.
2. **Supply Setup (`test_trade_engine_supply_setup_math`):**
   - Cluster: $[2000.0, 2080.0]$, ATR=50.0, Buffer=10.0, Current=1960.0.
   - Entry = $2000.0$, $\text{SL} = 2090.0$, $R = 90.0$, $T_1 = 1820.0$, $T_2 = 1685.0$, $T_3 = 1550.0$.
   - $\text{Distance \%} = 2.04\%$, $\text{is\_approaching} = \text{True}$, $\text{has\_ma\_confluence} = \text{True}$.
3. **Proximity Flag (`test_trade_engine_not_approaching`):**
   - Distance % = 5.0% (> 2.5%) $\implies \text{is\_approaching} = \text{False}$.

---

## 6. How to Run Locally

1. **Run Full Test Suite:**
   ```bash
   python -m pytest tests/ -v
   ```

2. **Start FastAPI Application:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. **Key API Endpoints:**
   - Swagger Documentation: `http://127.0.0.1:8000/docs`
   - Screener Shortlist: `GET http://127.0.0.1:8000/api/v1/screener/shortlist?min_achievements=2&approaching_only=true`
   - Resampled Candles: `GET http://127.0.0.1:8000/api/v1/charts/RELIANCE/candles?timeframe=125M&days=60`
   - Active Zones & Confluences: `GET http://127.0.0.1:8000/api/v1/charts/RELIANCE/zones?days=180`
   - Run EOD Batch Scan: `POST http://127.0.0.1:8000/api/v1/batch/run?min_achievements=2`
