# 🔁 PHASE 10.2J — END-TO-END PAPER TRADING REPLAY AUDIT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Ledger:** [`PAPER_TRADING_V1_1_REPLAY_TEST_EVENTS.csv`](file:///d:/New%20folder/AI%20Quant/PAPER_TRADING_V1_1_REPLAY_TEST_EVENTS.csv)  
**Historical Replay Sample:** **3,643 Events / 563 Closed Trades**

---

## 1. COMPLETE LIFECYCLE RECONSTRUCTION

The isolated replay engine validates natural execution progression across all states:

```mermaid
flowchart TD
    A["ZONE_DETECTED (HTF Demand Proximal/Distal)"] --> B["CONFIRMATION_PENDING (Price enters zone)"]
    B --> C["REJECTION_CONFIRMED (Green close + wick rejection)"]
    C --> D["ENTRY_PENDING (Awaiting next-bar open)"]
    D --> E["PAPER_FILLED (In Position + 25 bps cost)"]
    E --> F{"Price Evaluator"}
    F -->|Low <= Stop Loss| G["STOP_HIT (State: CLOSED, -1.0R)"]
    F -->|High >= Target 1| H["TARGET_1_HIT (State: CLOSED, +2.0R)"]
```

- **Demand Scope:** 100% Demand-only filtering active.
- **Timing Integrity:** `confirmation_timestamp < entry_timestamp` strictly verified across all 563 completed trades.
- **Prospective Cohort Isolation:** 0 replay events entered `PAPER_TRADING_V1_1_DEMANDCONF_EVENTS.csv`.
