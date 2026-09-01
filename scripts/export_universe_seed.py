"""
Export all scanned NIFTY 500 setups from SQLite (screener_shortlist_cache)
to frontend/src/data/nifty500_universe_setups.json for immediate instant startup hydration.
"""
import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "production_scanner.db")
OUTPUT_PATH = os.path.join(BASE_DIR, "frontend", "src", "data", "nifty500_universe_setups.json")

def export_universe():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM screener_shortlist_cache ORDER BY symbol")
    rows = cursor.fetchall()
    conn.close()

    setups = []
    for r in rows:
        try:
            item = json.loads(r[0])
            setups.append(item)
        except Exception as e:
            print(f"Error parsing row: {e}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(setups, f, indent=2)

    print(f"[OK] Exported {len(setups)} NIFTY 500 setups to {OUTPUT_PATH}")

if __name__ == "__main__":
    export_universe()
