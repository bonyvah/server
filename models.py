from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String)
    role = Column(String, nullable=False, default="regular")  # regular, company_manager, admin
    airline_id = Column(String, ForeignKey("airlines.id"))
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="user")


class Airport(Base):
    __tablename__ = "airports"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    timezone = Column(String, nullable=False)

    # Relationships
    departing_flights = relationship("Flight", foreign_keys="Flight.origin_id", back_populates="origin")
    arriving_flights = relationship("Flight", foreign_keys="Flight.destination_id", back_populates="destination")


class Airline(Base):
    __tablename__ = "airlines"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    logo = Column(String)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    manager_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    flights = relationship("Flight", back_populates="airline")


class Flight(Base):
    __tablename__ = "flights"

    id = Column(String, primary_key=True, index=True)
    flight_number = Column(String, nullable=False)
    airline_id = Column(String, ForeignKey("airlines.id"), nullable=False)
    origin_id = Column(String, ForeignKey("airports.id"), nullable=False)
    destination_id = Column(String, ForeignKey("airports.id"), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    price = Column(Float, nullable=False)
    available_seats = Column(Integer, nullable=False)
    total_seats = Column(Integer, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, boarding, departed, arrived, cancelled, delayed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    airline = relationship("Airline", back_populates="flights")
    origin = relationship("Airport", foreign_keys=[origin_id], back_populates="departing_flights")
    destination = relationship("Airport", foreign_keys=[destination_id], back_populates="arriving_flights")
    bookings = relationship("Booking", back_populates="flight")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, index=True)
    confirmation_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    flight_id = Column(String, ForeignKey("flights.id"), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="confirmed")  # confirmed, cancelled, completed
    payment_status = Column(String, default="paid")  # pending, paid, failed, refunded
    booked_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")
    passengers = relationship("Passenger", back_populates="booking")


class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(String, primary_key=True, index=True)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    date_of_birth = Column(String, nullable=False)
    passport_number = Column(String)
    nationality = Column(String)

    # Relationships
    booking = relationship("Booking", back_populates="passengers")


class Banner(Base):
    __tablename__ = "banners"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    image_url = Column(String)
    link = Column(String)
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Offer(Base):
    __tablename__ = "offers"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    discount = Column(Float, nullable=False)  # percentage
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    min_price = Column(Float)
    max_discount = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
