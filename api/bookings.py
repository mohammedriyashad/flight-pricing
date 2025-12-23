import sqlite3
import random
import string
from pathlib import Path
from fastapi import APIRouter, HTTPException

from .seats import lock_seat, confirm_seat, release_seat
from .pricing_engine import calculate_dynamic_price

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# DB path
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "milestone1" / "db" / "flight_simulator.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# -----------------------------
# Helper: Generate PNR
# -----------------------------
def generate_pnr():
    return "PNR" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


# -----------------------------
# Create Booking
# -----------------------------
@router.post("/create")
def create_booking(data: dict):
    flight_id = data["flight_id"]
    seat_number = data["seat_number"]
    passenger_name = data["passenger_name"]

    # 1️⃣ Lock seat
    lock_seat(flight_id, seat_number)

    try:
        # 2️⃣ Simulated payment
        payment_success = random.choice([True, True, False])
        if not payment_success:
            release_seat(flight_id, seat_number)
            raise HTTPException(status_code=402, detail="Payment failed")

        # 3️⃣ Calculate price (Milestone 2 logic)
        price = calculate_dynamic_price(flight_id) # type: ignore

        # 4️⃣ Store booking
        pnr = generate_pnr()
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO bookings (pnr, flight_id, passenger_name,
                                  seat_number, price, status)
            VALUES (?, ?, ?, ?, ?, 'CONFIRMED')
            """,
            (pnr, flight_id, passenger_name, seat_number, price),
        )

        conn.commit()
        conn.close()

        # 5️⃣ Confirm seat
        confirm_seat(flight_id, seat_number)

        return {
            "message": "Booking confirmed",
            "pnr": pnr,
            "seat": seat_number,
            "price": price,
        }

    except:
        release_seat(flight_id, seat_number)
        raise


# -----------------------------
# Cancel Booking
# -----------------------------
@router.post("/cancel/{pnr}")
def cancel_booking(pnr: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT flight_id, seat_number FROM bookings
        WHERE pnr = ? AND status = 'CONFIRMED'
        """,
        (pnr,),
    )

    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Booking not found")

    flight_id, seat_number = row

    cur.execute(
        """
        UPDATE bookings
        SET status = 'CANCELLED'
        WHERE pnr = ?
        """,
        (pnr,),
    )

    conn.commit()
    conn.close()

    release_seat(flight_id, seat_number)

    return {"message": "Booking cancelled", "pnr": pnr}
@router.get("/history/{passenger_name}")
def get_booking_history(passenger_name: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT pnr, flight_id, seat_number, price, status, created_at
        FROM bookings
        WHERE passenger_name = ?
        ORDER BY created_at DESC
    """, (passenger_name,))

    rows = cur.fetchall()
    conn.close()

    return {
        "passenger": passenger_name,
        "history": [
            {
                "pnr": r[0],
                "flight_id": r[1],
                "seat": r[2],
                "price": r[3],
                "status": r[4],
                "created_at": r[5]
            } for r in rows
        ]
    }