# ✈️ SkyBook – Flight Booking Simulator

SkyBook is a full-stack **Flight Booking Simulator Web Application** that allows users to search flights, book tickets, generate e-tickets, view booking history, and provides role-based access for admins.  
The project is built to simulate a real-world airline booking workflow using modern backend and frontend technologies.

---

## 🚀 Live Demo
- **Frontend: https://flyzen.netlify.app 
- **Backend API: https://flyzen-backend.onrender.com
- **API Docs (Swagger): https://flyzen-backend.onrender.com/docs

---

## 🧩 Features

### 👤 User Features
- User authentication (login/logout)
- Search available flights
- View real-time flight details
- Book flights with seat selection
- Generate booking confirmation (PNR)
- Download booking receipt (PDF via browser print)
- View booking history

### 🛠 Admin Features
- Admin login validation
- Restricted admin-only access
- Manage flight and booking data (API level)

---

## 🏗️ Project Architecture

###  Clean Project structure

```bash
FLIGHT_PRICING/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── app.py
│   │   └── pricing_engine.py
│   │
│   ├── db/
│   │   ├── db_schema.sql
│   │   └── flight_simulator.db
│   │
│   ├── tools/
│   │   ├── create_db_run.py
│   │   └── __init__.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── assets/
│   │   ├── css/
│   │   │   └── main.css
│   │   └── js/
│   │       ├── admin.js
│   │       ├── api.js
│   │       ├── auth.js
│   │       ├── bookings.js
│   │       ├── config.js
│   │       ├── history.js
│   │       ├── receipt.js
│   │       └── search.js
│   │
│   ├── admin.html
│   ├── booking.html
│   ├── history.html
│   ├── index.html
│   ├── login.html
│   ├── receipt.html
│   └── signup.html
│
├── .gitignore
├── LICENSE
└── README.md
---




## 🧪 Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla JS)
- LocalStorage for session handling

### Backend
- Python
- FastAPI
- SQLite
- REST APIs
- CORS Middleware

### Deployment
- **Frontend:** Netlify (Free)
- **Backend:** Render (Free)

---

## 🔐 Authentication & Authorization

- User session stored using `localStorage`
- Role-based access control (`user`, `admin`)
- Admin routes protected at frontend and backend level
- Unauthorized access blocked with alerts

---

## 📦 API Overview

| Method | Endpoint | Description |
|------|--------|-------------|
| GET | `/flights` | Fetch all available flights |
| POST | `/book` | Book a flight |
| GET | `/bookings/{email}` | User booking history |
| POST | `/login` | User login |
| GET | `/admin/*` | Admin-only routes |

Swagger UI available at: http://127.0.0.1:8000/docs

---

## 🧾 Booking Flow

1. User logs in
2. Searches for flights
3. Selects a flight
4. Enters passenger details
5. Confirms booking
6. Receives PNR (Booking ID)
7. Views e-ticket & booking history

---

## 🖨️ Receipt & PDF Download

- Booking receipt generated dynamically
- PDF download supported via browser print
- Optimized layout for printing

---

## 🛠️ Local Setup Instructions

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
=======
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
>>>>>>> 2a9a51e13acd671384947f802c870fd433dddd42
