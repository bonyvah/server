from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import datetime


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: Literal["regular", "company_manager", "admin"] = "regular"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[Literal["regular", "company_manager", "admin"]] = None
    airline_id: Optional[str] = None
    is_blocked: Optional[bool] = None


class User(UserBase):
    id: str
    airline_id: Optional[str] = None
    is_blocked: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


# Airport schemas
class AirportBase(BaseModel):
    name: str
    code: str
    city: str
    country: str
    timezone: str


class AirportCreate(AirportBase):
    pass


class Airport(AirportBase):
    id: str

    class Config:
        from_attributes = True


# Airline schemas
class AirlineBase(BaseModel):
    name: str
    code: str
    logo: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class AirlineCreate(AirlineBase):
    manager_id: Optional[str] = None


class AirlineUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    logo: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    manager_id: Optional[str] = None


class Airline(AirlineBase):
    id: str
    manager_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Flight schemas
class FlightBase(BaseModel):
    flight_number: str
    airline_id: str
    origin_id: str
    destination_id: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    total_seats: int


class FlightCreate(FlightBase):
    pass


class FlightUpdate(BaseModel):
    flight_number: Optional[str] = None
    origin_id: Optional[str] = None
    destination_id: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[float] = None
    total_seats: Optional[int] = None
    status: Optional[str] = None


class Flight(FlightBase):
    id: str
    duration: int
    available_seats: int
    status: str = "scheduled"
    created_at: datetime
    updated_at: datetime
    airline: Airline
    origin: Airport
    destination: Airport

    class Config:
        from_attributes = True


# Passenger schemas
class PassengerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: str
    passport_number: Optional[str] = None
    nationality: Optional[str] = None


class PassengerCreate(PassengerBase):
    pass


class Passenger(PassengerBase):
    id: str

    class Config:
        from_attributes = True


# Booking schemas
class BookingBase(BaseModel):
    flight_id: str
    passengers: List[PassengerCreate]


class BookingCreate(BookingBase):
    pass


class Booking(BaseModel):
    id: str
    confirmation_id: str
    user_id: str
    flight_id: str
    total_price: float
    status: str = "confirmed"
    payment_status: str = "paid"
    booked_at: datetime
    user: User
    flight: Flight
    passengers: List[Passenger]

    class Config:
        from_attributes = True


# Banner schemas
class BannerBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    link: Optional[str] = None
    is_active: bool = True
    order: int = 0


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    link: Optional[str] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None


class Banner(BannerBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Offer schemas
class OfferBase(BaseModel):
    title: str
    description: Optional[str] = None
    discount: float
    valid_from: datetime
    valid_to: datetime
    min_price: Optional[float] = None
    max_discount: Optional[float] = None
    is_active: bool = True


class OfferCreate(OfferBase):
    pass


class OfferUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    discount: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    min_price: Optional[float] = None
    max_discount: Optional[float] = None
    is_active: Optional[bool] = None


class Offer(OfferBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Search and filter schemas
class FlightSearchParams(BaseModel):
    origin: str  # airport code
    destination: str  # airport code
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    trip_type: Literal["one-way", "round-trip"] = "one-way"


class FlightFilters(BaseModel):
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    airlines: Optional[List[str]] = None
    departure_time_start: Optional[str] = None
    departure_time_end: Optional[str] = None
    arrival_time_start: Optional[str] = None
    arrival_time_end: Optional[str] = None
    max_stops: Optional[int] = None
    max_duration: Optional[int] = None


# Statistics schemas
class CompanyStatistics(BaseModel):
    total_flights: int
    active_flights: int
    completed_flights: int
    total_passengers: int
    total_revenue: float
    period: str


class AdminStatistics(CompanyStatistics):
    total_users: int
    total_airlines: int
    total_bookings: int


# Response schemas
class PaginatedResponse(BaseModel):
    data: List[dict]
    total: int
    page: int
    limit: int
    total_pages: int


class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    error: Optional[str] = None
