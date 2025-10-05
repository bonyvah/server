from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from auth import verify_token
import models

security = HTTPBearer()


def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    payload = verify_token(token.credentials)
    email = payload.get("sub")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is blocked",
        )
    
    return user


def require_admin(current_user: models.User = Depends(get_current_user)):
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_company_manager(current_user: models.User = Depends(get_current_user)):
    """Require company manager role."""
    if current_user.role != "company_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company manager access required",
        )
    return current_user


def require_company_manager_or_admin(current_user: models.User = Depends(get_current_user)):
    """Require company manager or admin role."""
    if current_user.role not in ["company_manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company manager or admin access required",
        )
    return current_user
