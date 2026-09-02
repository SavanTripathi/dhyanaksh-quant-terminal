# 🔬 BACKTEST CLASSIFICATION & TRADE ACCOUNTING FORENSICS AUDIT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Audit Standard:** Zero Look-Ahead, Conservative Execution, Independent Point-in-Time Accounting.

---

## 1. INDEPENDENTLY RECALCULATED PERFORMANCE TOTALS

Derived directly from the verified `TRADE_LEVEL_OOS_RESULTS.csv` ($N = 5,294$):

$$\begin{aligned}
\text{Total Trades Executed:} &\quad \mathbf{5,294} \\
\text{Total Winning Trades ($\ge 2.0R$):} &\quad \mathbf{1,424\ (26.9\%)} \\
\text{Total Losing Trades (Stop Hit):} &\quad \mathbf{3,870\ (73.1\%)} \\
\text{Mean Expectancy per Trade:} &\quad \mathbf{-0.16R} \\
\text{Profit Factor:} &\quad \mathbf{0.78} \\
\text{Out-of-Sample (OOS) Expectancy (Mar–Aug 2026):} &\quad \mathbf{-0.21R\ (PF\ 0.73)}
\end{aligned}$$

---

## 2. CONFLUENCE HIERARCHY ANALYSIS

| Confluence Level | Trades | Win Rate ($\ge 2.0R$) | Average $R$ | Profit Factor | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **ATZ (4-TF Confluence)** | **138** | **15.2%** | **$-0.53R$** | **0.37** | **Needs wider zone buffer / confirmation.** |
| **Triple Confluence (3-TF)** | **799** | **24.9%** | **$-0.21R$** | **0.72** | Intermediate structural resistance. |
| **Dual Confluence (2-TF)** | **2,116** | **25.7%** | **$-0.20R$** | **0.73** | Moderate resolution. |
| **Single Timeframe (1-TF)** | **2,241** | **29.5%** | **$-0.08R$** | **0.88** | Tighter base ranges resolve faster. |

---

## 3. DEMAND VS SUPPLY DIRECTIONAL ASYMMETRY

- **Demand in Bull Market ($>\text{SMA}_{200}$):**  
  $$\text{Trades: } 1,237 \quad \mid \quad \text{Win Rate: } 34.8\% \quad \mid \quad \text{Avg } R: \mathbf{+0.08R} \quad \mid \quad \mathbf{\text{PF: } 1.13}$$
- **Supply in Bull Market ($>\text{SMA}_{200}$):**  
  $$\text{Trades: } 1,652 \quad \mid \quad \text{Win Rate: } 20.9\% \quad \mid \quad \text{Avg } R: \mathbf{-0.34R} \quad \mid \quad \mathbf{\text{PF: } 0.57}$$
- **Conclusion:** Trading Supply zones on equity cash in a secular upward trending market without short confirmation produces a persistent negative drag.

---

## 4. SCORE DISCRIMINATION AUDIT

| Score Bucket | Trades | Win Rate | Average $R$ | Profit Factor | Quality Discrimination |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Score 78–85** | 4,357 | 27.6% | $-0.14R$ | 0.81 | Baseline setups |
| **Score 86–92** | 799 | 24.9% | $-0.21R$ | 0.72 | Multi-timeframe setups |
| **Score 93–100** | 138 | 15.2% | $-0.53R$ | 0.37 | Macro HTF (Needs structural confirmation) |

**Finding:** Higher conviction scores in unassisted limit trading correlate with wider HTF zones that get clipped on tight 0.20 ATR stops before achieving 2R. Score alone is **NON-DISCRIMINATIVE** for blind limit execution; directional regime gating is required.
