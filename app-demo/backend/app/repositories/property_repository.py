from typing import List, Optional
from sqlalchemy.orm import Session, selectinload, joinedload
from app.domain import entities
from app.models import models
from app.repositories import mappers

class PropertyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, property_id: str) -> Optional[entities.Property]:
        stmt = (
            self.db.query(models.PropertyModel)
            .options(
                # Carica i LINK delle amenities della Property (+ l'amenity collegata)
                selectinload(models.PropertyModel.amenity_links).joinedload(models.PropertyAmenityLinkModel.amenity),
                
                # Carica i media
                selectinload(models.PropertyModel.media),
                
                # Carica le stanze
                selectinload(models.PropertyModel.rooms).options(
                    # Per ogni stanza, carica i LINK delle amenities (+ l'amenity collegata)
                    selectinload(models.RoomModel.amenity_links).joinedload(models.RoomAmenityLinkModel.amenity),
                    # Carica i media della stanza
                    selectinload(models.RoomModel.media)
                )
            )
            .filter(models.PropertyModel.id == property_id)
        )
        
        model = stmt.first()
        return mappers.to_domain_property(model) if model else None
    
    def get_by_owner_id(self, owner_id: str) -> List[entities.Property]:
        stmt = (
            self.db.query(models.PropertyModel)
            .filter(models.PropertyModel.owner_id == owner_id)
            .options(
                # Stessa logica di caricamento del get_by_id
                selectinload(models.PropertyModel.amenity_links).joinedload(models.PropertyAmenityLinkModel.amenity),
                selectinload(models.PropertyModel.media),
                selectinload(models.PropertyModel.rooms).options(
                    selectinload(models.RoomModel.amenity_links).joinedload(models.RoomAmenityLinkModel.amenity),
                    selectinload(models.RoomModel.media)
                )
            )
        )
        
        models_list = stmt.all()
        return [mappers.to_domain_property(m) for m in models_list]
    
    def delete(self, property_id: str):
        model = self.db.query(models.PropertyModel).get(property_id)
        if model:
            self.db.delete(model)
            self.db.commit()

    def save(self, entity: entities.Property) -> entities.Property:
        existing_model = self.db.query(models.PropertyModel).get(entity.id)

        if not existing_model:
            # INSERT
            new_model = mappers.to_model_property(entity)
            
            # Sincronizza Amenities (creando i Link)
            self._sync_amenities(new_model, entity.amenities)
            
            # Sincronizza Stanze (e le loro amenities ricorsivamente)
            self._sync_rooms_insert(new_model, entity.rooms)
            
            self._sync_media_insert(new_model, entity.media)
            
            self.db.add(new_model)
        else:
            # UPDATE
            existing_model.name = entity.name
            existing_model.description = entity.description
            existing_model.address = entity.address
            existing_model.city = entity.city
            existing_model.country = entity.country
            existing_model.status = entity.status.value

            # Sync Amenities (Via Link Table)
            self._sync_amenities(existing_model, entity.amenities)

            # Sync Rooms
            self._sync_rooms_update(existing_model, entity.rooms)

            # Sync Media
            self._sync_media_update(existing_model, entity.media)

        self.db.commit()
        return self.get_by_id(entity.id)

    # =================================================================
    # HELPER PRIVATI DI SINCRONIZZAZIONE (AGGIORNATI)
    # =================================================================

    def _sync_amenities(self, model: models.PropertyModel, amenity_entities: List[entities.PropertyAmenity]):
        """
        AGGIORNATO: Gestisce la relazione Many-to-Many tramite PropertyAmenityLinkModel.
        Salva anche custom_description.
        """
        # Puliamo i link esistenti (cascade farà il delete sul DB)
        model.amenity_links = []

        if not amenity_entities:
            return

        new_links = []
        for a_entity in amenity_entities:
            # Creiamo il LINK esplicitamente
            link = models.PropertyAmenityLinkModel(
                property_id=model.id,
                amenity_id=a_entity.id,
                custom_description=a_entity.custom_description
            )
            new_links.append(link)
        
        model.amenity_links = new_links

    def _sync_room_amenities(self, room_model: models.RoomModel, amenities: List[entities.RoomAmenity]):
        
        room_model.amenity_links = []
        
        if not amenities:
            return

        new_links = []
        for a_entity in amenities:
            link = models.RoomAmenityLinkModel(
                room_id=room_model.id,
                amenity_id=a_entity.id,
                custom_description=a_entity.custom_description
            )
            new_links.append(link)
            
        room_model.amenity_links = new_links

    # --- GLI ALTRI HELPER RIMANGONO SIMILI MA CHIAMANO LE VERSIONI AGGIORNATE ---

    def _sync_rooms_insert(self, model: models.PropertyModel, room_entities: List[entities.Room]):
        for r_entity in room_entities:
            r_model = mappers.to_model_room(r_entity)
            # Chiamiamo l'helper aggiornato per le amenities della stanza
            self._sync_room_amenities(r_model, r_entity.amenities)
            model.rooms.append(r_model)

    def _sync_rooms_update(self, model: models.PropertyModel, room_entities: List[entities.Room]):
        db_rooms_map = {r.id: r for r in model.rooms}
        updated_orm_list = []

        for r_entity in room_entities:
            if r_entity.id in db_rooms_map:
                # UPDATE ROOM
                existing_room = db_rooms_map[r_entity.id]
                existing_room.type = r_entity.type.value
                existing_room.price = r_entity.price
                existing_room.capacity = r_entity.capacity
                existing_room.description = r_entity.description
                existing_room.is_available = r_entity.is_available
                
                # Sync amenities della stanza (Link Table)
                self._sync_room_amenities(existing_room, r_entity.amenities)
                # Sync media stanza (Logica invariata)
                self._sync_room_media_update(existing_room, r_entity.media)
                
                updated_orm_list.append(existing_room)
            else:
                # INSERT ROOM
                new_room = mappers.to_model_room(r_entity)
                self._sync_room_amenities(new_room, r_entity.amenities)
                # (Aggiungi sync media insert qui se necessario)
                updated_orm_list.append(new_room)
        
        model.rooms = updated_orm_list

    def _sync_media_insert(self, model: models.PropertyModel, media_entities: List[entities.Media]):
        for m_entity in media_entities:
            m_model = mappers.to_model_media(m_entity, property_id=model.id)
            model.media.append(m_model)

    def _sync_media_update(self, model: models.PropertyModel, media_entities: List[entities.Media]):
        db_media_map = {m.id: m for m in model.media}
        updated_media_list = []

        for m_entity in media_entities:
            if m_entity.id in db_media_map:
                existing = db_media_map[m_entity.id]
                existing.description = m_entity.description
                updated_media_list.append(existing)
            else:
                new_media = mappers.to_model_media(m_entity, property_id=model.id)
                updated_media_list.append(new_media)
        
        model.media = updated_media_list

    def _sync_room_media_update(self, room_model: models.RoomModel, media_entities: List[entities.Media]):

        db_media_map = {m.id: m for m in room_model.media}
        updated_list = []
        for m_entity in media_entities:
            if m_entity.id in db_media_map:
                existing = db_media_map[m_entity.id]
                existing.description = m_entity.description
                updated_list.append(existing)
            else:
                new_media = mappers.to_model_media(m_entity, room_id=room_model.id)
                updated_list.append(new_media)
        room_model.media = updated_list