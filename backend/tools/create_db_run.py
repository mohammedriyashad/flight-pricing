import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "flight_simulator.db")

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS flights (
        flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_number TEXT,
        airline TEXT,
        origin_code TEXT,
        dest_code TEXT,
        departure_time TEXT,
        arrival_time TEXT,
        available_seats INTEGER,
        base_price INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        flight_id INTEGER,
        seats INTEGER,
        price INTEGER,
        pnr TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS otp_logins (
        email TEXT PRIMARY KEY,
        otp TEXT,
        expires_at INTEGER
    )
    """)

    conn.commit()
    conn.close()

def seed_flights():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM flights")
    count = cur.fetchone()[0]

    if count == 0:
        cur.executemany("""
        INSERT INTO flights
        (flight_number, airline, origin_code, dest_code, departure_time, arrival_time, available_seats, base_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ("AI-202", "Air India", "DEL", "BLR", "10:00", "12:30", 50, 5200),
            ("6E-451", "IndiGo", "DEL", "BLR", "14:00", "16:15", 42, 4800),
            ("UK-812", "Vistara", "BOM", "DEL", "09:00", "11:05", 30, 6100)
        ])

    conn.commit()
    conn.close()