# ⚙️ PHASE 10.2G — IDEMPOTENCY & FINALIZED EOD STATE MACHINE SPECIFICATION

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Subsystem:** Daily Snapshot Idempotency Engine

---

## 1. GRANULAR DATE STATES

The daily ledger primary key transitions through distinct operational states:

1. `DATE_ABSENT`: Date has not been evaluated.
2. `DATE_QUARANTINED`: Premature or invalid run recorded; does **not** block subsequent legitimate post-15:45 IST EOD evaluation.
3. `FINALIZED_EOD`: Verified post-market close evaluation completed; strictly blocks repeat writes.
4. `DATE_FAILED`: Stale feed or data outage aborted safely.
