from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import auth, flights, bookings, airports, airlines, users, content, statistics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Asmanga - Flight Ticketing Service",
    description="A comprehensive flight ticketing web service with user management, flight booking, and admin features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://asmanga-uch.vercel.app",
        "https://asmanga-uch.vercel.app/",
        "http://localhost:3000",
        "http://localhost:3001",
        "https://server-raxe.onrender.com"
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(flights.router)
app.include_router(bookings.router)
app.include_router(airports.router)
app.include_router(airlines.router)
app.include_router(users.router)
app.include_router(content.router)
app.include_router(statistics.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Asmanga Flight Ticketing Service API"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
