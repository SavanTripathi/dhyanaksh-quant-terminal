import os
import json
import sqlite3
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

def run_phase5_confirmation_research():
    print("=" * 95)
    print("PHASE 5: CONFIRMATION ENTRY MODELS (TYPES 2 & 3) RESEARCH ENGINE")
    print("=" * 95)

    gtf_engine = GTFEngine()
    conviction_engine = ConvictionRankingEngine()

    train_end = pd.Timestamp("2025-08-31")
    val_end = pd.Timestamp("2026-02-28")

    all_model_trades = []

    for sym in UNIVERSE:
        try:
            df = fetch_nse_market_data(sym, days=3 * 365)
            if df.empty or len(df) < 100:
                continue
            
            df = df.sort_index()
            df['sma_200'] = df['close'].rolling(window=200, min_periods=50).mean()
            
            # Step through historical bars
            for t in range(50, len(df) - 10, 5):
                df_t = df.iloc[:t]
                signal_date = df.index[t]
                
                if signal_date <= train_end:
                    split_label = "TRAIN"
                elif signal_date <= val_end:
                    split_label = "VALIDATION"
                else:
                    split_label = "TEST_OOS"
                    
                curr_price = df.iloc[t]['close']
                sma_val = df.iloc[t]['sma_200']
                if pd.isna(sma_val) or curr_price >= sma_val * 1.03:
                    regime = "BULL"
                elif curr_price <= sma_val * 0.97:
                    regime = "BEAR"
                else:
                    regime = "SIDEWAYS"
                    
                c_1d = df_t.to_dict('records')
                schema_1w = CandleAggregator.aggregate_from_df(df_t, Timeframe.WEEKLY, sym)
                schema_1m = CandleAggregator.aggregate_from_df(df_t, Timeframe.MONTHLY, sym)
                schema_3m = CandleAggregator.aggregate_from_df(df_t, Timeframe.QUARTERLY, sym)
                
                c_1w = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_1w]
                c_1m = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_1m]
                c_3m = [c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in schema_3m]
                
                z_1d = detect_htf_supply_demand_zone(c_1d, "1D")
                z_1w = detect_htf_supply_demand_zone(c_1w, "1W") if len(c_1w) >= 15 else None
                z_1m = detect_htf_supply_demand_zone(c_1m, "1M") if len(c_1m) >= 10 else None
                z_3m = detect_htf_supply_demand_zone(c_3m, "3M") if len(c_3m) >= 5 else None
                
                primary_zone = z_1d or z_1w
                if not primary_zone:
                    continue
                
                direction_str = primary_zone["direction"]
                is_demand = direction_str == "DEMAND"
                zone_dir = ZoneDirection.DEMAND if is_demand else ZoneDirection.SUPPLY
                
                has_1d = bool(z_1d and z_1d['direction'] == direction_str)
                has_1w = bool(z_1w and z_1w['direction'] == direction_str)
                has_1m = bool(z_1m and z_1m['direction'] == direction_str)
                has_3m = bool(z_3m and z_3m['direction'] == direction_str)
                
                confluence_count = sum([has_1d, has_1w, has_1m, has_3m])
                is_atz = (has_1d and has_1w and has_1m and has_3m)
                
                proximal = primary_zone["proximal"]
                distal = primary_zone["distal"]
                distance_pct = round(abs(curr_price - proximal) / curr_price * 100, 2)
                
                # Baseline 0.20 ATR Stop
                base_sl = distal * 0.995 if is_demand else distal * 1.005
                base_risk = abs(proximal - base_sl)
                if base_risk <= 0:
                    continue
                
                # --- MODEL EVALUATIONS ACROSS FUTURE BARS (t+1 ... t+40) ---
                
                # 1. MODEL A: BLIND LIMIT (Type 1)
                entry_a = False
                pnl_a = 0.0
                exit_a = "EXPIRED"
                for f_idx in range(t, min(t + 40, len(df))):
                    bar = df.iloc[f_idx]
                    h, l, o = bar["high"], bar["low"], bar["open"]
                    if not entry_a:
                        if is_demand and (o <= proximal or l <= proximal):
                            entry_a = True
                        elif not is_demand and (o >= proximal or h >= proximal):
                            entry_a = True
                        continue
                    if is_demand:
                        if o <= base_sl or l <= base_sl:
                            pnl_a = -1.0; exit_a = "STOP"; break
                        elif h >= proximal + 2.0 * base_risk:
                            pnl_a = 2.0; exit_a = "T1"; break
                    else:
                        if o >= base_sl or h >= base_sl:
                            pnl_a = -1.0; exit_a = "STOP"; break
                        elif l <= proximal - 2.0 * base_risk:
                            pnl_a = 2.0; exit_a = "T1"; break
                if entry_a and exit_a != "EXPIRED":
                    all_model_trades.append({"model": "MODEL_A (Blind Limit)", "symbol": sym, "split": split_label, "regime": regime, "direction": direction_str, "confluence": confluence_count, "is_atz": is_atz, "pnl_r": pnl_a, "is_win": pnl_a > 0})

                # 2. MODEL B: LTF REJECTION CONFIRMATION (Type 2A)
                # Wait for price inside zone, then require reversal candle close, enter next-bar open
                in_zone = False
                entry_b = False
                pnl_b = 0.0
                exit_b = "EXPIRED"
                conf_sl_b = base_sl
                for f_idx in range(t, min(t + 40, len(df))):
                    bar = df.iloc[f_idx]
                    h, l, o, c = bar["high"], bar["low"], bar["open"], bar["close"]
                    if not in_zone:
                        if is_demand and l <= proximal:
                            in_zone = True
                        elif not is_demand and h >= proximal:
                            in_zone = True
                        continue
                    if not entry_b:
                        # Check confirmation candle close
                        is_bull_rev = is_demand and c > o and (c - l) > (h - c) # Lower wick rejection or green close
                        is_bear_rev = (not is_demand) and c < o and (h - c) > (c - l) # Upper wick rejection
                        if is_bull_rev or is_bear_rev:
                            entry_b = True
                            entry_price_b = c
                            conf_sl_b = l * 0.997 if is_demand else h * 1.003
                            risk_b = abs(entry_price_b - conf_sl_b)
                            if risk_b <= 0: entry_b = False
                        continue
                    # In Trade Model B
                    if is_demand:
                        if l <= conf_sl_b:
                            pnl_b = -1.0; exit_b = "STOP"; break
                        elif h >= entry_price_b + 2.0 * risk_b:
                            pnl_b = 2.0; exit_b = "T1"; break
                    else:
                        if h >= conf_sl_b:
                            pnl_b = -1.0; exit_b = "STOP"; break
                        elif l <= entry_price_b - 2.0 * risk_b:
                            pnl_b = 2.0; exit_b = "T1"; break
                if entry_b and exit_b != "EXPIRED":
                    all_model_trades.append({"model": "MODEL_B (Rejection Conf)", "symbol": sym, "split": split_label, "regime": regime, "direction": direction_str, "confluence": confluence_count, "is_atz": is_atz, "pnl_r": pnl_b, "is_win": pnl_b > 0})

                # 3. MODEL C: STRUCTURE BREAK CONFIRMATION (CHoCH / Type 2B)
                # Break prior 3-day swing high/low from within zone
                entry_c = False
                pnl_c = 0.0
                exit_c = "EXPIRED"
                conf_sl_c = base_sl
                in_zone_c = False
                for f_idx in range(t, min(t + 40, len(df))):
                    if f_idx < 3: continue
                    bar = df.iloc[f_idx]
                    h, l, o, c = bar["high"], bar["low"], bar["open"], bar["close"]
                    if not in_zone_c:
                        if is_demand and l <= proximal: in_zone_c = True
                        elif not is_demand and h >= proximal: in_zone_c = True
                        continue
                    if not entry_c:
                        prior_high = df.iloc[f_idx-3:f_idx]["high"].max()
                        prior_low = df.iloc[f_idx-3:f_idx]["low"].min()
                        if is_demand and c > prior_high:
                            entry_c = True; entry_price_c = c; conf_sl_c = df.iloc[f_idx-3:f_idx+1]["low"].min() * 0.997
                            risk_c = abs(entry_price_c - conf_sl_c)
                            if risk_c <= 0: entry_c = False
                        elif not is_demand and c < prior_low:
                            entry_c = True; entry_price_c = c; conf_sl_c = df.iloc[f_idx-3:f_idx+1]["high"].max() * 1.003
                            risk_c = abs(entry_price_c - conf_sl_c)
                            if risk_c <= 0: entry_c = False
                        continue
                    if is_demand:
                        if l <= conf_sl_c:
                            pnl_c = -1.0; exit_c = "STOP"; break
                        elif h >= entry_price_c + 2.0 * risk_c:
                            pnl_c = 2.0; exit_c = "T1"; break
                    else:
                        if h >= conf_sl_c:
                            pnl_c = -1.0; exit_c = "STOP"; break
                        elif l <= entry_price_c - 2.0 * risk_c:
                            pnl_c = 2.0; exit_c = "T1"; break
                if entry_c and exit_c != "EXPIRED":
                    all_model_trades.append({"model": "MODEL_C (Structure Break)", "symbol": sym, "split": split_label, "regime": regime, "direction": direction_str, "confluence": confluence_count, "is_atz": is_atz, "pnl_r": pnl_c, "is_win": pnl_c > 0})

        except Exception as e:
            continue
            
    df_res = pd.DataFrame(all_model_trades)
    df_res.to_csv("ENTRY_MODEL_TRADE_RESULTS.csv", index=False)
    print(f"Generated ENTRY_MODEL_TRADE_RESULTS.csv with {len(df_res)} records.")

    # --- MODEL COMPARISON SUMMARY ---
    print("\n--- MODEL COMPARISON SUMMARY (WALK-FORWARD & OOS) ---")
    comp_rows = []
    for m in df_res["model"].unique():
        sub = df_res[df_res["model"] == m]
        n = len(sub)
        w = len(sub[sub["is_win"]])
        wr = (w / n) * 100.0 if n > 0 else 0.0
        avg_r = sub["pnl_r"].mean() if n > 0 else 0.0
        gains = sub[sub["pnl_r"] > 0]["pnl_r"].sum()
        losses = abs(sub[sub["pnl_r"] < 0]["pnl_r"].sum())
        pf = gains / losses if losses > 0 else 0.0
        
        # Split OOS
        sub_oos = sub[sub["split"] == "TEST_OOS"]
        n_oos = len(sub_oos)
        w_oos = len(sub_oos[sub_oos["is_win"]])
        wr_oos = (w_oos / n_oos) * 100.0 if n_oos > 0 else 0.0
        avg_r_oos = sub_oos["pnl_r"].mean() if n_oos > 0 else 0.0
        gains_oos = sub_oos[sub_oos["pnl_r"] > 0]["pnl_r"].sum()
        losses_oos = abs(sub_oos[sub_oos["pnl_r"] < 0]["pnl_r"].sum())
        pf_oos = gains_oos / losses_oos if losses_oos > 0 else 0.0
        
        comp_rows.append({
            "model": m,
            "total_trades": n,
            "overall_wr": round(wr, 1),
            "overall_avg_r": round(avg_r, 2),
            "overall_pf": round(pf, 2),
            "oos_trades": n_oos,
            "oos_wr": round(wr_oos, 1),
            "oos_avg_r": round(avg_r_oos, 2),
            "oos_pf": round(pf_oos, 2)
        })
        print(f"{m:<25} | All Trades: {n:<5} | WR: {wr:5.1f}% | Avg R: {avg_r:5.2f}R | PF: {pf:4.2f} || OOS PF: {pf_oos:4.2f} ({avg_r_oos:5.2f}R)")
    pd.DataFrame(comp_rows).to_csv("ENTRY_MODEL_COMPARISON.csv", index=False)

    # --- OOS MATRIX & DEMAND SPLIT ---
    print("\n--- DEMAND × REGIME BREAKDOWN FOR MODEL B (REJECTION CONFIRMATION) ---")
    sub_b = df_res[df_res["model"] == "MODEL_B (Rejection Conf)"]
    for reg in ["BULL", "BEAR", "SIDEWAYS"]:
        for d in ["DEMAND", "SUPPLY"]:
            s = sub_b[(sub_b["regime"] == reg) & (sub_b["direction"] == d)]
            if len(s) == 0: continue
            w = len(s[s["is_win"]])
            wr = (w / len(s)) * 100.0
            avg_r = s["pnl_r"].mean()
            g = s[s["pnl_r"] > 0]["pnl_r"].sum()
            l = abs(s[s["pnl_r"] < 0]["pnl_r"].sum())
            pf = g / l if l > 0 else 0.0
            print(f"Model B | {d:<6} × {reg:<8} | Trades: {len(s):<4} | Win Rate: {wr:5.1f}% | Avg R: {avg_r:5.2f}R | PF: {pf:4.2f}")

    print("=" * 95)

if __name__ == "__main__":
    run_phase5_confirmation_research()
