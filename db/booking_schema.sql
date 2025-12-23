CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pnr TEXT UNIQUE NOT NULL,
    flight_id INTEGER NOT NULL,
    passenger_name TEXT NOT NULL,
    seat_number TEXT NOT NULL,
    price REAL NOT NULL,
    status TEXT CHECK(status IN ('CONFIRMED','CANCELLED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flight_seats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_id INTEGER NOT NULL,
    seat_number TEXT NOT NULL,
    status TEXT CHECK(status IN ('AVAILABLE','LOCKED','BOOKED')),
    locked_at TIMESTAMP,
    UNIQUE(flight_id, seat_number)
);