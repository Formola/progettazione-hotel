from pydantic import BaseModel, Field, ConfigDict
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
    SINGLE = 'Singola' 
    DOUBLE = 'Doppia'
    SUITE = 'Suite'

class MediaType(str, Enum):
    IMAGE = 'IMAGE'
    VIDEO = 'VIDEO'

class UserRole(str, Enum):
    GUEST = 'GUEST'
    OWNER = 'OWNER'
    ADMIN = 'ADMIN'
    
    
class UserContext(BaseModel):
    id: str
    email: Optional[str] = None 
    role: Optional[str] = None

# ==========================================
# MEDIA
# ==========================================
class MediaInput(BaseModel):
    file_name: str = Field(alias="fileName")
    file_type: MediaType = Field(alias="fileType")
    base_64_data: str = Field(alias="base64Data")
    description: Optional[str] = None

class MediaData(BaseModel):
    id: str
    file_name: str
    storage_path: str
    file_type: Optional[str] = None
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) 

# ==========================================
# AMENITIES
# ==========================================
class Amenity(BaseModel): 
    id: str
    name: str
    category: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class NewAmenityInput(BaseModel):
    name: str
    category: str
    description: Optional[str] = None

# ==========================================
# ROOMS
# ==========================================
class _RoomBase(BaseModel):
    type: RoomType
    description: Optional[str] = None
    price: float = Field(..., gt=0) # Validazione: deve essere > 0
    capacity: int = Field(..., gt=0)

class RoomInput(_RoomBase):
    amenity_ids: List[str] = []
    new_amenities: List[NewAmenityInput] = []
    media_ids: List[str] = [] 

class RoomData(_RoomBase):
    id: str
    amenities: List[Amenity] = []
    media: List[MediaData] = []

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# PROPERTIES
# ==========================================
class _PropertyBase(BaseModel):
    name: str
    address: str
    city: str
    country: str
    description: str

class PropertyInput(_PropertyBase):
    amenity_ids: List[str] = []
    new_amenities: List[NewAmenityInput] = []
    media_ids: List[str] = []

class PropertyData(_PropertyBase):
    id: str
    status: PropertyStatus
    owner_id: str
    
    amenities: List[Amenity] = []
    rooms: List[RoomData] = []
    media: List[MediaData] = []

    model_config = ConfigDict(from_attributes=True)

class OwnerSummary(BaseModel):
    id: str
    name: str
    email: str

# Aggiorniamo PropertyData per l'output della ricerca
class PropertySearchResponse(_PropertyBase):
    id: str
    status: PropertyStatus
    # Sostituiamo owner_id con l'oggetto owner completo
    owner: OwnerSummary 
    
    amenities: List[Amenity] = []
    rooms: List[RoomData] = []
    media: List[MediaData] = []

    model_config = ConfigDict(from_attributes=True)