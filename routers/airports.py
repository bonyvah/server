from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas
import crud
from database import get_db

router = APIRouter(prefix="/airports", tags=["airports"])


@router.get("/", response_model=List[schemas.Airport])
def get_all_airports(db: Session = Depends(get_db)):
    airports = crud.get_airports(db)
    return airports


@router.get("/search", response_model=List[schemas.Airport])
def search_airports(query: str, db: Session = Depends(get_db)):
    airports = crud.search_airports(db, query=query)
    return airports


@router.get("/{airport_id}", response_model=schemas.Airport)
def get_airport(airport_id: str, db: Session = Depends(get_db)):
    airport = crud.get_airport(db, airport_id=airport_id)
    if airport is None:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport
