import sqlite3
import json
import numpy as np

conn = sqlite3.connect('production_scanner.db')
cur = conn.cursor()
cur.execute('SELECT data FROM screener_shortlist_cache')
rows = cur.fetchall()
conn.close()

plans = [json.loads(r[0]) for r in rows]

conviction_scores = [float(p.get('conviction_score', 0)) for p in plans]
gtf_scores = [float(p.get('gtf_odds_score', 0)) for p in plans]

print("=" * 80)
print("PHASE 2: PRODUCTION SCORE STATISTICAL DISTRIBUTION AUDIT")
print("=" * 80)
print(f"Total Scanned Universe Size: {len(plans)}")
print("\n--- CONVICTION SCORE (0–100 Scale) ---")
print(f"Minimum: {np.min(conviction_scores):.1f}")
print(f"Maximum: {np.max(conviction_scores):.1f}")
print(f"Mean:    {np.mean(conviction_scores):.2f}")
print(f"Median:  {np.median(conviction_scores):.1f}")
print(f"P25:     {np.percentile(conviction_scores, 25):.1f}")
print(f"P75:     {np.percentile(conviction_scores, 75):.1f}")
print(f"P90:     {np.percentile(conviction_scores, 90):.1f}")
print(f"P95:     {np.percentile(conviction_scores, 95):.1f}")
print(f"P99:     {np.percentile(conviction_scores, 99):.1f}")

print("\n--- SCORE SATURATION COUNTS ---")
print(f"Count 90+:  {sum(1 for s in conviction_scores if s >= 90)} ({sum(1 for s in conviction_scores if s >= 90)/len(plans)*100:.1f}%)")
print(f"Count 95+:  {sum(1 for s in conviction_scores if s >= 95)} ({sum(1 for s in conviction_scores if s >= 95)/len(plans)*100:.1f}%)")
print(f"Count 98+:  {sum(1 for s in conviction_scores if s >= 98)} ({sum(1 for s in conviction_scores if s >= 98)/len(plans)*100:.1f}%)")
print(f"Count 99+:  {sum(1 for s in conviction_scores if s >= 99)} ({sum(1 for s in conviction_scores if s >= 99)/len(plans)*100:.1f}%)")
print(f"Count 100:  {sum(1 for s in conviction_scores if s == 100)} ({sum(1 for s in conviction_scores if s == 100)/len(plans)*100:.1f}%)")

print("\n--- GTF SCORE (0–13.0 Scale) ---")
print(f"Minimum: {np.min(gtf_scores):.1f}")
print(f"Maximum: {np.max(gtf_scores):.1f}")
print(f"Mean:    {np.mean(gtf_scores):.2f}")
print(f"Median:  {np.median(gtf_scores):.1f}")
print(f"P25:     {np.percentile(gtf_scores, 25):.1f}")
print(f"P75:     {np.percentile(gtf_scores, 75):.1f}")
print(f"P90:     {np.percentile(gtf_scores, 90):.1f}")
print(f"P95:     {np.percentile(gtf_scores, 95):.1f}")
print(f"P99:     {np.percentile(gtf_scores, 99):.1f}")
print("=" * 80)
