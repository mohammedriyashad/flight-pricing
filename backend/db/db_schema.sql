PRAGMA foreign_keys = ON;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE flight (
  flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
  flight_number TEXT,
  airline TEXT,
  origin_code TEXT,
  dest_code TEXT,
  departure_time TEXT,
  arrival_time TEXT,
  total_seats INTEGER,
  available_seats INTEGER,
  base_price REAL
);

CREATE TABLE airports (
  airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL UNIQUE,
  city TEXT NOT NULL,
  country TEXT DEFAULT 'India'
);

CREATE TABLE bookings (
  booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
  pnr TEXT UNIQUE,
  user_email TEXT,
  flight_id INTEGER,
  seats INTEGER,
  total_amount REAL,
  status TEXT DEFAULT 'CONFIRMED',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO airports (code, city, country) VALUES
('DEL', 'New Delhi', 'India'),
('BOM', 'Mumbai', 'India'),
('BLR', 'Bengaluru', 'India'),
('MAA', 'Chennai', 'India'),
('HYD', 'Hyderabad', 'India');

-- SAMPLE FLIGHTS
INSERT INTO flight
(flight_number, airline, origin_code, dest_code,
 departure_time, arrival_time, total_seats, available_seats, base_price)
VALUES
('AI-101','AirIndia','DEL','BOM','2025-12-05 08:30','2025-12-05 10:30',180,180,4500),
('6E-202','IndiGo','BLR','MAA','2025-12-06 14:00','2025-12-06 15:30',150,150,3200),
('SG-303','SpiceJet','DEL','BLR','2025-12-07 06:00','2025-12-07 08:30',160,160,4200);