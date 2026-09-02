# 📑 PAPER TRADING RESULTS SCHEMA & DATA DICTIONARY

**Project:** Dhyanaksh — HTF Supply & Demand Quant Terminal  
**Schema Purpose:** Strict point-in-time immutable capture of live quantitative setups for paper-tracking.

---

## 1. TABLE: `paper_trading_ledger`

| Field Name | Type | Immutability | Description |
| :--- | :--- | :---: | :--- |
| `signal_id` | `VARCHAR(64)` PRIMARY KEY | Immutable | Unique UUID for the setup. |
| `created_at` | `TIMESTAMP_UTC` | Immutable | Exact point-in-time emission timestamp. |
| `symbol` | `VARCHAR(32)` | Immutable | NSE equity symbol. |
| `direction` | `VARCHAR(16)` | Immutable | `DEMAND` or `SUPPLY`. |
| `timeframe` | `VARCHAR(8)` | Immutable | Primary timeframe (`3M`, `1M`, `1W`, `1D`). |
| `proximal_entry` | `DECIMAL(12,4)` | Immutable | Proximal entry level. |
| `distal_stop` | `DECIMAL(12,4)` | Immutable | Distal stop level. |
| `stop_loss_buffered`| `DECIMAL(12,4)` | Immutable | Stop loss price with 0.20 ATR buffer. |
| `target_1_2r` | `DECIMAL(12,4)` | Immutable | Target 1 (2.0R Multiple). |
| `target_2_3_5r` | `DECIMAL(12,4)` | Immutable | Target 2 (3.5R Multiple). |
| `target_3_5r` | `DECIMAL(12,4)` | Immutable | Target 3 (5.0R Multiple). |
| `gtf_7_score` | `DECIMAL(4,2)` | Immutable | 7-point core odds score (0.5 to 7.0). |
| `gtf_13_score` | `DECIMAL(4,2)` | Immutable | 13-point composite scorecard (1.0 to 13.0). |
| `conviction_score` | `INTEGER` | Immutable | 6-pillar composite conviction score (0 to 100). |
| `curve_location` | `VARCHAR(32)` | Immutable | Curve percentile classification. |
| `is_atz` | `BOOLEAN` | Immutable | True if 4-timeframe confluence confirmed. |
| `participating_tfs`| `JSON_ARRAY` | Immutable | Active participating timeframes. |
| `cmp_at_signal` | `DECIMAL(12,4)` | Immutable | Current market price when signal fired. |
| `distance_pct` | `DECIMAL(6,2)` | Immutable | Proximity percentage to entry. |
| `execution_status` | `VARCHAR(24)` | Updatable | `PENDING`, `FILLED`, `EXPIRED`, `RESOLVED`. |
| `entry_timestamp` | `TIMESTAMP_UTC` | Updatable | Exact time of live entry touch. |
| `exit_timestamp` | `TIMESTAMP_UTC` | Updatable | Exact time of exit (Stop or Target). |
| `exit_reason` | `VARCHAR(24)` | Updatable | `STOP_LOSS`, `WIN_T1`, `WIN_T2`, `WIN_T3`, `EXPIRED`. |
| `realized_r` | `DECIMAL(6,2)` | Updatable | Realized R multiple (e.g. +2.0, +3.5, -1.0). |
| `mae_pct` | `DECIMAL(6,2)` | Updatable | Maximum Adverse Excursion during trade. |
| `mfe_pct` | `DECIMAL(6,2)` | Updatable | Maximum Favorable Excursion during trade. |
| `holding_days` | `INTEGER` | Updatable | Total elapsed trading days. |
