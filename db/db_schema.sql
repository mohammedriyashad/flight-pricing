-- db/db_schema.sql
-- SQL schema for Flight Booking System

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  phone TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE airports (
  airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL UNIQUE,
  name TEXT,
  city TEXT,
  country TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE flight (
  flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
  flight_number TEXT NOT NULL,
  airline TEXT,
  origin_airport INTEGER NOT NULL,
  destination_airport INTEGER NOT NULL,
  departure_time TEXT NOT NULL,
  arrival_time TEXT NOT NULL,
  total_seats INTEGER NOT NULL DEFAULT 0,
  available_seats INTEGER NOT NULL DEFAULT 0,
  price REAL NOT NULL DEFAULT 0.0,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (origin_airport) REFERENCES airports(airport_id) ON DELETE RESTRICT,
  FOREIGN KEY (destination_airport) REFERENCES airports(airport_id) ON DELETE RESTRICT
);

CREATE TABLE bookings (
  booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  flight_id INTEGER NOT NULL,
  seats_booked INTEGER NOT NULL,
  booking_date TEXT DEFAULT (datetime('now')),
  status TEXT DEFAULT 'booked',
  total_amount REAL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (flight_id) REFERENCES flight(flight_id) ON DELETE CASCADE
);

-- ---------- SAMPLE DATA ----------
INSERT INTO airports (code, name, city, country) VALUES
('DEL', 'Indira Gandhi International Airport', 'Delhi', 'India'),
('BOM', 'Chhatrapati Shivaji Maharaj Intl Airport', 'Mumbai', 'India'),
('BLR', 'Kempegowda International Airport', 'Bengaluru', 'India'),
('MAA', 'Chennai International Airport', 'Chennai', 'India');

INSERT INTO users (name, email, password, phone) VALUES
('Mohammed Riyashad','riyashad@example.com','placeholder_hashed_pw','9999999999'),
('Test User','test@example.com','placeholder_hashed_pw','8888888888');

INSERT INTO flight (flight_number, airline, origin_airport, destination_airport, departure_time, arrival_time, total_seats, available_seats, price)
VALUES
('AI-101','AirIndia', (SELECT airport_id FROM airports WHERE code='DEL'), (SELECT airport_id FROM airports WHERE code='BOM'),
 '2025-12-05 08:30:00','2025-12-05 10:30:00', 180, 180, 4500.00),
('6E-202','IndiGo', (SELECT airport_id FROM airports WHERE code='BLR'), (SELECT airport_id FROM airports WHERE code='MAA'),
 '2025-12-06 14:00:00','2025-12-06 15:30:00', 150, 150, 3200.00),
('SG-303','SpiceJet', (SELECT airport_id FROM airports WHERE code='DEL'), (SELECT airport_id FROM airports WHERE code='BLR'),
 '2025-12-07 06:00:00','2025-12-07 08:30:00', 160, 160, 4200.00);

-- Sample booking
INSERT INTO bookings (user_id, flight_id, seats_booked, status, total_amount)
VALUES
(
  (SELECT id FROM users WHERE email='test@example.com'),
  (SELECT flight_id FROM flight WHERE flight_number='AI-101'),
  2, 'booked',
  (SELECT price * 2 FROM flight WHERE flight_number='AI-101')
);

UPDATE flight SET available_seats = available_seats - 2 WHERE flight_number = 'AI-101';