from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import sqlite3, random, string
from pathlib import Path
from datetime import datetime

APP = FastAPI(title="SkyBook Backend")

APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "flight_simulator.db"

# ---------- DB ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def normalize_email(v: str):
    return v.strip().lower()

# ---------- MODELS ----------
class Signup(BaseModel):
    name: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class BookingIn(BaseModel):
    user_email: str
    flight_id: int
    seats: int

class FlightOut(BaseModel):
    flight_id: int
    flight_number: str
    airline: str
    origin_code: str
    origin_city: str
    dest_code: str
    dest_city: str
    departure_time: str
    arrival_time: str
    total_seats: int
    available_seats: int
    price: float

def row_to_flight(row: sqlite3.Row) -> FlightOut:
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
        total_seats=row["total_seats"],
        available_seats=row["available_seats"],
        price=row["base_price"]
    )

# ---------- AUTH ----------
@APP.post("/users/signup")
def signup(data: Signup):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (name,email,password) VALUES (?,?,?)",
            (data.name, data.email.lower(), data.password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(400, "User already exists")
    finally:
        conn.close()
    return {"message": "Signup successful"}

@APP.post("/users/login")
def login(data: Login):
    conn = get_conn()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (data.email.lower(), data.password)
    ).fetchone()
    conn.close()
    if not user:
        raise HTTPException(401, "Invalid credentials")
    return dict(user)

# ---------- FLIGHTS ----------
@APP.get("/flights")
def get_flights(
    origin: str | None = Query(None),
    destination: str | None = Query(None),
):
    conn = get_conn()
    cur = conn.cursor()

    sql = """
    SELECT
        flight_id,
        flight_number,
        airline,
        origin_code,
        dest_code,
        departure_time,
        arrival_time,
        available_seats,
        base_price
    FROM flight
    WHERE 1=1
    """
    params = []

    if origin:
        o = origin.strip().lower()[:3]
        sql += " AND LOWER(origin_code) LIKE ?"
        params.append(f"%{o}%")

    if destination:
        d = destination.strip().lower()[:3]
        sql += " AND LOWER(dest_code) LIKE ?"
        params.append(f"%{d}%")

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "flight_id": r["flight_id"],
            "flight_number": r["flight_number"],
            "airline": r["airline"],
            "origin_code": r["origin_code"],
            "dest_code": r["dest_code"],
            "departure_time": r["departure_time"],
            "arrival_time": r["arrival_time"],
            "available_seats": r["available_seats"],
            "price": r["base_price"],
        }
        for r in rows
    ]
# ---------- BOOK ----------
def generate_pnr():
    return "PNR" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

@APP.post("/book")
def book_flight(data: BookingIn):
    conn = get_conn()

    flight = conn.execute(
        "SELECT * FROM flight WHERE flight_id=?",
        (data.flight_id,)
    ).fetchone()

    if not flight:
        conn.close()
        raise HTTPException(404, "Flight not found")

    if flight["available_seats"] < data.seats:
        conn.close()
        raise HTTPException(400, "Not enough seats")

    total = flight["base_price"] * data.seats
    pnr = generate_pnr()

    conn.execute("""
        INSERT INTO bookings
        (pnr,user_email,flight_id,seats,total_amount)
        VALUES (?,?,?,?,?)
    """, (pnr, data.user_email, data.flight_id, data.seats, total))

    conn.execute("""
        UPDATE flight
        SET available_seats = available_seats - ?
        WHERE flight_id = ?
    """, (data.seats, data.flight_id))

    conn.commit()
    conn.close()

    return {
        "booking_id": pnr,
        "flight_id": data.flight_id,
        "seats": data.seats,
        "total_amount": total
    }

# ---------- HISTORY ----------
@APP.get("/bookings/history/{email}")
def booking_history(email: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM bookings WHERE user_email=? ORDER BY created_at DESC",
        (email,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ---------- CANCEL ----------
@APP.post("/book/cancel/{booking_id}")
def cancel_booking(booking_id: str):
    conn = get_conn()
    booking = conn.execute(
        "SELECT * FROM bookings WHERE pnr=?",
        (booking_id,)
    ).fetchone()

    if not booking:
        conn.close()
        raise HTTPException(404, "Booking not found")

    conn.execute(
        "UPDATE bookings SET status='CANCELLED' WHERE pnr=?",
        (booking_id,)
    )

    conn.execute(
        "UPDATE flight SET available_seats = available_seats + ? WHERE flight_id=?",
        (booking["seats"], booking["flight_id"])
    )

    conn.commit()
    conn.close()
    return {"message": "Booking cancelled"}

from .admin import router as admin_router
APP.include_router(admin_router)