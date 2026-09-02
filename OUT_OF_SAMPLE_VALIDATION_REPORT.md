# 📊 OUT-OF-SAMPLE VALIDATION, BIAS AUDIT & STRATEGY CALIBRATION REPORT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Production Commit Baseline:** `e86b0ba`  
**Evaluation Scope:** True Temporal Walk-Forward, Market Regime Matrix, Survivorship Audit, and Out-of-Sample (OOS) Expectancy.

---

## 1. EXECUTIVE SUMMARY & DECISION CLASSIFICATION

$$\begin{aligned}
\text{Total Trades Evaluated:} &\quad N = 5,410 \text{ Trades (Sep-2023 to Aug-2026 across 30 Equities)} \\
\text{Overall Walk-Forward Expectancy:} &\quad -0.16R \quad (\text{Profit Factor } 0.78) \\
\text{Out-of-Sample (OOS) Test Expectancy:} &\quad -0.21R \quad (\text{Profit Factor } 0.73) \\
\text{Demand in Bull Regime:} &\quad \mathbf{+0.06R} \quad (\mathbf{PF\ } 1.10,\ 34.2\%\ \text{Win Rate at } 2.0R) \\
\text{Supply across All Regimes:} &\quad \mathbf{-0.30R} \quad (\mathbf{PF\ } 0.62,\ \text{Negative Drift Drag})
\end{aligned}$$

### Final Strategy Classification:
```text
🟡 B) PROMISING BUT UNPROVEN — UNASSISTED LIVE EXECUTION INSUFFICIENT
(RECOMMENDED GATE: IMMUTABLE PAPER FORWARD TRACKING)
```

**Key Finding:** Blind unassisted limit order execution across both Demand and Supply without regime filtering produces a negative expectancy ($-0.16R$); however, **Demand Setups in Bull Regimes ($+0.06R, \text{PF } 1.10$)** exhibit positive expectancy. Supply setups suffer from severe secular upward drift in Indian equities and should require confirmation entry rather than blind limit orders.

---

## 2. TRUE TEMPORAL WALK-FORWARD SPLIT

| Split Period | Date Horizon | Trades | Win Rate ($\ge 2.0R$) | Average $R$ | Profit Factor |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **TRAIN** | **Sep-2023 $\rightarrow$ Aug-2025** (24 Months) | **4,164** | **26.8%** | **$-0.16R$** | **0.78** |
| **VALIDATION** | **Sep-2025 $\rightarrow$ Feb-2026** (6 Months) | **642** | **28.5%** | **$-0.11R$** | **0.85** |
| **FINAL TEST (OOS)** | **Mar-2026 $\rightarrow$ Aug-2026** (6 Months) | **604** | **25.2%** | **$-0.21R$** | **0.73** |
| **AGGREGATE TOTAL** | **Sep-2023 $\rightarrow$ Aug-2026** (36 Months) | **5,410** | **26.8%** | **$-0.16R$** | **0.78** |

---

## 3. MARKET REGIME PERFORMANCE MATRIX

| Strategy Category | Bullish Market ($>\text{SMA}_{200}$) | Bearish Market ($<\text{SMA}_{200}$) | Sideways / Consolidation |
| :--- | :---: | :---: | :---: |
| **DEMAND** | **Trades: 1,294 \| Win: 34.2% \| Avg R: +0.06R \| PF: 1.10** | Trades: 575 \| Win: 29.6% \| Avg R: -0.07R \| PF: 0.90 | Trades: 421 \| Win: 29.9% \| Avg R: -0.05R \| PF: 0.93 |
| **SUPPLY** | Trades: 1,711 \| Win: 21.2% \| Avg R: -0.34R \| PF: 0.57 | Trades: 816 \| Win: 26.2% \| Avg R: -0.19R \| PF: 0.75 | Trades: 593 \| Win: 23.3% \| Avg R: -0.28R \| PF: 0.63 |
| **ATZ (4-TF)** | Trades: 3,005 \| Win: 26.8% \| Avg R: -0.16R \| PF: 0.78 | Trades: 1,391 \| Win: 27.6% \| Avg R: -0.14R \| PF: 0.81 | Trades: 1,014 \| Win: 26.0% \| Avg R: -0.19R \| PF: 0.75 |

---

## 4. SCORE CALIBRATION & DISCRIMINATION

- **Conviction Score Saturation:** $82.3\%$ of scanned setups receive $\ge 90$ points, and $56.7\%$ receive 98 points.
- **Root Cause:** The shortlist pipeline filters out low-achievement stocks prior to persistence, resulting in heavy clustering in the upper decile.
- **Statistical Implication:** Conviction score alone does not separate winners from losers; ranking discrimination relies primarily on **Proximity ($\text{Distance \%}$)** and **Directional Regime Alignment**.

---

## 5. TRANSACTION COST SENSITIVITY

| Friction Assumption | Strategy Expectancy ($R$) | Profit Factor | Viability |
| :--- | :---: | :---: | :---: |
| **0 bps (Raw)** | $-0.16R$ | 0.78 | Baseline |
| **10 bps (STT + Brokerage)** | $-0.19R$ | 0.74 | Reduced |
| **25 bps (Slippage + Friction)** | $-0.24R$ | 0.69 | Sub-optimal |
| **50 bps (High Volatility)** | $-0.32R$ | 0.61 | Non-viable |
| **Demand in Bull Regime (10 bps)** | **$+0.03R$** | **1.05** | **Viable** |
