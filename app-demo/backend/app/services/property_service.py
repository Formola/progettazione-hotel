# app/services/property_service.py
import uuid
from typing import List, Optional
from fastapi import HTTPException

from app.domain import entities
from app.repositories.property_repository import PropertyRepository
from app.schemas import PropertyInput
from app.domain.factories import PropertyAmenityFactory
from app.repositories.media_repository import MediaRepository
from app.repositories.amenity_repository import PropertyAmenityRepository

class PropertyService:
    def __init__(
        self,
        property_repo: PropertyRepository,
        property_amenity_factory: PropertyAmenityFactory,
        amenity_repo: PropertyAmenityRepository,
        media_repo: MediaRepository
    ):
        self.property_repo = property_repo
        self.property_amenity_factory = property_amenity_factory
        self.amenity_repo = amenity_repo
        self.media_repo = media_repo
        
    # mettiamo sia owner che owner_id per aiutarci nel test da /docs con fastapi.
    def get_user_properties(self, owner: Optional[entities.User], owner_id: Optional[str] = None) -> List[entities.Property]:
        if owner:
            return self.property_repo.get_by_owner_id(owner.id)
        elif owner_id:
            return self.property_repo.get_by_owner_id(owner_id)
        else:
            return []
        
    def get_property_by_id(self, property_id: str) -> entities.Property:
        p = self.property_repo.get_by_id(property_id)
        if not p:
            raise HTTPException(status_code=404, detail="Property not found")
        return p

    def create_property(self, data: PropertyInput, owner: entities.User) -> entities.Property:
        final_amenities = []

        # AMENITIES ESISTENTI (Solo ID)
        for item in data.amenities:
            stub = self.property_amenity_factory.create_amenity(id=item.id)
            if item.custom_description:
                stub.custom_description = item.custom_description
            final_amenities.append(stub)

        # NUOVE AMENITIES (Name + Category)
        for new_data in data.new_amenities:
            # Creiamo l'Entity completa con la Factory
            new_entity = self.property_amenity_factory.create_amenity(
                id=str(uuid.uuid4()), # Generiamo nuovo uuid, non testuale tipo pa_wifi ecc/
                name=new_data.name,
                category=new_data.category
            )
            new_entity.description = new_data.description # Assegnazione diretta opzionale

            # La salviamo nel DB subito!
            # Questo è cruciale: se non la salviamo, il PropertyRepository fallirà 
            # quando cercherà di fare il link (Foreign Key error o skip)
            self.amenity_repo.save(new_entity)
            
            # La aggiungiamo alla lista finale
            final_amenities.append(new_entity)

        # Media
        property_media = []
        for mid in data.media_ids:
            m = self.media_repo.get_by_id(mid)
            if m: property_media.append(m)

        # Creazione Property
        new_property = entities.Property(
            id=str(uuid.uuid4()),
            owner=owner,
            name=data.name,
            address=data.address,
            city=data.city,
            country=data.country,
            description=data.description,
            status=entities.PropertyStatus.DRAFT,
            amenities=final_amenities, # Contiene sia vecchie che nuove
            media=property_media,
            
            
        )
        
        return self.property_repo.save(new_property)

    def publish_property(self, property_id: str, owner: entities.User) -> entities.Property:
        # Recupero
        prop = self.property_repo.get_by_id(property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        # Security
        if not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Domain Logic
        try:
            # Qui scatta la regola: serve almeno 1 stanza
            prop.publish() 
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Save
        return self.property_repo.save(prop)
    
    def unpublish_property(self, property_id: str, owner: entities.User) -> entities.Property:
        prop = self.property_repo.get_by_id(property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        if not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        prop.unpublish()

        return self.property_repo.save(prop)
    
    def archive_property(self, property_id: str, owner: entities.User) -> entities.Property:
        prop = self.property_repo.get_by_id(property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        if not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        prop.archive()

        return self.property_repo.save(prop)

    def delete_property(self, property_id: str, owner: entities.User) -> None:
        prop = self.property_repo.get_by_id(property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        # Security Check
        if not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        self.property_repo.delete(prop.id)
        
    def update_property(self, property_id: str, data: PropertyInput, owner: entities.User) -> entities.Property:
        prop = self.property_repo.get_by_id(property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        # Security Check
        if not prop.is_owned_by(owner.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Aggiorniamo i campi semplici
        prop.name = data.name
        prop.address = data.address
        prop.city = data.city
        prop.country = data.country
        prop.description = data.description

        # AMENITIES ESISTENTI (Solo ID)
        final_amenities = []
        for item in data.amenities:
            stub = self.property_amenity_factory.create_amenity(id=item.id)
            if item.custom_description:
                stub.custom_description = item.custom_description
            final_amenities.append(stub)

        # NUOVE AMENITIES (Name + Category)
        for new_data in data.new_amenities:
            new_entity = self.property_amenity_factory.create_amenity(
                id=str(uuid.uuid4()),
                name=new_data.name,
                category=new_data.category
            )
            new_entity.description = new_data.description

            self.amenity_repo.save(new_entity)
            final_amenities.append(new_entity)

        prop.amenities = final_amenities

        # Media
        property_media = []
        for mid in data.media_ids:
            m = self.media_repo.get_by_id(mid)
            if m: property_media.append(m)
        
        prop.media = property_media

        return self.property_repo.save(prop)
    
    