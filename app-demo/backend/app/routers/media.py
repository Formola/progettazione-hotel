from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import MediaInput, MediaData
from app.services.media_service import MediaService
from app import dependencies as deps
from app.domain.entities import User

router = APIRouter(prefix="/api/media", tags=["media"])

@router.get("/all", response_model=list[MediaData])
def list_all_media(
    service: MediaService = Depends(deps.get_media_service)
):
    """
    List all media in the system.
    Does not require authentication.
    """
    return service.list_all_media()

@router.post("/", response_model=MediaData, status_code=status.HTTP_201_CREATED)
def upload_media(
    payload: MediaInput,
    service: MediaService = Depends(deps.get_media_service),
    # Richiediamo l'utente loggato per sicurezza (anche se non usiamo owner_id direttamente qui, 
    # serve per proteggere l'endpoint da utenti anonimi)
    current_user: User = Depends(deps.get_current_user) 
):
    """
    Upload a media file (Base64) and link it directly to a Property OR a Room.
    Payload must contain either propertyId OR roomId.
    """
    
    # VALIDAZIONE: Il media deve appartenere a qualcuno!
    if not payload.property_id and not payload.room_id:
        raise HTTPException(
            status_code=400, 
            detail="Media must be associated with either a Property or a Room."
        )

    # Se arrivano entrambi (caso raro), potresti voler dare priorità o errore.
    # diamo errore.
    if payload.property_id and payload.room_id:
        raise HTTPException(
            status_code=400, 
            detail="Media cannot be associated with both Property and Room simultaneously."
        )
        
    return service.upload_media(payload)

@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    media_id: str,
    service: MediaService = Depends(deps.get_media_service),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete media from Storage and DB.
    """
    service.delete_media(media_id)
    return None

@router.get("/{media_id}", response_model=MediaData)
def get_media(
    media_id: str,
    service: MediaService = Depends(deps.get_media_service)
):
    """
    Fetch media details by ID.
    Does not require authentication.
    """
    media = service.get_media_by_id(media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media

@router.get("/property/{property_id}", response_model=list[MediaData])
def list_media_by_property(
    property_id: str,
    service: MediaService = Depends(deps.get_media_service)
):
    """
    List all media linked to a specific Property.
    Does not require authentication.
    """
    return service.list_media_by_property(property_id)

@router.get("/room/{room_id}", response_model=list[MediaData])
def list_media_by_room(
    room_id: str,
    service: MediaService = Depends(deps.get_media_service)
):
    """
    List all media linked to a specific Room.
    Does not require authentication.
    """
    return service.list_media_by_room(room_id)

