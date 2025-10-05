# Asmanga Flight Ticketing Service - Backend

## Overview

This is the backend API for the Asmanga Flight Ticketing Service built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- User authentication and authorization (JWT)
- Flight search and management
- Booking system
- User management (Admin)
- Airline management (Admin)
- Content management (Banners, Offers)
- Statistics and analytics
- Role-based access control

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Relational database
- **JWT** - JSON Web Tokens for authentication
- **Alembic** - Database migration tool
- **Uvicorn** - ASGI server

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

1. Install PostgreSQL and create a database named `asmanga`
2. Copy `.env.example` to `.env` and update database credentials:

```bash
cp .env.example .env
```

### 4. Initialize Database

```bash
# Run migrations (if using Alembic)
alembic upgrade head

# Or seed with initial data
python seed_data.py
```

### 5. Run Development Server

```bash
python run_dev.py
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Flights

- `GET /flights/search` - Search flights
- `GET /flights/` - Get all flights
- `GET /flights/{flight_id}` - Get flight by ID
- `POST /flights/` - Create flight (Admin/Manager)
- `PUT /flights/{flight_id}` - Update flight (Admin/Manager)
- `DELETE /flights/{flight_id}` - Delete flight (Admin/Manager)
- `GET /flights/company/{airline_id}` - Get company flights

### Bookings

- `POST /bookings/` - Create booking
- `GET /bookings/my-bookings` - Get user bookings
- `GET /bookings/confirmation/{confirmation_id}` - Get booking by confirmation
- `GET /bookings/company/{airline_id}` - Get company bookings

### Airports

- `GET /airports/` - Get all airports
- `GET /airports/search` - Search airports
- `GET /airports/{airport_id}` - Get airport by ID

### Airlines

- `GET /airlines/` - Get all airlines
- `GET /airlines/{airline_id}` - Get airline by ID
- `POST /airlines/` - Create airline (Admin)
- `PUT /airlines/{airline_id}` - Update airline (Admin)
- `DELETE /airlines/{airline_id}` - Delete airline (Admin)
- `POST /airlines/{airline_id}/assign-manager` - Assign manager (Admin)

### Users

- `GET /users/` - Get all users (Admin)
- `GET /users/{user_id}` - Get user by ID (Admin)
- `PUT /users/{user_id}` - Update user (Admin)
- `POST /users/{user_id}/block` - Block user (Admin)
- `POST /users/{user_id}/unblock` - Unblock user (Admin)
- `GET /users/managers/company-managers` - Get company managers (Admin)
- `POST /users/` - Create user (Admin)

### Content Management

- `GET /content/banners` - Get banners
- `POST /content/banners` - Create banner (Admin)
- `PUT /content/banners/{banner_id}` - Update banner (Admin)
- `DELETE /content/banners/{banner_id}` - Delete banner (Admin)
- `GET /content/offers` - Get offers
- `POST /content/offers` - Create offer (Admin)
- `PUT /content/offers/{offer_id}` - Update offer (Admin)
- `DELETE /content/offers/{offer_id}` - Delete offer (Admin)

### Statistics

- `GET /statistics/company/{airline_id}` - Get company statistics
- `GET /statistics/admin` - Get admin statistics

## User Roles

- **Regular User**: Can search flights, book tickets, view bookings
- **Company Manager**: Can manage flights for their airline, view passengers
- **Admin**: Full access to all features, user management, airline management

## Default Test Accounts

After running `seed_data.py`, you can use these accounts:

- **Regular User**: `u@u.u` / `u`
- **Company Manager**: `m@m.m` / `m` (manages American Airlines)
- **Admin**: `a@a.a` / `a`

## Environment Variables

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/asmanga
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

## Development

```bash
# Run with auto-reload
python run_dev.py

# Run tests (if implemented)
pytest

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Production Deployment

1. Set up PostgreSQL database
2. Update environment variables for production
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Start server: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Project Structure

```
server/
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── crud.py                # Database operations
├── auth.py                # Authentication utilities
├── dependencies.py        # FastAPI dependencies
├── seed_data.py          # Database seeding script
├── run_dev.py            # Development server runner
├── requirements.txt       # Python dependencies
├── alembic.ini           # Alembic configuration
├── .env.example          # Environment variables template
└── routers/              # API route handlers
    ├── auth.py
    ├── flights.py
    ├── bookings.py
    ├── airports.py
    ├── airlines.py
    ├── users.py
    ├── content.py
    └── statistics.py
```
