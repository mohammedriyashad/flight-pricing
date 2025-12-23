import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from milestone1.api.seats import lock_seat

lock_seat(1, "A1")
print("✅ Seat A1 locked")