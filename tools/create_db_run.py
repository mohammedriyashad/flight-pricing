import sqlite3
from pathlib import Path
import sys, traceback

BASE = Path(__file__).resolve().parent.parent
SQL = BASE / "db" / "db_schema.sql"
DB = BASE / "db" / "flight_simulator.db"

print("SQL FILE:", SQL)
print("DB FILE:", DB)

if not SQL.exists():
    print("ERROR: SQL file not found at", SQL.resolve())
    sys.exit(1)

# Create db folder if missing
DB.parent.mkdir(parents=True, exist_ok=True)

# Remove old DB (safe for development)
if DB.exists():
    DB.unlink()

try:
    sql = SQL.read_text(encoding="utf-8")
    conn = sqlite3.connect(str(DB))
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print("SUCCESS: Database created at", DB.resolve())
except Exception:
    print("ERROR while creating DB:")
    traceback.print_exc()