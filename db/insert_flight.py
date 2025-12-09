# milestone1/db/insert_flight.py
import sqlite3, pathlib
p = pathlib.Path(__file__).resolve().parent / "flight_simulator.db"
conn = sqlite3.connect(str(p))
cur = conn.cursor()

cur.execute("""
INSERT INTO flight (flight_number, airline, origin_airport, destination_airport,
                    departure_time, arrival_time, total_seats, available_seats, price)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", ("RM500","TestAir", 1, 2, "2025-12-20 09:00:00", "2025-12-20 11:00:00", 150, 150, 3000.0))

conn.commit()
print("Inserted flight id:", cur.lastrowid)
conn.close()