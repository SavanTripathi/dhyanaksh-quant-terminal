# 🔬 PHASE 6 — MODEL B FORENSIC VALIDATION & MULTI-MODEL RESEARCH AUDIT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Production Strategy Baseline:** `Dhyanaksh-HTF-SD-v1.0.0` (`v1.0.0-c90ed1b`) — **FROZEN & UNTOUCHED**  
**Research Strategy:** `v1.1-research`  
**Dataset Evaluated:** $N = 22,889$ Simulated Trade Observations across Models A, B, C, D, E

---

## 1. COMPLETE 5-MODEL COMPARATIVE EXECUTIVE TABLE

$$\begin{aligned}
\text{Model A (Blind Limit Baseline):} &\quad 5,276 \text{ Trades} \mid \text{Win: } 26.8\% \mid \text{All Avg } R: \mathbf{-0.20R} \mid \text{All PF: } \mathbf{0.73} \mid \text{OOS PF: } \mathbf{0.65} \\
\text{Model B (Rejection Confirmation):} &\quad 5,344 \text{ Trades} \mid \text{Win: } 33.5\% \mid \text{All Avg } R: \mathbf{0.00R} \mid \text{All PF: } \mathbf{1.01} \mid \text{OOS PF: } \mathbf{0.91} \\
\text{Model C (Structure Break):} &\quad 4,048 \text{ Trades} \mid \text{Win: } 28.9\% \mid \text{All Avg } R: \mathbf{-0.13R} \mid \text{All PF: } \mathbf{0.81} \mid \text{OOS PF: } \mathbf{0.67} \\
\text{Model D (Displacement + Structure):} &\quad 4,245 \text{ Trades} \mid \text{Win: } 31.0\% \mid \text{All Avg } R: \mathbf{-0.07R} \mid \text{All PF: } \mathbf{0.90} \mid \text{OOS PF: } \mathbf{0.72} \\
\text{Model E (Confirmation + Retest):} &\quad 3,976 \text{ Trades} \mid \text{Win: } 34.5\% \mid \text{All Avg } R: \mathbf{+0.04R} \mid \text{All PF: } \mathbf{1.05} \mid \text{OOS PF: } \mathbf{0.97}
\end{aligned}$$

---

## 2. CRITICAL ANSWERS TO CORE RESEARCH QUESTIONS

### 1. Is Model B statistically and economically better than Model A?
**Yes.** Model B lifts overall win rate from $26.8\%$ to $33.5\%$, improving all-period Profit Factor from $0.73$ to $1.01$ and OOS PF from $0.65$ to $0.91$.

### 2. Does Model B remain viable in Final OOS?
**Near break-even ($\text{OOS PF } 0.91, \text{Avg } R: -0.06R$).** Model B avoids disastrous stop-outs on bad limit orders, but still exhibits slight negative drift when including short Supply setups on equity cash.

### 3. Is the Demand result broad or concentrated?
**Broadly Distributed.** Demand setups with confirmation show positive PF across **all 30 symbols** and across all market regimes:
- **Demand $\times$ Bull:** $\text{PF } 1.17$
- **Demand $\times$ Bear:** $\text{PF } 1.30$
- **Demand $\times$ Sideways:** $\text{PF } 1.14$

### 4. Does confirmation make GTF / Conviction predictive?
**Partially.** Confirmation mitigates the severe inversion of Quarterly/Monthly setups, but scoring still requires regime gating to avoid shorting uptrends.

### 5. Does Model D or E outperform Model B?
**Model E (Confirmation + Retest)** achieves the highest overall win rate ($34.5\%$) and all-period PF ($1.05$), with an OOS PF of $0.97$ ($-0.02R$), demonstrating that entering on a $50\%$ pullback of the displacement candle offers superior risk-reward.

### 6. Should ANY research model replace the frozen production strategy?
**NO.** Production strategy `Dhyanaksh-HTF-SD-v1.0.0` remains locked. Live paper trading in `PAPER_TRADING_DAILY.csv` will continue running its 8–12 week baseline observation period.

---

# 🏁 FINAL DECISION GATE

```text
🟡 B) OOS PROMISING BUT INSUFFICIENT FOR PRODUCTION DEPLOYMENT
(PRIMARY RESEARCH CANDIDATES FOR v1.1-research: MODEL B & MODEL E ON DEMAND ONLY)
```
