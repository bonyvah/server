# Seed data for the database
from datetime import datetime, timedelta, timezone
from database import SessionLocal, engine
import models
# from auth import get_password_hash  # Commented out due to bcrypt issues

# Create tables
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_data():
    """Seed the database with initial data."""
    
    # Check if data already exists
    if db.query(models.User).first():
        print("Database already seeded.")
        return
    
    print("Seeding database...")
    
    # Create airports
    airports_data = [
        {"id": "1", "name": "John F. Kennedy International Airport", "code": "JFK", "city": "New York", "country": "USA", "timezone": "America/New_York"},
        {"id": "2", "name": "Los Angeles International Airport", "code": "LAX", "city": "Los Angeles", "country": "USA", "timezone": "America/Los_Angeles"},
        {"id": "3", "name": "London Heathrow Airport", "code": "LHR", "city": "London", "country": "UK", "timezone": "Europe/London"},
        {"id": "4", "name": "Dubai International Airport", "code": "DXB", "city": "Dubai", "country": "UAE", "timezone": "Asia/Dubai"},
        {"id": "5", "name": "Tokyo Haneda Airport", "code": "HND", "city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
    ]
    
    for airport_data in airports_data:
        airport = models.Airport(**airport_data)
        db.add(airport)
    
    # Create airlines
    airlines_data = [
        {"id": "1", "name": "American Airlines", "code": "AA", "description": "Major American airline headquartered in Fort Worth, Texas"},
        {"id": "2", "name": "Delta Air Lines", "code": "DL", "description": "Major American airline headquartered in Atlanta, Georgia"},
        {"id": "3", "name": "British Airways", "code": "BA", "description": "Flag carrier airline of the United Kingdom"},
        {"id": "4", "name": "Emirates", "code": "EK", "description": "Flag carrier airline of the United Arab Emirates"},
    ]
    
    for airline_data in airlines_data:
        airline = models.Airline(**airline_data)
        db.add(airline)
    
    # Create users (using plain text passwords for development)
    users_data = [
        {"id": "1", "email": "u@u.u", "password": "u", "first_name": "John", "last_name": "Doe", "phone": "+1234567890", "role": "regular"},
        {"id": "2", "email": "admin@asmanga.com", "password": "admin123", "first_name": "Admin", "last_name": "User", "phone": "+1234567891", "role": "admin"},
        {"id": "3", "email": "aa_manager@asmanga.com", "password": "manager123", "first_name": "AA", "last_name": "Manager", "phone": "+1234567892", "role": "company_manager", "airline_id": "1"},
        {"id": "4", "email": "delta_manager@asmanga.com", "password": "manager123", "first_name": "Delta", "last_name": "Manager", "phone": "+1234567893", "role": "company_manager", "airline_id": "2"},
    ]
    
    for user_data in users_data:
        user = models.User(**user_data)
        db.add(user)
    
    # Commit the initial data first
    db.commit()
    
    # Update airlines with manager IDs
    airline_1 = db.query(models.Airline).filter(models.Airline.id == "1").first()
    if airline_1:
        airline_1.manager_id = "3"  # AA manager
        
    airline_2 = db.query(models.Airline).filter(models.Airline.id == "2").first()
    if airline_2:
        airline_2.manager_id = "4"  # Delta manager
    
    # Create flights
    base_time =  datetime.now(timezone.utc) + timedelta(days=30)  # Flights in the future
    
    flights_data = [
        {
            "id": "1", "flight_number": "AA101", "airline_id": "1", "origin_id": "1", "destination_id": "2",
            "departure_time": base_time + timedelta(hours=8), "arrival_time": base_time + timedelta(hours=14, minutes=30),
            "duration": 390, "price": 299.0, "available_seats": 45, "total_seats": 180
        },
        {
            "id": "2", "flight_number": "DL205", "airline_id": "2", "origin_id": "2", "destination_id": "3",
            "departure_time": base_time + timedelta(hours=14), "arrival_time": base_time + timedelta(days=1, hours=9),
            "duration": 660, "price": 789.0, "available_seats": 23, "total_seats": 250
        },
        {
            "id": "3", "flight_number": "BA403", "airline_id": "3", "origin_id": "3", "destination_id": "4",
            "departure_time": base_time + timedelta(hours=16, minutes=30), "arrival_time": base_time + timedelta(days=1, hours=1, minutes=30),
            "duration": 420, "price": 599.0, "available_seats": 67, "total_seats": 200
        },
        {
            "id": "4", "flight_number": "EK701", "airline_id": "4", "origin_id": "4", "destination_id": "5",
            "departure_time": base_time + timedelta(hours=2), "arrival_time": base_time + timedelta(hours=15),
            "duration": 540, "price": 899.0, "available_seats": 12, "total_seats": 300
        },
    ]
    
    for flight_data in flights_data:
        flight = models.Flight(**flight_data)
        db.add(flight)
    
    # Create banners
    banners_data = [
        {
            "id": "1", "title": "Summer Sale - Up to 50% Off!", "description": "Book your dream vacation now and save big on international flights",
            "is_active": True, "order": 1
        },
        {
            "id": "2", "title": "New Routes to Asia", "description": "Discover our new direct flights to Tokyo, Seoul, and Bangkok",
            "is_active": True, "order": 2
        },
    ]
    
    for banner_data in banners_data:
        banner = models.Banner(**banner_data)
        db.add(banner)
    
    # Create offers
    offers_data = [
        {
            "id": "1", "title": "Early Bird Special", "description": "Book 60 days in advance and get 25% off",
            "discount": 25.0, "valid_from":  datetime.now(timezone.utc), "valid_to":  datetime.now(timezone.utc) + timedelta(days=90),
            "min_price": 200.0, "max_discount": 200.0, "is_active": True
        },
        {
            "id": "2", "title": "Weekend Getaway", "description": "20% off on weekend flights within the country",
            "discount": 20.0, "valid_from":  datetime.now(timezone.utc), "valid_to":  datetime.now(timezone.utc) + timedelta(days=60),
            "max_discount": 150.0, "is_active": True
        },
    ]
    
    for offer_data in offers_data:
        offer = models.Offer(**offer_data)
        db.add(offer)
    
    db.commit()
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_data()
    db.close()
