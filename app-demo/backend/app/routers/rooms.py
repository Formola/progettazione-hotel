from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas
from app import dependencies as deps
from app.domain.entities import User
from app.services.room_service import RoomService 

# gli URL saranno tipo: PUT /api/rooms/{room_id}
router = APIRouter(prefix="/api/rooms", tags=["rooms"])

@router.get("/{room_id}", response_model=schemas.RoomData)
def get_room_details(
    room_id: str,
    service: RoomService = Depends(deps.get_room_service)
):
    """
    Fetch room details by ID.
    Does not require authentication.
    """
    return service.get_room(room_id)


@router.put("/{room_id}", response_model=schemas.RoomData)
def update_room(
    room_id: str,
    payload: schemas.RoomInput,
    service: RoomService = Depends(deps.get_room_service),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update room details (e.g., price, room type...).
    Requires being the Owner of the property to which the room belongs.
    """
    return service.update_room(room_id=room_id, data=payload, owner=current_user)

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: str,
    service: RoomService = Depends(deps.get_room_service),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a room by ID.
    Requires being the Owner of the property to which the room belongs.
    """
    service.delete_room(room_id=room_id, owner=current_user)
    return None



@router.post("/{room_id}/amenities", response_model=schemas.RoomData)
def add_amenity_to_room(
    room_id: str,
    payload: schemas.NewAmenityInput, # Input DTO (name, category...)
    service: RoomService = Depends(deps.get_room_service),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Create a new amenity and link it to the room.
    """
    return service.add_new_amenity(room_id=room_id, data=payload, owner=current_user)

@router.delete("/{room_id}/amenities/{amenity_id}", response_model=schemas.RoomData)
def remove_amenity_from_room(
    room_id: str,
    amenity_id: str,
    service: RoomService = Depends(deps.get_room_service),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Remove an amenity from the room.
    """
    return service.remove_room_amenity(room_id, amenity_id, owner=current_user)