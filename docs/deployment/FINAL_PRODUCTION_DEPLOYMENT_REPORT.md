# FINAL PRODUCTION DEPLOYMENT & GO-LIVE REPORT

**System**: Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Execution Stage**: FINAL CONTROLLED GO-LIVE & DEPLOYMENT PROTOCOL  
**Deployment Date**: 2026-09-09  
**Frozen Baseline Tag**: `v3.1.0-GTF-TARGET1-FROZEN`  
**Frozen Commit**: `c5d330500f7b88fb2aee686811556cd5908a0024`  
**Accepted Production HEAD**: `f444ebd0c7932bc61e16f7ee1a8f902636fcb993`  

---

## A. Git State Verification

| Metric | Required Specification | Observed State | Status |
| :--- | :--- | :--- | :---: |
| **Current HEAD** | `f444ebd0c7932bc61e16f7ee1a8f902636fcb993` | `f444ebd0c7932bc61e16f7ee1a8f902636fcb993` | **PASS** |
| **Active Branch** | `main` | `main` | **PASS** |
| **ZoneDetector Diff** | `0 DIFF` from `c5d3305` | `git diff c5d3305 -- app/engine/zone_detector.py` = **0 DIFF** | **PASS** |
| **Working Tree Hygiene** | No uncommitted analytical/theory changes | Uncommitted changes strictly limited to Phase 5–8 audits & docs | **PASS** |

---

## B. Complete System Regression

- **Exact Execution Command**:
  ```bash
  python -m pytest tests/test_phase5_canonical_scanner.py tests/test_phase6_engine_db_api_parity.py tests/test_phase7_production_audit.py tests/test_phase7_idempotency_closure.py tests/test_phase8_acceptance.py -v --tb=short -q
  ```
- **Collected Test Count**: 57 items
- **Passed Test Count**: **57 items (100.0%)**
- **Failed Test Count**: **0 items (0.0%)**
- **Errors**: **0 errors**
- **Unresolved Tests**: **0**
- **Execution Duration**: **95.55 seconds (0:01:35)**

---

## C. Canonical Production-Equivalent Scan Telemetry

- **Assigned Run ID**: `96`
- **Execution Timestamp (UTC)**: `2026-09-09T13:04:11.016173Z`
- **IST Trading Date**: `2026-09-09`
- **Master Universe Target**: 500 equities
- **Scanned Equities**: 500 / 500 (100.0%)
- **Timeframe Evaluations**: 2,000 / 2,000 (1D, 1W, 1M, 3M)
- **Evaluation Failures**: **0**
- **Trade Plans Generated**: 373 active setups
  - **Demand Setups**: 225
  - **Supply Setups**: 148
  - **ATZ Confluence Setups**: 89
- **Execution Duration**: 165.47 seconds (~2.75 minutes)
- **Persistence Outcome**: `COMPLETED`

---

## D. Multi-Run Determinism Verification

Comparison of repeated full scans under identical static inputs:

| Metric | Run A | Run B | Run C | Observed Drift |
| :--- | :--- | :--- | :--- | :---: |
| **Evaluated Universe** | 500 | 500 | 500 | **0.00%** |
| **Evaluation Count** | 2,000 | 2,000 | 2,000 | **0.00%** |
| **Total Setups Generated** | 373 | 373 | 373 | **0.00%** |
| **Demand Setups** | 225 | 225 | 225 | **0.00%** |
| **Supply Setups** | 148 | 148 | 148 | **0.00%** |
| **ATZ Setups** | 89 | 89 | 89 | **0.00%** |
| **BSOFT Trade Plan** | Entry 300.69 / SL 235.29 / T1 431.49 / T2 529.59 / T3 627.69 | Identical | Identical | **0.00%** |
| **TCS Trade Plan** | Entry 2284.0 / SL 2633.11 / T1 1585.78 / T2 1062.12 / T3 538.45 | Identical | Identical | **0.00%** |
| **INFY Trade Plan** | Entry 1169.2 / SL 1200.68 / T1 1106.24 / T2 1059.02 / T3 1011.80 | Identical | Identical | **0.00%** |

**Unexplained Drift**: **0.00%**.

---

## E. End-to-End Data Lineage & Boundary Parity

Lineage across **ZoneDetector $\to$ Trade Plan $\to$ SQLite $\to$ API $\to$ Frontend $\to$ Chart**:

1. **Database Integrity**:
   - `trade_plans` row count: **373**
   - `screener_shortlist_cache` row count: **373**
   - Duplicate symbol count: **0**
   - Orphan records: **0**
   - Negative Target 3 setups ($T_3 \le 0$): **0**
2. **API Parity**:
   - `GET /api/v1/screener/shortlist?limit=500` delivers all 373 plans.
   - Parity variance against SQLite database: **0 / 373 (100.0% match)**.
3. **Frontend Presentation**:
   - React Screener table renders 373 setups.
   - Live CMP, badges, and risk-reward ratios mirror API payload bitwise.
4. **Timeframe Isolation**:
   - Chart zone lines rendered strictly from `all_timeframe_zones[selectedTimeframe]`.
   - Cross-timeframe leakage count: **0**.
   - Ghost / stale lines count: **0**.

---

## F. Deployment & Production Build Verification

1. **Frontend Production Build**:
   - Command: `npm run build` (`tsc && vite build`)
   - Module Transformation: **1,675 modules transformed**
   - Output Bundle: `dist/index.html`, `dist/assets/index-BPnRcnlC.css`, `dist/assets/index-CcKIjcgE.js`
   - TypeScript Compilation Errors: **0**
   - Build Duration: **31.17 seconds**
2. **Backend Runtime Validation**:
   - FastAPI server operational on port 8000.
   - Database connection pool verified on `production_scanner.db`.
   - Scheduler initialized for **16:30 IST Monday–Friday (`Asia/Kolkata`)**.
3. **Smoke Test on Representative Stocks**:
   - **BSOFT**: DEMAND active plan, ATZ 4-HTF confluence, Entry ₹300.69, SL ₹235.29.
   - **TCS**: SUPPLY active plan, 2-HTF confluence, Entry ₹2,284.00, SL ₹2,633.11.
   - **INFY**: SUPPLY active plan, 2-HTF confluence, Entry ₹1,169.20, SL ₹1,200.68.
   - **RELIANCE & HDFCBANK**: Filtered out cleanly (no unviable/negative target setups manufactured).

---

## G. Final Go-Live Verdict

```text
╔══════════════════════════════════════════════════════════╗
║                    GO-LIVE APPROVED                      ║
╚══════════════════════════════════════════════════════════╝
```

The Dhyanaksh HTF Supply & Demand Quant Terminal is fully verified, frozen, deterministic, and approved for production go-live. Controlled production observation is now initiated.
