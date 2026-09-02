import sqlite3
import json

conn = sqlite3.connect('production_scanner.db')
cur = conn.cursor()
cur.execute('SELECT data FROM screener_shortlist_cache')
rows = cur.fetchall()
conn.close()

plans = [json.loads(r[0]) for r in rows]
demand_plans = [p for p in plans if p.get('direction') == 'DEMAND']
demand_plans.sort(key=lambda x: (x.get('conviction_score', 0), x.get('achievements', 0), -x.get('distance_pct', 999)), reverse=True)
top10 = demand_plans[:10]

print("=" * 80)
print("DHYANAKSH QUANT TERMINAL — TOP 10 INSTITUTIONAL DEMAND SETUPS")
print("=" * 80)

for i, p in enumerate(top10, 1):
    sym = p['symbol']
    name = p.get('name', sym)
    cmp = p.get('cmp', 0.0)
    entry = p.get('entry_price', 0.0)
    sl = p.get('stop_loss', 0.0)
    t1 = p.get('target_1', 0.0)
    t2 = p.get('target_2', 0.0)
    t3 = p.get('target_3', 0.0)
    risk = p.get('risk_per_share', 0.0)
    dist = p.get('distance_pct', 0.0)
    score = p.get('conviction_score', 0)
    gtf = p.get('gtf_odds_score', 0.0)
    curve = p.get('gtf_curve_location', 'LOW_ON_CURVE')
    tf = p.get('zone_timeframe', '3M')
    zones = p.get('all_timeframe_zones', {})
    
    print(f"#{i} {sym} ({name})")
    print(f"   CMP: Rs {cmp:.2f} | Entry (Proximal): Rs {entry:.2f} | Stop Loss (Distal): Rs {sl:.2f}")
    print(f"   Targets -> T1: Rs {t1:.2f} | T2: Rs {t2:.2f} | T3: Rs {t3:.2f}")
    print(f"   Risk/Share: Rs {risk:.2f} | Distance to Base: {dist:.2f}%")
    print(f"   Conviction: {score}/100 | GTF Odds: {gtf:.1f}/13.0 | Curve: {curve}")
    print(f"   Timeframe Confluences: {list(zones.keys())}")
    for tf_key, z in zones.items():
        print(f"      - {tf_key}: Proximal Rs {z.get('proximal'):.2f}, Distal Rs {z.get('distal'):.2f}")
    print("-" * 80)
