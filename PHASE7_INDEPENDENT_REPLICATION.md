# 📊 PHASE 7 — INDEPENDENT REPLICATION, BOOTSTRAP SIGNIFICANCE & ROBUSTNESS AUDIT REPORT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Production Strategy Baseline:** `Dhyanaksh-HTF-SD-v1.0.0` (`v1.0.0-c90ed1b`) — **STRICTLY FROZEN & UNTOUCHED**  
**Research Version:** `v1.1-research`  
**Dataset Replicated:** $N = 22,889$ Raw Trade Observations across Models A, B, C, D, E

---

## 1. FINAL EXECUTIVE COMPARISON TABLE

| Model Architecture | Trades ($N$) | All PF | Final OOS PF | OOS Avg $R$ | 95% Bootstrap CI for OOS Avg $R$ | Cost-Adjusted PF (25 bps) | Symbol Robust? | Time Robust? | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Model A (Blind Limit)** | 5,276 | **0.73** | **0.65** | $-0.27R$ | $[-0.38R, -0.17R]$ | 0.66 | NO | NO | **INADEQUATE** |
| **Model B (Rejection Conf)** | 5,344 | **1.01** | **0.91** | $-0.06R$ | $[-0.17R, +0.05R]$ | 0.93 | YES | PARTIAL | **OOS PROMISING** |
| **Model C (Structure Break)**| 4,048 | **0.81** | **0.67** | $-0.25R$ | $[-0.37R, -0.13R]$ | 0.74 | NO | NO | **INADEQUATE** |
| **Model D (Displacement+Str)**| 4,245 | **0.90** | **0.72** | $-0.20R$ | $[-0.33R, -0.09R]$ | 0.83 | NO | NO | **INADEQUATE** |
| **Model E (Conf + Retest)** | 3,976 | **1.05** | **0.97** | $-0.02R$ | $[-0.15R, +0.11R]$ | 0.98 | YES | PARTIAL | **OOS PROMISING** |

---

## 2. STATISTICAL HYPOTHESIS TESTING (CLUSTERED BOOTSTRAP)

$$\begin{aligned}
\text{Model B minus Model A Difference:} &\quad \mathbf{+0.20R} \quad \text{95\% CI: } [+0.15R, +0.26R] \quad \longrightarrow \mathbf{\text{Statistically Significant (p < 0.01)}} \\
\text{Model E minus Model A Difference:} &\quad \mathbf{+0.23R} \quad \text{95\% CI: } [+0.18R, +0.29R] \quad \longrightarrow \mathbf{\text{Statistically Significant (p < 0.01)}} \\
\text{Model E minus Model B Difference:} &\quad \mathbf{+0.03R} \quad \text{95\% CI: } [-0.03R, +0.09R] \quad \longrightarrow \mathbf{\text{Not Statistically Distinguishable}}
\end{aligned}$$

---

## 3. EVIDENCE-BASED ANSWERS TO MANDATORY QUESTIONS

### Q1: Is Model B statistically better than Model A?
**YES.** Clustered bootstrap yields $+0.20R$ ($95\%\text{ CI: } [+0.15R, +0.26R]$). Lower-Timeframe rejection confirmation significantly reduces premature stop-outs compared to blind limit orders.

### Q2: Is Model E statistically better than Model A?
**YES.** Clustered bootstrap yields $+0.23R$ ($95\%\text{ CI: } [+0.18R, +0.29R]$).

### Q3: Is Model E statistically better than Model B?
**NO.** The mean difference is $+0.03R$ ($95\%\text{ CI: } [-0.03R, +0.09R]$), crossing zero. Model E's added execution complexity is not statistically superior to Model B.

### Q4: Is either model genuinely positive in Final OOS?
**NO (Statistically Indistinguishable from Zero).**
- Model B Final OOS Avg $R$: $-0.06R$ ($95\%\text{ CI: } [-0.17R, +0.05R]$).
- Model E Final OOS Avg $R$: $-0.02R$ ($95\%\text{ CI: } [-0.15R, +0.11R]$).
Both intervals cross zero. Thus, an all-direction unconstrained edge is **NOT STATISTICALLY ESTABLISHED**.

### Q5: Does the Demand result survive symbol and quarter removal?
**YES.** When evaluated on **Demand setups only**, Model B and E exhibit positive expectancy across all 30 equities ($\text{PF } 1.14\text{--}1.30$) and survive leave-one-symbol-out and leave-one-quarter-out cross-validation.

### Q6: Does the result survive realistic costs?
**Demand-only setups survive friction ($+0.06R\text{ net at } 25\text{ bps}$)**. Supply setups fail under any friction.

### Q7: Does HTF confluence genuinely improve expectancy?
**Partially.** Confluence holds support only when confirmation is required. Without confirmation, macro base widths lead to stop-loss clipping.

### Q8 & Q9: Do GTF and Conviction scores become predictive?
**Partially.** Confirmation removes the inverse drag on macro setups, but directional regime filtering is required to prevent counter-trend degradation.

### Q10: Was the 50% Model-E pullback rule pre-specified or discovered post-hoc?
**POST-HOC EXPLORATORY.** The $50\%$ retracement was introduced in research exploration and must not be treated as a pre-specified confirmatory hypothesis.

### Q11: Does Model E justify its additional complexity over Model B?
**NO.** Because Model E is not statistically superior to Model B ($p > 0.05$), the simpler Model B is the preferred confirmation model.

### Q12: Does the placebo test destroy the apparent confirmation advantage?
**YES.** Randomizing confirmation breaks timing alignment and degrades performance to random baseline levels.

### Q13: Is survivorship bias still unresolved?
**YES (`SURVIVORSHIP_BIAS: UNRESOLVED`).** Results reflect surviving NIFTY 500 equities.

### Q14: What strategy deserves a NEW prospective paper cohort?
**Candidate Cohort:** `v1.1-research-DemandConf` (Model B applied strictly to **Demand setups**).

### Q15: Should ANY model replace v1.0.0?
**NO.** Production baseline `Dhyanaksh-HTF-SD-v1.0.0` remains 100% frozen. Live paper trading continues under `PAPER_TRADING_DAILY.csv`.
