from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

class PropertyStatus(str, Enum):
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'
    INACTIVE = 'INACTIVE'

class RoomType(str, Enum):
    SINGLE = 'SINGLE' 
    DOUBLE = 'DOUBLE'
    SUITE = 'SUITE'

class MediaType(str, Enum):
    IMAGE = 'IMAGE'
    VIDEO = 'VIDEO'

class UserRole(str, Enum):
    GUEST = 'GUEST'
    OWNER = 'OWNER'
    ADMIN = 'ADMIN'

## USER

@dataclass
class User:
    id: str
    name: str
    email: str
    cognito_uuid: str
    


## AMENITIES

class IAmenity(ABC):
    """
    Interfaccia base per tutti i servizi (Product Interface).
    In Python usiamo ABC per simulare le interfacce pure.
    """
    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def getCategory(self) -> str:
        pass
    
    @abstractmethod
    def getDescription(self) -> str:
        pass

@dataclass
class PropertyAmenity(IAmenity):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    
    # --- IMPLEMENTAZIONE METODI ASTRATTI ---
    def getName(self) -> str:
        return self.name

    def getCategory(self) -> str:
        return self.category
    
    def getDescription(self) -> str:
        return self.description or ""

@dataclass
class RoomAmenity(IAmenity):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    
    # --- IMPLEMENTAZIONE METODI ASTRATTI ---
    def getName(self) -> str:
        return self.name

    def getCategory(self) -> str:
        return self.category
    
    def getDescription(self) -> str:
        return self.description or ""
    
## MEDIA

@dataclass
class Media:
    id: str
    file_name: str
    storage_path: str
    description: Optional[str] = None
    file_type: Optional[str] = None
    # Nota: property_id e room_id sono impliciti nella struttura gerarchica


## ROOM

@dataclass
class Room:
    id: str
    type: RoomType
    price: float
    capacity: int
    property_id: str
    description: Optional[str] = None
    is_available: bool = True
    
    amenities: List[RoomAmenity] = field(default_factory=list)
    media: List[Media] = field(default_factory=list)

    def add_amenity(self, amenity: RoomAmenity):
        # Type Check opzionale ma utile nel dominio
        if not isinstance(amenity, RoomAmenity):
            raise TypeError("Can only add RoomAmenity to a Room")
            
        # Evita duplicati (logica di dominio)
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    def update_price(self, new_price: float):
        if new_price <= 0:
            raise ValueError("Price must be positive")
        self.price = new_price


## PROPERTY

@dataclass
class Property:
    id: str
    name: str
    description: str
    address: str
    city: str
    country: str
    
    
    owner_id: Optional[str] = None
    owner: Optional[User] = None
    
    status: PropertyStatus = PropertyStatus.DRAFT
    
    rooms: List[Room] = field(default_factory=list)
    amenities: List[PropertyAmenity] = field(default_factory=list)
    media: List[Media] = field(default_factory=list)
    
    def __post_init__(self):
        # Se mi passi l'oggetto owner, mi prendo l'ID da lì
        if self.owner:
            self.owner_id = self.owner.id
        # Se non c'è owner, owner_id deve essere stato impostato.
        elif not hasattr(self, 'owner_id'):
             raise ValueError("Property must have either owner object or owner_id")

    def can_be_published(self) -> bool:
        """
        Regola: Per pubblicare servono almeno 1 stanza.
        """
        has_rooms = len(self.rooms) > 0
        return has_rooms

    def publish(self):
        """
        Transizione di stato: DRAFT -> PUBLISHED
        """
        if self.status == PropertyStatus.PUBLISHED:
            return 

        if not self.can_be_published():
            # Questo errore verrà catturato dal Service e trasformato in HTTP 400
            raise ValueError("Cannot publish property without rooms or media.")
        
        self.status = PropertyStatus.PUBLISHED

    def unpublish(self):
        self.status = PropertyStatus.INACTIVE

    def add_room(self, room: Room):
        if self.status == PropertyStatus.INACTIVE:
             raise ValueError("Cannot add rooms to inactive property")
        self.rooms.append(room)
        
    def remove_room(self, room_id: str):
        # Filtra la lista rimuovendo la stanza con quell'ID
        self.rooms = [r for r in self.rooms if r.id != room_id]

    def add_amenity(self, amenity: PropertyAmenity):
        if not isinstance(amenity, PropertyAmenity):
            raise TypeError("Can only add PropertyAmenity to a Property")
            
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    def is_owned_by(self, user_id: str) -> bool:
        return self.owner_id == user_id