# 📐 CONFIRMATION ENTRY MODEL SPECIFICATION (RESEARCH ONLY)

**Document Identifier:** `ENTRY_MODEL_SPEC-v1.1-research`  
**Purpose:** Formal deterministic definition of Lower-Timeframe (LTF) confirmation entry models for High-Timeframe Supply & Demand setups.

---

## 1. FORMAL ENTRY MODEL DEFINITIONS

### MODEL A: Baseline Blind Limit (Type 1)
- **Condition:** Place limit order directly at Proximal line.
- **Trigger:** Candle low $\le \text{Proximal}$ (Demand) or candle high $\ge \text{Proximal}$ (Supply).
- **Execution Price:** Exact Proximal Price.
- **Stop Loss:** $\text{Distal} - 0.20\text{ ATR}$ (Demand) / $\text{Distal} + 0.20\text{ ATR}$ (Supply).

### MODEL B: LTF Rejection / Hammer / Engulfing Confirmation (Type 2A)
- **Condition:** Price enters zone interval $[\text{Distal}, \text{Proximal}]$.
- **Confirmation Candle:** On the Lower Timeframe (1D for 1W/1M/3M setups), the candle must close in the direction of the trade after touching the zone:
  - **Demand:** Candle Close $>$ Candle Open AND (Lower Wick $\ge 2 \times$ Real Body OR Bullish Engulfing).
  - **Supply:** Candle Close $<$ Candle Open AND (Upper Wick $\ge 2 \times$ Real Body OR Bearish Engulfing).
- **Execution:** Next-bar Open following confirmed close.
- **Stop Loss:** Below the lowest point of the confirmation candle or Distal (whichever is lower for Demand).

### MODEL C: LTF Structure Break Confirmation (CHoCH / Type 2B)
- **Condition:** Price penetrates zone and breaks prior swing high/low on the execution timeframe.
- **Confirmation Trigger:** Candle Close $>$ Prior 3-bar High (Demand) or Candle Close $<$ Prior 3-bar Low (Supply).
- **Execution:** Next-bar Open after structure break close.
- **Stop Loss:** Lowest wick of the structural reaction base.

### MODEL D: Displacement + Structure Confirmation (Type 3A)
- **Condition:** Strong Extended Range Candle (ERC) departure (body $> 60\%$ of total candle range) initiating from within the zone.
- **Execution:** Next-bar Open.
- **Stop Loss:** Below origin of the displacement impulse.

### MODEL E: Confirmation + Retest Entry (Type 3B)
- **Condition:** After displacement/structure break, place limit order on $50\%$ retracement of the displacement candle.
- **Execution:** Filled only if subsequent bar retests the $50\%$ impulse level.
- **Stop Loss:** Origin of displacement.
