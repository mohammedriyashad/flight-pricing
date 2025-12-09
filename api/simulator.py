# milestone1/api/simulator.py
import sqlite3
import threading
import time
import random
from datetime import datetime

# Import pathlib.Path with an alias to avoid collision with fastapi.Path
from pathlib import Path as PathlibPath

from .pricing_engine import calculate_dynamic_price

# Resolve DB using the same logic as main.py, using the unambiguous alias
BASE_DIR = PathlibPath(__file__).resolve().parents[1]  # milestone1/
DB_FILE = (BASE_DIR / "db" / "flight_simulator.db").resolve()

def _get_conn():
    # use str(DB_FILE) to ensure sqlite accepts the path
    return sqlite3.connect(str(DB_FILE), timeout=30, isolation_level=None)

def _update_one(cur, row):
    fid = row[0]
    departure = row[5]
    total_seats = row[7] or 1
    available_seats = row[8] or 0
    base_fare = row[9] or 0.0

    demand = random.choices(["low", "medium", "high"], weights=[20, 60, 20])[0]
    sale_prob = {"low": 0.02, "medium": 0.08, "high": 0.2}[demand]
    if random.random() < sale_prob and available_seats > 0:
        sold = random.randint(1, min(5, available_seats))
        available_seats = max(0, available_seats - sold)

    new_price = calculate_dynamic_price(
        base_fare=base_fare,
        seats_left=available_seats,
        total_seats=total_seats,
        departure_iso=departure,
        demand_level=demand,
        now=datetime.utcnow()
    )

    # fetch last_price if present
    cur.execute("SELECT last_price FROM flight WHERE flight_id = ?", (fid,))
    last = cur.fetchone()
    last_price = last[0] if last else None

    cur.execute(
        "UPDATE flight SET available_seats = ?, last_price = ?, demand_level = ? WHERE flight_id = ?",
        (available_seats, new_price, demand, fid)
    )

    if last_price is None or abs(new_price - (last_price or 0.0)) >= 1.0:
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO fare_history (flight_id, timestamp, price) VALUES (?, ?, ?)",
                    (fid, ts, new_price))

def run_simulator_loop(interval_seconds: int = 15, stop_event: threading.Event = None): # type: ignore
    def loop():
        while True:
            if stop_event and stop_event.is_set():
                break
            conn = _get_conn()
            cur = conn.cursor()
            try:
                cur.execute("""SELECT flight_id, flight_number, airline, origin_airport, destination_airport,
                                    departure_time, arrival_time, total_seats, available_seats, price
                               FROM flight""")
                rows = cur.fetchall()
                for row in rows:
                    try:
                        _update_one(cur, row)
                    except Exception as e:
                        print("simulator update error for flight", row[0], e)
                conn.commit()
            except Exception as e:
                try:
                    conn.rollback()
                except:
                    pass
                print("simulator loop error:", e)
            finally:
                conn.close()
            time.sleep(interval_seconds)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return t