from app.domain import entities
from app.models import models

# ==========================================
# AMENITIES MAPPERS
# ==========================================

def to_domain_property_amenity(model: models.PropertyAmenityModel) -> entities.PropertyAmenity:
    return entities.PropertyAmenity(
        id=model.id,
        name=model.name,
        category=model.category,
        description=model.description
    )

def to_domain_room_amenity(model: models.RoomAmenityModel) -> entities.RoomAmenity:
    return entities.RoomAmenity(
        id=model.id,
        name=model.name,
        category=model.category,
        description=model.description
    )

# ==========================================
# MEDIA MAPPERS
# ==========================================

def to_domain_media(model: models.MediaModel) -> entities.Media:
    return entities.Media(
        id=model.id,
        file_name=model.file_name,
        storage_path=model.storage_path,
        description=model.description,
        file_type=model.file_type
    )

# ==========================================
# USER MAPPERS
# ==========================================

def to_domain_user(model: models.UserModel) -> entities.User:
    if not model:
        return None
    return entities.User(
        id=model.id,
        name=model.name,
        email=model.email,
        cognito_uuid=model.cognito_uuid
    )

# ==========================================
# ROOM MAPPERS
# ==========================================

def to_domain_room(model: models.RoomModel) -> entities.Room:
    return entities.Room(
        id=model.id,
        property_id=model.property_id,
        type=entities.RoomType(model.type),
        price=model.price,
        capacity=model.capacity,
        description=model.description,
        is_available=model.is_available,
        media=[to_domain_media(m) for m in model.media],
        amenities=[to_domain_room_amenity(a) for a in model.amenities]
    )

def to_model_room(entity: entities.Room) -> models.RoomModel:
    # Nota: NON mappiamo media e amenities qui dentro per il save.
    # Le gestiremo esplicitamente nel repository per fare il "diffing".
    return models.RoomModel(
        id=entity.id,
        property_id=entity.property_id,
        type=entity.type.value,
        price=entity.price,
        capacity=entity.capacity,
        description=entity.description,
        is_available=entity.is_available
    )

# ==========================================
# PROPERTY MAPPERS
# ==========================================

def to_domain_property(model: models.PropertyModel) -> entities.Property:
    return entities.Property(
        id=model.id,
        # Qui passiamo l'ID perché viene dal DB
        owner_id=model.owner_id, 
        
        name=model.name,
        address=model.address,
        city=model.city,
        country=model.country,
        description=model.description,
        status=entities.PropertyStatus(model.status),
        
        rooms=[to_domain_room(r) for r in model.rooms],
        amenities=[to_domain_property_amenity(a) for a in model.amenities],
        media=[to_domain_media(m) for m in model.media],
        
        # Qui passiamo l'Owner se SQLAlchemy lo ha caricato, altrimenti None
        owner=to_domain_user(model.owner) 
    )

def to_model_property(entity: entities.Property) -> models.PropertyModel:
    return models.PropertyModel(
        id=entity.id,
        owner_id=entity.owner_id,
        name=entity.name,
        address=entity.address,
        city=entity.city,
        country=entity.country,
        description=entity.description,
        status=entity.status.value # Enum -> String
    )
    
def to_domain_media(model: models.MediaModel) -> entities.Media:
    return entities.Media(
        id=model.id,
        file_name=model.file_name,
        storage_path=model.storage_path,
        description=model.description,
        file_type=model.file_type
    )

def to_model_media(entity: entities.Media, property_id: str = None, room_id: str = None) -> models.MediaModel:
    return models.MediaModel(
        id=entity.id,
        file_name=entity.file_name,
        file_type=entity.file_type,
        storage_path=entity.storage_path,
        description=entity.description,
        property_id=property_id,
        room_id=room_id
    )