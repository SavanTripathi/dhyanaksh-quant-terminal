# 🛡️ PHASE 10.2I — ADVERSARIAL FAILURE-INJECTION SAFETY AUDIT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Scope:** Adversarial Stress Testing against Isolated Test Ledgers  
**Safety Gate:** `ENABLE_LIVE_BROKER_EXECUTION=false`

---

## 1. ADVERSARIAL TEST MATRIX (ISOLATED RUNS)

| Failure Category | Injected Adversarial Condition | Expected Behavior | Actual Behavior | Result | Exit Code | Ledger Mutation |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **Timing** | Execution at 09:00 IST | Prospective write forbidden | Blocked (`MARKET_NOT_FINALIZED_ABORT`) | **PASS** | 1 | None |
| **Timing** | Execution at 15:44 IST | Prospective write forbidden | Blocked (`MARKET_NOT_FINALIZED_ABORT`) | **PASS** | 1 | None |
| **Timing** | Execution at 16:00 IST | Prospective evaluation permitted | Permitted with complete EOD bars | **PASS** | 0 | Expected EOD snapshot |
| **Data Outage** | Feed timeout / network drop | Fail closed safely | Logged `STALE_FEED_ABORT` | **PASS** | 1 | None |
| **Data Corrupt** | Corrupted OHLC range (>3x median) | Anomaly spike filtered | Stripped by spike anomaly filter | **PASS** | 0 | Clean evaluation |
| **Safety** | Candidate hash mismatch | Immediate hard abort | Assert failed on manifest hash | **PASS** | 1 | None |
| **Safety** | `ENABLE_LIVE_BROKER_EXECUTION=true` | Immediate hard abort | Hard gate caught & terminated | **PASS** | 1 | None |
| **Concurrency** | Duplicate run on same date | Idempotent skip | Detected `FINALIZED_EOD` and exited | **PASS** | 0 | None (Zero duplicate) |
| **Mode** | Default manual CLI invocation | Read-only dry run | Ingested data without writing ledgers | **PASS** | 0 | None |
