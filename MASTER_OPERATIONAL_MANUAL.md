# HTF SUPPLY & DEMAND ZONE SCANNER TERMINAL — MASTER OPERATIONAL MANUAL
**System Version:** 4.0.0 PRO  
**Market Universe:** NSE Equities (NIFTY 500 / Market Cap $\ge$ ₹5,000 Cr)  
**Architecture:** Modular Asynchronous Monolith (Python / FastAPI / SQLAlchemy / React 18 / Lightweight Charts)  

---

## 1. System Overview & Core Philosophy
The **HTF Zone Scanner Terminal** is an institutional-grade quantitative platform that systematically scans, filters, and models higher-timeframe Supply and Demand zones across the National Stock Exchange (NSE) of India.

The platform strictly enforces:
1. **Multi-Timeframe Hierarchy:** Quarterly (`3M`), Monthly (`1M`), Weekly (`1W`), Daily (`1D`), 125-Minute (`125M`), and 75-Minute (`75M`).
2. **Strict Zero-Touch Freshness:** Only unpenetrated zones with 0 prior test touches qualify for trade plan admission.
3. **Geometric Spatial Overlap Confluence:** Only setups with **Achievements > 1** (Tier 2 Dual Confluence & Tier 3 Triple Confluence) are monitored.
4. **Deterministic Mathematical Risk Levels:** 
   - Entry Limit at Proximal Line
   - Stop Loss buffered by $0.20 \times \text{ATR}_{1\text{D}}(14)$ past the Common Distal Line
   - Multi-Tier Targets at $T_1 (2.0R), T_2 (3.5R), \text{ and } T_3 (5.0R)$.

---

## 2. Complete Step 1 to Step 8 Architecture Map

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                 HTF ZONE SCANNER PLATFORM                                 │
├───────────────────────────────┬─────────────────────────────┬─────────────────────────────┤
│ STEP 1: Foundation & Overlaps │ STEP 2: Batch Trade Engine  │ STEP 3: Alert Dispatcher    │
│ - MTF Resampling (3M - 75M)   │ - NIFTY 500 Market Cap Filter│ - Telegram Bot Dispatcher   │
│ - Strict Zero-Touch Freshness │ - Deterministic SL / Targets│ - Outbound Webhook Client   │
│ - Achievements > 1 Clusters   │ - 20/50 EMA & 200 SMA Nested│ - Idempotent Alert History  │
├───────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ STEP 4: Terminal UI & Themes  │ STEP 5: Multi-Grid & Shading│ STEP 6: Backtest & Hit-Rate │
│ - TradingView Lightweight Cht │ - 1x1, 1x2, 2x2 Split Panes │ - Walk-Forward Simulator    │
│ - Light / Dark Mode Toggle    │ - Canvas Zone Overlays      │ - Statistical Expectancy R  │
│ - NIFTY 500 Search Autocomp   │ - Time-Horizon Forecasting  │ - Tier Benchmark Comparison │
├───────────────────────────────┴─────────────────────────────┴─────────────────────────────┤
│ STEP 7: Macro Regime, Sector Rotation (MRS) & Derivatives (F&O) Intelligence              │
│ - 52-Week Mansfield Relative Strength (MRS) with 4-Quadrant Rotation Mapping              │
│ - Institutional FII/DII Net Flow Liquidity & Index Futures Long/Short (L/S) Ratio Meter   │
│ - Option Chain Strike-wise Open Interest, Max Pain Strike, Put Support & Call Walls       │
│ - Composite 0-100 Institutional Confluence Conviction Score                               │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│ STEP 8: Production Packaging, Scheduler Automation & System Hardening                     │
│ - Automated Daily EOD Scheduler (16:00 IST / Indian Market Close Trigger)                 │
│ - One-Click Desktop Batch Scripts (`start_terminal.bat` / `stop_terminal.bat`)            │
│ - Production Docker & Docker Compose Containerization (`nginx.conf`, `Dockerfile.*`)      │
│ - Real-Time System Diagnostics Endpoint (`/api/v1/system/status`)                         │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Quick Start & Operational Instructions

### A. 1-Click Windows Desktop Launch
Double-click `start_terminal.bat` in the project root:
- Starts the FastAPI backend daemon on `http://127.0.0.1:8000`.
- Starts the React + Vite frontend dev server on `http://localhost:5173`.
- Automatically opens your default web browser to the interactive terminal.
- To terminate all background services, run `stop_terminal.bat`.

### B. Production Docker Deployment
```bash
# Build and run containers in detached mode
docker-compose up --build -d

# View live logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### C. Developer Command Center (Makefile)
```bash
make test          # Run full pytest test suite (31+ tests)
make run-backend   # Start FastAPI server on port 8000
make run-frontend  # Start Vite frontend terminal
make scan          # Run on-demand full NIFTY 500 EOD scan
make build         # Compile production TypeScript frontend bundle
```

---

## 4. Daily EOD Automation Workflow (16:00 IST)

The background scheduler daemon (`scripts/scheduler_daemon.py`) runs automatically every trading day at **16:00 IST**:
1. Ingests completed daily OHLCV candles from NSE.
2. Resamples all multi-timeframe aggregations (`3M`, `1M`, `1W`, `1D`, `125M`, `75M`).
3. Evaluates zero-touch strict freshness and geometric spatial overlaps ($\text{Achievements} > 1$).
4. Updates 52-week Mansfield Relative Strength sector rankings.
5. Ingests daily FII/DII net flows and calculates the Index Futures L/S ratio.
6. Computes Option Chain Max Pain and Call/Put walls.
7. Evaluates proximity against active zones and dispatches immediate high-priority alerts to configured Telegram channels and outbound Webhooks.

---

## 5. API Reference & REST Endpoints

| Endpoint | Method | Purpose |
| :--- | :---: | :--- |
| `/api/v1/screener/shortlist` | `GET` | Returns deduplicated high-conviction trade plans ($\text{Achievements} > 1$). |
| `/api/v1/charts/{symbol}/candles` | `GET` | Supplies 7–10 year resampled OHLCV candle series for any timeframe. |
| `/api/v1/charts/{symbol}/zones` | `GET` | Supplies active fresh zones and multi-timeframe spatial overlap bounds. |
| `/api/v1/context/market-regime` | `GET` | Live FII/DII net cash flows, Long/Short ratio, and macro market regime. |
| `/api/v1/context/sectors` | `GET` | 52-week Mansfield Relative Strength (MRS) sector rankings and 4-quadrant mapping. |
| `/api/v1/context/fo/{symbol}` | `GET` | Option Chain Open Interest distribution, Max Pain strike, Put Floor & Call Wall. |
| `/api/v1/backtest/run` | `POST` | Executes walk-forward point-in-time backtesting simulation (1Y to 5Y). |
| `/api/v1/backtest/results/{id}` | `GET` | Returns backtest KPI metrics, equity curve points, and tier comparison matrix. |
| `/api/v1/system/status` | `GET` | System diagnostics, database record metrics, and component operational health. |

---

## 6. System Hardening & Acceptance Criteria
- [x] All 31 backend unit and integration test suites pass with a 100% success rate.
- [x] Zero TypeScript or Vite compilation errors in production build.
- [x] Real-time sub-second query responses across all terminal endpoints.
- [x] Complete multi-channel notification idempotency preventing duplicate alert spam.
