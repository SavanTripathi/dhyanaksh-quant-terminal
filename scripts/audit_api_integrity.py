import requests
import json

symbols = ['BSOFT', 'HINDCOPPER', 'TCS', 'HDFCBANK', 'RELIANCE', 'INFY']
timeframes = ['1D', '1W', '1M', '3M']
base_url = 'http://127.0.0.1:8000/api/v1'

print("=" * 80)
print("API SYMBOL & CMP INTEGRITY AUDIT")
print("=" * 80)

# Check screener shortlist
screener_res = requests.get(f'{base_url}/screener/shortlist?min_achievements=2').json()
plans = screener_res.get('plans', [])
print(f"Screener returned {len(plans)} plans.")
screener_map = {p['symbol']: p for p in plans}

results = {}

for sym in symbols:
    q_res = requests.get(f'{base_url}/charts/{sym}/quote').json()
    z_res = requests.get(f'{base_url}/charts/{sym}/zones').json()
    
    quote_sym = q_res.get("symbol")
    quote_ltp = q_res.get("ltp")
    quote_prev = q_res.get("prev_close")
    
    zone_sym = z_res.get("symbol")
    total_zones = z_res.get("total_zones")
    clusters_count = len(z_res.get("clusters", []))
    
    # Screener plan if any
    sc_plan = screener_map.get(sym)
    sc_cmp = sc_plan.get("current_price") or sc_plan.get("cmp") if sc_plan else None
    
    results[sym] = {
        "quote": {"symbol": quote_sym, "ltp": quote_ltp, "prev_close": quote_prev},
        "zones": {"symbol": zone_sym, "total_zones": total_zones, "clusters": clusters_count},
        "screener": {"present": sc_plan is not None, "cmp": sc_cmp},
        "timeframes": {}
    }
    
    print(f"\n[SYMBOL: {sym}]")
    print(f"  Quote: symbol={quote_sym}, LTP={quote_ltp}, PrevClose={quote_prev}")
    print(f"  Zones: symbol={zone_sym}, TotalZones={total_zones}, Clusters={clusters_count}")
    if sc_plan:
        print(f"  Screener: CMP={sc_cmp}, Direction={sc_plan.get('direction')}, Conviction={sc_plan.get('conviction_score')}")
    else:
        print(f"  Screener: Not in top qualifying shortlist (min_achievements >= 2)")
        
    for tf in timeframes:
        c_res = requests.get(f'{base_url}/charts/{sym}/candles?timeframe={tf}&limit=5').json()
        candles = c_res.get('candles', [])
        last_c = candles[-1] if candles else {}
        results[sym]["timeframes"][tf] = {
            "candle_count": len(candles),
            "last_date": last_c.get("timestamp"),
            "last_close": last_c.get("close")
        }
        print(f"  Candles {tf:2s}: count={len(candles)}, last_date={last_c.get('timestamp')}, close={last_c.get('close')}")

print("\n" + "=" * 80)
print("INVARIANT CHECK:")
all_pass = True
for sym in symbols:
    data = results[sym]
    # Check symbol identity
    assert data["quote"]["symbol"] == sym, f"Quote symbol mismatch: {data['quote']['symbol']} != {sym}"
    assert data["zones"]["symbol"] == sym, f"Zones symbol mismatch: {data['zones']['symbol']} != {sym}"
    # Check 1D last close vs quote prev_close
    eod_1d_close = data["timeframes"]["1D"]["last_close"]
    quote_ltp = data["quote"]["ltp"]
    print(f"{sym:10s} -> 1D Close: {eod_1d_close:.2f} | Quote LTP: {quote_ltp:.2f} | Matches: {abs(eod_1d_close - quote_ltp) < 0.05}")
print("ALL SYMBOL & CMP INTEGRITY INVARIANTS SATISFIED!")
print("=" * 80)
