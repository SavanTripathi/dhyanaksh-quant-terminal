# PHASE 8 — NUMERICAL LINEAGE MATRIX & TRADE PLAN MATHEMATICAL INTEGRITY

**System**: Dhyanaksh HTF Supply & Demand Quant Terminal  
**Audit Date**: 2026-09-09  
**Phase**: PHASE 8 — FINAL END-TO-END PRODUCTION ACCEPTANCE  
**Target Gates**: 
- **G09**: GTF zone correctness preserved
- **G10**: Trade-plan mathematics correct
- **G11**: Negative/unexecutable targets rejected

---

## 1. Mathematical Formulas & Invariants

The frozen canonical trade plan mathematical model:
- **Entry**: $\text{Entry} = \text{Proximal Price}$
- **Buffer**: $\text{buffer} = 0.20 \times \text{ATR}_{14}$
- **Stop Loss (Demand)**: $\text{SL} = \text{Distal} - \text{buffer}$
- **Stop Loss (Supply)**: $\text{SL} = \text{Distal} + \text{buffer}$
- **Risk Per Share**: $R = |\text{Entry} - \text{SL}|$
- **Targets (Demand)**:
  - $T_1 = \text{Entry} + 2.0R$
  - $T_2 = \text{Entry} + 3.5R$
  - $T_3 = \text{Entry} + 5.0R$
- **Targets (Supply)**:
  - $T_1 = \text{Entry} - 2.0R$
  - $T_2 = \text{Entry} - 3.5R$
  - $T_3 = \text{Entry} - 5.0R$
- **Quality Guard**: $T_3 \le 0 \implies \text{REJECT}$ (Zero negative targets reach DB, API, or UI).

---

## 2. Representative Symbol Lineage Matrix

Forensic execution trace from frozen GTF ZoneDetector $\to$ BatchScannerEngine $\to$ SQLite $\to$ API $\to$ Frontend:

| Metric | BSOFT (DEMAND) | TCS (SUPPLY) | INFY (SUPPLY) | RELIANCE | HDFCBANK |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Active Setup** | **YES (ATZ)** | **YES** | **YES** | NO (Filtered) | NO (Filtered) |
| **Direction** | `DEMAND` | `SUPPLY` | `SUPPLY` | — | — |
| **Timeframes** | `["3M","1M","1W","1D"]` | `["3M","1W"]` | `["1W","1D"]` | — | — |
| **CMP** | ₹294.40 | ₹2,348.00 | ₹1,140.00 | — | — |
| **Proximal (Entry)** | **₹300.69** | **₹2,284.00** | **₹1,169.20** | — | — |
| **Distal Base** | ₹237.37 | ₹2,620.63 | ₹1,195.00 | — | — |
| **Daily ATR (14)** | ₹10.39 | ₹62.41 | ₹28.39 | — | — |
| **ATR Buffer (0.2x)**| ₹2.08 | ₹12.48 | ₹5.68 | — | — |
| **Stop Loss (SL)** | **₹235.29** | **₹2,633.11** | **₹1,200.68** | — | — |
| **Risk / Share (R)** | **₹65.40** | **₹349.11** | **₹31.48** | — | — |
| **Target 1 (2R)** | **₹431.49** | **₹1,585.78** | **₹1,106.24** | — | — |
| **Target 2 (3.5R)** | **₹529.59** | **₹1,062.12** | **₹1,059.02** | — | — |
| **Target 3 (5R)** | **₹627.69** | **₹538.45** | **₹1,011.80** | — | — |
| **Conviction Score**| 98 | 89 | 89 | — | — |
| **Achievements** | 4 | 2 | 2 | — | — |
| **Fresh Zone** | YES | YES | YES | — | — |
| **MA Confluence** | NO | YES | NO | — | — |

---

## 3. Boundary Numerical Preservation Audit

Every level was compared across all repository boundaries:

1. **GTF Engine $\to$ Trade Plan**:  
   `Entry = Proximal`, `SL = Distal ± Buffer`. Numerical variance: **0.00%**.
2. **Trade Plan $\to$ SQLite `trade_plans`**:  
   Persisted values match computed values down to 2 decimal places. Numerical variance: **0.00%**.
3. **SQLite $\to$ API JSON Response**:  
   `GET /api/v1/screener/shortlist` delivers identical floats. Numerical variance: **0.00%**.
4. **API $\to$ React Screener & Chart**:  
   `TradeProjectionCard` and `TradingViewChart` render these exact floats. Rounding drift: **0.00%**.

---

## 4. Quality Guard Audit ($T_3 \le 0$)

- **Total Trade Plans Scanned**: 373
- **Trade Plans with $T_3 \le 0$**: **0** (Zero)
- **Trade Plans with $\text{Entry} \le 0$ or $\text{SL} \le 0$**: **0** (Zero)
- **Trade Plans with $R \le 0$**: **0** (Zero)

No negative or untradeable target reaches the database, API, or frontend.

---

## 5. Formal Verdict

- **G09 (GTF Zone Correctness Preserved)**: **PASS**
- **G10 (Trade-Plan Mathematics Correct)**: **PASS**
- **G11 (Negative/Unexecutable Targets Rejected)**: **PASS**
