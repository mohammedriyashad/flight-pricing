import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "milestone1" / "db" / "flight_simulator.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

seats = [f"{row}{num}" for row in "ABCDEF" for num in range(1, 31)]

for seat in seats:
    cur.execute(
        """
        INSERT OR IGNORE INTO flight_seats
        (flight_id, seat_number, status)
        VALUES (1, ?, 'AVAILABLE')
        """,
        (seat,),
    )

conn.commit()
conn.close()

print("✅ Seats seeded successfully")