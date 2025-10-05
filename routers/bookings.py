from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import schemas
import crud
from database import get_db
from dependencies import get_current_user
import traceback

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=schemas.Booking)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        print(f"Creating booking for user {current_user.id}")
        print(f"Booking data: {booking.dict()}")
        
        # Check if flight exists and has enough seats
        flight = crud.get_flight(db, booking.flight_id)
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        if flight.available_seats < len(booking.passengers):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough available seats"
            )
        
        db_booking = crud.create_booking(db=db, booking=booking, user_id=current_user.id)
        if not db_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create booking"
            )
        
        return db_booking
    except Exception as e:
        print(f"Booking creation error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise


@router.get("/my-bookings", response_model=List[schemas.Booking])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    bookings = crud.get_user_bookings(db, user_id=current_user.id)
    return bookings


@router.get("/confirmation/{confirmation_id}", response_model=schemas.Booking)
def get_booking_by_confirmation(
    confirmation_id: str,
    db: Session = Depends(get_db)
):
    booking = crud.get_booking_by_confirmation(db, confirmation_id=confirmation_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.get("/company/{airline_id}", response_model=List[schemas.Booking])
def get_company_bookings(
    airline_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check permissions - only company managers of the airline or admins can access
    if current_user.role == "company_manager":
        if current_user.airline_id != airline_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or company manager access required"
        )
    
    bookings = crud.get_company_bookings(db, airline_id=airline_id)
    return bookings


@router.post("/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Get the booking
    booking = crud.get_booking(db, booking_id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user owns this booking
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings"
        )
    
    # Check if booking is already cancelled
    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )
    
    # Check if flight has already departed
    flight = crud.get_flight(db, booking.flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    now = datetime.utcnow()
    flight_departure = flight.departure_time
    
    # Check if it's less than 24 hours before departure
    hours_until_departure = (flight_departure - now).total_seconds() / 3600
    
    if hours_until_departure < 24:
        # No refund - mark as cancelled
        booking.status = "cancelled"
        booking.payment_status = "non_refundable"
        
        # Don't restore seats for non-refundable cancellations
        db.commit()
        
        return {
            "message": "Booking cancelled successfully. No refund available for cancellations less than 24 hours before departure.",
            "refund_status": "non_refundable"
        }
    else:
        # Refund available - mark as cancelled with refund
        booking.status = "cancelled"
        booking.payment_status = "refunded"
        
        # Restore seats to flight
        flight.available_seats += len(booking.passengers)
        
        db.commit()
        
        return {
            "message": "Booking cancelled successfully. Refund will be processed.",
            "refund_status": "refunded"
        }
