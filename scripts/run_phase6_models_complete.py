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

def run_phase6_models_complete():
    print("=" * 95)
    print("PHASE 6: COMPLETE FORENSIC VALIDATION OF CONFIRMATION MODELS A, B, C, D, E")
    print("=" * 95)

    gtf_engine = GTFEngine()
    conviction_engine = ConvictionRankingEngine()

    train_end = pd.Timestamp("2025-08-31")
    val_end = pd.Timestamp("2026-02-28")

    all_phase6_trades = []

    for sym in UNIVERSE:
        try:
            df = fetch_nse_market_data(sym, days=3 * 365)
            if df.empty or len(df) < 100:
                continue
            
            df = df.sort_index()
            df['sma_50'] = df['close'].rolling(window=50, min_periods=20).mean()
            df['sma_200'] = df['close'].rolling(window=200, min_periods=50).mean()
            
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
                sma_200_val = df.iloc[t]['sma_200']
                sma_50_val = df.iloc[t]['sma_50']
                
                if pd.isna(sma_200_val) or curr_price >= sma_200_val * 1.03:
                    regime = "BULL"
                elif curr_price <= sma_200_val * 0.97:
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
                
                basing_count = primary_zone.get("basing_count", 2)
                gtf_7_res = gtf_engine.calculate_gtf_7_point_trade_score(0, 2.5, basing_candle_count=basing_count, direction=zone_dir)
                gtf_7_val = gtf_7_res["gtf_score_7"]
                
                demand_bound = min(proximal, distal) * 0.95
                supply_bound = max(proximal, distal) * 1.05
                curve_res = gtf_engine.calculate_location_on_curve(curr_price, demand_bound, supply_bound, zone_dir)
                curve_loc = curve_res["curve_location"]
                
                gtf_13_res = gtf_engine.score_gtf_13_point_odds(2.5, basing_count, True, confluence_count, curve_loc, zone_dir)
                gtf_13_val = gtf_13_res["gtf_odds_score"]
                
                conv_res = conviction_engine.compute_conviction_score(
                    sym, zone_dir, confluence_count, distance_pct, True, (confluence_count>=2),
                    sma_50_val, sma_200_val, curr_price, True, True, True
                )
                conv_val = conv_res["conviction_score"]

                # =========================================================================
                # 1. MODEL A: BLIND LIMIT (Type 1)
                # =========================================================================
                entry_a = False; pnl_a = 0.0; exit_a = "EXPIRED"
                for f_idx in range(t, min(t + 40, len(df))):
                    bar = df.iloc[f_idx]
                    h, l, o = bar["high"], bar["low"], bar["open"]
                    if not entry_a:
                        if is_demand and (o <= proximal or l <= proximal): entry_a = True
                        elif not is_demand and (o >= proximal or h >= proximal): entry_a = True
                        continue
                    if is_demand:
                        if o <= base_sl or l <= base_sl: pnl_a = -1.0; exit_a = "STOP"; break
                        elif h >= proximal + 2.0 * base_risk: pnl_a = 2.0; exit_a = "T1"; break
                    else:
                        if o >= base_sl or h >= base_sl: pnl_a = -1.0; exit_a = "STOP"; break
                        elif l <= proximal - 2.0 * base_risk: pnl_a = 2.0; exit_a = "T1"; break
                if entry_a and exit_a != "EXPIRED":
                    all_phase6_trades.append({"model": "MODEL_A", "symbol": sym, "date": signal_date.strftime("%Y-%m-%d"), "split": split_label, "regime": regime, "direction": direction_str, "confluence": confluence_count, "is_atz": is_atz, "gtf_7": gtf_7_val, "gtf_13": gtf_13_val, "conviction": conv_val, "pnl_r": pnl_a, "is_win": pnl_a > 0})

                # =========================================================================
                # 2. MODEL B: REJECTION CONFIRMATION (Type 2A)
                # =========================================================================
                in_zone_b = False; entry_b = False; pnl_b = 0.0; exit_b = "EXPIRED"; risk_b = 0.0; conf_sl_b = base_sl; entry_price_b = 0.0
                for f_idx in range(t, min(t + 40, len(df))):
                    bar = df.iloc[f_idx]
                    h, l, o, c = bar["high"], bar["low"], bar["open"], bar["close"]
                    if not in_zone_b:
                        if is_demand and l <= proximal: in_zone_b = True
                        elif not is_demand and h >= proximal: in_zone_b = True
                        continue
                    if not entry_b:
                        is_bull_rev = is_demand and c > o and (c - l) > (h - c)
                        is_bear_rev = (not is_demand) and c < o and (h - c) > (c - l)
                        if is_bull_rev or is_bear_rev:
                            entry_b = True; entry_price_b = c
                            conf_sl_b = l * 0.997 if is_demand else h * 1.003
                            risk_b = abs(entry_price_b - conf_sl_b)
                            if risk_b <= 0: entry_b = False
                        continue
                    if is_demand:
                        if l <= conf_sl_b: pnl_b = -1.0; exit_b = "STOP"; break
                        elif h >= entry_price_b + 2.0 * risk_b: pnl_b = 2.0; exit_b = "T1"; break
                    else:
                        if h >= conf_sl_b: pnl_b = -1.0; exit_b = "STOP"; break
                        elif l <= entry_price_b - 2.0 * risk_b: pnl_b = 2.0; exit_b = "T1"; break
                if entry_b and exit_b != "EXPIRED":
                    all_phase6_trades.append({"model": "MODEL_B", "symbol": sym, "date": signal_date.strftime("%Y-%m-%d"), "split": split_label, "regime": regime, "direction": direction_str, "confluence": confluence_count, "is_atz": is_atz, "gtf_7": gtf_7_val, "gtf_13": gtf_13_val, "conviction": conv_val, "pnl_r": pnl_b, "is_win": pnl_b > 0})

                # =========================================================================
                # 3. MODEL C: STRUCTURE BREAK CONFIRMATION (Type 2B)
                # =========================================================================
                entry_c = False; pnl_c = 0.0; exit_c = "EXPIRED"; in_zone_c = False; risk_c = 0.0; conf_sl_c = base_sl; entry_price_c = 0.0
                for f_idx in range(t, min(t + 40, len(df))):
                    if f_idx < 3: continue
                    bar = df.iloc[f_idx]
                    h, l, o, c = bar["high"], bar["low"], bar["open"], bar["close"]
                    if not in_zone_c:
                        if is_demand and l <= proximal: in_zone_c = True
                        elif not is_demand and h >= proximal: in_zone_c = True
                        continue
                    if not entry_c:
                        p_high = df.iloc[f_idx-3:f_idx]["high"].max()
                        p_low = df.iloc[f_idx-3:f_idx]["low"].min()
                        if is_demand and c > p_high:
                            entry_c = True; entry_price_c = c; conf_sl_c = df.iloc[f_idx-3:f_idx+1]["low"].min() * 0.997
                            risk_c = abs(entry_price_c - conf_sl_c)
                            if risk_c <= 0: entry_c = False
                        elif not is_demand and c < p_low:
                            entry_c = True; entry_price_c = c; conf_sl_c = df.iloc[f_idx-3:f_idx+1]["high"].max() * 1.003
                            risk_c = abs(entry_price_c - conf_sl_c)
                            if risk_c <= 0: entry_c = False
                        continue
                    if is_demand:
                        if l <= conf_sl_c: pnl_c = -1.0; exit_c = "STOP"; break
                        elif h >= entry_price_c + 2.0 * risk_c: pnl_c = 2.0; exit_c = "T1"; break
                    else:
                        if h >= conf_sl_c: pnl_c = -1.0; exit_c = "STOP"; break
                        elif l <= entry_price_c - 2.0 * risk_c: pnl_c = 2.0; exit_c = "T1"; break
                if entry_c and exit_c != "EXPIRED":
                    all_phase6_trades.append({"model": "MODEL_C", "symbol": sym, "date": signal_date.strftime("%Y-%m-%d"), "split": split_label, "regime": regime, "direction": direction_str, "confluence": confluence_count, "is_atz": is_atz, "gtf_7": gtf_7_val, "gtf_13": gtf_13_val, "conviction": conv_val, "pnl_r": pnl_c, "is_win": pnl_c > 0})

                # =========================================================================
                # 4. MODEL D: DISPLACEMENT + STRUCTURE BREAK (Type 3A)
                # =========================================================================
                entry_d = False; pnl_d = 0.0; exit_d = "EXPIRED"; in_zone_d = False; risk_d = 0.0; conf_sl_d = base_sl; entry_price_d = 0.0
                for f_idx in range(t, min(t + 40, len(df))):
                    if f_idx < 3: continue
                    bar = df.iloc[f_idx]
                    h, l, o, c = bar["high"], bar["low"], bar["open"], bar["close"]
                    rng = h - l; bdy = abs(c - o)
                    if not in_zone_d:
                        if is_demand and l <= proximal: in_zone_d = True
                        elif not is_demand and h >= proximal: in_zone_d = True
                        continue
                    if not entry_d:
                        is_erc = (rng > 0 and (bdy / rng) >= 0.60)
                        p_high = df.iloc[f_idx-3:f_idx]["high"].max()
                        p_low = df.iloc[f_idx-3:f_idx]["low"].min()
                        if is_demand and is_erc and c > o and c > p_high:
                            entry_d = True; entry_price_d = c; conf_sl_d = l * 0.997
                            risk_d = abs(entry_price_d - conf_sl_d)
                            if risk_d <= 0: entry_d = False
                        elif not is_demand and is_erc and c < o and c < p_low:
                            entry_d = True; entry_price_d = c; conf_sl_d = h * 1.003
                            risk_d = abs(entry_price_d - conf_sl_d)
                            if risk_d <= 0: entry_d = False
                        continue
                    if is_demand:
                        if l <= conf_sl_d: pnl_d = -1.0; exit_d = "STOP"; break
                        elif h >= entry_price_d + 2.0 * risk_d: pnl_d = 2.0; exit_d = "T1"; break
                    else:
                        if h >= conf_sl_d: pnl_d = -1.0; exit_d = "STOP"; break
                        elif l <= entry_price_d - 2.0 * risk_d: pnl_d = 2.0; exit_d = "T1"; break
                if entry_d and exit_d != "EXPIRED":
                    all_phase6_trades.append({"model": "MODEL_D", "symbol": sym, "date": signal_date.strftime("%Y-%m-%d"), "split": split_label, "regime": regime, "direction": direction_str, "confluence": confluence_count, "is_atz": is_atz, "gtf_7": gtf_7_val, "gtf_13": gtf_13_val, "conviction": conv_val, "pnl_r": pnl_d, "is_win": pnl_d > 0})

                # =========================================================================
                # 5. MODEL E: CONFIRMATION + RETEST ENTRY (Type 3B)
                # =========================================================================
                entry_e = False; pnl_e = 0.0; exit_e = "EXPIRED"; in_zone_e = False; displacement_seen = False; retest_lvl = 0.0; risk_e = 0.0; conf_sl_e = base_sl
                for f_idx in range(t, min(t + 40, len(df))):
                    if f_idx < 3: continue
                    bar = df.iloc[f_idx]
                    h, l, o, c = bar["high"], bar["low"], bar["open"], bar["close"]
                    rng = h - l; bdy = abs(c - o)
                    if not in_zone_e:
                        if is_demand and l <= proximal: in_zone_e = True
                        elif not is_demand and h >= proximal: in_zone_e = True
                        continue
                    if not displacement_seen:
                        is_erc = (rng > 0 and (bdy / rng) >= 0.60)
                        p_high = df.iloc[f_idx-3:f_idx]["high"].max()
                        p_low = df.iloc[f_idx-3:f_idx]["low"].min()
                        if is_demand and is_erc and c > o and c > p_high:
                            displacement_seen = True
                            retest_lvl = (o + c) / 2.0 # 50% retracement level
                            conf_sl_e = l * 0.997
                            risk_e = abs(retest_lvl - conf_sl_e)
                        elif not is_demand and is_erc and c < o and c < p_low:
                            displacement_seen = True
                            retest_lvl = (o + c) / 2.0
                            conf_sl_e = h * 1.003
                            risk_e = abs(conf_sl_e - retest_lvl)
                        continue
                    if displacement_seen and not entry_e:
                        # Check retest touch
                        if is_demand and l <= retest_lvl: entry_e = True
                        elif not is_demand and h >= retest_lvl: entry_e = True
                        continue
                    if entry_e:
                        if is_demand:
                            if l <= conf_sl_e: pnl_e = -1.0; exit_e = "STOP"; break
                            elif h >= retest_lvl + 2.0 * risk_e: pnl_e = 2.0; exit_e = "T1"; break
                        else:
                            if h >= conf_sl_e: pnl_e = -1.0; exit_e = "STOP"; break
                            elif l <= retest_lvl - 2.0 * risk_e: pnl_e = 2.0; exit_e = "T1"; break
                if entry_e and exit_e != "EXPIRED" and risk_e > 0:
                    all_phase6_trades.append({"model": "MODEL_E", "symbol": sym, "date": signal_date.strftime("%Y-%m-%d"), "split": split_label, "regime": regime, "direction": direction_str, "confluence": confluence_count, "is_atz": is_atz, "gtf_7": gtf_7_val, "gtf_13": gtf_13_val, "conviction": conv_val, "pnl_r": pnl_e, "is_win": pnl_e > 0})

        except Exception as e:
            continue
            
    df_all = pd.DataFrame(all_phase6_trades)
    df_all.to_csv("PHASE6_MODEL_COMPARISON.csv", index=False)
    print(f"Generated PHASE6_MODEL_COMPARISON.csv with {len(df_all)} total trade records across all 5 models.")

    # --- EXECUTIVE COMPARISON TABLE ---
    print("\n" + "=" * 95)
    print("EXECUTIVE MODEL COMPARISON SUMMARY (MODELS A, B, C, D, E)")
    print("=" * 95)
    for m in ["MODEL_A", "MODEL_B", "MODEL_C", "MODEL_D", "MODEL_E"]:
        sub = df_all[df_all["model"] == m]
        n = len(sub)
        w = len(sub[sub["is_win"]])
        wr = (w / n) * 100.0 if n > 0 else 0.0
        avg_r = sub["pnl_r"].mean() if n > 0 else 0.0
        g = sub[sub["pnl_r"] > 0]["pnl_r"].sum()
        l = abs(sub[sub["pnl_r"] < 0]["pnl_r"].sum())
        pf = g / l if l > 0 else 0.0
        
        # OOS
        oos = sub[sub["split"] == "TEST_OOS"]
        n_oos = len(oos)
        w_oos = len(oos[oos["is_win"]])
        wr_oos = (w_oos / n_oos) * 100.0 if n_oos > 0 else 0.0
        avg_r_oos = oos["pnl_r"].mean() if n_oos > 0 else 0.0
        g_oos = oos[oos["pnl_r"] > 0]["pnl_r"].sum()
        l_oos = abs(oos[oos["pnl_r"] < 0]["pnl_r"].sum())
        pf_oos = g_oos / l_oos if l_oos > 0 else 0.0
        
        print(f"{m:<10} | All Trades: {n:<5} | Win: {wr:5.1f}% | Avg R: {avg_r:5.2f}R | PF: {pf:4.2f} || OOS Trades: {n_oos:<4} | OOS Win: {wr_oos:5.1f}% | OOS Avg R: {avg_r_oos:5.2f}R | OOS PF: {pf_oos:4.2f}")

    # Model B OOS Breakdown
    sub_b = df_all[df_all["model"] == "MODEL_B"]
    sub_b.to_csv("PHASE6_MODEL_B_OOS.csv", index=False)
    
    # Model B by Symbol
    sym_rows = []
    for sym in UNIVERSE:
        s = sub_b[sub_b["symbol"] == sym]
        if len(s) == 0: continue
        g = s[s["pnl_r"] > 0]["pnl_r"].sum()
        l = abs(s[s["pnl_r"] < 0]["pnl_r"].sum())
        pf = g / l if l > 0 else 0.0
        sym_rows.append({"symbol": sym, "trades": len(s), "win_rate": round((len(s[s["is_win"]])/len(s))*100, 1), "avg_r": round(s["pnl_r"].mean(), 2), "profit_factor": round(pf, 2)})
    pd.DataFrame(sym_rows).to_csv("PHASE6_MODEL_B_SYMBOL.csv", index=False)

    # Model B by Regime
    reg_rows = []
    for d in ["DEMAND", "SUPPLY"]:
        for reg in ["BULL", "BEAR", "SIDEWAYS"]:
            s = sub_b[(sub_b["direction"] == d) & (sub_b["regime"] == reg)]
            if len(s) == 0: continue
            g = s[s["pnl_r"] > 0]["pnl_r"].sum()
            l = abs(s[s["pnl_r"] < 0]["pnl_r"].sum())
            pf = g / l if l > 0 else 0.0
            reg_rows.append({"direction": d, "regime": reg, "trades": len(s), "win_rate": round((len(s[s["is_win"]])/len(s))*100, 1), "avg_r": round(s["pnl_r"].mean(), 2), "profit_factor": round(pf, 2)})
    pd.DataFrame(reg_rows).to_csv("PHASE6_MODEL_B_REGIME.csv", index=False)

    # Model B by Score
    sc_rows = []
    for b_min, b_max in [(60, 69), (70, 79), (80, 84), (85, 89), (90, 93), (94, 97), (98, 100)]:
        s = sub_b[(sub_b["conviction"] >= b_min) & (sub_b["conviction"] <= b_max)]
        if len(s) == 0: continue
        g = s[s["pnl_r"] > 0]["pnl_r"].sum()
        l = abs(s[s["pnl_r"] < 0]["pnl_r"].sum())
        pf = g / l if l > 0 else 0.0
        sc_rows.append({"score_bucket": f"{b_min}-{b_max}", "trades": len(s), "win_rate": round((len(s[s["is_win"]])/len(s))*100, 1), "avg_r": round(s["pnl_r"].mean(), 2), "profit_factor": round(pf, 2)})
    pd.DataFrame(sc_rows).to_csv("PHASE6_MODEL_B_SCORE.csv", index=False)

    # Cost Sensitivity
    cost_rows = []
    for bps in [0, 10, 25, 50]:
        friction_r = bps * 0.002
        adj_r = sub_b["pnl_r"].mean() - friction_r
        cost_rows.append({"friction_bps": bps, "adjusted_avg_r": round(adj_r, 2)})
    pd.DataFrame(cost_rows).to_csv("PHASE6_MODEL_B_COST.csv", index=False)

    print("=" * 95)

if __name__ == "__main__":
    run_phase6_models_complete()
