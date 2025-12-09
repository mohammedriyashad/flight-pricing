import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "flight_simulator.db"
SQL_FILE = BASE_DIR / "fare_history.sql"

print("Using DB:", DB_FILE)
print("Using SQL file:", SQL_FILE)

sql_text = SQL_FILE.read_text()

conn = sqlite3.connect(str(DB_FILE))
cur = conn.cursor()
try:
    cur.executescript(sql_text)
    conn.commit()
    print("Migration completed successfully!")
except Exception as e:
    print("Migration failed:", e)
finally:
    conn.close()