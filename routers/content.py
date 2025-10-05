from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import schemas
import crud
from database import get_db
from dependencies import require_admin

router = APIRouter(prefix="/content", tags=["content"])


# Banner endpoints
@router.get("/banners", response_model=List[schemas.Banner])
def get_banners(db: Session = Depends(get_db)):
    banners = crud.get_banners(db)
    return banners


@router.post("/banners", response_model=schemas.Banner)
def create_banner(
    banner: schemas.BannerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return crud.create_banner(db=db, banner=banner)


@router.put("/banners/{banner_id}", response_model=schemas.Banner)
def update_banner(
    banner_id: str,
    banner_update: schemas.BannerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    banner = crud.update_banner(db=db, banner_id=banner_id, banner_update=banner_update)
    if banner is None:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner


@router.delete("/banners/{banner_id}")
def delete_banner(
    banner_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    banner = crud.delete_banner(db=db, banner_id=banner_id)
    if banner is None:
        raise HTTPException(status_code=404, detail="Banner not found")
    return {"message": "Banner deleted successfully"}


# Offer endpoints
@router.get("/offers", response_model=List[schemas.Offer])
def get_offers(db: Session = Depends(get_db)):
    offers = crud.get_offers(db)
    return offers


@router.post("/offers", response_model=schemas.Offer)
def create_offer(
    offer: schemas.OfferCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return crud.create_offer(db=db, offer=offer)


@router.put("/offers/{offer_id}", response_model=schemas.Offer)
def update_offer(
    offer_id: str,
    offer_update: schemas.OfferUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    offer = crud.update_offer(db=db, offer_id=offer_id, offer_update=offer_update)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


@router.delete("/offers/{offer_id}")
def delete_offer(
    offer_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    offer = crud.delete_offer(db=db, offer_id=offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    return {"message": "Offer deleted successfully"}
