import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "flight_simulator.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Reset ONLY base_price
cur.execute("""
UPDATE flight
SET base_price = 3000
""")

conn.commit()
conn.close()

print("Base price reset successfully")