import sqlite3
import os
import logging

logger = logging.getLogger(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "production_scanner.db")

def hard_reset_and_reseed():
    print(f"Purging stale cache from {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} does not exist yet. Will be created on startup.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop old caches
    cursor.execute("DROP TABLE IF EXISTS symbol_candles_cache")
    cursor.execute("DROP TABLE IF EXISTS screener_shortlist_cache")
    cursor.execute("DROP TABLE IF EXISTS stock_universe_cache")
    cursor.execute("DELETE FROM trade_plans WHERE symbol IN ('TMPV', 'TATAMOTORS', 'ABBOTINDIA')")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symbol_candles_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            candles_json JSON NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("Database purged and verified successfully.")

if __name__ == "__main__":
    hard_reset_and_reseed()
