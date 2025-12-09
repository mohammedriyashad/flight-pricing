CREATE TABLE IF NOT EXISTS fare_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  flight_id INTEGER NOT NULL,
  timestamp TEXT NOT NULL,
  price REAL NOT NULL,
  FOREIGN KEY (flight_id) REFERENCES flight(flight_id)
);

ALTER TABLE flight ADD COLUMN last_price REAL;
ALTER TABLE flight ADD COLUMN demand_level TEXT;