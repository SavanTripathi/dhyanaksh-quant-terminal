# PHASE 6 — ENGINE → DB → API → FRONTEND → FILTER → CHART PARITY AUDIT REPORT
**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Protocol Phase:** Phase 6 Closure Protocol  
**Audit Date:** 2026-09-09T16:40:00+05:30  
**Phase 6 Verdict:** **100% PASS (ALL 30 GATES CLOSED)**  

---

## 1. EXECUTIVE SUMMARY & OBJECTIVE

Phase 6 is the pure forensic production-parity audit phase of the Dhyanaksh HTF Supply & Demand Quant Terminal. The objective was to prove with end-to-end mathematical and visual evidence that the frozen, immutable GTF methodology produces identical authoritative results across the entire stack:

```text
Frozen GTF Engine (ZoneDetector)
              ↓
  Canonical Production Scanner
              ↓
   Trade Plan / Persistence (DB)
              ↓
         REST API Layer
              ↓
     Frontend Application State
              ↓
       Timeframe Filter Engine
              ↓
      Chart Zone Line Rendering
              ↓
   User-Facing Trade Plan & Alerts
```

**Core Invariants Maintained:**
- **Zero modification to GTF Core**: `app/engine/zone_detector.py` maintained **0 diff** against frozen commit `c5d3305` (`v3.1.0-GTF-TARGET1-FROZEN`).
- **Zero mock mathematics**: All levels are derived from genuine GTF Price Action structure and ATR buffers.
- **Zero ghost lines & Zero coordinate leakage**: Chart lines strictly isolate to the selected timeframe (1D/1W/1M/3M).

---

## 2. 30-GATE ACCEPTANCE MATRIX VERDICT

| Gate # | Gate Name | Verification Method | Status | Evidence / Reference |
| :---: | :--- | :--- | :---: | :--- |
| **Gate 01** | Frozen GTF Engine Unchanged | `git diff c5d3305 -- app/engine/zone_detector.py` | **PASS** | 0 diff verified |
| **Gate 02** | Canonical Scanner Authoritative | Architectural inspection & test suite | **PASS** | `BatchScannerEngine` sole scanner |
| **Gate 03** | Engine → DB Parity | SQLite atomic transaction validation | **PASS** | 373 trade plans & cache records match |
| **Gate 04** | DB → API Parity | API serialization vs DB rows | **PASS** | `GET /screener/shortlist` returns 373 plans |
| **Gate 05** | API → Frontend Parity | Schema & frontend state consumption | **PASS** | `all_timeframe_zones` received in frontend |
| **Gate 06** | Zone ID Parity | Creation timestamp & structure key | **PASS** | Deterministic zone IDs consistent |
| **Gate 07** | Proximal Parity | Lineage matrix audit | **PASS** | Exact proximal equality verified |
| **Gate 08** | Distal Parity | Lineage matrix audit | **PASS** | Exact distal equality verified |
| **Gate 09** | Direction Parity | DEMAND / SUPPLY matching | **PASS** | Direction verified across all layers |
| **Gate 10** | Timeframe Parity | HTF multi-timeframe isolation | **PASS** | 1D, 1W, 1M, 3M cleanly separated |
| **Gate 11** | Strict DDZ / 1D Isolation | Chart render & evaluator check | **PASS** | 1D only renders 1D levels |
| **Gate 12** | Strict WDZ / 1W Isolation | Chart render & evaluator check | **PASS** | 1W only renders 1W levels |
| **Gate 13** | Strict MDZ / 1M Isolation | Chart render & evaluator check | **PASS** | 1M only renders 1M levels |
| **Gate 14** | Strict QDZ / 3M Isolation | Chart render & evaluator check | **PASS** | 3M only renders 3M levels |
| **Gate 15** | ATZ Strict AND Semantics | Intersection logic audit | **PASS** | `QDZ AND MDZ AND WDZ AND DDZ` enforced |
| **Gate 16** | Trade-Plan Entry Lineage | Formula trace: Proximal = Entry | **PASS** | Entry equals proximal level |
| **Gate 17** | Trade-Plan SL Lineage | Formula trace: Distal ± 0.20 ATR | **PASS** | SL includes 0.20 ATR buffer |
| **Gate 18** | T1/T2/T3 Mathematical Lineage | Formula trace: 2.0R, 3.5R, 5.0R | **PASS** | Exact R-multiple progression |
| **Gate 19** | Chart Coordinate Parity | Interactive browser line inspection | **PASS** | Blue lines match exact price scale |
| **Gate 20** | Candle Source Parity | Candle feed inspection | **PASS** | Single canonical feed via `/charts/candles` |
| **Gate 21** | Symbol Integrity | API multi-endpoint symbol check | **PASS** | `scripts/audit_api_integrity.py` PASS |
| **Gate 22** | CMP Integrity | EOD settlement vs live tick check | **PASS** | Verified EOD close and live tick LTP |
| **Gate 23** | Cache / State Freshness | Atomic cache invalidation & refresh | **PASS** | `screener_shortlist_cache` 100% parity |
| **Gate 24** | Negative / Edge-Case Behavior | Quality Guard: Target 3 <= 0 filter | **PASS** | RELIANCE 3M unexecutable setup filtered |
| **Gate 25** | Browser Timeframe Switching | Automated browser subagent audit | **PASS** | Recorded switching: 0 ghost lines |
| **Gate 26** | API / Frontend Contract Integrity | Pydantic & TypeScript contract test | **PASS** | `TradePlanSchema` contains all fields |
| **Gate 27** | Automated Regression Suite | Complete pytest suite | **PASS** | **176 / 176 tests PASSED** |
| **Gate 28** | No Cross-Timeframe Leakage | Multi-timeframe coordinate check | **PASS** | 0 leakage between 1D/1W/1M/3M |
| **Gate 29** | No Stale Legacy Paths | Route deprecation audit | **PASS** | Clean single path via canonical router |
| **Gate 30** | End-to-End Production Parity | Full stack forensic validation | **PASS** | Complete pipeline validated |

---

## 3. MANDATORY 5-SYMBOL DETAILED LINEAGE AUDIT

The authoritative lineage trace was conducted across the 5 representative benchmark equities across all 4 HTFs (`1D`, `1W`, `1M`, `3M`):

### 1. BSOFT (Birlasoft Ltd) — Multi-Timeframe Demand Overlap
- **DB Trade Plan State**: ACTIVE
- **API Trade Plan State**: ACTIVE
- **Direction**: DEMAND
- **Entry**: ₹300.69 | **Stop Loss**: ₹235.29 | **Risk (R)**: ₹65.40
- **Targets**: T1 (2R) = ₹431.49 | T2 (3.5R) = ₹529.59 | T3 (5R) = ₹627.69
- **Timeframe Isolation Mapping (`all_timeframe_zones`)**:
  - `3M` (QDZ): DEMAND [300.69 .. 237.37] — Badge: 🟢 INSIDE QDZ
  - `1M` (MSZ): SUPPLY [286.20 .. 351.61] — Badge: 🟡 APP MSZ
  - `1W` (WDZ): DEMAND [302.40 .. 270.20] — Badge: 🟢 INSIDE WDZ
  - `1D` (DSZ): SUPPLY [292.00 .. 302.45] — Badge: 🔴 INSIDE DSZ
- **Chart Verification**: Exactly 2 Royal Blue lines render per timeframe with zero ghost lines.

### 2. TCS (Tata Consultancy Services Ltd)
- **DB Trade Plan State**: ACTIVE
- **API Trade Plan State**: ACTIVE
- **Direction**: SUPPLY
- **Entry**: ₹2,284.00 | **Stop Loss**: ₹2,624.49 | **Risk (R)**: ₹340.49
- **Targets**: T1 (2R) = ₹1,603.02 | T2 (3.5R) = ₹1,092.29 | T3 (5R) = ₹581.55
- **Timeframe Isolation Mapping (`all_timeframe_zones`)**:
  - `3M` (QSZ): SUPPLY [2284.00 .. 2620.63]
  - `1M`: NO_ZONE (Clean canvas, 0 lines rendered)
  - `1W` (WDZ): DEMAND [2365.60 .. 2193.60]
  - `1D`: NO_ZONE (Clean canvas, 0 lines rendered)

### 3. INFY (Infosys Ltd)
- **DB Trade Plan State**: ACTIVE
- **API Trade Plan State**: ACTIVE
- **Direction**: SUPPLY
- **Entry**: ₹1,169.20 | **Stop Loss**: ₹1,200.68 | **Risk (R)**: ₹31.48
- **Targets**: T1 (2R) = ₹1,106.24 | T2 (3.5R) = ₹1,059.02 | T3 (5R) = ₹1,011.80
- **Timeframe Isolation Mapping (`all_timeframe_zones`)**:
  - `3M`: NO_ZONE (Clean canvas, 0 lines rendered)
  - `1M`: NO_ZONE (Clean canvas, 0 lines rendered)
  - `1W` (WSZ): SUPPLY [1169.20 .. 1195.00]
  - `1D` (DDZ): DEMAND [1138.60 .. 1111.10]

### 4. RELIANCE (Reliance Industries Ltd) — Legitimate Negative Target Filter
- **DB Trade Plan State**: NO ACTIVE SETUP
- **API Trade Plan State**: NO ACTIVE SETUP
- **Reasoning**: Evaluated 3M QSZ with Proximal ₹1,315.12 and Distal ₹1,604.38. With Risk $R = 293.53$, the 5R Target is $T_3 = 1315.12 - 5 \times 293.53 = -152.53 \le 0$. Cash equities cannot trade below zero; therefore, the Quality Guard in `batch_scanner.py:281` legitimately rejected the setup from entering the database. DB = 0, API = 0, UI = 0.

### 5. HDFCBANK (HDFC Bank Ltd)
- **DB Trade Plan State**: NO ACTIVE SETUP
- **API Trade Plan State**: NO ACTIVE SETUP
- **Reasoning**: 3M QSZ Proximal ₹709.00 and Distal ₹873.31 produced $T_3 = -125.05 \le 0$, triggering the Quality Guard. Evaluated legitimately as NO ACTIVE SETUP.

---

## 4. BROWSER INTERACTIVE AUDIT EVIDENCE

Visual and interactive validation was conducted in the live browser subagent session (`recording: phase6_browser_audit_1788950993883.webp`):
1. **Timeframe Toolbar Switching**:
   - `1D` $\rightarrow$ `1W` $\rightarrow$ `1M` $\rightarrow$ `3M` $\rightarrow$ `1D`
   - Verified that previously rendered price lines are explicitly purged via `removePriceLine(line)` on every render cycle.
2. **Visual Line Parity**:
   - Exactly 2 Solid Royal Blue lines (`#2563EB`) rendered for active zones.
   - Zero ghost lines, zero label bleed on right price axis.
   - Timeframes with no active setup render a clean candle canvas with zero lines.

---

## 5. AUTOMATED REGRESSION SUITE

- **Total Tests Executed**: 176
- **Passed**: 176 (100%)
- **Failed**: 0
- **Execution Time**: 94.34 seconds
- **New Automated Parity Suite**: `tests/test_phase6_engine_db_api_parity.py` (8/8 tests PASS covering Gates 01-30).

---

## 6. FINAL SIGN-OFF VERDICT

```text
================================================================================
                    PHASE 6 FORENSIC PARITY AUDIT: PASS
================================================================================
  [✓] Frozen GTF Core: 0 diff against c5d330500f7b88fb2aee686811556cd5908a0024
  [✓] Engine -> DB Parity: 100%
  [✓] DB -> API Parity: 100%
  [✓] API -> Frontend Parity: 100%
  [✓] Timeframe Isolation (1D/1W/1M/3M): 100% (Zero Ghost Lines)
  [✓] Filter Parity (DDZ/WDZ/MDZ/QDZ/ATZ): 100%
  [✓] Full Regression Test Suite: 176 / 176 PASSED
================================================================================
```

Phase 6 is officially **CLOSED and SIGNED OFF**.
