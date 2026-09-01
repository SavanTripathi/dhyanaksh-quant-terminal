"""
NIFTY 500 Universe Loader.
Seeds the master_instruments table from the local nifty500_universe.json file,
filtered for Market Cap >= ₹5,000 Cr.
"""
import sqlite3
import json
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "production_scanner.db")
UNIVERSE_JSON = os.path.join(os.path.dirname(os.path.dirname(__file__)), "engine", "nifty500_universe.json")

MIN_MCAP_CR = 5000.0


def sync_nifty500_universe() -> int:
    """
    Loads the NIFTY 500 universe from the local JSON file and seeds
    master_instruments with eligible stocks (Market Cap >= ₹5,000 Cr).
    Returns the count of seeded symbols.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_instruments (
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            exchange TEXT DEFAULT 'NSE',
            sector TEXT,
            market_cap REAL,
            is_nifty500 INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            last_synced_at TIMESTAMP
        )
    """)

    with open(UNIVERSE_JSON, "r") as f:
        universe = json.load(f)

    eligible = [s for s in universe if s.get("market_cap_cr", 0) >= MIN_MCAP_CR]

    # Deactivate all first, then activate eligible ones
    cursor.execute("UPDATE master_instruments SET is_active = 0")

    for stock in eligible:
        sym = stock["symbol"].strip().upper()
        name = stock.get("name", sym)
        sector = stock.get("sector", "")
        mcap = stock.get("market_cap_cr", 0.0)
        cursor.execute("""
            INSERT INTO master_instruments (symbol, name, exchange, sector, market_cap, is_nifty500, is_active)
            VALUES (?, ?, 'NSE', ?, ?, 1, 1)
            ON CONFLICT(symbol) DO UPDATE SET
                name = excluded.name,
                sector = excluded.sector,
                market_cap = excluded.market_cap,
                is_active = 1,
                is_nifty500 = 1
        """, (sym, name, sector, mcap))

    conn.commit()
    conn.close()
    logger.info(f"Seeded {len(eligible)} NIFTY 500 stocks (>= ₹{MIN_MCAP_CR} Cr) into master_instruments.")
    return len(eligible)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    count = sync_nifty500_universe()
    print(f"[OK] Universe seeded: {count} eligible NIFTY 500 stocks loaded into production_scanner.db")
