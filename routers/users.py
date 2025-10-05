from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import schemas
import crud
from database import get_db
from dependencies import require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[schemas.User])
def get_all_users(
    skip: int = Query(0, description="Number of users to skip"),
    limit: int = Query(100, description="Maximum number of users to return"),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: str,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/block")
def block_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    user_update = schemas.UserUpdate(is_blocked=True)
    user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User blocked successfully"}


@router.post("/{user_id}/unblock")
def unblock_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    user_update = schemas.UserUpdate(is_blocked=False)
    user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User unblocked successfully"}


@router.get("/managers/company-managers", response_model=List[schemas.User])
def get_company_managers(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    users = crud.get_users(db)
    company_managers = [user for user in users if user.role == "company_manager"]
    return company_managers


@router.post("/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud.create_user(db=db, user=user)
