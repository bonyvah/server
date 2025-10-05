from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import schemas
import crud
from database import get_db
from dependencies import get_current_user, require_company_manager_or_admin

router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/search", response_model=List[schemas.Flight])
def search_flights(
    origin: str = Query(..., description="Origin airport code"),
    destination: str = Query(..., description="Destination airport code"),
    departure_date: str = Query(..., description="Departure date"),
    passengers: int = Query(1, description="Number of passengers"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    airlines: Optional[str] = Query(None, description="Comma-separated airline IDs"),
    max_duration: Optional[int] = Query(None, description="Maximum duration in minutes"),
    db: Session = Depends(get_db)
):
    # Create search parameters
    search_params = schemas.FlightSearchParams(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        passengers=passengers
    )
    
    # Create filters
    filters = schemas.FlightFilters(
        price_min=price_min,
        price_max=price_max,
        airlines=airlines.split(",") if airlines else None,
        max_duration=max_duration
    )
    
    flights = crud.search_flights(db, search_params, filters)
    return flights


@router.get("/", response_model=List[schemas.Flight])
def get_all_flights(
    skip: int = Query(0, description="Number of flights to skip"),
    limit: int = Query(100, description="Maximum number of flights to return"),
    db: Session = Depends(get_db)
):
    flights = crud.get_flights(db, skip=skip, limit=limit)
    return flights


@router.get("/{flight_id}", response_model=schemas.Flight)
def get_flight(flight_id: str, db: Session = Depends(get_db)):
    flight = crud.get_flight(db, flight_id=flight_id)
    if flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


@router.post("/", response_model=schemas.Flight)
def create_flight(
    flight: schemas.FlightCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_company_manager_or_admin)
):
    # If user is company manager, they can only create flights for their airline
    if current_user.role == "company_manager":
        if current_user.airline_id != flight.airline_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company managers can only create flights for their own airline"
            )
    
    return crud.create_flight(db=db, flight=flight)


@router.put("/{flight_id}", response_model=schemas.Flight)
def update_flight(
    flight_id: str,
    flight_update: schemas.FlightUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_company_manager_or_admin)
):
    # Check if flight exists
    existing_flight = crud.get_flight(db, flight_id)
    if not existing_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    # If user is company manager, they can only update flights for their airline
    if current_user.role == "company_manager":
        if current_user.airline_id != existing_flight.airline_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company managers can only update flights for their own airline"
            )
    
    return crud.update_flight(db=db, flight_id=flight_id, flight_update=flight_update)


@router.delete("/{flight_id}")
def delete_flight(
    flight_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_company_manager_or_admin)
):
    # Check if flight exists
    existing_flight = crud.get_flight(db, flight_id)
    if not existing_flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    # If user is company manager, they can only delete flights for their airline
    if current_user.role == "company_manager":
        if current_user.airline_id != existing_flight.airline_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company managers can only delete flights for their own airline"
            )
    
    # Check if flight has bookings
    if existing_flight.bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete flight with existing bookings. Please cancel all bookings first."
        )
    
    crud.delete_flight(db=db, flight_id=flight_id)
    return {"success": True, "message": "Flight deleted successfully"}


@router.get("/company/{airline_id}", response_model=List[schemas.Flight])
def get_company_flights(
    airline_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_company_manager_or_admin)
):
    # If user is company manager, they can only view flights for their airline
    if current_user.role == "company_manager":
        if current_user.airline_id != airline_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company managers can only view flights for their own airline"
            )
    
    flights = crud.get_company_flights(db, airline_id=airline_id)
    return flights
