# milestone1/api/routes/search.py
import sqlite3
from datetime import datetime
from zipfile import Path
from ..pricing_engine import calculate_dynamic_price
from pathlib import Path as PathlibPath

DB_FILE = (PathlibPath(__file__).resolve().parents[1] / "db" / "flight_simulator.db").resolve()

def _get_conn():
    return sqlite3.connect(str(DB_FILE), timeout=30, isolation_level=None)


def search_flights(origin=None, destination=None, date_iso=None):
    """
    Return list of flights with dynamic_price computed.
    date_iso expected as YYYY-MM-DD or full ISO; we match by date part if provided.
    """
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = "SELECT id, airline, origin, destination, departure, base_fare, total_seats, seats_left, demand_level, last_price FROM flights WHERE 1=1"
    params = []

    if origin:
        sql += " AND origin = ?"
        params.append(origin)
    if destination:
        sql += " AND destination = ?"
        params.append(destination)
    if date_iso:
        # match date prefix (YYYY-MM-DD)
        sql += " AND substr(departure,1,10) = ?"
        params.append(date_iso[:10])

    cur.execute(sql, params)
    rows = cur.fetchall()
    results = []
    now = datetime.utcnow()

    for r in rows:
        departure = r["departure"]
        dyn_price = calculate_dynamic_price(
            base_fare=r["base_fare"],
            seats_left=r["seats_left"],
            total_seats=r["total_seats"],
            departure_iso=departure,
            demand_level=r["demand_level"],
            now=now
        )

        results.append({
            "id": r["id"],
            "airline": r["airline"],
            "origin": r["origin"],
            "destination": r["destination"],
            "departure": departure,
            "base_fare": r["base_fare"],
            "seats_left": r["seats_left"],
            "demand_level": r["demand_level"],
            "dynamic_price": dyn_price,
            "last_price": r["last_price"]
        })

    conn.close()
    return results