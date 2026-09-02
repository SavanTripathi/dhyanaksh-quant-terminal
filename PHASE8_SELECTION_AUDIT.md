# 🔍 PHASE 8 — SELECTION AUDIT & COMMON-OPPORTUNITY RECONCILIATION REPORT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Candidate Identifier:** `Dhyanaksh-DemandConf-B-v1.1-research`  
**Candidate Hash:** `1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852`

---

## 1. SELECTION EFFECT VS EXECUTION EFFECT DECOMPOSITION

When evaluating the identical underlying pool of trade opportunities:

| Metric | Opportunity Count | Model A (Blind Limit) | Model B (Rejection Conf) | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: |
| **Common Opportunities** | **5,197** | $\text{Avg } R: \mathbf{-0.20R} \mid \text{PF: } \mathbf{0.73}$ | $\text{Avg } R: \mathbf{0.00R} \mid \text{PF: } \mathbf{1.00}$ | $\mathbf{+0.20R}$ (**Pure Execution Effect**) |
| **Model A Only** | **79** | $\text{Avg } R: -1.00R \mid \text{PF: } 0.00$ | *Rejected by confirmation* | **Avoided Bad Trades** |
| **Model B Only** | **147** | *Not triggered* | $\text{Avg } R: +0.02R \mid \text{PF: } 1.04$ | **New Confirmed Entries** |

### Key Discovery:
1. **Execution Effect ($+0.20R$ on 5,197 shared setups):** Waiting for a lower-timeframe rejection candle prevents buying into knife-falls, shifting the execution entry to a point where the local reaction has already begun.
2. **Selection Effect:** Model B refuses 79 disastrous runaway setups that Model A blindly entered.

---

## 2. POST-HOC CLASSIFICATION OF DEMAND-ONLY RULE

- **Pre-Registration Status:** Demand-only filtering was identified **POST-HOC** following historical forensic analysis of secular equity drift.
- **Classification:** `Dhyanaksh-DemandConf-B-v1.1-research` is formally cataloged as a **HYPOTHESIS-GENERATING RESEARCH CANDIDATE**.
- **Prospective Gate:** All historical backtesting is now **CLOSED**. Future validity will be decided exclusively on unseen forward data via [`PAPER_TRADING_V1_1_DEMANDCONF.csv`](file:///d:/New%20folder/AI%20Quant/PAPER_TRADING_V1_1_DEMANDCONF.csv).
