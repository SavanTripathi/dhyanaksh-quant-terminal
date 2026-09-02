# 📋 RESULT RECONCILIATION REPORT (PHASE 1 VS PHASE 2 VS PHASE 3)

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Audit Purpose:** Root cause forensic breakdown of ATZ classification, timeframe aggregation bugs, and edge validation.

---

## 1. ROOT CAUSE OF THE ATZ CLASSIFICATION DISCREPANCY

In the Phase 2 script (`run_phase2_oos_validation.py`), the multi-timeframe detection calls were:
```python
# DEFECT in Phase 2 script:
z_1d = detect_htf_supply_demand_zone(hist_slice, "1D")
z_1w = detect_htf_supply_demand_zone(hist_slice, "1W")  # Passed un-aggregated daily candles!
z_1m = detect_htf_supply_demand_zone(hist_slice, "1M")  # Passed un-aggregated daily candles!
z_3m = detect_htf_supply_demand_zone(hist_slice, "3M")  # Passed un-aggregated daily candles!
```
Because the same raw daily candle slice was passed with `"1W"`, `"1M"`, `"3M"` string tags, `detect_htf_supply_demand_zone` evaluated daily candles and returned `has_1w=True`, `has_1m=True`, `has_3m=True` whenever a daily zone was found. This artificially flagged **100% of trades as ATZ (5,410 / 5,410)**.

### Phase 3 Rectification:
In Phase 3 (`run_phase3_forensic_backtest.py`), candles are strictly aggregated using `CandleAggregator.aggregate_from_df` into true Weekly (`W-FRI`), Monthly (`ME`), and Quarterly (`QE`) bars:
- **True ATZ (4-TF Confluence) Count:** **138 Trades** (out of 5,294 total trades, ~2.6%).
- **Triple Confluence (3-TF):** **799 Trades** (15.1%).
- **Dual Confluence (2-TF):** **2,116 Trades** (40.0%).
- **Single Timeframe (1-TF):** **2,241 Trades** (42.3%).
- **Assertion:** $\text{ATZ (138)} + \text{Triple (799)} + \text{Dual (2,116)} + \text{Single (2,241)} = \mathbf{5,294\ Total\ Trades}$ (**100% Reconciled**).

---

## 2. ROW-BY-ROW HISTORICAL COMPARISON MATRIX

| Dimension | Phase 1 Early Benchmark | Phase 2 Initial Run | Phase 3 Forensic Reconciled | Reason for Change |
| :--- | :--- | :--- | :--- | :--- |
| **Total Trades** | 4,509 | 5,410 | **5,294** | True point-in-time MTF bar aggregation requirement ($\ge 50$ bars). |
| **ATZ Trade Count** | Not Isolated | 5,410 (100% Saturated) | **138 (2.6%)** | **Fixed Phase 2 classification bug.** Daily candles were falsely labelled as 4-TF. |
| **ATZ Win Rate** | 38.4% (Estimated) | 26.8% (Saturated) | **15.2%** | True 4-TF confluence has wider base structures; tight 0.20 ATR stop triggers on noise. |
| **Demand in Bull Regime**| +0.01R | +0.06R / PF 1.10 | **+0.08R / PF 1.13 (34.8% Win Rate)** | **Robust Edge confirmed:** Secular trend support for long setups in bull regimes. |
| **Supply Performance** | -0.30R / PF 0.62 | -0.34R / PF 0.57 | **-0.34R / PF 0.57 (20.9% Win Rate)** | **Severe Asymmetry:** Indian equities have secular upward drift. Blind limit orders fail. |
| **Overall Strategy PF** | 0.78 | 0.78 | **0.78** | Consistent across all runs. Unassisted blind limit orders require confirmation gate. |
