# app/repositories/amenity_repository.py
from abc import ABC, abstractmethod
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.domain import entities
from app.models import models

class AmenityRepository(ABC):
    @abstractmethod
    def save(self, entity: entities.IAmenity) -> entities.IAmenity:
        pass
    
    @abstractmethod
    def delete(self, amenity_id: str):
        pass
    
    @abstractmethod
    def get_by_id(self, amenity_id: str) -> Optional[entities.IAmenity]:
        pass
    

class PropertyAmenityRepository(AmenityRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, entity: entities.PropertyAmenity) -> entities.PropertyAmenity:
        # Check se esiste già (per ID)
        model = self.db.query(models.PropertyAmenityModel).get(entity.id)
        if not model:
            model = models.PropertyAmenityModel(
                id=entity.id,
                name=entity.name,
                category=entity.category,
                description=entity.description
            )
            self.db.add(model)
        else:
            # Update (opzionale, se volessimo modificare amenities esistenti)
            model.name = entity.name
            model.description = entity.description
        
        self.db.commit()
        return entity
    
    def delete(self, amenity_id: str):
        model = self.db.query(models.PropertyAmenityModel).get(amenity_id)
        if model:
            self.db.delete(model)
            self.db.commit()
            
    def get_by_id(self, amenity_id: str) -> Optional[entities.PropertyAmenity]:
        model = self.db.query(models.PropertyAmenityModel).get(amenity_id)
        if not model:
            return None
        return entities.PropertyAmenity(
            id=model.id,
            name=model.name,
            category=model.category,
            description=model.description
        )

class RoomAmenityRepository(AmenityRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, entity: entities.RoomAmenity) -> entities.RoomAmenity:
        model = self.db.query(models.RoomAmenityModel).get(entity.id)
        if not model:
            model = models.RoomAmenityModel(
                id=entity.id,
                name=entity.name,
                category=entity.category,
                description=entity.description
            )
            self.db.add(model)
        self.db.commit()
        return entity
    
    def delete(self, amenity_id: str):
        model = self.db.query(models.RoomAmenityModel).get(amenity_id)
        if model:
            self.db.delete(model)
            self.db.commit()
            
    def get_by_id(self, amenity_id: str) -> Optional[entities.RoomAmenity]:
        model = self.db.query(models.RoomAmenityModel).get(amenity_id)
        if not model:
            return None
        return entities.RoomAmenity(
            id=model.id,
            name=model.name,
            category=model.category,
            description=model.description
        )