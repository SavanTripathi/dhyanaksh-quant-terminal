# PHASE 6 — REPOSITORY & ARCHITECTURE MAP
**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Subphase:** 6A — Complete Pipeline Path Architecture Establishment  
**Date:** 2026-09-09  

---

## 1. PIPELINE OVERVIEW & DATA FLOW

```text
Frozen GTF Engine (ZoneDetector)
      │
      ▼
Canonical Production Scanner (BatchScannerEngine: 500 Equities × 4 HTFs = 2,000 evaluations)
      │
      ├── Quality Guard (Rejects unexecutable setups where T3 <= 0)
      │
      ▼
Atomic Persistence Layer (Single SQLite Transaction)
      ├── Primary Table: trade_plans (Full 369 active qualified setups)
      ├── Derived Table: screener_shortlist_cache (Atomically synchronized JSON documents)
      ├── Audit Tables : batch_scan_runs, sync_audit_log
      │
      ▼
REST API Layer (FastAPI: app/api/v1/router.py)
      ├── GET /api/v1/screener/shortlist (Reads trade_plans; query params: min_achievements, direction, etc.)
      ├── GET /api/v1/charts/{symbol}/quote (Real-time verified NSE quotes with prev_close & change)
      ├── GET /api/v1/charts/{symbol}/candles (Timeframe-isolated candles: 1D, 1W, 1M, 3M, 125M, 75M)
      ├── GET /api/v1/charts/{symbol}/zones (Timeframe-isolated zone boundaries & clusters)
      └── GET /api/v1/system/cached-shortlist (Reads screener_shortlist_cache directly)
      │
      ▼
Frontend Client & State Layer (React + TypeScript: frontend/src/)
      ├── API Client: frontend/src/services/api.ts
      ├── State Engine: frontend/src/App.tsx (selectedSymbol, timeframe, activeTradePlan, allPlans, filteredPlans)
      │
      ├── Filter Engine: frontend/src/components/screener/FilterBar.tsx
      │     └── Evaluator: frontend/src/utils/zoneEvaluator.ts (Near DDZ, WDZ, MDZ, QDZ, ATZ)
      │
      ├── Shortlist UI: frontend/src/components/screener/ScreenerTable.tsx
      │
      ├── Interactive Chart: frontend/src/components/chart/TradingViewChart.tsx
      │     └── Timeframe Switcher: frontend/src/components/chart/TimeframeToolbar.tsx
      │
      └── Trade Plan / Projection: frontend/src/components/projection/TradeProjectionCard.tsx
```

---

## 2. COMPONENT SOURCE FILE & RESPONSIBILITY MAPPING

### 1. Engine Layer
- **`app/engine/zone_detector.py`**:
  - `ZoneDetector.detect_zones(candles: List[CandleSchema]) -> List[ZoneSchema]`
  - Frozen GTF baseline commit `c5d330500f7b88fb2aee686811556cd5908a0024` (0 diff).
- **`app/engine/freshness_evaluator.py`**:
  - `FreshnessEvaluator.evaluate_zone_freshness(zone, candles) -> ZoneFreshnessResult`
  - Evaluates touch count, breach status, and GTF scoring.
- **`app/engine/trade_engine.py`**:
  - Authoritative trade plan formula reference ($E = \text{proximal}$, $\text{SL} = \text{distal} \pm \text{buffer}$, $T_1 = 2R$, $T_2 = 3.5R$, $T_3 = 5R$).

### 2. Canonical Production Scanner Layer
- **`app/engine/batch_scanner.py`**:
  - `BatchScannerEngine`: Single authoritative scanner.
  - `evaluate_stock_canonical(sym, name, lookback_days)`:
    - Evaluates strictly 4 HTFs (1D, 1W, 1M, 3M) = 4 GTF evaluations per stock.
    - Computes daily ATR-14 and ATR buffer ($0.20 \times \text{ATR}$).
    - Calculates Entry, SL, $T_1$, $T_2$, $T_3$.
    - Applies Setup Quality Guard: rejects setups where $T_3 \le 0$ (untradeable 5R price).
  - `execute_batch_scan(db, ...)`:
    - 10-worker concurrent execution across NIFTY 500.
    - Atomic SQLite transaction: deletes and inserts `trade_plans`, `screener_shortlist_cache`, `batch_scan_runs`, `sync_audit_log`.

### 3. Persistence Layer
- **Database File**: `production_scanner.db` (SQLite)
- **`app/domain/models.py`**:
  - `TradePlanModel`: `symbol`, `direction`, `entry_price`, `stop_loss`, `risk_per_share`, `target_1`, `target_2`, `target_3`, `overlap_min_price`, `overlap_max_price`, `achievements`, `participating_timeframes`, `conviction_score`, `is_approaching`, `has_opposing_violation`, etc.
  - `BatchScanRunModel`: Records run ID, scan date, universe count, scanned count, duration, status.
  - `SymbolCandlesCacheModel`: Resampled candle caches for fast loading.
- **`screener_shortlist_cache` table**: Atomically synced JSON records for fast UI retrieval.

### 4. API Layer
- **`app/api/v1/router.py`**:
  - `GET /screener/shortlist`: Queries `trade_plans` filtered by `min_achievements`, `direction`, `approaching_only`, `opposing_violation_only`, `deduplicate`, `limit`. Returns `ScreenerShortlistResponse(total_plans, approaching_plans_count, plans)`.
  - `GET /screener/top-picks`: Returns top-conviction picks filtered by `min_score`.
  - `GET /charts/{symbol}/quote`: Official live quote (CMP, prev_close, change, change_pct).
  - `GET /charts/{symbol}/candles`: Resampled mode-aware OHLCV candles (1D, 1W, 1M, 3M, 125M, 75M).
  - `GET /charts/{symbol}/zones`: Detected fresh zones and spatial overlap clusters.
  - `POST /system/sync-eod`: Production 16:30 IST idempotent trigger.
  - `GET /system/cached-shortlist`: Direct dump from `screener_shortlist_cache`.

### 5. Frontend Layer
- **`frontend/src/services/api.ts`**: Axios client pointing to `/api/v1`.
  - `fetchScreenerShortlist`: Calls `/screener/shortlist`.
  - `fetchCandles`: Calls `/charts/{symbol}/candles`.
  - `fetchZones`: Calls `/charts/{symbol}/zones`.
  - `fetchQuote`: Calls `/charts/{symbol}/quote`.
- **`frontend/src/App.tsx`**:
  - Central state orchestration.
  - `loadScreener`: Loads shortlist plans and selects top setup.
  - `loadChartData`: Fetches candles and zones for `selectedSymbol` and `timeframe`.
- **`frontend/src/components/screener/FilterBar.tsx`**:
  - Quick filter tabs: Near DDZ, Near WDZ, Near MDZ, Near QDZ, ATZ, Score $\ge$ 85, Top 3, Top 5.
- **`frontend/src/utils/zoneEvaluator.ts`**:
  - `evaluateZoneMatch(plan, filterType)`: Matches specific timeframe flags (`has_ddz`, `has_wdz`, `has_mdz`, `has_qdz`).
  - `evaluateATZMatch(plan)`: Strict All-Timeframe Zone confluence: `QDZ AND MDZ AND WDZ AND DDZ`.
- **`frontend/src/components/screener/ScreenerTable.tsx`**:
  - Shortlist display table rendering Symbol, Direction badge, CMP, Entry, SL, T1, Score, Achievements.
- **`frontend/src/components/chart/TradingViewChart.tsx`**:
  - Lightweight-charts container.
  - Renders timeframe-isolated zone bounds (Solid Royal Blue lines `#2563EB`).
  - Renders trade plan overlay ($T_1$, $T_2$, $T_3$, SL) on demand.
  - Clears all previous price lines on timeframe change to prevent coordinate bleed.
- **`frontend/src/components/chart/TimeframeToolbar.tsx`**:
  - Timeframe selection buttons (3M, 1M, 1W, 1D, 125M, 75M).
- **`frontend/src/components/projection/TradeProjectionCard.tsx`**:
  - Displays Entry, Stop Loss, Risk, Targets ($2R$, $3.5R$, $5R$), Reward-to-Risk ratio.
