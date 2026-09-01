import sqlite3
import os
import logging

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "production_scanner.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "schema.sql")

def migrate_db():
    print(f"Applying schema migrations to {DB_PATH}...")
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database migration executed successfully.")

if __name__ == "__main__":
    migrate_db()
