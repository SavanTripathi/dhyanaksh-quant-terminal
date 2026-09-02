import os
import json
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime

from app.engine.data_feed import fetch_nse_market_data
from app.engine.aggregator import CandleAggregator
from app.engine.zone_detector import detect_htf_supply_demand_zone
from app.engine.gtf_engine import GTFEngine
from app.engine.conviction_ranker import ConvictionRankingEngine
from app.domain.enums import Timeframe, ZoneDirection

UNIVERSE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC",
    "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN",
    "BAJFINANCE", "ULTRACEMCO", "NTPC", "ONGC", "WIPRO", "HCLTECH",
    "POWERGRID", "COALINDIA", "TATASTEEL", "TMPV", "BERGEPAINT", "EMAMILTD",
    "TITAGARH", "MAZDOCK", "BIKAJI"
]

LOCKED_CANDIDATE_HASH = "1378ece5ef6837748b9f1dc63a900f79b04fe76afc015e95032088a7c8953852"
PROSPECTIVE_START_BOUNDARY = "2026-09-01T00:00:00Z"

def run_replay_simulation():
    print("=" * 95)
    print("PHASE 10.2B: ISOLATED HISTORICAL REPLAY & ENGINEERING VALIDATION ENGINE")
    print("=" * 95)

    # Assert broker execution hard disabled
    assert os.getenv("ENABLE_LIVE_BROKER_EXECUTION", "false").lower() == "false"

    gtf_engine = GTFEngine()
    conviction_engine = ConvictionRankingEngine()

    replay_events = []
    replay_daily = []
    
    event_counter = 1
    total_closed_trades = 0
    cumulative_pnl = 0.0

    # Run replay across historical data window (e.g. recent 180 days)
    for sym in UNIVERSE:
        try:
            df = fetch_nse_market_data(sym, days=365)
            if df.empty or len(df) < 50:
                continue
            
            df = df.sort_index()
            df['sma_50'] = df['close'].rolling(window=50, min_periods=20).mean()
            df['sma_200'] = df['close'].rolling(window=200, min_periods=50).mean()

            # Iterate through bars simulating EOD evaluation
            for t in range(30, len(df) - 15, 5):
                df_t = df.iloc[:t]
                eval_date = df.index[t]
                eval_date_str = eval_date.strftime("%Y-%m-%d")
                
                # Check boundary: Replay mode strictly labels pre-boundary data as REPLAY
                is_prospective = eval_date.strftime("%Y-%m-%dT%H:%M:%SZ") >= PROSPECTIVE_START_BOUNDARY
                ledger_tag = "PROSPECTIVE_EVIDENCE" if is_prospective else "TEST_HISTORICAL_REPLAY"

                curr_price = df.iloc[t]['close']
                sma_200 = df.iloc[t]['sma_200']
                sma_50 = df.iloc[t]['sma_50']
                
                regime = "BULL" if (pd.isna(sma_200) or curr_price >= sma_200 * 1.03) else ("BEAR" if curr_price <= sma_200 * 0.97 else "SIDEWAYS")

                c_1d = df_t.to_dict('records')
                schema_1w = CandleAggregator.aggregate_from_df(df_t, Timeframe.WEEKLY, sym)
                schema_1m = CandleAggregator.aggregate_from_df(df_t, Timeframe.MONTHLY, sym)
                
                c_1w = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_1w]
                c_1m = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_1m]
                
                z_1d = detect_htf_supply_demand_zone(c_1d, "1D")
                z_1w = detect_htf_supply_demand_zone(c_1w, "1W") if len(c_1w) >= 15 else None
                z_1m = detect_htf_supply_demand_zone(c_1m, "1M") if len(c_1m) >= 10 else None
                
                primary_zone = z_1d or z_1w
                if not primary_zone:
                    continue
                
                # DEMAND ONLY FILTER
                if primary_zone["direction"] != "DEMAND":
                    continue
                
                proximal = primary_zone["proximal"]
                distal = primary_zone["distal"]
                zone_id = f"{sym}_DEMAND_{eval_date_str}"
                
                # State 1: ZONE_DETECTED
                replay_events.append({
                    "event_id": f"REPLAY-EVT-{event_counter:05d}",
                    "setup_id": zone_id,
                    "symbol": sym,
                    "timestamp": f"{eval_date_str}T15:30:00Z",
                    "event_type": "ZONE_DETECTED",
                    "state": "ZONE_ACTIVE",
                    "ledger_type": ledger_tag,
                    "candidate_hash": LOCKED_CANDIDATE_HASH
                })
                event_counter += 1

                # Evaluate Forward Bars for Rejection Confirmation & Fill
                in_zone = False
                confirmed = False
                filled = False
                entry_price = 0.0
                stop_loss = distal * 0.995
                risk = abs(proximal - stop_loss)
                t1 = proximal + 2.0 * risk
                
                for f_idx in range(t + 1, min(t + 20, len(df))):
                    f_bar = df.iloc[f_idx]
                    f_date_str = df.index[f_idx].strftime("%Y-%m-%d")
                    h, l, o, c = f_bar["high"], f_bar["low"], f_bar["open"], f_bar["close"]
                    
                    if not in_zone:
                        if l <= proximal:
                            in_zone = True
                            replay_events.append({
                                "event_id": f"REPLAY-EVT-{event_counter:05d}",
                                "setup_id": zone_id,
                                "symbol": sym,
                                "timestamp": f"{f_date_str}T10:00:00Z",
                                "event_type": "ZONE_ENTERED",
                                "state": "CONFIRMATION_PENDING",
                                "ledger_type": ledger_tag,
                                "candidate_hash": LOCKED_CANDIDATE_HASH
                            })
                            event_counter += 1
                        continue
                    
                    if in_zone and not confirmed:
                        # Model B Confirmation rule: Green close with lower wick rejection
                        if c > o and (c - l) >= (h - c):
                            confirmed = True
                            replay_events.append({
                                "event_id": f"REPLAY-EVT-{event_counter:05d}",
                                "setup_id": zone_id,
                                "symbol": sym,
                                "timestamp": f"{f_date_str}T15:30:00Z",
                                "event_type": "REJECTION_CONFIRMED",
                                "state": "ENTRY_PENDING",
                                "ledger_type": ledger_tag,
                                "candidate_hash": LOCKED_CANDIDATE_HASH
                            })
                            event_counter += 1
                        continue
                    
                    if confirmed and not filled:
                        # Fill next-bar open
                        filled = True
                        entry_price = o
                        stop_loss = min(distal * 0.995, l * 0.997)
                        risk = abs(entry_price - stop_loss)
                        t1 = entry_price + 2.0 * risk
                        replay_events.append({
                            "event_id": f"REPLAY-EVT-{event_counter:05d}",
                            "setup_id": zone_id,
                            "symbol": sym,
                            "timestamp": f"{f_date_str}T09:15:00Z",
                            "event_type": "PAPER_FILLED",
                            "state": "IN_POSITION",
                            "ledger_type": ledger_tag,
                            "candidate_hash": LOCKED_CANDIDATE_HASH
                        })
                        event_counter += 1
                        continue
                    
                    if filled:
                        if l <= stop_loss:
                            # STOPPED OUT
                            replay_events.append({
                                "event_id": f"REPLAY-EVT-{event_counter:05d}",
                                "setup_id": zone_id,
                                "symbol": sym,
                                "timestamp": f"{f_date_str}T14:00:00Z",
                                "event_type": "STOP_HIT",
                                "state": "CLOSED",
                                "pnl_r": -1.0,
                                "ledger_type": ledger_tag,
                                "candidate_hash": LOCKED_CANDIDATE_HASH
                            })
                            event_counter += 1
                            total_closed_trades += 1
                            cumulative_pnl -= 1.0
                            break
                        elif h >= t1:
                            # TARGET T1 HIT
                            replay_events.append({
                                "event_id": f"REPLAY-EVT-{event_counter:05d}",
                                "setup_id": zone_id,
                                "symbol": sym,
                                "timestamp": f"{f_date_str}T14:00:00Z",
                                "event_type": "TARGET_1_HIT",
                                "state": "CLOSED",
                                "pnl_r": 2.0,
                                "ledger_type": ledger_tag,
                                "candidate_hash": LOCKED_CANDIDATE_HASH
                            })
                            event_counter += 1
                            total_closed_trades += 1
                            cumulative_pnl += 2.0
                            break

        except Exception as e:
            continue

    df_events = pd.DataFrame(replay_events)
    df_events.to_csv("PAPER_TRADING_V1_1_REPLAY_TEST_EVENTS.csv", index=False)
    print(f"Generated PAPER_TRADING_V1_1_REPLAY_TEST_EVENTS.csv with {len(df_events)} simulated events.")
    print(f"Total Replay Closed Trades Encountered: {total_closed_trades}")

    # Generate Replay Daily Snapshot
    replay_daily.append({
        "date": "2026-08-31",
        "total_replay_events": len(df_events),
        "total_replay_closed_trades": total_closed_trades,
        "cumulative_net_r": round(cumulative_pnl, 2),
        "candidate_hash": LOCKED_CANDIDATE_HASH,
        "mode": "TEST_HISTORICAL_REPLAY"
    })
    pd.DataFrame(replay_daily).to_csv("PAPER_TRADING_V1_1_REPLAY_TEST_DAILY.csv", index=False)
    print("Generated PAPER_TRADING_V1_1_REPLAY_TEST_DAILY.csv.")
    print("=" * 95)

if __name__ == "__main__":
    run_replay_simulation()
