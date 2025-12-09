# milestone1/db/reset_price.py  (create & run)
import sqlite3, pathlib
p = pathlib.Path("milestone1/db/flight_simulator.db").resolve()
conn = sqlite3.connect(str(p))
cur = conn.cursor()
flight_id = 1        # <- change this to the flight_id you want to fix
new_base_price = 3000.0  # <- change to a sensible base fare
cur.execute("UPDATE flight SET price = ? WHERE flight_id = ?", (new_base_price, flight_id))
conn.commit()
conn.close()
print("Reset flight", flight_id, "price ->", new_base_price)