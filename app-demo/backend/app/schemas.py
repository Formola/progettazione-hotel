from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum
from datetime import date
from app.domain.entities import PropertyStatus, RoomType, MediaType

# ==========================================
# MEDIA
# ==========================================
class MediaInput(BaseModel):
    file_name: str = Field(alias="fileName")
    file_type: MediaType = Field(alias="fileType")
    base_64_data: str = Field(alias="base64Data")
    description: Optional[str] = None
    
class MediaOutput(BaseModel):
    id: str
    file_name: str
    storage_path: str
    description: Optional[str] = None
    file_type: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

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
    
class AmenityOutput(Amenity):
    custom_description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
class NewAmenityInput(BaseModel):
    name: str
    category: str
    description: Optional[str] = None

class AmenityLinkInput(BaseModel):
    id: str
    custom_description: Optional[str] = None
    
# ==========================================
# ROOMS
# ==========================================
class _RoomBase(BaseModel):
    type: RoomType
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    capacity: int = Field(..., gt=0)

class RoomInput(_RoomBase):
    amenities: List[AmenityLinkInput] = []
    new_amenities: List[NewAmenityInput] = []
    media_ids: List[str] = [] 

class RoomData(_RoomBase):
    id: str
    amenities: List[AmenityOutput] = [] 
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
    amenities: List[AmenityLinkInput] = []
    new_amenities: List[NewAmenityInput] = []
    media_ids: List[str] = []

class PropertyData(_PropertyBase):
    id: str
    status: PropertyStatus
    owner_id: str
    
    amenities: List[AmenityOutput] = [] 
    rooms: List[RoomData] = []
    media: List[MediaData] = []

    model_config = ConfigDict(from_attributes=True)

class OwnerSummary(BaseModel):
    id: str
    name: str
    email: str

class PropertySearchResponse(_PropertyBase):
    id: str
    status: PropertyStatus
    owner: OwnerSummary 
    
    amenities: List[AmenityOutput] = [] 
    rooms: List[RoomData] = []
    media: List[MediaData] = []

    model_config = ConfigDict(from_attributes=True)