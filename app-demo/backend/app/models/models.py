from sqlalchemy import Column, String, Integer, Text, Boolean, Float, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import relationship
import uuid
from app.db import Base

# ==========================================
# ASSOCIATION MODELS (Tabelle di Link come Classi)
# ==========================================

class PropertyAmenityLinkModel(Base):
    __tablename__ = 'property_amenities_link'
    
    # Chiavi Esterne
    property_id = Column(String, ForeignKey('properties.id', ondelete="CASCADE"), primary_key=True)
    amenity_id = Column(String, ForeignKey('property_amenities.id', ondelete="CASCADE"), primary_key=True)
    
    # Campi Extra
    custom_description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni (Many-to-One verso i genitori)
    property = relationship("PropertyModel", back_populates="amenity_links")
    amenity = relationship("PropertyAmenityModel") # Accesso diretto all'amenity dal link


class RoomAmenityLinkModel(Base):
    __tablename__ = 'room_amenities_link'

    # Chiavi Esterne
    room_id = Column(String, ForeignKey('rooms.id', ondelete="CASCADE"), primary_key=True)
    amenity_id = Column(String, ForeignKey('room_amenities.id', ondelete="CASCADE"), primary_key=True)
    
    # Campi Extra
    custom_description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni (Many-to-One verso i genitori)
    room = relationship("RoomModel", back_populates="amenity_links")
    amenity = relationship("RoomAmenityModel") # Accesso diretto all'amenity dal link

# ==========================================
# MODELLI ORM PRINCIPALI
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
    category = Column(String)
    description = Column(Text) # Descrizione generica dal catalogo
    is_global = Column(Boolean, default=False) # Indica se è un'amenity globale o personalizzata
    
    # Nota: Non definiamo relationship inverse complesse qui per evitare cicli,
    # se serve trovare le property che hanno questa amenity, si fa via query sul LinkModel.


class RoomAmenityModel(Base):
    __tablename__ = "room_amenities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(Text) # Descrizione generica dal catalogo
    is_global = Column(Boolean, default=False) # Indica se è un'amenity globale o personalizzata


class PropertyModel(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    country = Column(String)
    description = Column(Text)
    status = Column(String, default="DRAFT") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni
    owner = relationship("UserModel", back_populates="properties")
    rooms = relationship("RoomModel", back_populates="property", cascade="all, delete-orphan")
    media = relationship("MediaModel", back_populates="property", cascade="all, delete-orphan")
    
    # MODIFICA IMPORTANTE: Relazione verso il LINK, non direttamente alle amenities
    amenity_links = relationship("PropertyAmenityLinkModel", back_populates="property", cascade="all, delete-orphan")

    # Indici
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
    
    # se una stanza viene cancellata, i media associati devono essere cancellati
    media = relationship("MediaModel", back_populates="room", cascade="all, delete-orphan")
    
    # MODIFICA IMPORTANTE: Relazione verso il LINK
    amenity_links = relationship("RoomAmenityLinkModel", back_populates="room", cascade="all, delete-orphan")


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