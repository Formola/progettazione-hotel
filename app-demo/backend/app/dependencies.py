from fastapi import Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from app.db import get_db
from app.repositories.user_repository import UserRepository
from app.domain import entities
from app.domain.factories import PropertyAmenityFactory, RoomAmenityFactory
from fastapi import Depends, HTTPException
from app.repositories.search_repository import SearchRepository
from app.services.search_service import SearchService
from app.repositories.property_repository import PropertyRepository
from app.services.property_service import PropertyService
from app.repositories.room_repository import RoomRepository
from app.services.room_service import RoomService
from app.repositories.media_repository import MediaRepository
from app.services.media_service import MediaService
from app.repositories.amenity_repository import PropertyAmenityRepository, RoomAmenityRepository


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

# DEPENDENCY PER GLI OWNER (STRICT)
# Da usare per rotte protette: Create Property, Add Room, Publish, etc.
def get_or_create_user_from_headers(
    x_user_cognito_sub: str,
    x_user_email: Optional[str],
    user_repo: UserRepository
) -> entities.User:
    user = user_repo.get_by_cognito_id(x_user_cognito_sub)

    if not user:
        name_fallback = x_user_email.split("@")[0] if x_user_email else "user"
        user = user_repo.create_from_cognito(
            cognito_uuid=x_user_cognito_sub,
            email=x_user_email,
            name=name_fallback
        )

    return user


def get_current_user(
    x_user_cognito_sub: str = Header(..., alias="x-user-cognito-sub"),
    x_user_email: Optional[str] = Header(..., alias="x-user-email"),
    x_user_role: Optional[str] = Header(..., alias="x-user-role"),
    user_repo: UserRepository = Depends(get_user_repo)
) -> entities.User:

    if x_user_role != "OWNER":
        raise HTTPException(403, "Owners only")

    return get_or_create_user_from_headers(
        x_user_cognito_sub,
        x_user_email,
        user_repo
    )


def get_optional_user(
    x_user_cognito_sub: Optional[str] = Header(None, alias="x-user-cognito-sub"),
    x_user_email: Optional[str] = Header(None, alias="x-user-email"),
    user_repo: UserRepository = Depends(get_user_repo)
) -> Optional[entities.User]:

    if not x_user_cognito_sub:
        return None

    return get_or_create_user_from_headers(
        x_user_cognito_sub,
        x_user_email,
        user_repo
    )

# DEPS SERVICE E REPOSITORY

## SEARCH

def get_search_repo(db: Session = Depends(get_db)) -> SearchRepository:
    return SearchRepository(db)

def get_search_service(
    search_repo: SearchRepository = Depends(get_search_repo)
) -> SearchService:
    return SearchService(search_repo)

## AMENITY

def get_property_amenity_repo(db: Session = Depends(get_db)):
    return PropertyAmenityRepository(db)

def get_room_amenity_repo(db: Session = Depends(get_db)):
    return RoomAmenityRepository(db)


## MEDIA

def get_media_repo(db: Session = Depends(get_db)):
    return MediaRepository(db)

def get_media_service(
    media_repo: MediaRepository = Depends(get_media_repo)
) -> MediaService:
    return MediaService(media_repo)

## PROPERTY

def get_property_repo(db: Session = Depends(get_db)):
    return PropertyRepository(db)

def get_property_amenity_factory() -> PropertyAmenityFactory:
    return PropertyAmenityFactory()

def get_property_service(
    property_repo: PropertyRepository = Depends(get_property_repo),
    property_amenity_factory: PropertyAmenityFactory = Depends(get_property_amenity_factory), 
    amenity_repo: PropertyAmenityRepository = Depends(get_property_amenity_repo),
    media_repo: MediaRepository = Depends(get_media_repo)
) -> PropertyService:
    return PropertyService(property_repo, property_amenity_factory, amenity_repo, media_repo)

## ROOM

def get_room_repo(db: Session = Depends(get_db)):
    return RoomRepository(db)

def get_room_amenity_factory() -> RoomAmenityFactory:
    return RoomAmenityFactory()

def get_room_service(
    room_repo: RoomRepository = Depends(get_room_repo),
    room_amenity_factory: RoomAmenityFactory = Depends(get_room_amenity_factory),
    amenity_repo: RoomAmenityRepository = Depends(get_room_amenity_repo),
    property_repo: PropertyRepository = Depends(get_property_repo),
    media_repo: MediaRepository = Depends(get_media_repo)
) -> RoomService:
    return RoomService(room_repo, room_amenity_factory, amenity_repo, property_repo, media_repo)
