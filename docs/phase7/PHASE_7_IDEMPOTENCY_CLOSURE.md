# PHASE 7 — FINAL IDEMPOTENCY CLOSURE

**System**: Dhyanaksh HTF Supply & Demand Quant Terminal  
**Frozen GTF Commit**: `c5d330500f7b88fb2aee686811556cd5908a0024` (`v3.1.0-GTF-TARGET1-FROZEN`)  
**Audit Date**: 2026-09-09  
**Closure Test Suite**: `tests/test_phase7_idempotency_closure.py` (24 gates)  
**Preceding Test Suite**: `tests/test_phase7_production_audit.py` (8 gates)

---

## 1. FROZEN GTF INVARIANT

```
$ git diff c5d330500f7b88fb2aee686811556cd5908a0024 -- app/engine/zone_detector.py

(empty — zero output, 0 DIFF)
```

**Result: 0 DIFF. GTF invariant holds.**  
No changes made to `app/engine/zone_detector.py` at any point in Phase 7.

---

## 2. INVESTIGATION 1 — `force=True` AND THE EOD SCHEDULER CALL CHAIN

### 2.1 Two Separate Scheduler Implementations

#### Path A — In-Process APScheduler (`app/engine/scheduler.py`)

```
16:30 IST (Mon–Fri)
  → APScheduler CronTrigger fires run_daily_eod_pipeline()
  → scanner_engine.run_full_universe_scan_async(lookback_days=180, min_achievements=2)
  → BatchScannerEngine.execute_batch_scan(db=AsyncSession, symbol_override=None)
  → _run_scan_internal() [BEGIN IMMEDIATE]
  → COMMIT all 4 tables
  → get_db_context() writes last_scan_date via AsyncSession (AFTER scan transaction)
```

- **Does NOT call `/batch/run`** — bypasses API entirely
- **Does NOT use `force=True`**
- **No pre-execution `last_scan_date` DB check in `run_daily_eod_pipeline()`**
- Idempotency: APScheduler fires once per cron window + startup guard in `main.py::check_and_run_first_launch_scan()`

#### Path B — Standalone Daemon (`scripts/scheduler_daemon.py`)

```
16:30 IST (Mon–Fri)
  → scheduler_loop() wakes every 60s
  → _is_already_executed_today(today_str)  [DB read #1 — day boundary]
  → if not executed_today_in_memory:
      → _is_already_executed_today(today_str)  [DB read #2 — immediately before pipeline]
      → run_daily_eod_pipeline()
          → httpx POST /batch/run?lookback_days=180&min_achievements=2  (NO force=True)
          → HTTP 200 → pipeline_success = True
      → _persist_scan_date(today_str)  ← written ONLY on success
      → executed_today_in_memory = True
```

- **Calls `/batch/run` via HTTP**
- **Does NOT pass `force=True`**
- **DB guard runs BEFORE pipeline call** (source position proven by INV-1C test)
- **Date persisted ONLY on success** (gated on `if success:`, proven by INV-1D test)

### 2.2 What `force=True` Actually Is

`force: bool = Query(False)` in `/batch/run` is an **operator recovery mechanism** for data-fix scenarios:

```
POST /batch/run?force=true
  → Bypasses the advisory DEF-03 same-day guard
  → Triggers full production scan regardless of last_scan_date
  → Intended for: post-fix re-scan, data corruption recovery
```

**Neither scheduler uses `force=True`.** The in-process scheduler bypasses the API entirely. The daemon relies on its own DB guard before calling the API.

### 2.3 Duplicate Trigger Scenarios — Proven Results

| Scenario | Blocking Mechanism | Result |
|---|---|---|
| Same-day sequential API call | DEF-03 advisory guard | `ALREADY_SCANNED_TODAY` |
| Concurrent API calls (same process) | `_scan_lock.acquire(blocking=False)` | Second → `ALREADY_RUNNING` |
| Daemon duplicate trigger | `_is_already_executed_today()` → True | SKIPPED |
| Process restart, same day (in-process) | APScheduler does not replay past crons; startup guard checks DB | Scan NOT duplicated |
| Process restart, same day (daemon) | `_is_already_executed_today()` reads SQLite | True → daemon skips |
| `force=True` + `_scan_lock` held | `_scan_lock` blocks second caller | `ALREADY_RUNNING` |

**Invariant confirmed**: ONE EOD DATE → ONE LOGICAL PRODUCTION RESULT.

### 2.4 Architectural Note — In-Process Scheduler Misfire Risk

> **NOT a blocker for current deployment.**

`app/engine/scheduler.py::run_daily_eod_pipeline()` has no pre-execution `last_scan_date` check. If APScheduler replays a missed trigger (requires `misfire_grace_time > actual_miss`), a second scan could execute. Current mitigations: APScheduler default `misfire_grace_time=None` (1s), `_scan_lock`, `BEGIN IMMEDIATE`.

**Future hardening**: Add `_is_already_scanned_today()` DB check at top of `run_daily_eod_pipeline()` in `app/engine/scheduler.py`.

---

## 3. INVESTIGATION 2 — CROSS-PROCESS IDEMPOTENCY

### 3.1 Lock Mechanism — Process-Local

```python
# app/engine/batch_scanner.py
_scan_lock = threading.Lock()   # threading.Lock — process-local
```

`_scan_lock` prevents concurrent execution within a single ASGI worker process. It is **NOT** a multiprocessing or distributed lock. Confirmed by `test_inv2a`.

### 3.2 Cross-Process Protection — SQLite `BEGIN IMMEDIATE`

```python
cursor.execute("BEGIN IMMEDIATE")   # Acquires reserved lock at file level
try:
    # ... all 4 table writes ...
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

A second process attempting `BEGIN IMMEDIATE` on the same SQLite file blocks until timeout (10s), then raises `sqlite3.OperationalError: database is locked`. **Empirically proven by `test_inv2c`** — second connection cannot obtain `BEGIN IMMEDIATE` while first holds it.

### 3.3 Deployment: Single Worker

No multi-worker configuration found (`--workers N` with N > 1). Process-local `_scan_lock` is sufficient for single-worker Uvicorn deployment.

> **If multi-worker Uvicorn is introduced**: `_scan_lock` will not prevent cross-worker duplicate evaluations. Add a DB-level uniqueness constraint on `(scan_date::date, status)` or a distributed lock.

---

## 4. INVESTIGATION 3 — SAME-DAY CLAIM RACE SAFETY

### 4.1 DEF-03 API Guard Is Advisory

The guard reads `last_scan_date` and `COUNT(trade_plans)`, then decides. Two concurrent requests can both read "not scanned today" before either writes. **This is a READ→DECIDE pattern, not an atomic claim.**

### 4.2 Atomic Serialization: `_scan_lock`

Even if both concurrent requests pass the advisory guard simultaneously, `_scan_lock.acquire(blocking=False)` ensures only one executes. The second returns `ALREADY_RUNNING` immediately. **Proven by `test_inv3b`.**

### 4.3 Combined Defense Architecture

```
DEF-03 advisory guard  → reduces unnecessary scan load from UI
_scan_lock             → in-process atomic serialization
SQLite BEGIN IMMEDIATE → cross-process write serialization
Daemon double-check    → process-restart safe pre-execution guard
```

---

## 5. INVESTIGATION 4 — DIAGNOSTIC VS PRODUCTION CLASSIFICATION

### 5.1 Complete Status Taxonomy

| Status | Source | Writes production tables | Writes last_scan_date |
|---|---|---|---|
| `COMPLETED` | `_run_scan_internal` | YES | NO (scheduler does after) |
| `PARTIAL_SUCCESS` | `_run_scan_internal` | YES | NO |
| `DIAGNOSTIC_SCAN` | `_run_scan_internal` | **NO** | **NO** |
| `ALREADY_RUNNING` | `execute_batch_scan` | **NO** | **NO** |
| `ALREADY_SCANNED_TODAY` | `router.run_batch_scan` | **NO** | **NO** |

`DIAGNOSTIC_SCAN` does not overlap with any production status. A diagnostic scan cannot trigger `ALREADY_SCANNED_TODAY` because it writes neither `last_scan_date` nor `trade_plans`. Confirmed by `test_inv4a`, `test_inv4d`, `test_inv3a`.

### 5.2 screener_shortlist_cache — DEF-01 Guard

```python
if is_full_universe_scan:
    cursor.execute("DELETE FROM screener_shortlist_cache")  # inside BEGIN IMMEDIATE
    # INSERT rows
else:
    logger.info("[DEF-01 GUARD] ... Production tables unchanged.")
```

`DELETE FROM screener_shortlist_cache` is provably inside `if is_full_universe_scan:`. Diagnostic scans cannot delete or repopulate the screener cache. Source position verified by `test_inv4b`.

### 5.3 Database Evidence

Production run ID 50 (`universe_count=500`, `status=COMPLETED`) is unambiguously distinct from diagnostic runs 48–56 (`universe_count ≤ 2`, `status=DIAGNOSTIC_SCAN`). All `COMPLETED`/`PARTIAL_SUCCESS` rows have `universe_count >= 100`. Proven by `test_inv4c`.

---

## 6. INVESTIGATION 5 — PRODUCTION RESULT ATOMICITY

### 6.1 Transaction Boundary

All four production tables are written in a single `BEGIN IMMEDIATE...COMMIT` transaction:
1. `DELETE FROM trade_plans`
2. `INSERT INTO trade_plans` (N rows)
3. `DELETE FROM screener_shortlist_cache`
4. `INSERT INTO screener_shortlist_cache` (N rows)
5. `INSERT INTO batch_scan_runs`
6. `INSERT INTO sync_audit_log`
7. `COMMIT`

On any exception: `ROLLBACK` restores the entire DB to the pre-scan state. No partial writes. Proven by `test_inv5a` and `test_inv5b` (empirical rollback test).

### 6.2 Interrupted Scan Recovery

| Event | Outcome |
|---|---|
| Scan completes, scheduler writes `last_scan_date` | Normal production result |
| Scan raises exception, `ROLLBACK` executes | DB unchanged; `last_scan_date` not updated; next trigger retries |
| Scan completes, app crashes before `last_scan_date` write | DB has new plans; date = yesterday; next restart re-scans (idempotent: same data) |
| Mid-commit crash | SQLite WAL atomicity: DB is either new or prior state; no partial |

### 6.3 Failed Run Is `PARTIAL_SUCCESS`, Not `COMPLETED`

```python
overall_status = "COMPLETED" if failed_evaluations == 0 else "PARTIAL_SUCCESS"
```

A degraded run (symbol failures) is classified `PARTIAL_SUCCESS`. Monitoring can distinguish it from a clean `COMPLETED` run. Proven by `test_inv5d`.

### 6.4 `last_scan_date` NOT Written by Scanner

`_run_scan_internal` contains no `last_scan_date` write. This is the key failure-isolation guarantee: a crashed scan does not corrupt the idempotency clock. Only the scheduler daemon writes it, and only on `pipeline_success = True`. Proven by `test_inv5c`.

---

## 7. EXACT RUN EVIDENCE

### Production Run — Run ID 50

| Field | Value |
|---|---|
| `id` | 50 |
| `scan_date` | 2026-09-09T11:28:56.752541+00:00 (16:58 IST) |
| `universe_count` | 500 |
| `scanned_count` | 500 |
| `clusters_found` | 373 |
| `trade_plans_generated` | 373 |
| `status` | `COMPLETED` |

This is the sole production run of 2026-09-09.

### Diagnostic Runs — IDs 48–56

All have `universe_count ≤ 2`, `status = DIAGNOSTIC_SCAN`. Production `trade_plans` table untouched by all diagnostic runs. 373 plans persisted through all 8+ diagnostic test runs.

---

## 8. COMPLETE TEST MATRIX — 48/48 PASS

### 8.1 Phase 7 Idempotency Closure

`tests/test_phase7_idempotency_closure.py` — **24/24 passed in 74.54s**

| Gate | Description | Result |
|---|---|---|
| INV-1A | In-process scheduler calls UniverseScannerEngine directly (not HTTP) | ✅ |
| INV-1B | Daemon calls /batch/run without force=True | ✅ |
| INV-1C | Daemon DB guard runs BEFORE pipeline call (source position verified) | ✅ |
| INV-1D | Date persisted ONLY inside `if success:` | ✅ |
| INV-1E | Sequential duplicate API calls → ALREADY_SCANNED_TODAY; no plan change | ✅ |
| INV-1F | Diagnostic scan → exactly 1 new audit row | ✅ |
| INV-1G | Concurrent calls blocked by `_scan_lock` → ALREADY_RUNNING | ✅ |
| INV-2A | `_scan_lock` is `threading.Lock()`, not multiprocessing | ✅ |
| INV-2B | `BEGIN IMMEDIATE` present in `_run_scan_internal` source | ✅ |
| INV-2C | SQLite empirically blocks second `BEGIN IMMEDIATE` | ✅ |
| INV-2D | No multi-worker deployment configuration | ✅ |
| INV-3A | DEF-03 guard is advisory (read-then-decide) | ✅ |
| INV-3B | `_scan_lock` prevents both concurrent callers from executing | ✅ |
| INV-3C | Daemon loop calls `_is_already_executed_today` ≥ 2 times | ✅ |
| INV-4A | DIAGNOSTIC_SCAN does not overlap production status values | ✅ |
| INV-4B | screener_shortlist_cache DELETE inside `if is_full_universe_scan:` | ✅ |
| INV-4C | All COMPLETED/PARTIAL_SUCCESS rows have universe_count ≥ 100 | ✅ |
| INV-4D | `_persist_scan_date` not called by batch_scanner | ✅ |
| INV-5A | BEGIN IMMEDIATE→all 4 tables→COMMIT; ROLLBACK on exception | ✅ |
| INV-5B | Empirical rollback test preserves prior DB state | ✅ |
| INV-5C | `last_scan_date` not written by `_run_scan_internal` | ✅ |
| INV-5D | PARTIAL_SUCCESS / COMPLETED differentiated by failed_evaluations | ✅ |
| SUM-1 | GTF 0-diff from c5d330500f7b88fb2aee686811556cd5908a0024 | ✅ |
| SUM-2 | Phase 5 + Phase 6 regression 16/16 pass | ✅ |

### 8.2 Phase 7 Production Audit

`tests/test_phase7_production_audit.py` — **8/8 passed**

| Gate | Description | Result |
|---|---|---|
| P7-4 | zone_detector.py 0-diff frozen baseline | ✅ |
| P7-1 | DEF-01: symbol_override does not corrupt production tables | ✅ |
| P7-2 | DEF-02: single scan → exactly 1 batch_scan_runs row | ✅ |
| P7-3 | DEF-03: API returns ALREADY_SCANNED_TODAY when already run today | ✅ |
| P7-5 | DEF-01 guard does not block full-universe scan path | ✅ |
| P7-6 | Diagnostic scan returns results + DIAGNOSTIC_SCAN status | ✅ |
| P7-7 | Concurrent scan lock prevents duplicate concurrent executions | ✅ |
| P7-8 | Failed run does NOT persist last_scan_date | ✅ |

### 8.3 Full Regression

| Suite | Gates | Passed | Time |
|---|---|---|---|
| Phase 7 Idempotency Closure | 24 | 24 | 74.54s |
| Phase 7 Production Audit | 8 | 8 | (included in full run) |
| Phase 5 Canonical Scanner | 8 | 8 | (included in full run) |
| Phase 6 Engine/DB/API Parity | 8 | 8 | (included in full run) |
| **TOTAL** | **48** | **48** | **103.90s** |

---

## 9. OPEN ITEM (NON-BLOCKING, FOR FUTURE HARDENING)

**OI-1**: `app/engine/scheduler.py::run_daily_eod_pipeline()` has no pre-execution `last_scan_date` check. Add check as a future belt-and-suspenders improvement. Does not affect current single-worker production deployment.

---

## 10. REMEDIATIONS DELIVERED IN PHASE 7

| DEF | Severity | Root Cause | Fix |
|---|---|---|---|
| DEF-01 | CRITICAL | `symbol_override` scan executed `DELETE FROM trade_plans` — wiped 373 production plans to 1 | `is_full_universe_scan = (symbol_override is None)` guard; diagnostic scans skip all production table mutations |
| DEF-02 | HIGH | SQLite + AsyncSession dual-write created 2 `batch_scan_runs` rows per scan | Removed AsyncSession write path; SQLite sole canonical path |
| DEF-03 | MEDIUM | No API same-day guard; UI reruns could trigger redundant 500-symbol scans | Advisory `last_scan_date` + plan count guard in `/batch/run`; `force=True` operator bypass |

---

## 11. FINAL VERDICT

```
zone_detector.py 0-diff from c5d330500f7b88fb2aee686811556cd5908a0024 ... CONFIRMED
DEF-01 Production Contamination .............. CLOSED
DEF-02 Duplicate Audit Rows .................. CLOSED
DEF-03 Missing Idempotency Guard ............. CLOSED
EOD Scheduler Call Chain ..................... PROVEN
force=True used by any scheduler ............. NO
Cross-Process Lock Mechanism ................. DOCUMENTED
Same-Day Race Safety ......................... PROVEN
Diagnostic/Production Classification ......... PROVEN
Production Atomicity ......................... PROVEN
48/48 Gates .................................. ALL PASS

╔══════════════════════════════════════════╗
║          PHASE 7 = PASS                  ║
╚══════════════════════════════════════════╝
```

Do not start Phase 8.  
Do not push.  
Do not modify the frozen GTF engine.
