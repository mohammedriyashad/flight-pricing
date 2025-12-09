# milestone1/api/pricing_engine.py
# Raw-SQL friendly dynamic pricing functions for Milestone 2

from datetime import datetime
from math import ceil

def calculate_dynamic_price(base_fare: float,
                            seats_left: int,
                            total_seats: int,
                            departure_iso: str,
                            demand_level: str,
                            now: datetime = None) -> float: # type: ignore
    """
    Compute dynamic fare (raw-SQL friendly).
    departure_iso: ISO-format datetime string stored in DB
    demand_level: 'low'|'medium'|'high'
    """
    if now is None:
        now = datetime.utcnow()

    # safe conversions
    try:
        seats_left = int(seats_left)
        total_seats = int(total_seats)
        base_fare = float(base_fare)
    except Exception:
        # fallback defaults
        seats_left = max(0, seats_left or 0)
        total_seats = max(1, total_seats or 1)
        base_fare = float(base_fare or 0.0)

    # 1) Seat-based factor
    if total_seats <= 0:
        seat_pct = 0.0
    else:
        seat_pct = seats_left / total_seats

    if seat_pct <= 0.05:
        seat_factor = 2.0
    elif seat_pct <= 0.20:
        seat_factor = 1.5
    elif seat_pct <= 0.50:
        seat_factor = 1.2
    else:
        seat_factor = 1.0

    # 2) Time-to-departure factor (in days)
    time_factor = 1.0
    try:
        dep = datetime.fromisoformat(departure_iso)
        delta_days = max((dep - now).total_seconds() / 86400.0, 0.0)
        if delta_days <= 0.0208:   # ~30 minutes
            time_factor = 2.2
        elif delta_days <= 0.5:    # 12 hours
            time_factor = 2.0
        elif delta_days <= 1:
            time_factor = 1.8
        elif delta_days <= 7:
            time_factor = 1.4
        elif delta_days <= 15:
            time_factor = 1.15
        else:
            time_factor = 1.0
    except Exception:
        time_factor = 1.0

    # 3) Demand factor
    demand_map = {
        "low": 0.95,
        "medium": 1.0,
        "high": 1.25
    }
    demand_factor = demand_map.get((demand_level or "").lower(), 1.0)

    price = base_fare * seat_factor * time_factor * demand_factor

    # rounding rules: round to 2 decimals
    final_price = round(price, 2)
    return final_price