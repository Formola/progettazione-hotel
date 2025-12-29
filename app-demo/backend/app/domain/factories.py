from abc import ABC, abstractmethod
from typing import Optional
from app.domain import entities

# ABSTRACT CREATOR
class AmenityFactory(ABC):
    
    @abstractmethod
    def create_amenity(
        self, 
        id: str, 
        name: str = "", 
        category: str = "", 
        description: str = "",
        custom_description: Optional[str] = None
    ) -> entities.IAmenity:
        
        """
        Abstract method to create an Amenity entity.
        """
        pass

# CONCRETE CREATORS

class PropertyAmenityFactory(AmenityFactory):
    
    def create_amenity(
        self, 
        id: str, 
        name: str = "", 
        category: str = "", 
        description: str = "",
        custom_description: Optional[str] = None
    ) -> entities.PropertyAmenity:

        return entities.PropertyAmenity(
            id=id,
            name=name,
            category=category,
            description=description,
            custom_description=custom_description 
        )

class RoomAmenityFactory(AmenityFactory):
    
    def create_amenity(
        self, 
        id: str, 
        name: str = "", 
        category: str = "", 
        description: str = "",
        custom_description: Optional[str] = None
    ) -> entities.RoomAmenity:
        
        return entities.RoomAmenity(
            id=id,
            name=name,
            category=category,
            description=description,
            custom_description=custom_description
        )