import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB = BASE_DIR / "db" / "flight_simulator.db"
SCHEMA = BASE_DIR / "db" / "db_schema.sql"

DB.parent.mkdir(exist_ok=True)

if DB.exists():
    DB.unlink()

conn = sqlite3.connect(DB)
conn.executescript(SCHEMA.read_text())
conn.commit()
conn.close()

print("✅ Database created at:", DB)