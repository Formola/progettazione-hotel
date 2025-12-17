from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import date

# ==========================================
# ENUMS
# ==========================================
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

# ==========================================
# MEDIA
# ==========================================
class MediaInput(BaseModel):  # Payload Upload
    fileName: str
    fileType: MediaType
    base64Data: str
    description: Optional[str] = None

class MediaData(BaseModel):   # Visualizzazione
    id: str
    url: str
    type: MediaType
    description: Optional[str] = None

    class Config:
        from_attributes = True

# ==========================================
# AMENITIES
# ==========================================
class Amenity(BaseModel): 
    id: str
    name: str
    category: str
    icon: Optional[str] = None

    class Config:
        from_attributes = True

# ==========================================
# ROOMS
# ==========================================
# Campi comuni per non ripeterci
class _RoomBase(BaseModel):
    type: RoomType
    description: Optional[str] = None
    price: float
    capacity: int

# INPUT: Aggiunge la lista di ID per la creazione
class RoomInput(_RoomBase):
    amenity_ids: List[str] = []

# OUTPUT: Aggiunge ID, oggetti completi e Media
class RoomData(_RoomBase):
    id: str
    amenities: List[Amenity] = []
    media: List[MediaData] = []

    class Config:
        from_attributes = True

# ==========================================
# PROPERTIES
# ==========================================
# Campi comuni (Nome, Indirizzo...)
class _PropertyBase(BaseModel):
    name: str
    address: str
    city: str
    country: str
    description: str

# INPUT: Quello che l'Owner compila (+ amenity_ids)
class PropertyInput(_PropertyBase):
    amenity_ids: List[str] = []

# OUTPUT: Quello che l'Owner vede (+ oggetti completi, status, id)
class PropertyData(_PropertyBase):
    id: str
    status: PropertyStatus
    owner_id: str
    
    amenities: List[Amenity] = []
    rooms: List[RoomData] = []
    media: List[MediaData] = []

    class Config:
        from_attributes = True

# ==========================================
# SEARCH & USER
# ==========================================
class UserData(BaseModel):
    id: str
    email: str
    role: UserRole

class SearchCriteria(BaseModel):
    location: Optional[str] = None
    minPrice: Optional[float] = None
    maxPrice: Optional[float] = None
    checkIn: Optional[date] = None
    checkOut: Optional[date] = None
    guests: Optional[int] = None