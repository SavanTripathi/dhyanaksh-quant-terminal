# PHASE 8 — FAILURE RECOVERY & ATOMIC ROLLBACK SMOKE TEST

**System**: Dhyanaksh HTF Supply & Demand Quant Terminal  
**Audit Date**: 2026-09-09  
**Phase**: PHASE 8 — FINAL END-TO-END PRODUCTION ACCEPTANCE  
**Target Gate**: **G26** (Failure/Recovery Smoke Test PASS)  

---

## 1. Executive Summary & Forensic Verification

The robustness of the Dhyanaksh persistence engine was evaluated under simulated crash, network interruption, and mid-transaction failure scenarios.  
**Result**: In all simulated failure conditions:
- **No false `COMPLETED` state**: Unfinished scans are flagged `FAILED` or `PARTIAL_SUCCESS`.
- **No false `last_scan_date`**: The EOD date clock is written only upon full completion.
- **No partial production dataset**: The database is atomically rolled back to its exact pre-failure state.
- **Gate G26 Verdict**: **PASS**

---

## 2. Forensic Failure Scenarios & Behavioral Evidence

### Scenario A: Exception During Batch Write (Atomic Rollback)
- **Injection**: Simulated runtime exception during insertion of setup #150 of 373 into `trade_plans`.
- **Expected Behavior**: The `try...except` block in `_run_scan_internal()` catches the error, calls `conn.rollback()`, closes the connection, and re-raises.
- **Observed Result**:
  - `trade_plans` retained its pre-failure rows.
  - Zero partial setups were persisted.
  - `screener_shortlist_cache` remained synchronized with `trade_plans`.

### Scenario B: Process Crash / Mid-Execution Termination
- **Condition**: Process terminated during worker thread evaluation (before persistence).
- **Observed Result**:
  - `system_meta.last_scan_date` was **NOT** updated.
  - On restart, the same-day scheduler guard detects that no completed scan exists for today and permits a clean retry.
  - Retried execution completes without orphaned records or corrupted keys.

### Scenario C: Concurrent Scan Interception (Non-Blocking Lock)
- **Condition**: Two triggers invoked simultaneously on the same process.
- **Observed Result**:
  - Worker 1 acquires `_scan_lock`.
  - Worker 2 fails non-blocking acquisition (`_scan_lock.acquire(blocking=False)` returns `False`).
  - Worker 2 returns `BatchScanRunSchema(status="ALREADY_RUNNING")` immediately without waiting or thrashing CPU.
  - When Worker 1 completes, the lock is guaranteed released in the `finally:` block.

---

## 3. Database Journal Mode & Lock Configuration

The production database connection enforces:
- **Journal Mode**: `WAL` (Write-Ahead Logging) or standard atomic journal ensuring concurrent readers are never blocked by writes.
- **Busy Timeout**: 10,000 ms (`timeout=10`), allowing graceful waiting for transient write locks without immediate `OperationalError: database is locked`.

---

## 4. Formal Verdict

- **G26 (Failure/Recovery Smoke Test)**: **PASS**
