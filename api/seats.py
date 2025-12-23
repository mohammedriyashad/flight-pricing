import sqlite3
from datetime import datetime
from pathlib import Path
from fastapi import HTTPException

# Absolute DB path (safe on Windows)
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "milestone1" / "db" / "flight_simulator.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# -----------------------------
# LOCK SEAT (Concurrency-safe)
# -----------------------------
def lock_seat(flight_id: int, seat_number: str):
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Lock DB immediately to avoid race conditions
        conn.execute("BEGIN IMMEDIATE")

        cur.execute(
            """
            SELECT status FROM flight_seats
            WHERE flight_id = ? AND seat_number = ?
            """,
            (flight_id, seat_number),
        )

        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Seat not found")

        if row[0] != "AVAILABLE":
            raise HTTPException(status_code=409, detail="Seat already booked")

        cur.execute(
            """
            UPDATE flight_seats
            SET status = 'LOCKED',
                locked_at = ?
            WHERE flight_id = ? AND seat_number = ?
            """,
            (datetime.utcnow(), flight_id, seat_number),
        )

        conn.commit()

    except:
        conn.rollback()
        raise
    finally:
        conn.close()


# -----------------------------
# CONFIRM SEAT (after payment)
# -----------------------------
def confirm_seat(flight_id: int, seat_number: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE flight_seats
        SET status = 'BOOKED'
        WHERE flight_id = ?
          AND seat_number = ?
          AND status = 'LOCKED'
        """,
        (flight_id, seat_number),
    )

    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=409, detail="Seat confirmation failed")

    conn.commit()
    conn.close()


# -----------------------------
# RELEASE SEAT (cancel/fail)
# -----------------------------
def release_seat(flight_id: int, seat_number: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE flight_seats
        SET status = 'AVAILABLE',
            locked_at = NULL
        WHERE flight_id = ? AND seat_number = ?
        """,
        (flight_id, seat_number),
    )

    conn.commit()
    conn.close()