from fastapi import APIRouter, Depends
from typing import List
from app import schemas
from app import dependencies as deps
from app.repositories.amenity_repository import PropertyAmenityRepository, RoomAmenityRepository

router = APIRouter(prefix="/api/amenities", tags=["amenities"])

# dovremmo usare un service, ma per ora sono solo letture semplici
@router.get("/property", response_model=List[schemas.AmenityOutput])
def get_property_amenities_catalog(
    repo: PropertyAmenityRepository = Depends(deps.get_property_amenity_repo)
):
    """
    Returns the global catalog of property amenities (e.g., WiFi, Pool).
    Used in property management.
    """
    return repo.get_all()

@router.get("/room", response_model=List[schemas.AmenityOutput])
def get_room_amenities_catalog(
    repo: RoomAmenityRepository = Depends(deps.get_room_amenity_repo)
):
    """
    Returns the global catalog of room amenities (e.g., TV, Mini-bar).
    Used in room management.
    """
    return repo.get_all()