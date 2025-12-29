from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas import PropertyInput, PropertyData, RoomInput, RoomData
from app import dependencies as deps
from app.domain.entities import User
from app.services.property_service import PropertyService
from app.services.room_service import RoomService

router = APIRouter(prefix="/api/properties", tags=["properties"])

@router.post("/", response_model=PropertyData, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyInput,
    service: PropertyService = Depends(deps.get_property_service),
    current_user: User = Depends(deps.get_current_user)
):
    
    """
    Create a new property owned by the current user.
    """
    
    return service.create_property(data=payload, owner=current_user)

@router.get("/mine", response_model=List[PropertyData])
def get_my_properties(
    service: PropertyService = Depends(deps.get_property_service),
    current_user: User = Depends(deps.get_current_user)
):
    
    """
    Ritorna tutte le proprietà dell'owner loggato.
    """
    
    return service.get_user_properties(owner=current_user)

@router.get("/{property_id}", response_model=PropertyData)
def get_property_details(
    property_id: str,
    service: PropertyService = Depends(deps.get_property_service)
):
    
    """
    Ritorna i dettagli di una proprietà specifica.
    """
    
    return service.get_property_by_id(property_id)

# get by owner_id. useful for testing via /docs
@router.get("/owner/{owner_id}", response_model=List[PropertyData])
def get_properties_by_owner(
    owner_id: str,
    service: PropertyService = Depends(deps.get_property_service)
):
    """
    Ritorna tutte le proprietà di un owner specifico.
    """
    return service.get_user_properties(owner_id=owner_id, owner=None)

@router.get("/{property_id}/rooms", response_model=List[RoomData])
def get_rooms_for_property(
    property_id: str,
    service: RoomService = Depends(deps.get_room_service)
):
    """
    Fetch all rooms for a specific property.
    """
    return service.get_rooms_by_property_id(property_id=property_id)

@router.post("/{property_id}/publish", response_model=PropertyData)
def publish_property(
    property_id: str,
    service: PropertyService = Depends(deps.get_property_service),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Publish a property owned by the current user.
    """
    
    return service.publish_property(property_id=property_id, owner=current_user)

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: str,
    service: PropertyService = Depends(deps.get_property_service),
    current_user: User = Depends(deps.get_current_user)
):
    
    """
    Delete a property owned by the current user.
    """
    
    service.delete_property(property_id=property_id, owner=current_user)
    return None

@router.put("/{property_id}", response_model=PropertyData)
def update_property(
    property_id: str,
    payload: PropertyInput,
    service: PropertyService = Depends(deps.get_property_service),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update an existing property owned by the current user.
    """
    
    return service.update_property(property_id=property_id, data=payload, owner=current_user)

@router.post("/{property_id}/rooms", response_model=RoomData, status_code=status.HTTP_201_CREATED)
def add_room_to_property(
    property_id: str,
    payload: RoomInput,
    room_service: RoomService = Depends(deps.get_room_service), 
    current_user: User = Depends(deps.get_current_user)
):
    """
    Add a new room to a property owned by the current user.
    1. Verify that the property exists and is owned by the current user.
    2. Create the room associated with that property.
    3. Return the created room data.
    """
    return room_service.add_room(property_id=property_id, data=payload, owner=current_user)