# Flight Simulator — Milestone 1

## What is included
- SQLite schema & seed: db/db_schema.sql
- Create DB script: tools/create_db.py
- FastAPI app: api/main.py with:
  - GET /flights/
  - GET /flights/search
  - POST /simulate_feed/
  - POST /book/
  - GET /bookings/{id}
- requirements.txt

## Quick start (from milestone1/)
1. Create & activate venv:
   - Windows:
     
     python -m venv venv
     venv\Scripts\activate
     
   - macOS/Linux:
     
     python3 -m venv venv
     source venv/bin/activate
     

2. Install dependencies:
3. Create DB
4. Run the API
