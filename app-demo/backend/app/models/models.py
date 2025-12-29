from sqlalchemy import Column, String, Integer, Text, Boolean, Float, ForeignKey, DateTime, Table, Index, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db import Base

property_amenities_link = Table(
    'property_amenities_link',
    Base.metadata,
    Column('property_id', String, ForeignKey('properties.id', ondelete="CASCADE"), primary_key=True),
    Column('amenity_id', String, ForeignKey('property_amenities.id', ondelete="CASCADE"), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

room_amenities_link = Table(
    'room_amenities_link',
    Base.metadata,
    Column('room_id', String, ForeignKey('rooms.id', ondelete="CASCADE"), primary_key=True),
    Column('amenity_id', String, ForeignKey('room_amenities.id', ondelete="CASCADE"), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

# ==========================================
# MODELLI ORM
# ==========================================

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cognito_uuid = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni
    properties = relationship("PropertyModel", back_populates="owner")


class PropertyAmenityModel(Base):
    __tablename__ = "property_amenities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    
    # Relazione inversa (opzionale, utile per query)
    properties = relationship("PropertyModel", secondary=property_amenities_link, back_populates="amenities")


class RoomAmenityModel(Base):
    __tablename__ = "room_amenities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    
    rooms = relationship("RoomModel", secondary=room_amenities_link, back_populates="amenities")


class PropertyModel(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    country = Column(String)
    description = Column(Text)
    status = Column(String, default="DRAFT") # Mappato poi a Enum nel Domain
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni
    # cascade="all, delete-orphan" per eliminare tutto se la property viene cancellata
    # importante, se si elimina una property, si eliminano anche stanze e media associati
    # oppure se se si rimuove una stanza dalla property, si elimina la stanza stessa e non si lascia orfana, stesso per i media.
    owner = relationship("UserModel", back_populates="properties")
    rooms = relationship("RoomModel", back_populates="property", cascade="all, delete-orphan")
    media = relationship("MediaModel", back_populates="property", cascade="all, delete-orphan")
    amenities = relationship("PropertyAmenityModel", secondary=property_amenities_link, back_populates="properties")

    # Indici (Gin/Trigram per ricerca veloce)
    __table_args__ = (
        Index('idx_properties_city_trgm', 'city', postgresql_using='gin', postgresql_ops={'city': 'gin_trgm_ops'}),
        Index('idx_properties_name_trgm', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),
        Index('idx_properties_status', 'status'),
    )


class RoomModel(Base):
    __tablename__ = "rooms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id = Column(String, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String)
    description = Column(Text)
    price = Column(Float, nullable=False)
    capacity = Column(Integer)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni
    property = relationship("PropertyModel", back_populates="rooms")
    media = relationship("MediaModel", back_populates="room", cascade="all, delete-orphan")
    amenities = relationship("RoomAmenityModel", secondary=room_amenities_link, back_populates="rooms")


class MediaModel(Base):
    __tablename__ = "media"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id = Column(String, ForeignKey("properties.id", ondelete="CASCADE"), nullable=True, index=True)
    room_id = Column(String, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=True)
    
    file_name = Column(String, nullable=False)
    file_type = Column(String)
    storage_path = Column(String, nullable=False)
    description = Column(Text)
    inserted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni
    property = relationship("PropertyModel", back_populates="media")
    room = relationship("RoomModel", back_populates="media")