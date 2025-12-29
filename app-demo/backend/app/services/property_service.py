# app/services/property_service.py
import uuid
from typing import List
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

    def create_property(self, data: PropertyInput, owner: entities.User) -> entities.Property:
        final_amenities = []

        # AMENITIES ESISTENTI (Solo ID)
        # Creiamo stub fittizi, il repo PropertyRepository farà il link leggendo l'ID
        for aid in data.amenity_ids:
            # Usiamo la factory anche qui, passando solo l'ID
            stub = self.property_amenity_factory.create_amenity(id=aid)
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
            media=property_media
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

    def get_user_properties(self, owner: entities.User) -> List[entities.Property]:
        return self.property_repo.get_by_owner_id(owner.id)
        
    def get_property(self, property_id: str) -> entities.Property:
        p = self.property_repo.get_by_id(property_id)
        if not p:
            raise HTTPException(status_code=404, detail="Property not found")
        return p