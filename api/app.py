# api/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, constr
from typing import Optional, List
import sqlite3, os, random
from datetime import datetime, timedelta
from pathlib import Path as PathlibPath
from .pricing_engine import calculate_dynamic_price
from .simulator import run_simulator_loop

APP = FastAPI(title="Flight Simulator - Milestone 1 (simple)")

BASE_DIR = PathlibPath(__file__).resolve().parents[1]  # milestone1/
DB_FILE = (BASE_DIR / "db" / "flight_simulator.db").resolve()

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

    demand_level = row["demand_level"] if "demand_level" in row.keys() else "medium"

    dyn_price = calculate_dynamic_price(
        base_fare=row["base_price"],           # ✅ FIX
        seats_left=row["available_seats"],     # ✅ FIX
        total_seats=row["total_seats"],
        departure_iso=row["departure_time"],
        demand_level=demand_level,
        now=datetime.utcnow()
    )

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
        price=float(dyn_price)                 # ✅ runtime only
    )
# ---------- Endpoints ----------
@APP.get("/flights/", response_model=List[FlightOut])
def list_flights():
    conn = get_conn()
    cur = conn.execute("""
        SELECT f.flight_id, f.flight_number, f.airline,
               a1.code AS origin_code, a1.city AS origin_city,
               a2.code AS dest_code, a2.city AS dest_city,
               f.departure_time, f.arrival_time, f.total_seats, f.available_seats, f.base_price
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
               f.departure_time, f.arrival_time, f.total_seats, f.available_seats, f.base_price
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
    Milestone 3 – Atomic booking with:
    - concurrency safety
    - dynamic pricing
    - PNR generation
    """

    conn = get_conn()

    try:
        # ---------- 1. Validate user ----------
        user = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (b.user_email.lower(),)
        ).fetchone()

        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # ---------- 2. Begin transaction (LOCK DB) ----------
        conn.execute("BEGIN IMMEDIATE")

        # ---------- 3. Fetch flight (LOCKED) ----------
        flight = conn.execute("""
            SELECT flight_id, departure_time,
                   total_seats, available_seats,
                   base_price
            FROM flight
            WHERE flight_id = ?
        """, (b.flight_id,)).fetchone()

        if not flight:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=400, detail="Flight not found")

        if flight["available_seats"] < b.seats:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=400, detail="Not enough seats")

        # ---------- 4. Calculate SAFE dynamic price ----------
        dyn_price = calculate_dynamic_price(
            base_fare=flight["base_price"],
            seats_left=flight["available_seats"],
            total_seats=flight["total_seats"],
            departure_iso=flight["departure_time"],
            demand_level="medium"
        )

        total_amount = float(dyn_price) * b.seats

        # ---------- 5. Generate PNR ----------
        pnr = f"PNR{random.randint(100000,999999)}"

        # ---------- 6. Insert booking ----------
        conn.execute("""
            INSERT INTO bookings (
                pnr, user_id, flight_id,
                seats_booked, status, total_amount
            )
            VALUES (?, ?, ?, ?, 'booked', ?)
        """, (
            pnr,
            user["id"],
            b.flight_id,
            b.seats,
            total_amount
        ))

        # ---------- 7. Update seat count ----------
        conn.execute("""
            UPDATE flight
            SET available_seats = available_seats - ?
            WHERE flight_id = ?
        """, (b.seats, b.flight_id))

        # ---------- 8. Commit transaction ----------
        conn.commit()

        # ---------- 9. Fetch booking ----------
        rec = conn.execute("""
            SELECT booking_id, pnr, user_id,
                   flight_id, seats_booked,
                   total_amount, booking_date, status
            FROM bookings
            WHERE pnr = ?
        """, (pnr,)).fetchone()

        return BookingOut(
            booking_id=rec["booking_id"],
            user_id=rec["user_id"],
            flight_id=rec["flight_id"],
            seats_booked=rec["seats_booked"],
            total_amount=float(rec["total_amount"]),
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
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()

@APP.post("/book/cancel/{booking_id}")
def cancel_booking(booking_id: int):
    """
    Milestone 3 – Booking cancellation
    - restore seats
    - mark booking cancelled
    - transaction safe
    """

    conn = get_conn()

    try:
        # ---------- 1. Start transaction ----------
        conn.execute("BEGIN IMMEDIATE")

        # ---------- 2. Fetch booking ----------
        booking = conn.execute("""
            SELECT booking_id, flight_id, seats_booked, status
            FROM bookings
            WHERE booking_id = ?
        """, (booking_id,)).fetchone()

        if not booking:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking["status"] == "cancelled":
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=400, detail="Booking already cancelled")

        # ---------- 3. Restore seats ----------
        conn.execute("""
            UPDATE flight
            SET available_seats = available_seats + ?
            WHERE flight_id = ?
        """, (booking["seats_booked"], booking["flight_id"]))

        # ---------- 4. Update booking status ----------
        conn.execute("""
            UPDATE bookings
            SET status = 'cancelled'
            WHERE booking_id = ?
        """, (booking_id,))

        # ---------- 5. Commit ----------
        conn.commit()

        return {
            "message": "Booking cancelled successfully",
            "booking_id": booking_id
        }

    except HTTPException:
        raise

    except Exception as e:
        try:
            conn.execute("ROLLBACK")
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))

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

@APP.get("/bookings/history/{user_email}", response_model=List[BookingOut])
def booking_history(user_email: str):
    """
    Milestone 3 – Booking history retrieval
    Returns all bookings (active + cancelled) for a user
    """

    conn = get_conn()

    try:
        # ---------- 1. Get user ----------
        user = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (user_email.lower(),)
        ).fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ---------- 2. Fetch bookings ----------
        rows = conn.execute("""
            SELECT booking_id, user_id, flight_id,
                   seats_booked, total_amount,
                   booking_date, status
            FROM bookings
            WHERE user_id = ?
            ORDER BY booking_date DESC
        """, (user["id"],)).fetchall()

        # ---------- 3. Convert to response ----------
        return [
            BookingOut(
                booking_id=r["booking_id"],
                user_id=r["user_id"],
                flight_id=r["flight_id"],
                seats_booked=r["seats_booked"],
                total_amount=float(r["total_amount"] or 0.0),
                booking_date=r["booking_date"],
                status=r["status"]
            )
            for r in rows
        ]

    finally:
        conn.close()
        
# --- start simulator on app startup ---
@APP.on_event("startup")
def startup_simulator():
    # Start simulator thread with 15s interval. It runs as daemon so it won't block server.
    try:
        run_simulator_loop(interval_seconds=15)
        print("Simulator started (background thread).")
    except Exception as e:
        print("Failed to start simulator:", e)
from .bookings import router as bookings_router
APP.include_router(bookings_router)
def generate_pnr():
    return "PNR" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
