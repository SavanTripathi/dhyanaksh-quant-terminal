# PHASE 5 GATE 19 - TRADE PLAN NUMERICAL LINEAGE REPORT
======================================================================
Generated: 2026-09-09


## SYMBOL: BSOFT
------------------------------------------------------------

  ### LAYER 1: DATABASE (trade_plans)
  Direction              : DEMAND
  Participating TFs      : ["3M", "1M", "1W", "1D"]
  Achievements           : 4
  overlap_min (L_common) : 237.37
  overlap_max (H_common) : 300.69
  entry_price            : 300.69
  stop_loss              : 235.29
  risk_per_share (R)     : 65.4
  target_1  (2.0R)       : 431.49
  target_2  (3.5R)       : 529.59
  target_3  (5.0R)       : 627.69
  atr_14                 : 10.39
  atr_buffer (0.20*ATR)  : 2.08
  current_price (CMP)    : 294.4
  distance_pct           : 2.14
  is_fresh               : 1
  created_at             : 2026-09-09 06:44:46.623245

  ### LAYER 2: MATHEMATICAL RE-DERIVATION
  Expected Entry         : 300.69
  Expected SL            : 235.29
  Expected R             : 65.4
  T1 (2R from entry)     : 431.49
  T2 (3.5R from entry)   : 529.59
  T3 (5R from entry)     : 627.69

  ### PARITY: DB vs MATH
  Entry  matches expected        : PASS
  SL     matches expected        : PASS
  R      matches expected        : PASS
  T1     matches DB R-calc       : PASS
  T2     matches DB R-calc       : PASS
  T3     matches DB R-calc       : PASS

  ### LAYER 3: API (/api/v1/screener/shortlist)
  API entry_price        : 300.69
  API stop_loss          : 235.29
  API target_1           : 431.49
  API target_2           : 529.59
  API target_3           : 627.69
  API direction          : DEMAND
  API cmp                : 294.4

  ### PARITY: DB vs API
  Entry  DB=300.69 API=300.69   : PASS
  SL     DB=235.29 API=235.29   : PASS
  T1     DB=431.49 API=431.49   : PASS

  ### VERDICT: PASS

## SYMBOL: RELIANCE
------------------------------------------------------------
  [DB] NO ACTIVE trade plan in database for RELIANCE
  REASON: Evaluated 3M QSZ [1315.12 .. 1604.38] -> SL=1608.65, R=293.53, T3=-152.53 <= 0
  ACTION: Quality Guard (batch_scanner.py:281) rejected setup from persistence (untradeable 5R price)
  PARITY: DB = 0, API = 0, UI = 0 (100% consistent across all layers)
  VERDICT: PASS (LEGITIMATE TRANSFORMATION - Quality Guard Filtered)

## SYMBOL: TCS
------------------------------------------------------------

  ### LAYER 1: DATABASE (trade_plans)
  Direction              : DEMAND
  Participating TFs      : ["1W"]
  Achievements           : 2
  overlap_min (L_common) : 2193.6
  overlap_max (H_common) : 2365.6
  entry_price            : 2365.6
  stop_loss              : 2181.12
  risk_per_share (R)     : 184.48
  target_1  (2.0R)       : 2734.56
  target_2  (3.5R)       : 3011.28
  target_3  (5.0R)       : 3288.0
  atr_14                 : 62.41
  atr_buffer (0.20*ATR)  : 12.48
  current_price (CMP)    : 2348.0
  distance_pct           : 0.75
  is_fresh               : 1
  created_at             : 2026-09-09 06:44:46.623245

  ### LAYER 2: MATHEMATICAL RE-DERIVATION
  Expected Entry         : 2365.6
  Expected SL            : 2181.12
  Expected R             : 184.48
  T1 (2R from entry)     : 2734.56
  T2 (3.5R from entry)   : 3011.28
  T3 (5R from entry)     : 3288.0

  ### PARITY: DB vs MATH
  Entry  matches expected        : PASS
  SL     matches expected        : PASS
  R      matches expected        : PASS
  T1     matches DB R-calc       : PASS
  T2     matches DB R-calc       : PASS
  T3     matches DB R-calc       : PASS

  ### LAYER 3: API (/api/v1/screener/shortlist)
  API entry_price        : 2365.6
  API stop_loss          : 2181.12
  API target_1           : 2734.56
  API target_2           : 3011.28
  API target_3           : 3288.0
  API direction          : DEMAND
  API cmp                : 2348.0

  ### PARITY: DB vs API
  Entry  DB=2365.6 API=2365.6   : PASS
  SL     DB=2181.12 API=2181.12   : PASS
  T1     DB=2734.56 API=2734.56   : PASS

  ### VERDICT: PASS

## SYMBOL: INFY
------------------------------------------------------------

  ### LAYER 1: DATABASE (trade_plans)
  Direction              : SUPPLY
  Participating TFs      : ["1W", "1D"]
  Achievements           : 2
  overlap_min (L_common) : 1169.2
  overlap_max (H_common) : 1195.0
  entry_price            : 1169.2
  stop_loss              : 1200.68
  risk_per_share (R)     : 31.48
  target_1  (2.0R)       : 1106.24
  target_2  (3.5R)       : 1059.02
  target_3  (5.0R)       : 1011.8
  atr_14                 : 28.39
  atr_buffer (0.20*ATR)  : 5.68
  current_price (CMP)    : 1140.0
  distance_pct           : 2.56
  is_fresh               : 1
  created_at             : 2026-09-09 06:44:46.623245

  ### LAYER 2: MATHEMATICAL RE-DERIVATION
  Expected Entry         : 1169.2
  Expected SL            : 1200.68
  Expected R             : 31.48
  T1 (2R from entry)     : 1106.24
  T2 (3.5R from entry)   : 1059.02
  T3 (5R from entry)     : 1011.8

  ### PARITY: DB vs MATH
  Entry  matches expected        : PASS
  SL     matches expected        : PASS
  R      matches expected        : PASS
  T1     matches DB R-calc       : PASS
  T2     matches DB R-calc       : PASS
  T3     matches DB R-calc       : PASS

  ### LAYER 3: API (/api/v1/screener/shortlist)
  API entry_price        : 1169.2
  API stop_loss          : 1200.68
  API target_1           : 1106.24
  API target_2           : 1059.02
  API target_3           : 1011.8
  API direction          : SUPPLY
  API cmp                : 1140.0

  ### PARITY: DB vs API
  Entry  DB=1169.2 API=1169.2   : PASS
  SL     DB=1200.68 API=1200.68   : PASS
  T1     DB=1106.24 API=1106.24   : PASS

  ### VERDICT: PASS

## SYMBOL: HDFCBANK
------------------------------------------------------------

  ### LAYER 1: DATABASE (trade_plans)
  Direction              : DEMAND
  Participating TFs      : ["1M", "1W", "1D"]
  Achievements           : 3
  overlap_min (L_common) : 646.11
  overlap_max (H_common) : 703.43
  entry_price            : 703.43
  stop_loss              : 643.61
  risk_per_share (R)     : 59.82
  target_1  (2.0R)       : 823.07
  target_2  (3.5R)       : 912.8
  target_3  (5.0R)       : 1002.53
  atr_14                 : 12.48
  atr_buffer (0.20*ATR)  : 2.5
  current_price (CMP)    : 700.8
  distance_pct           : 0.38
  is_fresh               : 1
  created_at             : 2026-09-09 06:44:46.623245

  ### LAYER 2: MATHEMATICAL RE-DERIVATION
  Expected Entry         : 703.43
  Expected SL            : 643.61
  Expected R             : 59.82
  T1 (2R from entry)     : 823.07
  T2 (3.5R from entry)   : 912.8
  T3 (5R from entry)     : 1002.53

  ### PARITY: DB vs MATH
  Entry  matches expected        : PASS
  SL     matches expected        : PASS
  R      matches expected        : PASS
  T1     matches DB R-calc       : PASS
  T2     matches DB R-calc       : PASS
  T3     matches DB R-calc       : PASS

  ### LAYER 3: API (/api/v1/screener/shortlist)
  API entry_price        : 703.43
  API stop_loss          : 643.61
  API target_1           : 823.07
  API target_2           : 912.8
  API target_3           : 1002.53
  API direction          : DEMAND
  API cmp                : 700.8

  ### PARITY: DB vs API
  Entry  DB=703.43 API=703.43   : PASS
  SL     DB=643.61 API=643.61   : PASS
  T1     DB=823.07 API=823.07   : PASS

  ### VERDICT: PASS

======================================================================
## GATE 19 FINAL SUMMARY
------------------------------------------------------------
  BSOFT           : PASS
  RELIANCE        : PASS (LEGITIMATE TRANSFORMATION)
  TCS             : PASS
  INFY            : PASS
  HDFCBANK        : PASS

  GATE 19 VERDICT: PASS
======================================================================