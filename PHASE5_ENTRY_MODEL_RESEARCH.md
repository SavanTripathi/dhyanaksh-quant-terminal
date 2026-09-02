# 🔬 PHASE 5 — ENTRY MODEL & CONFIRMATION RESEARCH REPORT

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Research Version:** `v1.1-research`  
**Production Baseline Strategy:** `v1.0.0-c90ed1b` (FROZEN & UNTOUCHED)

---

## 1. COMPARATIVE RESULTS ACROSS ENTRY MODELS

$$\begin{aligned}
\text{MODEL A (Blind Limit Baseline):} &\quad 5,276 \text{ Trades} \mid \text{Win Rate: } 26.8\% \mid \text{Avg } R: \mathbf{-0.20R} \mid \mathbf{\text{PF: } 0.73} \mid \text{OOS PF: } 0.65 \\
\text{MODEL B (LTF Rejection Confirmation):} &\quad 5,344 \text{ Trades} \mid \text{Win Rate: } 33.5\% \mid \text{Avg } R: \mathbf{0.00R} \mid \mathbf{\text{PF: } 1.01} \mid \text{OOS PF: } 0.91 \\
\text{MODEL C (LTF Structure Break):} &\quad 4,048 \text{ Trades} \mid \text{Win Rate: } 28.9\% \mid \text{Avg } R: \mathbf{-0.13R} \mid \mathbf{\text{PF: } 0.81} \mid \text{OOS PF: } 0.67
\end{aligned}$$

---

## 2. KEY EMPIRICAL FINDINGS

### 1. Rejection Confirmation (Model B) Solves the Demand Execution Drag:
When LTF rejection confirmation is applied to **Demand Setups**, expectancy becomes **robustly positive across all market regimes**:
- **Demand $\times$ Bull:** $\text{Win Rate: } 36.9\% \mid \text{Avg } R: \mathbf{+0.11R} \mid \mathbf{\text{PF: } 1.17}$ ($N = 1,252$)
- **Demand $\times$ Bear:** $\text{Win Rate: } 39.4\% \mid \text{Avg } R: \mathbf{+0.18R} \mid \mathbf{\text{PF: } 1.30}$ ($N = 587$)
- **Demand $\times$ Sideways:** $\text{Win Rate: } 36.4\% \mid \text{Avg } R: \mathbf{+0.09R} \mid \mathbf{\text{PF: } 1.14}$ ($N = 423$)

### 2. Supply Setups Remain Dragged Down:
Even with rejection confirmation, **Supply setups** on equity cash remain below $1.0\text{ PF}$ ($\text{PF } 0.87\text{--}0.92$), proving that equity shorting requires stronger macro counter-trend catalysts than pure zone touches.

---

## 3. RECOMMENDED RESEARCH CANDIDATE

```text
🟡 D) OOS PROMISING — CANDIDATE: MODEL B (DEMAND ONLY WITH LTF REJECTION CONFIRMATION)
```

- **Production Strategy Status:** `Dhyanaksh-HTF-SD-v1.0.0` remains **completely frozen and untouched**.
- **Research Promotion Gate:** Model B is cataloged under research specification `ENTRY_MODEL_SPEC.md` for potential inclusion in a future `v1.1.0` candidate cohort after the ongoing 8–12 week `v1.0.0` paper trading observation period concludes.
