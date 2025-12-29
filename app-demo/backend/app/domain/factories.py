# app/domain/factories.py
from abc import ABC, abstractmethod
from app.domain import entities

# ABSTRACT CREATOR
class AmenityFactory(ABC):
    
    @abstractmethod
    def create_amenity(self, id: str, name: str = "", category: str = "", description: str = "") -> entities.IAmenity:
        """Metodo astratto che le sottoclassi devono implementare"""
        pass

# CONCRETE CREATORS

class PropertyAmenityFactory(AmenityFactory):
    
    def create_amenity(self, id: str, name: str = "", category: str = "", description: str = "") -> entities.PropertyAmenity:

        return entities.PropertyAmenity(
            id=id,
            name=name,
            category=category,
            description=description
        )

class RoomAmenityFactory(AmenityFactory):
    def create_amenity(self, id: str, name: str = "", category: str = "", description: str = "") -> entities.RoomAmenity:
        return entities.RoomAmenity(
            id=id,
            name=name,
            category=category,
            description=description
        )