import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from app.engine.data_feed import fetch_nse_market_data
from app.engine.zone_detector import detect_htf_supply_demand_zone

def run_production_historical_backtest(symbols, lookback_years=3):
    """
    Simulates historical zone entries, stops, and target hits with zero look-ahead bias
    and conservative same-candle execution rules.
    """
    all_trades = []
    
    for sym in symbols:
        try:
            df = fetch_nse_market_data(sym, days=lookback_years * 365)
            if df.empty or len(df) < 100:
                continue
            
            # Step forward candle by candle (Walk-Forward)
            # Minimum window for zone detection is 20 bars
            for t in range(20, len(df) - 5, 5): # sample every 5 bars to form rolling historical setups
                historical_slice = df.iloc[:t].to_dict('records')
                
                # Detect zone on available history ONLY
                zone = detect_htf_supply_demand_zone(historical_slice, "1D")
                if not zone:
                    continue
                
                proximal = zone["proximal"]
                distal = zone["distal"]
                direction = zone["direction"]
                is_demand = direction == "DEMAND"
                
                # ATR buffer for SL
                sl = distal * 0.995 if is_demand else distal * 1.005
                risk = abs(proximal - sl)
                if risk <= 0:
                    continue
                
                t1 = proximal + 2.0 * risk if is_demand else proximal - 2.0 * risk
                t2 = proximal + 3.5 * risk if is_demand else proximal - 3.5 * risk
                t3 = proximal + 5.0 * risk if is_demand else proximal - 5.0 * risk
                
                # Forward simulation across future candles [t:]
                entry_filled = False
                exit_reason = "EXPIRED"
                pnl_r = 0.0
                bars_to_entry = 0
                bars_held = 0
                deepest_adverse = proximal
                deepest_favorable = proximal
                
                for f_idx in range(t, min(t + 40, len(df))): # 40-bar holding limit
                    bar = df.iloc[f_idx]
                    high = bar["high"]
                    low = bar["low"]
                    close = bar["close"]
                    
                    if not entry_filled:
                        bars_to_entry += 1
                        # Entry triggered if price touches proximal
                        if is_demand and low <= proximal:
                            entry_filled = True
                            deepest_adverse = low
                            deepest_favorable = high
                        elif not is_demand and high >= proximal:
                            entry_filled = True
                            deepest_adverse = high
                            deepest_favorable = low
                        continue
                    
                    # Trade Active
                    bars_held += 1
                    if is_demand:
                        deepest_adverse = min(deepest_adverse, low)
                        deepest_favorable = max(deepest_favorable, high)
                        
                        # Conservative same-candle priority: Stop evaluated first
                        if low <= sl:
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
                        
                        if high >= sl:
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
                        "direction": direction,
                        "entry": proximal,
                        "sl": sl,
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
            
    return pd.DataFrame(all_trades)

# Run on Top 25 liquid NIFTY names representing broad sectors
sample_universe = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", 
    "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN", 
    "BAJFINANCE", "ULTRACEMCO", "NTPC", "TATAMOTORS", "ONGC", "WIPRO", "HCLTECH", 
    "POWERGRID", "COALINDIA", "TATASTEEL"
]

print("Running Comprehensive Walk-Forward Backtest across 25 Nifty Equities (3-Year Horizon)...")
df_results = run_production_historical_backtest(sample_universe, lookback_years=3)

print("=" * 80)
print("COMPREHENSIVE HISTORICAL BACKTEST & HIT-RATE METRICS")
print("=" * 80)
total_trades = len(df_results)
wins = len(df_results[df_results['is_win']])
losses = len(df_results[df_results['exit_reason'] == 'STOP'])
t1_hits = len(df_results[df_results['exit_reason'].isin(['T1', 'T2', 'T3'])])
t2_hits = len(df_results[df_results['exit_reason'].isin(['T2', 'T3'])])
t3_hits = len(df_results[df_results['exit_reason'] == 'T3'])

win_rate = (wins / total_trades) * 100.0 if total_trades > 0 else 0.0
avg_r = df_results['pnl_r'].mean() if total_trades > 0 else 0.0
median_r = df_results['pnl_r'].median() if total_trades > 0 else 0.0
gross_gains_r = df_results[df_results['pnl_r'] > 0]['pnl_r'].sum()
gross_losses_r = abs(df_results[df_results['pnl_r'] < 0]['pnl_r'].sum())
pf = gross_gains_r / gross_losses_r if gross_losses_r > 0 else 999.0

# Equity drawdown
equity_curve = df_results['pnl_r'].cumsum()
peak = equity_curve.cummax()
drawdown = peak - equity_curve
max_dd_r = drawdown.max()

print(f"Total Executed Trades: {total_trades}")
print(f"Wins: {wins} | Losses: {losses}")
print(f"Win Rate: {win_rate:.1f}%")
print(f"T1 Hit Rate (>= 2.0R): {(t1_hits / total_trades)*100:.1f}%")
print(f"T2 Hit Rate (>= 3.5R): {(t2_hits / total_trades)*100:.1f}%")
print(f"T3 Hit Rate (>= 5.0R): {(t3_hits / total_trades)*100:.1f}%")
print(f"Stop Hit Rate:        {(losses / total_trades)*100:.1f}%")
print(f"Average R per Trade:  {avg_r:.2f}R")
print(f"Median R per Trade:   {median_r:.2f}R")
print(f"Profit Factor:        {pf:.2f}")
print(f"Max Drawdown:         {max_dd_r:.2f}R")
print(f"Expectancy:           {avg_r:.2f}R per trade")

print("\n--- R-MULTIPLE DISTRIBUTION ---")
print(f"Mean:   {df_results['pnl_r'].mean():.2f}")
print(f"Median: {df_results['pnl_r'].median():.2f}")
print(f"P10:    {np.percentile(df_results['pnl_r'], 10):.2f}")
print(f"P25:    {np.percentile(df_results['pnl_r'], 25):.2f}")
print(f"P50:    {np.percentile(df_results['pnl_r'], 50):.2f}")
print(f"P75:    {np.percentile(df_results['pnl_r'], 75):.2f}")
print(f"P90:    {np.percentile(df_results['pnl_r'], 90):.2f}")

print("\n--- HOLDING PERIODS (Bars / Days) ---")
print(f"Median Time to Entry: {df_results['bars_to_entry'].median():.1f} bars")
print(f"Median Time in Trade: {df_results['bars_held'].median():.1f} bars")
print(f"P75 Time in Trade:    {np.percentile(df_results['bars_held'], 75):.1f} bars")
print(f"Mean MAE (Adverse):   {df_results['mae_pct'].mean():.2f}%")
print(f"Mean MFE (Favorable): {df_results['mfe_pct'].mean():.2f}%")

print("\n--- DEMAND VS SUPPLY SPLIT ---")
for d in ['DEMAND', 'SUPPLY']:
    sub = df_results[df_results['direction'] == d]
    if len(sub) > 0:
        sub_wins = len(sub[sub['is_win']])
        sub_losses = len(sub[sub['exit_reason'] == 'STOP'])
        sub_pf = sub[sub['pnl_r'] > 0]['pnl_r'].sum() / max(1.0, abs(sub[sub['pnl_r'] < 0]['pnl_r'].sum()))
        print(f"[{d}] Trades: {len(sub)} | Win Rate: {(sub_wins/len(sub))*100:.1f}% | Avg R: {sub['pnl_r'].mean():.2f}R | PF: {sub_pf:.2f}")

print("=" * 80)
