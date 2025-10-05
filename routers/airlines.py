from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import schemas
import crud
from database import get_db
from dependencies import require_admin

router = APIRouter(prefix="/airlines", tags=["airlines"])


@router.get("/", response_model=List[schemas.Airline])
def get_all_airlines(db: Session = Depends(get_db)):
    airlines = crud.get_airlines(db)
    return airlines


@router.get("/{airline_id}", response_model=schemas.Airline)
def get_airline(airline_id: str, db: Session = Depends(get_db)):
    airline = crud.get_airline(db, airline_id=airline_id)
    if airline is None:
        raise HTTPException(status_code=404, detail="Airline not found")
    return airline


@router.post("/", response_model=schemas.Airline)
def create_airline(
    airline: schemas.AirlineCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return crud.create_airline(db=db, airline=airline)


@router.put("/{airline_id}", response_model=schemas.Airline)
def update_airline(
    airline_id: str,
    airline_update: schemas.AirlineUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    airline = crud.update_airline(db=db, airline_id=airline_id, airline_update=airline_update)
    if airline is None:
        raise HTTPException(status_code=404, detail="Airline not found")
    return airline


@router.delete("/{airline_id}")
def delete_airline(
    airline_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    airline = crud.delete_airline(db=db, airline_id=airline_id)
    if airline is None:
        raise HTTPException(status_code=404, detail="Airline not found")
    return {"message": "Airline deleted successfully"}


@router.post("/{airline_id}/assign-manager")
def assign_manager(
    airline_id: str,
    manager_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    # Check if airline exists
    airline = crud.get_airline(db, airline_id)
    if not airline:
        raise HTTPException(status_code=404, detail="Airline not found")
    
    # Check if user exists and is a company manager
    user = crud.get_user(db, manager_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != "company_manager":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be a company manager"
        )
    
    # Update airline and user
    airline_update = schemas.AirlineUpdate(manager_id=manager_id)
    crud.update_airline(db, airline_id, airline_update)
    
    user_update = schemas.UserUpdate(airline_id=airline_id)
    crud.update_user(db, manager_id, user_update)
    
    return {"message": "Manager assigned successfully"}
