import sqlite3, pathlib, sys

db = pathlib.Path("db/flight_simulator.db")

if not db.exists():
    print("DB missing at", db.resolve())
    sys.exit(1)

conn = sqlite3.connect(str(db))
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cur.fetchall()

print("TABLES:", tables)

for t in tables:
    table_name = t[0]
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    print(f"{table_name}: {cur.fetchone()[0]} rows")

conn.close()