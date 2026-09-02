import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from app.engine.data_feed import fetch_nse_market_data
from app.engine.aggregator import CandleAggregator
from app.engine.zone_detector import detect_htf_supply_demand_zone
from app.domain.enums import Timeframe

UNIVERSE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", 
    "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", 
    "BAJFINANCE", "ULTRACEMCO", "NTPC", "ONGC", "WIPRO", "HCLTECH", 
    "POWERGRID", "COALINDIA", "TATASTEEL", "TMPV", "BERGEPAINT", "EMAMILTD", 
    "TITAGARH", "MAZDOCK", "BIKAJI"
]

def run_corrected_phase3_backtest():
    print("=" * 95)
    print("PHASE 3 FORENSIC BACKTEST: RIGOROUS MTF AGGREGATION & STRICT ATZ CLASSIFICATION")
    print("=" * 95)

    train_end = pd.Timestamp("2025-08-31")
    val_end = pd.Timestamp("2026-02-28")
    
    all_trades = []
    
    for sym in UNIVERSE:
        try:
            df = fetch_nse_market_data(sym, days=3 * 365)
            if df.empty or len(df) < 100:
                continue
            
            df = df.sort_index()
            df['sma_200'] = df['close'].rolling(window=200, min_periods=50).mean()
            
            # Step forward through time
            for t in range(50, len(df) - 5, 5):
                df_t = df.iloc[:t]
                signal_date = df.index[t]
                
                # Split label
                if signal_date <= train_end:
                    split_label = "TRAIN"
                elif signal_date <= val_end:
                    split_label = "VALIDATION"
                else:
                    split_label = "TEST_OOS"
                
                # Market Regime
                curr_price = df.iloc[t]['close']
                sma_val = df.iloc[t]['sma_200']
                if pd.isna(sma_val) or curr_price >= sma_val * 1.03:
                    regime = "BULL"
                elif curr_price <= sma_val * 0.97:
                    regime = "BEAR"
                else:
                    regime = "SIDEWAYS"
                
                # 1. True Point-In-Time Multi-Timeframe Resampling
                c_1d = df_t.to_dict('records')
                
                # Aggregate 1W, 1M, 3M properly
                schema_1w = CandleAggregator.aggregate_from_df(df_t, Timeframe.WEEKLY, sym)
                schema_1m = CandleAggregator.aggregate_from_df(df_t, Timeframe.MONTHLY, sym)
                schema_3m = CandleAggregator.aggregate_from_df(df_t, Timeframe.QUARTERLY, sym)
                
                c_1w = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_1w]
                c_1m = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_1m]
                c_3m = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_3m]
                
                # 2. Detect Zones across respective timeframe histories
                z_1d = detect_htf_supply_demand_zone(c_1d, "1D")
                z_1w = detect_htf_supply_demand_zone(c_1w, "1W") if len(c_1w) >= 15 else None
                z_1m = detect_htf_supply_demand_zone(c_1m, "1M") if len(c_1m) >= 10 else None
                z_3m = detect_htf_supply_demand_zone(c_3m, "3M") if len(c_3m) >= 5 else None
                
                # We trade if an active zone exists on 1D or 1W
                primary_zone = z_1d or z_1w
                if not primary_zone:
                    continue
                
                direction = primary_zone["direction"]
                is_demand = direction == "DEMAND"
                
                has_1d = bool(z_1d and z_1d['direction'] == direction)
                has_1w = bool(z_1w and z_1w['direction'] == direction)
                has_1m = bool(z_1m and z_1m['direction'] == direction)
                has_3m = bool(z_3m and z_3m['direction'] == direction)
                
                confluence_count = sum([has_1d, has_1w, has_1m, has_3m])
                is_atz = (has_1d and has_1w and has_1m and has_3m)
                
                if is_atz:
                    conf_tier = "ATZ (4-TF)"
                elif confluence_count == 3:
                    conf_tier = "TRIPLE (3-TF)"
                elif confluence_count == 2:
                    conf_tier = "DUAL (2-TF)"
                else:
                    conf_tier = "SINGLE (1-TF)"
                
                proximal = primary_zone["proximal"]
                distal = primary_zone["distal"]
                
                sl = distal * 0.995 if is_demand else distal * 1.005
                risk = abs(proximal - sl)
                if risk <= 0:
                    continue
                
                t1 = proximal + 2.0 * risk if is_demand else proximal - 2.0 * risk
                t2 = proximal + 3.5 * risk if is_demand else proximal - 3.5 * risk
                t3 = proximal + 5.0 * risk if is_demand else proximal - 5.0 * risk
                
                gtf_score = 7.0 + (confluence_count * 1.5)
                conviction_score = int(round(70 + (confluence_count * 7.5)))
                
                # Simulation Walk-Forward (Conservative Execution)
                entry_filled = False
                exit_reason = "EXPIRED"
                pnl_r = 0.0
                bars_to_entry = 0
                bars_held = 0
                deepest_adverse = proximal
                deepest_favorable = proximal
                
                for f_idx in range(t, min(t + 40, len(df))):
                    bar = df.iloc[f_idx]
                    high = bar["high"]
                    low = bar["low"]
                    open_p = bar["open"]
                    
                    if not entry_filled:
                        bars_to_entry += 1
                        if is_demand and (open_p <= proximal or low <= proximal):
                            entry_filled = True
                            deepest_adverse = min(deepest_adverse, low)
                            deepest_favorable = max(deepest_favorable, high)
                        elif not is_demand and (open_p >= proximal or high >= proximal):
                            entry_filled = True
                            deepest_adverse = max(deepest_adverse, high)
                            deepest_favorable = min(deepest_favorable, low)
                        continue
                    
                    # In Trade
                    bars_held += 1
                    if is_demand:
                        deepest_adverse = min(deepest_adverse, low)
                        deepest_favorable = max(deepest_favorable, high)
                        
                        # Stop Loss takes strict precedence on same-bar touches
                        if open_p <= sl or low <= sl:
                            exit_reason = "STOP"
                            pnl_r = -1.0
                            break
                        elif high >= t3:
                            exit_reason = "T3"
                            pnl_r = 5.0
                            break
                        elif high >= t2:
                            exit_reason = "T2"
                            pnl_r = 3.5
                            break
                        elif high >= t1:
                            exit_reason = "T1"
                            pnl_r = 2.0
                            break
                    else:
                        deepest_adverse = max(deepest_adverse, high)
                        deepest_favorable = min(deepest_favorable, low)
                        
                        if open_p >= sl or high >= sl:
                            exit_reason = "STOP"
                            pnl_r = -1.0
                            break
                        elif low <= t3:
                            exit_reason = "T3"
                            pnl_r = 5.0
                            break
                        elif low <= t2:
                            exit_reason = "T2"
                            pnl_r = 3.5
                            break
                        elif low <= t1:
                            exit_reason = "T1"
                            pnl_r = 2.0
                            break
                
                if entry_filled and exit_reason != "EXPIRED":
                    mae = abs(deepest_adverse - proximal) / proximal * 100.0
                    mfe = abs(deepest_favorable - proximal) / proximal * 100.0
                    all_trades.append({
                        "symbol": sym,
                        "date": signal_date.strftime("%Y-%m-%d"),
                        "split": split_label,
                        "regime": regime,
                        "direction": direction,
                        "confluence_tier": conf_tier,
                        "confluence_count": confluence_count,
                        "is_atz": is_atz,
                        "has_3m": has_3m,
                        "has_1m": has_1m,
                        "has_1w": has_1w,
                        "has_1d": has_1d,
                        "gtf_score": gtf_score,
                        "conviction_score": conviction_score,
                        "pnl_r": pnl_r,
                        "exit_reason": exit_reason,
                        "bars_to_entry": bars_to_entry,
                        "bars_held": bars_held,
                        "mae_pct": mae,
                        "mfe_pct": mfe,
                        "is_win": pnl_r > 0
                    })
        except Exception as e:
            continue
            
    df_trades = pd.DataFrame(all_trades)
    df_trades.to_csv("TRADE_LEVEL_OOS_RESULTS.csv", index=False)
    print(f"Generated corrected TRADE_LEVEL_OOS_RESULTS.csv with {len(df_trades)} verified trades.")
    
    # 1. Total & Confluence Breakdown
    print("\n--- CONFLUENCE TIER DECOMPOSITION ---")
    conf_summary = []
    for tier in ["ATZ (4-TF)", "TRIPLE (3-TF)", "DUAL (2-TF)", "SINGLE (1-TF)"]:
        sub = df_trades[df_trades["confluence_tier"] == tier]
        n = len(sub)
        if n == 0:
            print(f"{tier:<15} | Trades: 0")
            continue
        w = len(sub[sub["is_win"]])
        wr = (w / n) * 100.0
        avg_r = sub["pnl_r"].mean()
        gains = sub[sub["pnl_r"] > 0]["pnl_r"].sum()
        losses = abs(sub[sub["pnl_r"] < 0]["pnl_r"].sum())
        pf = gains / losses if losses > 0 else 0.0
        conf_summary.append({"tier": tier, "trades": n, "win_rate": round(wr, 1), "avg_r": round(avg_r, 2), "profit_factor": round(pf, 2)})
        print(f"{tier:<15} | Trades: {n:<5} | Win Rate: {wr:5.1f}% | Avg R: {avg_r:5.2f}R | Profit Factor: {pf:4.2f}")
    pd.DataFrame(conf_summary).to_csv("CONFLUENCE_ANALYSIS.csv", index=False)
    
    # 2. Re-evaluate Temporal Splits
    print("\n--- TEMPORAL WALK-FORWARD SPLITS ---")
    wf_summary = []
    for sp in ["TRAIN", "VALIDATION", "TEST_OOS"]:
        sub = df_trades[df_trades["split"] == sp]
        n = len(sub)
        w = len(sub[sub["is_win"]])
        wr = (w / n) * 100.0 if n > 0 else 0.0
        avg_r = sub["pnl_r"].mean() if n > 0 else 0.0
        gains = sub[sub["pnl_r"] > 0]["pnl_r"].sum()
        losses = abs(sub[sub["pnl_r"] < 0]["pnl_r"].sum())
        pf = gains / losses if losses > 0 else 0.0
        wf_summary.append({"split": sp, "trades": n, "win_rate": round(wr, 1), "avg_r": round(avg_r, 2), "profit_factor": round(pf, 2)})
        print(f"[{sp:<10}] Trades: {n:<5} | Win Rate: {wr:5.1f}% | Avg R: {avg_r:5.2f}R | Profit Factor: {pf:4.2f}")
    pd.DataFrame(wf_summary).to_csv("OOS_RECALCULATED_RESULTS.csv", index=False)

    # 3. Market Regime Matrix
    print("\n--- REGIME × DIRECTION MATRIX ---")
    reg_summary = []
    for cat in ["DEMAND", "SUPPLY", "ATZ", "NON_ATZ"]:
        for reg in ["BULL", "BEAR", "SIDEWAYS"]:
            if cat == "DEMAND":
                sub = df_trades[(df_trades["direction"] == "DEMAND") & (df_trades["regime"] == reg)]
            elif cat == "SUPPLY":
                sub = df_trades[(df_trades["direction"] == "SUPPLY") & (df_trades["regime"] == reg)]
            elif cat == "ATZ":
                sub = df_trades[(df_trades["is_atz"] == True) & (df_trades["regime"] == reg)]
            else:
                sub = df_trades[(df_trades["is_atz"] == False) & (df_trades["regime"] == reg)]
            n = len(sub)
            if n == 0:
                continue
            w = len(sub[sub["is_win"]])
            wr = (w / n) * 100.0
            avg_r = sub["pnl_r"].mean()
            gains = sub[sub["pnl_r"] > 0]["pnl_r"].sum()
            losses = abs(sub[sub["pnl_r"] < 0]["pnl_r"].sum())
            pf = gains / losses if losses > 0 else 0.0
            reg_summary.append({"category": cat, "regime": reg, "trades": n, "win_rate": round(wr, 1), "avg_r": round(avg_r, 2), "profit_factor": round(pf, 2)})
            print(f"{cat:<10} × {reg:<8} | Trades: {n:<5} | Win Rate: {wr:5.1f}% | Avg R: {avg_r:5.2f}R | PF: {pf:4.2f}")
    pd.DataFrame(reg_summary).to_csv("REGIME_ANALYSIS.csv", index=False)

    # 4. Score Discrimination Analysis
    print("\n--- SCORE DISCRIMINATION BUCKETS ---")
    score_summary = []
    for sc_min, sc_max in [(70, 77), (78, 85), (86, 92), (93, 100)]:
        sub = df_trades[(df_trades["conviction_score"] >= sc_min) & (df_trades["conviction_score"] <= sc_max)]
        n = len(sub)
        if n == 0:
            continue
        w = len(sub[sub["is_win"]])
        wr = (w / n) * 100.0
        avg_r = sub["pnl_r"].mean()
        gains = sub[sub["pnl_r"] > 0]["pnl_r"].sum()
        losses = abs(sub[sub["pnl_r"] < 0]["pnl_r"].sum())
        pf = gains / losses if losses > 0 else 0.0
        score_summary.append({"score_bucket": f"{sc_min}-{sc_max}", "trades": n, "win_rate": round(wr, 1), "avg_r": round(avg_r, 2), "profit_factor": round(pf, 2)})
        print(f"Score {sc_min}-{sc_max:<3} | Trades: {n:<5} | Win Rate: {wr:5.1f}% | Avg R: {avg_r:5.2f}R | PF: {pf:4.2f}")
    pd.DataFrame(score_summary).to_csv("SCORE_DISCRIMINATION_ANALYSIS.csv", index=False)

    # 5. Signal Dependence / Cluster Analysis
    print("\n--- SIGNAL DEPENDENCE & CORRELATION AUDIT ---")
    trades_per_sym = df_trades.groupby("symbol").size()
    trades_per_date = df_trades.groupby("date").size()
    print(f"Total Unique Trading Dates: {len(trades_per_date)}")
    print(f"Mean Concurrent Trades per Day: {trades_per_date.mean():.1f} (Max: {trades_per_date.max()})")
    print(f"Mean Trades per Symbol: {trades_per_sym.mean():.1f} (Min: {trades_per_sym.min()}, Max: {trades_per_sym.max()})")
    
    dep_summary = [{
        "total_trades": len(df_trades),
        "unique_dates": len(trades_per_date),
        "max_concurrent_day": int(trades_per_date.max()),
        "mean_trades_per_sym": round(trades_per_sym.mean(), 1),
        "max_trades_per_sym": int(trades_per_sym.max())
    }]
    pd.DataFrame(dep_summary).to_csv("SIGNAL_DEPENDENCE_ANALYSIS.csv", index=False)
    print("=" * 95)

if __name__ == "__main__":
    run_corrected_phase3_backtest()
