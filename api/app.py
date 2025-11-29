# api/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, constr
from typing import Optional, List
import sqlite3, os, random
from datetime import datetime, timedelta
from pathlib import Path

APP = FastAPI(title="Flight Simulator - Milestone 1 (simple)")

BASE_DIR = Path(__file__).resolve().parents[1]  # milestone1/
DB_FILE = BASE_DIR / "db" / "flight_simulator.db"

# ---------- Pydantic models ----------
class FlightOut(BaseModel):
    flight_id: int
    flight_number: str
    airline: Optional[str]
    origin_code: Optional[str]
    origin_city: Optional[str]
    dest_code: Optional[str]
    dest_city: Optional[str]
    departure_time: str
    arrival_time: str
    duration_min: int
    total_seats: int
    available_seats: int
    price: float

class FeedIn(BaseModel):
    flight_number: constr(min_length=1) # type: ignore
    airline: Optional[str]
    origin_code: constr(min_length=2, max_length=5) # type: ignore
    dest_code: constr(min_length=2, max_length=5) # type: ignore
    departure_time: datetime
    arrival_time: datetime
    total_seats: int = Field(..., gt=0)
    price: float = Field(..., ge=0.0)

class BookIn(BaseModel):
    user_email: constr(min_length=5) # type: ignore
    flight_id: int
    seats: int = Field(..., gt=0)

class BookingOut(BaseModel):
    booking_id: int
    user_id: int
    flight_id: int
    seats_booked: int
    total_amount: float
    booking_date: str
    status: str

# ---------- DB helpers ----------
def get_conn():
    if not DB_FILE.exists():
        raise HTTPException(status_code=500, detail=f"DB missing. Run tools/create_db.py to create {DB_FILE}")
    conn = sqlite3.connect(str(DB_FILE), timeout=30, isolation_level=None)  # isolation_level=None => autocommit off, we will control tx
    conn.row_factory = sqlite3.Row
    return conn

def row_to_flight(row):
    dep = datetime.strptime(row["departure_time"], "%Y-%m-%d %H:%M:%S")
    arr = datetime.strptime(row["arrival_time"], "%Y-%m-%d %H:%M:%S")
    dur = int((arr - dep).total_seconds() // 60)
    return FlightOut(
        flight_id=row["flight_id"],
        flight_number=row["flight_number"],
        airline=row["airline"],
        origin_code=row["origin_code"],
        origin_city=row["origin_city"],
        dest_code=row["dest_code"],
        dest_city=row["dest_city"],
        departure_time=row["departure_time"],
        arrival_time=row["arrival_time"],
        duration_min=dur,
        total_seats=row["total_seats"],
        available_seats=row["available_seats"],
        price=float(row["price"])
    )

# ---------- Endpoints ----------
@APP.get("/flights/", response_model=List[FlightOut])
def list_flights():
    conn = get_conn()
    cur = conn.execute("""
        SELECT f.flight_id, f.flight_number, f.airline,
               a1.code AS origin_code, a1.city AS origin_city,
               a2.code AS dest_code, a2.city AS dest_city,
               f.departure_time, f.arrival_time, f.total_seats, f.available_seats, f.price
        FROM flight f
        JOIN airports a1 ON f.origin_airport = a1.airport_id
        JOIN airports a2 ON f.destination_airport = a2.airport_id
        ORDER BY f.departure_time;
    """)
    rows = cur.fetchall()
    conn.close()
    return [row_to_flight(r) for r in rows]

@APP.get("/flights/search", response_model=List[FlightOut])
def search_flights(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    sort: Optional[str] = Query(None)
):
    q_where = []
    params = []
    if origin:
        q_where.append("a1.code = ?")
        params.append(origin.upper())
    if destination:
        q_where.append("a2.code = ?")
        params.append(destination.upper())
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")
        q_where.append("DATE(f.departure_time) = ?")
        params.append(date)
    where_sql = ("WHERE " + " AND ".join(q_where)) if q_where else ""
    sql = f"""
        SELECT f.flight_id, f.flight_number, f.airline,
               a1.code AS origin_code, a1.city AS origin_city,
               a2.code AS dest_code, a2.city AS dest_city,
               f.departure_time, f.arrival_time, f.total_seats, f.available_seats, f.price
        FROM flight f
        JOIN airports a1 ON f.origin_airport = a1.airport_id
        JOIN airports a2 ON f.destination_airport = a2.airport_id
        {where_sql}
    """
    conn = get_conn()
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    results = [row_to_flight(r) for r in rows]

    if sort:
        if sort == "price":
            results.sort(key=lambda x: x.price)
        elif sort == "duration":
            results.sort(key=lambda x: x.duration_min)
        else:
            raise HTTPException(status_code=400, detail="sort must be 'price' or 'duration'")

    return results

@APP.post("/simulate_feed/", response_model=FlightOut)
def simulate_feed(payload: Optional[FeedIn] = None):
    conn = get_conn()
    cur = conn.cursor()
    if payload is None:
        # random between existing airports
        codes = [r["code"] for r in conn.execute("SELECT code FROM airports").fetchall()]
        if len(codes) < 2:
            conn.close()
            raise HTTPException(status_code=400, detail="Not enough airports to create random flight")
        o, d = random.sample(codes, 2)
        dep = datetime.utcnow() + timedelta(days=random.randint(2, 15), hours=random.randint(0,23))
        arr = dep + timedelta(hours=random.randint(1,5))
        fn = f"RM{random.randint(100,999)}"
        airline = random.choice(["AirSample","TestAir","MiniJet"])
        total_seats = random.choice([120,150,180])
        price = float(random.choice([2000,3000,4000,5000]))
        payload = FeedIn(
            flight_number=fn,
            airline=airline,
            origin_code=o,
            dest_code=d,
            departure_time=dep,
            arrival_time=arr,
            total_seats=total_seats,
            price=price
        )

    # get airport ids
    a_o = conn.execute("SELECT airport_id, code, city FROM airports WHERE code = ?", (payload.origin_code.upper(),)).fetchone()
    a_d = conn.execute("SELECT airport_id, code, city FROM airports WHERE code = ?", (payload.dest_code.upper(),)).fetchone()
    if not a_o or not a_d:
        conn.close()
        raise HTTPException(status_code=400, detail="origin or destination airport code doesn't exist")

    # insert flight
    conn.execute("""
        INSERT INTO flight (flight_number, airline, origin_airport, destination_airport,
                            departure_time, arrival_time, total_seats, available_seats, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.flight_number,
        payload.airline,
        a_o["airport_id"],
        a_d["airport_id"],
        payload.departure_time.strftime("%Y-%m-%d %H:%M:%S"),
        payload.arrival_time.strftime("%Y-%m-%d %H:%M:%S"),
        payload.total_seats,
        payload.total_seats,
        payload.price
    ))
    # get inserted flight
    flight_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    row = conn.execute("""
        SELECT f.flight_id, f.flight_number, f.airline,
               a1.code AS origin_code, a1.city AS origin_city,
               a2.code AS dest_code, a2.city AS dest_city,
               f.departure_time, f.arrival_time, f.total_seats, f.available_seats, f.price
        FROM flight f
        JOIN airports a1 ON f.origin_airport = a1.airport_id
        JOIN airports a2 ON f.destination_airport = a2.airport_id
        WHERE f.flight_id = ?
    """, (flight_id,)).fetchone()
    conn.commit()
    conn.close()
    return row_to_flight(row)

@APP.post("/book/", response_model=BookingOut)
def book(b: BookIn):
    """
    Atomic booking:
    - validate user exists by email
    - check available seats
    - begin immediate transaction to lock DB for update
    - insert booking, update available_seats, commit
    """
    conn = get_conn()
    try:
        # find user
        user = conn.execute("SELECT id FROM users WHERE email = ?", (b.user_email.lower(),)).fetchone()
        if not user:
            raise HTTPException(status_code=400, detail="user not found (use registered email)")

        # check flight exists
        flight = conn.execute("SELECT flight_id, available_seats, price FROM flight WHERE flight_id = ?", (b.flight_id,)).fetchone()
        if not flight:
            raise HTTPException(status_code=400, detail="flight not found")

        if flight["available_seats"] < b.seats:
            raise HTTPException(status_code=400, detail="not enough seats available")

        # Begin immediate transaction to prevent race conditions (exclusive lock for writes)
        conn.execute("BEGIN IMMEDIATE")
        # re-check inside tx
        flight2 = conn.execute("SELECT available_seats, price FROM flight WHERE flight_id = ?", (b.flight_id,)).fetchone()
        if flight2["available_seats"] < b.seats:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=400, detail="not enough seats available (concurrent)")

        total = float(flight2["price"]) * b.seats
        cur = conn.execute("""
            INSERT INTO bookings (user_id, flight_id, seats_booked, status, total_amount)
            VALUES (?, ?, ?, 'booked', ?)
        """, (user["id"], b.flight_id, b.seats, total))
        # update seats
        conn.execute("""
            UPDATE flight SET available_seats = available_seats - ? WHERE flight_id = ?
        """, (b.seats, b.flight_id))
        # commit
        conn.commit()
        booking_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        rec = conn.execute("SELECT booking_id, user_id, flight_id, seats_booked, total_amount, booking_date, status FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
        return BookingOut(
            booking_id=rec["booking_id"],
            user_id=rec["user_id"],
            flight_id=rec["flight_id"],
            seats_booked=rec["seats_booked"],
            total_amount=float(rec["total_amount"] or 0.0),
            booking_date=rec["booking_date"],
            status=rec["status"]
        )
    except HTTPException:
        raise
    except Exception as e:
        try:
            conn.execute("ROLLBACK")
        except:
            pass
        raise HTTPException(status_code=500, detail=f"internal error: {e}")
    finally:
        conn.close()

@APP.get("/bookings/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int):
    conn = get_conn()
    rec = conn.execute("SELECT booking_id, user_id, flight_id, seats_booked, total_amount, booking_date, status FROM bookings WHERE booking_id = ?", (booking_id,)).fetchone()
    conn.close()
    if not rec:
        raise HTTPException(status_code=404, detail="booking not found")
    return BookingOut(
        booking_id=rec["booking_id"],
        user_id=rec["user_id"],
        flight_id=rec["flight_id"],
        seats_booked=rec["seats_booked"],
        total_amount=float(rec["total_amount"] or 0.0),
        booking_date=rec["booking_date"],
        status=rec["status"]
    )