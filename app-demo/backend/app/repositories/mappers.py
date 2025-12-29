from app.domain import entities
from app.models import models
from app.domain.entities import RoomType

# Room Type Parsing with Aliases

ROOM_TYPE_SYNONYMS = {
    RoomType.SINGLE: ["single", "singola", "1", "uno", "sola"],
    RoomType.DOUBLE: ["double", "doppia", "2", "due", "coppia"],
    RoomType.SUITE:  ["suite", "junior suite", "senior suite", "presidential suite"]
}

def build_room_type_aliases():
    aliases = {}
    for room_type, values in ROOM_TYPE_SYNONYMS.items():
        for v in values:
            aliases[v.lower()] = room_type
    return aliases


ROOM_TYPE_ALIASES = build_room_type_aliases()

def parse_room_type(value: str) -> RoomType:
    if not value:
        raise ValueError("Room type is required")

    key = value.strip().lower()

    try:
        return ROOM_TYPE_ALIASES[key]
    except KeyError:
        raise ValueError(f"Invalid room type: {value}")


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
    if not model:
        return None
    
    # MAPPING AMENITIES
    # Iteriamo sui LINK, non direttamente sulle amenities
    domain_amenities = []
    for link in model.amenity_links:
        # link.amenity è l'oggetto RoomAmenityModel (catalogo)
        # link.custom_description è il testo personalizzato nella tabella link
        domain_amenities.append(
            entities.RoomAmenity(
                id=link.amenity.id,
                name=link.amenity.name,
                category=link.amenity.category,
                description=link.amenity.description,
                custom_description=link.custom_description
            )
        )

    # MAPPING MEDIA
    domain_media = [to_domain_media(m) for m in model.media]

    return entities.Room(
        id=model.id,
        property_id=model.property_id,
        type=parse_room_type(model.type),
        price=model.price,
        capacity=model.capacity,
        description=model.description,
        is_available=model.is_available,
        amenities=domain_amenities,
        media=domain_media
    )

def to_model_room(entity: entities.Room) -> models.RoomModel:
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
    if not model:
        return None

    # MAPPING AMENITIES (CORRETTO PER ASSOCIATION OBJECT)
    domain_amenities = []
    if model.amenity_links: # Iteriamo sui LINK, non su model.amenities
        for link in model.amenity_links:
            domain_amenities.append(
                entities.PropertyAmenity(
                    id=link.amenity.id,
                    name=link.amenity.name,
                    category=link.amenity.category,
                    description=link.amenity.description,
                    custom_description=link.custom_description # Campo Custom
                )
            )

    return entities.Property(
        id=model.id,
        owner_id=model.owner_id,
        name=model.name,
        address=model.address,
        city=model.city,
        country=model.country,
        description=model.description,
        status=entities.PropertyStatus(model.status) if model.status else entities.PropertyStatus.DRAFT,
        
        rooms=[to_domain_room(r) for r in model.rooms],
        amenities=domain_amenities,
        media=[to_domain_media(m) for m in model.media],
        
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
        status=entity.status.value
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