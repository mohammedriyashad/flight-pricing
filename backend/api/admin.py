from fastapi import APIRouter, HTTPException
import sqlite3
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["Admin"])

BASE_DIR = Path(__file__).resolve().parents[1]
DB = BASE_DIR / "db" / "flight_simulator.db"


def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@router.post("/login")
def admin_login(data: dict):
    conn = get_conn()
    admin = conn.execute("""
        SELECT id, email FROM users
        WHERE email=? AND password=? AND role='admin'
    """, (data["email"], data["password"])).fetchone()
    conn.close()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    return {"message": "Admin login successful"}

@router.get("/flights")
def get_all_flights():
    conn = get_conn()
    rows = conn.execute("""
        SELECT f.flight_id, f.flight_number, f.airline,
               a1.code AS origin, a2.code AS destination,
               f.departure_time, f.available_seats, f.base_price
        FROM flight f
        JOIN airports a1 ON f.origin_airport = a1.airport_id
        JOIN airports a2 ON f.destination_airport = a2.airport_id
        ORDER BY f.departure_time
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/bookings")
def get_all_bookings():
    conn = get_conn()
    rows = conn.execute("""
        SELECT b.booking_id, b.pnr, u.email,
               f.flight_number, b.seats_booked,
               b.total_amount, b.status, b.booking_date
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN flight f ON b.flight_id = f.flight_id
        ORDER BY b.booking_date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/revenue")
def revenue_summary():
    conn = get_conn()
    total = conn.execute("""
        SELECT SUM(total_amount)
        FROM bookings
        WHERE status='booked'
    """).fetchone()[0]
    conn.close()
    return {"total_revenue": total or 0}

@router.post("/cancel/{booking_id}")
def admin_cancel_booking(booking_id: int):
    conn = get_conn()

    booking = conn.execute("""
        SELECT flight_id, seats_booked
        FROM bookings
        WHERE booking_id=? AND status='booked'
    """, (booking_id,)).fetchone()

    if not booking:
        conn.close()
        raise HTTPException(404, "Booking not found")

    conn.execute("""
        UPDATE bookings
        SET status='cancelled'
        WHERE booking_id=?
    """, (booking_id,))

    conn.execute("""
        UPDATE flight
        SET available_seats = available_seats + ?
        WHERE flight_id = ?
    """, (booking["seats_booked"], booking["flight_id"]))

    conn.commit()
    conn.close()
    return {"message": "Booking cancelled by admin"}
