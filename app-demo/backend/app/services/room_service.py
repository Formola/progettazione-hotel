# app/services/room_service.py
import uuid
from fastapi import HTTPException
from app.domain import entities
from app.repositories.room_repository import RoomRepository
from app.repositories.property_repository import PropertyRepository
from app.repositories.media_repository import MediaRepository
from app.schemas import NewAmenityInput, RoomInput
from app.domain.factories import RoomAmenityFactory
from app.repositories.amenity_repository import RoomAmenityRepository

class RoomService:
    def __init__(
        self, 
        room_repo: RoomRepository, 
        property_repo: PropertyRepository,
        media_repo: MediaRepository,
        room_amenity_factory: RoomAmenityFactory,
        amenity_repo: RoomAmenityRepository
    ):
        self.room_repo = room_repo
        self.property_repo = property_repo
        self.media_repo = media_repo
        self.room_amenity_factory = room_amenity_factory
        self.amenity_repo = amenity_repo
        
    def add_room(self, property_id: str, data: RoomInput, owner: entities.User) -> entities.Room:
        # Recupero Property (Serve per validazione logica)
        prop = self.property_repo.get_by_id(property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Security Check (Solo l'owner può aggiungere stanze)
        if not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        final_amenities = []
        
        # Amenity Esistenti
        for item in data.amenities:
            # Creiamo l'entità usando l'ID
            amenity_entity = self.room_amenity_factory.create_amenity(id=item.id)
            
            # Assegniamo la descrizione custom se presente
            if item.custom_description:
                amenity_entity.custom_description = item.custom_description
                
            final_amenities.append(amenity_entity)
            
        # Nuove
        for new_data in data.new_amenities:
            new_entity = self.room_amenity_factory.create_amenity(
                id=str(uuid.uuid4()),
                name=new_data.name,
                category=new_data.category
            )
            # Salvataggio persistente della nuova amenity
            self.amenity_repo.save(new_entity)
            final_amenities.append(new_entity)
        
        # Recupero Media Esistenti
        room_media = []
        for mid in data.media_ids:
            m = self.media_repo.get_by_id(mid)
            if m: 
                room_media.append(m)

        # Creazione Entità Stanza
        new_room = entities.Room(
            id=str(uuid.uuid4()),
            property_id=property_id,
            type=entities.RoomType(data.type),
            price=data.price,
            capacity=data.capacity,
            description=data.description,
            amenities=final_amenities,
            media=room_media
        )

        # DOMAIN CHECK: Usiamo la logica della Property!
        # La classe Property decide se la stanza può essere aggiunta (es. stato != INACTIVE)
        try:
            prop.add_room(new_room) 
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return self.room_repo.save(new_room)
    
    def get_room(self, room_id: str) -> entities.Room:
        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room
    
    def get_rooms_by_property_id(self, property_id: str) -> list[entities.Room]:
        return self.room_repo.get_by_property_id(property_id)
    
    def delete_room(self, room_id: str, owner: entities.User):
        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        prop = self.property_repo.get_by_id(room.property_id)
        if not prop or not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        self.room_repo.delete(room_id)
        
    def update_room(self, room_id: str, data: RoomInput, owner: entities.User) -> entities.Room:
        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        prop = self.property_repo.get_by_id(room.property_id)
        if not prop or not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Aggiorna i campi della stanza
        room.type = entities.RoomType(data.type)
        room.price = data.price
        room.capacity = data.capacity
        room.description = data.description

        # Aggiorna Amenities
        updated_amenities = []
        for item in data.amenities:
            amenity_entity = self.room_amenity_factory.create_amenity(id=item.id)
            if item.custom_description:
                amenity_entity.custom_description = item.custom_description
            updated_amenities.append(amenity_entity)
            
        room.amenities = updated_amenities

        # Aggiorna Media
        room.media = []
        for mid in data.media_ids:
            m = self.media_repo.get_by_id(mid)
            if m: 
                room.media.append(m)

        return self.room_repo.save(room)
    
    # intendiamo creazione di una nuova amenity e collegamento alla stanza
    def add_new_amenity(self, room_id: str, data: NewAmenityInput):
        room = self.room_repo.get_by_id(room_id)

        # CERCA SE ESISTE GIÀ (Case insensitive per sicurezza)
        existing_amenity = self.amenity_repo.get_by_name(data.name)

        if existing_amenity:
            target_amenity = existing_amenity
            
            
        else:
            # SE NON ESISTE, CREALA
            target_amenity = self.room_amenity_factory.create_amenity(
                id=str(uuid.uuid4()),
                name=data.name,
                category=data.category
            )
            self.amenity_repo.save(target_amenity)

        # COLLEGA CON DESCRIZIONE CUSTOM
        # Qui il metodo add_amenity della Room deve accettare anche la descrizione
        room.add_amenity(target_amenity, custom_description=data.description)
        
        return self.room_repo.save(room)
    
    def remove_room_amenity(self, room_id: str, amenity_id: str, owner: entities.User) -> entities.Room:
        # Recuperi
        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        prop = self.property_repo.get_by_id(room.property_id)
        if not prop or not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # DOMAIN LOGIC
        room.remove_amenity(amenity_id)
        
        # SAVE
        return self.room_repo.save(room)