from datetime import datetime
from math import ceil


def calculate_dynamic_price(
    base_fare: float,
    seats_left: int,
    total_seats: int,
    departure_iso: str,
    demand_level: str,
    now: datetime | None = None
) -> int:
    """
    SAFE dynamic pricing (NO exponential growth)
    """

    if now is None:
        now = datetime.utcnow()

    # ---------- Seat demand factor ----------
    seat_ratio = seats_left / total_seats

    if seat_ratio > 0.7:
        seat_factor = 1.0
    elif seat_ratio > 0.4:
        seat_factor = 1.15
    elif seat_ratio > 0.2:
        seat_factor = 1.35
    else:
        seat_factor = 1.6

    # ---------- Time to departure factor ----------
    departure_time = datetime.fromisoformat(departure_iso)
    hours_left = (departure_time - now).total_seconds() / 3600

    if hours_left > 72:
        time_factor = 1.0
    elif hours_left > 24:
        time_factor = 1.2
    else:
        time_factor = 1.4

    # ---------- Demand factor ----------
    demand_factor = {
        "low": 1.0,
        "medium": 1.15,
        "high": 1.3
    }.get(demand_level.lower(), 1.0)

    # ---------- Final price ----------
    final_price = base_fare * seat_factor * time_factor * demand_factor

    return ceil(final_price)