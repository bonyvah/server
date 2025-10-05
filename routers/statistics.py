from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import models
import schemas
from database import get_db
from dependencies import get_current_user, require_admin

router = APIRouter(prefix="/statistics", tags=["statistics"])


def get_date_filter(period: str):
    """Get date filter based on period."""
    now = datetime.utcnow()
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:  # "all"
        start_date = None
    
    return start_date


@router.get("/company/{airline_id}", response_model=schemas.CompanyStatistics)
def get_company_statistics(
    airline_id: str,
    period: str = Query("all", description="Statistics period: today, week, month, all"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check permissions
    if current_user.role == "company_manager":
        if current_user.airline_id != airline_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
    elif current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin or company manager access required"
        )
    
    start_date = get_date_filter(period)
    
    # Base query for flights
    flights_query = db.query(models.Flight).filter(models.Flight.airline_id == airline_id)
    if start_date:
        flights_query = flights_query.filter(models.Flight.created_at >= start_date)
    
    # Total flights
    total_flights = flights_query.count()
    
    # Active flights (future flights)
    active_flights = flights_query.filter(
        models.Flight.departure_time > datetime.utcnow(),
        models.Flight.status.in_(["scheduled", "boarding"])
    ).count()
    
    # Completed flights
    completed_flights = flights_query.filter(
        models.Flight.departure_time <= datetime.utcnow(),
        models.Flight.status.in_(["departed", "arrived"])
    ).count()
    
    # Bookings query
    bookings_query = db.query(models.Booking).join(models.Flight).filter(
        models.Flight.airline_id == airline_id
    )
    if start_date:
        bookings_query = bookings_query.filter(models.Booking.booked_at >= start_date)
    
    # Total passengers and revenue
    bookings = bookings_query.all()
    total_passengers = sum(len(booking.passengers) for booking in bookings)
    total_revenue = sum(booking.total_price for booking in bookings)
    
    return schemas.CompanyStatistics(
        total_flights=total_flights,
        active_flights=active_flights,
        completed_flights=completed_flights,
        total_passengers=total_passengers,
        total_revenue=total_revenue,
        period=period
    )


@router.get("/admin", response_model=schemas.AdminStatistics)
def get_admin_statistics(
    period: str = Query("all", description="Statistics period: today, week, month, all"),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    start_date = get_date_filter(period)
    
    # Base queries
    flights_query = db.query(models.Flight)
    bookings_query = db.query(models.Booking)
    users_query = db.query(models.User)
    
    if start_date:
        flights_query = flights_query.filter(models.Flight.created_at >= start_date)
        bookings_query = bookings_query.filter(models.Booking.booked_at >= start_date)
        users_query = users_query.filter(models.User.created_at >= start_date)
    
    # Total flights
    total_flights = flights_query.count()
    
    # Active flights
    active_flights = flights_query.filter(
        models.Flight.departure_time > datetime.utcnow(),
        models.Flight.status.in_(["scheduled", "boarding"])
    ).count()
    
    # Completed flights
    completed_flights = flights_query.filter(
        models.Flight.departure_time <= datetime.utcnow(),
        models.Flight.status.in_(["departed", "arrived"])
    ).count()
    
    # Bookings and passengers
    bookings = bookings_query.all()
    total_bookings = len(bookings)
    total_passengers = sum(len(booking.passengers) for booking in bookings)
    total_revenue = sum(booking.total_price for booking in bookings)
    
    # Users and airlines
    total_users = users_query.count()
    total_airlines = db.query(models.Airline).filter(models.Airline.is_active == True).count()
    
    return schemas.AdminStatistics(
        total_flights=total_flights,
        active_flights=active_flights,
        completed_flights=completed_flights,
        total_passengers=total_passengers,
        total_revenue=total_revenue,
        total_users=total_users,
        total_airlines=total_airlines,
        total_bookings=total_bookings,
        period=period
    )
