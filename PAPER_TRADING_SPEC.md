# 📝 IMMUTABLE PAPER-TRADING LOGGING SPECIFICATION

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Purpose:** Real-time forward logging of unassisted quantitative signals for live statistical validation.

---

## 1. IMMUTABLE SIGNAL SCHEMA

Every signal emitted by `full_batch_scanner.py` and saved to `production_scanner.db` (`screener_shortlist_cache`) must capture:

```json
{
  "signal_id": "STRING (UUID)",
  "timestamp": "ISO_TIMESTAMP_UTC",
  "symbol": "NSE_TICKER",
  "direction": "DEMAND | SUPPLY",
  "zone_timeframe": "3M | 1M | 1W | 1D",
  "proximal_entry": "FLOAT",
  "distal_stop": "FLOAT",
  "stop_loss_buffered": "FLOAT",
  "target_1_2r": "FLOAT",
  "target_2_3_5r": "FLOAT",
  "target_3_5r": "FLOAT",
  "risk_per_share": "FLOAT",
  "gtf_7_point_score": "FLOAT (0.5 to 7.0)",
  "gtf_13_point_score": "FLOAT (1.0 to 13.0)",
  "conviction_score": "INTEGER (0 to 100)",
  "curve_location": "VERY_LOW | EQUILIBRIUM | VERY_HIGH",
  "sma_50_trend_angle": "TREND_UP | TREND_DOWN | TREND_SIDEWAYS",
  "is_atz": "BOOLEAN",
  "participating_timeframes": ["3M", "1M", "1W", "1D"],
  "all_timeframe_zones": "MAP<TF, ZONE_COORDINATES>",
  "cmp_at_signal": "FLOAT",
  "distance_pct": "FLOAT",
  "execution_status": "PENDING_ENTRY",
  "entry_timestamp": "NULLABLE_ISO_TIMESTAMP",
  "exit_timestamp": "NULLABLE_ISO_TIMESTAMP",
  "exit_reason": "OPEN | STOP_LOSS | TARGET_1 | TARGET_2 | TARGET_3 | EXPIRED",
  "realized_r_multiple": "NULLABLE_FLOAT"
}
```

---

## 2. STATE TRANSITION RULES

1. **Signal Creation:** Immutable timestamp and entry/SL/target levels frozen at time $T$.
2. **Order Trigger:** Marked `ACTIVE_IN_TRADE` only when subsequent real-time bar touches `proximal_entry`.
3. **Resolution:** Evaluates Stop Loss first if both Stop and Target are touched in the same intraday window.
