from abc import ABC, abstractmethod
from typing import Optional
from app.domain import entities

# ABSTRACT CREATOR

# <<creator>>
class AmenityFactory(ABC):
    
    @abstractmethod
    def create_amenity(
        self, 
        id: str, 
        name: str = "", 
        category: str = "", 
        description: str = "",
        custom_description: Optional[str] = None,
        is_global: bool = False
    ) -> entities.IAmenity:
        
        """
        Abstract method to create an Amenity entity.
        """
        pass

# CONCRETE CREATORS

# <<concrete creator>>
class PropertyAmenityFactory(AmenityFactory):
    
    def create_amenity(
        self, 
        id: str, 
        name: str = "", 
        category: str = "", 
        description: str = "",
        custom_description: Optional[str] = None,
        is_global: bool = False
    ) -> entities.IAmenity:

        return entities.PropertyAmenity(
            id=id,
            name=name,
            category=category,
            description=description,
            custom_description=custom_description,
            is_global=is_global
        )

# <<concrete creator>>
class RoomAmenityFactory(AmenityFactory):
    
    def create_amenity(
        self, 
        id: str, 
        name: str = "", 
        category: str = "", 
        description: str = "",
        custom_description: Optional[str] = None,
        is_global: bool = False
    ) -> entities.IAmenity:
        
        return entities.RoomAmenity(
            id=id,
            name=name,
            category=category,
            description=description,
            custom_description=custom_description,
            is_global=is_global
        )