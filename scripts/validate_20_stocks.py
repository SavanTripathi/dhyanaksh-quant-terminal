import sqlite3
import json

conn = sqlite3.connect('production_scanner.db')
cur = conn.cursor()
cur.execute('SELECT data FROM screener_shortlist_cache')
rows = cur.fetchall()
conn.close()

plans = [json.loads(r[0]) for r in rows]

# Group stocks
demands = [p for p in plans if p.get('direction') == 'DEMAND']
supplies = [p for p in plans if p.get('direction') == 'SUPPLY']
atz_stocks = [p for p in plans if p.get('has_qdz') and p.get('has_mdz') and p.get('has_wdz') and p.get('has_ddz')]

demands.sort(key=lambda x: (x.get('conviction_score', 0), -x.get('distance_pct', 999)), reverse=True)
supplies.sort(key=lambda x: (x.get('conviction_score', 0), -x.get('distance_pct', 999)), reverse=True)

sample_stocks = []
sample_stocks.extend(demands[:5])      # 5 High Demand
sample_stocks.extend(demands[-3:])     # 3 Lower Demand
sample_stocks.extend(supplies[:5])     # 5 High Supply
sample_stocks.extend(supplies[-3:])    # 3 Lower Supply
sample_stocks.extend(atz_stocks[:4])   # 4 ATZ Confluent

# Deduplicate
seen = set()
unique_samples = []
for s in sample_stocks:
    if s['symbol'] not in seen:
        seen.add(s['symbol'])
        unique_samples.append(s)

print(f"Total Unique Validated Samples: {len(unique_samples)}")
print("=" * 110)
print(f"{'#':<3} {'Symbol':<12} {'Dir':<7} {'TF':<4} {'CMP':<9} {'Entry':<9} {'SL':<9} {'T1':<9} {'Risk':<7} {'Dist%':<6} {'Score':<6} {'GTF':<5} {'ATZ':<5}")
print("-" * 110)

for i, p in enumerate(unique_samples, 1):
    sym = p['symbol']
    dir_val = p.get('direction', 'DEMAND')
    tf = p.get('zone_timeframe', '3M')
    cmp_val = p.get('cmp', 0.0)
    entry = p.get('entry_price', 0.0)
    sl = p.get('stop_loss', 0.0)
    t1 = p.get('target_1', 0.0)
    risk = p.get('risk_per_share', 0.0)
    dist = p.get('distance_pct', 0.0)
    score = p.get('conviction_score', 0)
    gtf = p.get('gtf_odds_score', 0.0)
    is_atz = "YES" if (p.get('has_qdz') and p.get('has_mdz') and p.get('has_wdz') and p.get('has_ddz')) else "NO"
    
    print(f"{i:<3} {sym:<12} {dir_val:<7} {tf:<4} {cmp_val:<9.2f} {entry:<9.2f} {sl:<9.2f} {t1:<9.2f} {risk:<7.2f} {dist:<6.2f} {score:<6} {gtf:<5.1f} {is_atz:<5}")

print("=" * 110)
