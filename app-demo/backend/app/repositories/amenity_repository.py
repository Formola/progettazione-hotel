from abc import ABC, abstractmethod
from ast import List
from typing import List, Optional
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
            # INSERT
            model = models.PropertyAmenityModel(
                id=entity.id,
                name=entity.name,
                category=entity.category,
                description=entity.description,
                is_global=entity.is_global
                # NOTA: Qui NON salviamo custom_description, perché questa è la tabella del dominio, non il link
            )
            self.db.add(model)
        else:
            # UPDATE (Aggiorniamo i dati del catalogo se sono cambiati)
            model.name = entity.name
            model.category = entity.category
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
            description=model.description,
            is_global=model.is_global
        )
        
    def get_by_name(self, name: str) -> Optional[entities.PropertyAmenity]:
        model = (
            self.db.query(models.PropertyAmenityModel)
            .filter(models.PropertyAmenityModel.name.ilike(name))
            .first()
        )
        if not model:
            return None
        return entities.PropertyAmenity(
            id=model.id,
            name=model.name,
            category=model.category,
            description=model.description,
            is_global=model.is_global
        )
        
    # fetch all global amenities (for dropdowns, etc.)
    def get_all(self) -> List[entities.PropertyAmenity]:
        # Filtra per is_global == True
        models_list = (
            self.db.query(models.PropertyAmenityModel)
            .filter(models.PropertyAmenityModel.is_global == True) 
            .all()
        )
        
        return [
            entities.PropertyAmenity(
                id=m.id,
                name=m.name,
                category=m.category,
                description=m.description,
                is_global=m.is_global
            ) for m in models_list
        ]

class RoomAmenityRepository(AmenityRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, entity: entities.RoomAmenity) -> entities.RoomAmenity:
        model = self.db.query(models.RoomAmenityModel).get(entity.id)
        
        if not model:
            # INSERT
            model = models.RoomAmenityModel(
                id=entity.id,
                name=entity.name,
                category=entity.category,
                description=entity.description,
                is_global=entity.is_global
            )
            self.db.add(model)
        else:
            model.name = entity.name
            model.category = entity.category
            model.description = entity.description
            
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
            description=model.description,
            is_global=model.is_global
        )
    
    def get_by_name(self, name: str) -> Optional[entities.RoomAmenity]:
        model = (
            self.db.query(models.RoomAmenityModel)
            .filter(models.RoomAmenityModel.name.ilike(name))
            .first()
        )
        if not model:
            return None
        return entities.RoomAmenity(
            id=model.id,
            name=model.name,
            category=model.category,
            description=model.description,
            is_global=model.is_global
        )
        
    # fetch all global amenities (for dropdowns, etc.)
    def get_all(self) -> List[entities.RoomAmenity]:
        # Filtra per is_global == True
        models_list = (
            self.db.query(models.RoomAmenityModel)
            .filter(models.RoomAmenityModel.is_global == True) 
            .all()
        )
        
        return [
            entities.RoomAmenity(
                id=m.id,
                name=m.name,
                category=m.category,
                description=m.description,
                is_global=m.is_global
            ) for m in models_list
        ]