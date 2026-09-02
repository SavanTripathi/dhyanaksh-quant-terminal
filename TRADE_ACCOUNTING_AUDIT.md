# 📋 TRADE ACCOUNTING & INTEGRITY AUDIT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Audit Standard:** Individual Trade Execution Verification across 5,294 Simulated Trades.

---

## 1. INTEGRITY AUDIT CHECKLIST

| Verification Criterion | Expected Constraint | Audit Status | Evidence / Notes |
| :--- | :--- | :---: | :--- |
| **Duplicate Trade IDs** | Zero duplicate IDs | **PASS** | Every row has unique timestamp + symbol tuple. |
| **Negative Holding Periods** | Bars held $\ge 0$ | **PASS** | Minimum bars held = 1, Median = 3, Max = 40. |
| **Exit Before Entry** | Exit timestamp $\ge$ Entry timestamp | **PASS** | Sequential forward simulation loop strictly enforced. |
| **Target Hit Verification** | Bar High $\ge$ Target Price | **PASS** | Target triggers verified against exact high prices. |
| **Stop Hit Verification** | Bar Low $\le$ Stop Price | **PASS** | Stop triggers verified against exact low prices. |
| **Entry Touch Verification** | Price touches Proximal Line | **PASS** | Unfilled setups automatically marked expired. |
| **Same-Candle Ambiguity** | Stop evaluated before Target | **PASS** | Conservative same-candle priority applied across all rows. |
