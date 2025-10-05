from sqlalchemy.orm import Session, aliased
from typing import List, Optional
import models
import schemas
from auth import get_password_hash, verify_password
import uuid
from datetime import datetime, timedelta


# User CRUD operations
def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        id=str(uuid.uuid4()),
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: str, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# Airport CRUD operations
def get_airports(db: Session):
    return db.query(models.Airport).all()


def get_airport(db: Session, airport_id: str):
    return db.query(models.Airport).filter(models.Airport.id == airport_id).first()


def search_airports(db: Session, query: str):
    return db.query(models.Airport).filter(
        models.Airport.name.ilike(f"%{query}%") |
        models.Airport.code.ilike(f"%{query}%") |
        models.Airport.city.ilike(f"%{query}%")
    ).all()


# Airline CRUD operations
def get_airlines(db: Session):
    return db.query(models.Airline).all()


def get_airline(db: Session, airline_id: str):
    return db.query(models.Airline).filter(models.Airline.id == airline_id).first()


def create_airline(db: Session, airline: schemas.AirlineCreate):
    db_airline = models.Airline(
        id=str(uuid.uuid4()),
        name=airline.name,
        code=airline.code,
        logo=airline.logo,
        description=airline.description,
        is_active=airline.is_active,
        manager_id=airline.manager_id,
    )
    db.add(db_airline)
    db.commit()
    db.refresh(db_airline)
    return db_airline


def update_airline(db: Session, airline_id: str, airline_update: schemas.AirlineUpdate):
    db_airline = db.query(models.Airline).filter(models.Airline.id == airline_id).first()
    if db_airline:
        for field, value in airline_update.dict(exclude_unset=True).items():
            setattr(db_airline, field, value)
        db.commit()
        db.refresh(db_airline)
    return db_airline


def delete_airline(db: Session, airline_id: str):
    db_airline = db.query(models.Airline).filter(models.Airline.id == airline_id).first()
    if db_airline:
        db.delete(db_airline)
        db.commit()
    return db_airline


# Flight CRUD operations
def get_flights(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Flight).offset(skip).limit(limit).all()


def get_flight(db: Session, flight_id: str):
    return db.query(models.Flight).filter(models.Flight.id == flight_id).first()


def get_company_flights(db: Session, airline_id: str):
    return db.query(models.Flight).filter(models.Flight.airline_id == airline_id).all()


def search_flights(db: Session, search_params: schemas.FlightSearchParams, filters: Optional[schemas.FlightFilters] = None):
    # Create aliases for airports table to avoid duplicate table name error
    origin_airport = aliased(models.Airport)
    destination_airport = aliased(models.Airport)
    
    query = db.query(models.Flight).join(
        origin_airport, models.Flight.origin_id == origin_airport.id
    ).join(
        destination_airport, models.Flight.destination_id == destination_airport.id
    )
    
    # Basic search filters
    query = query.filter(
        origin_airport.code == search_params.origin,
        destination_airport.code == search_params.destination,
        models.Flight.departure_time >= datetime.fromisoformat(search_params.departure_date)
    )
    
    # Apply additional filters if provided
    if filters:
        if filters.price_min is not None:
            query = query.filter(models.Flight.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.filter(models.Flight.price <= filters.price_max)
        if filters.airlines:
            query = query.filter(models.Flight.airline_id.in_(filters.airlines))
        if filters.max_duration:
            query = query.filter(models.Flight.duration <= filters.max_duration)
    
    return query.all()


def create_flight(db: Session, flight: schemas.FlightCreate):
    # Calculate duration
    departure = datetime.fromisoformat(str(flight.departure_time))
    arrival = datetime.fromisoformat(str(flight.arrival_time))
    duration = int((arrival - departure).total_seconds() / 60)
    
    db_flight = models.Flight(
        id=str(uuid.uuid4()),
        flight_number=flight.flight_number,
        airline_id=flight.airline_id,
        origin_id=flight.origin_id,
        destination_id=flight.destination_id,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        duration=duration,
        price=flight.price,
        available_seats=flight.total_seats,
        total_seats=flight.total_seats,
    )
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight


def update_flight(db: Session, flight_id: str, flight_update: schemas.FlightUpdate):
    db_flight = db.query(models.Flight).filter(models.Flight.id == flight_id).first()
    if db_flight:
        for field, value in flight_update.dict(exclude_unset=True).items():
            setattr(db_flight, field, value)
        
        # Recalculate duration if times changed
        if flight_update.departure_time or flight_update.arrival_time:
            duration = int((db_flight.arrival_time - db_flight.departure_time).total_seconds() / 60)
            db_flight.duration = duration
        
        db.commit()
        db.refresh(db_flight)
    return db_flight


def delete_flight(db: Session, flight_id: str):
    db_flight = db.query(models.Flight).filter(models.Flight.id == flight_id).first()
    if db_flight:
        db.delete(db_flight)
        db.commit()
    return db_flight


# Booking CRUD operations
def get_user_bookings(db: Session, user_id: str):
    return db.query(models.Booking).filter(models.Booking.user_id == user_id).all()


def get_booking_by_confirmation(db: Session, confirmation_id: str):
    return db.query(models.Booking).filter(models.Booking.confirmation_id == confirmation_id).first()


def get_booking(db: Session, booking_id: str):
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()


def get_company_bookings(db: Session, airline_id: str):
    return db.query(models.Booking).join(models.Flight).filter(models.Flight.airline_id == airline_id).all()


def create_booking(db: Session, booking: schemas.BookingCreate, user_id: str):
    # Get flight
    flight = get_flight(db, booking.flight_id)
    if not flight or flight.available_seats < len(booking.passengers):
        return None
    
    # Create booking
    confirmation_id = f"ASM-2025-{str(uuid.uuid4())[:6].upper()}"
    total_price = flight.price * len(booking.passengers)
    
    db_booking = models.Booking(
        id=str(uuid.uuid4()),
        confirmation_id=confirmation_id,
        user_id=user_id,
        flight_id=booking.flight_id,
        total_price=total_price,
    )
    db.add(db_booking)
    
    # Create passengers
    for passenger_data in booking.passengers:
        passenger = models.Passenger(
            id=str(uuid.uuid4()),
            booking_id=db_booking.id,
            **passenger_data.dict()
        )
        db.add(passenger)
    
    # Update flight availability
    flight.available_seats -= len(booking.passengers)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking


# Banner CRUD operations
def get_banners(db: Session):
    return db.query(models.Banner).filter(models.Banner.is_active == True).order_by(models.Banner.order).all()


def create_banner(db: Session, banner: schemas.BannerCreate):
    db_banner = models.Banner(
        id=str(uuid.uuid4()),
        **banner.dict()
    )
    db.add(db_banner)
    db.commit()
    db.refresh(db_banner)
    return db_banner


def update_banner(db: Session, banner_id: str, banner_update: schemas.BannerUpdate):
    db_banner = db.query(models.Banner).filter(models.Banner.id == banner_id).first()
    if db_banner:
        for field, value in banner_update.dict(exclude_unset=True).items():
            setattr(db_banner, field, value)
        db.commit()
        db.refresh(db_banner)
    return db_banner


def delete_banner(db: Session, banner_id: str):
    db_banner = db.query(models.Banner).filter(models.Banner.id == banner_id).first()
    if db_banner:
        db.delete(db_banner)
        db.commit()
    return db_banner


# Offer CRUD operations
def get_offers(db: Session):
    return db.query(models.Offer).filter(
        models.Offer.is_active == True,
        models.Offer.valid_from <= datetime.utcnow(),
        models.Offer.valid_to >= datetime.utcnow()
    ).all()


def create_offer(db: Session, offer: schemas.OfferCreate):
    db_offer = models.Offer(
        id=str(uuid.uuid4()),
        **offer.dict()
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer


def update_offer(db: Session, offer_id: str, offer_update: schemas.OfferUpdate):
    db_offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if db_offer:
        for field, value in offer_update.dict(exclude_unset=True).items():
            setattr(db_offer, field, value)
        db.commit()
        db.refresh(db_offer)
    return db_offer


def delete_offer(db: Session, offer_id: str):
    db_offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if db_offer:
        db.delete(db_offer)
        db.commit()
    return db_offer
