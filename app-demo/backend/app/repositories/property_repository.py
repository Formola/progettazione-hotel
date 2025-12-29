from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain import entities
from app.models import models
from app.repositories import mappers

class PropertyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, property_id: str) -> Optional[entities.Property]:
        model = self.db.query(models.PropertyModel).get(property_id)
        return mappers.to_domain_property(model) if model else None
    
    def get_by_owner_id(self, owner_id: str) -> List[entities.Property]:
        models_list = self.db.query(models.PropertyModel).filter(
            models.PropertyModel.owner_id == owner_id
        ).all()
        return [mappers.to_domain_property(m) for m in models_list]
    
    def delete(self, property_id: str):
        model = self.db.query(models.PropertyModel).get(property_id)
        if model:
            self.db.delete(model)
            self.db.commit()

    def save(self, entity: entities.Property) -> entities.Property:
        # Recupera il modello esistente
        existing_model = self.db.query(models.PropertyModel).get(entity.id)

        if not existing_model:
            # CASO INSERT: È facile, creiamo tutto da zero
            new_model = mappers.to_model_property(entity)
            
            # Dobbiamo associare manualmente le Amenities per far scattare il link many-to-many
            self._sync_amenities(new_model, entity.amenities)
            # Idem per Stanze e Media
            self._sync_rooms_insert(new_model, entity.rooms)
            self._sync_media_insert(new_model, entity.media)
            
            self.db.add(new_model)
        else:
            # CASO UPDATE: Sincronizzazione.
            
            # Campi Semplici
            existing_model.name = entity.name
            existing_model.description = entity.description
            existing_model.address = entity.address
            existing_model.city = entity.city
            existing_model.country = entity.country
            existing_model.status = entity.status.value

            # Sync Amenities (Many-to-Many)
            # Sostituiamo la lista di oggetti ORM associati
            self._sync_amenities(existing_model, entity.amenities)

            # Sync Rooms (One-to-Many con Orphan Removal)
            self._sync_rooms_update(existing_model, entity.rooms)

            # Sync Media (One-to-Many)
            self._sync_media_update(existing_model, entity.media)

        self.db.commit()
        return self.get_by_id(entity.id)

    # =================================================================
    # HELPER PRIVATI DI SINCRONIZZAZIONE
    # =================================================================

    def _sync_amenities(self, model: models.PropertyModel, amenity_entities: List[entities.PropertyAmenity]):
        """
        Recupera gli oggetti AmenityModel dal DB basandosi sugli ID delle entity
        e sostituisce la lista nel modello. SQLAlchemy aggiornerà la tabella link.
        """
        if not amenity_entities:
            model.amenities = []
            return

        ids = [a.id for a in amenity_entities]
        # Query per ottenere gli oggetti ORM reali
        amenity_models = self.db.query(models.PropertyAmenityModel).filter(
            models.PropertyAmenityModel.id.in_(ids)
        ).all()
        
        model.amenities = amenity_models

    def _sync_rooms_insert(self, model: models.PropertyModel, room_entities: List[entities.Room]):
        """Helper per inserimento iniziale delle stanze"""
        for r_entity in room_entities:
            r_model = mappers.to_model_room(r_entity)
            # Gestiamo ricorsivamente le amenities della stanza
            self._sync_room_amenities(r_model, r_entity.amenities)
            model.rooms.append(r_model)

    def _sync_media_insert(self, model: models.PropertyModel, media_entities: List[entities.Media]):
        for m_entity in media_entities:
            m_model = mappers.to_model_media(m_entity, property_id=model.id)
            model.media.append(m_model)

    def _sync_rooms_update(self, model: models.PropertyModel, room_entities: List[entities.Room]):
        """
        Logica: Aggiorna esistenti, Crea nuovi, Cancella orfani.
        """
        # Mappa delle stanze esistenti nel DB {id: oggetto_orm}
        db_rooms_map = {r.id: r for r in model.rooms}
        
        # Lista finale che il modello dovrà avere
        updated_orm_list = []

        for r_entity in room_entities:
            if r_entity.id in db_rooms_map:
                # UPDATE: La stanza esiste, aggiorniamo i campi
                existing_room = db_rooms_map[r_entity.id]
                existing_room.type = r_entity.type.value
                existing_room.price = r_entity.price
                existing_room.capacity = r_entity.capacity
                existing_room.description = r_entity.description
                existing_room.is_available = r_entity.is_available
                
                # Ricorsione: Sync amenities della stanza
                self._sync_room_amenities(existing_room, r_entity.amenities)
                
                updated_orm_list.append(existing_room)
            else:
                # INSERT: Nuova stanza nell'entity
                new_room = mappers.to_model_room(r_entity)
                self._sync_room_amenities(new_room, r_entity.amenities)
                updated_orm_list.append(new_room)
        
        # DELETE: Assegnando la nuova lista, SQLAlchemy rimuove quelle che non ci sono più
        # (richiede cascade="all, delete-orphan" nel PropertyModel)
        model.rooms = updated_orm_list

    def _sync_media_update(self, model: models.PropertyModel, media_entities: List[entities.Media]):
        """Stessa logica delle rooms ma per i media"""
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

    def _sync_room_amenities(self, room_model: models.RoomModel, amenities: List[entities.RoomAmenity]):
        """Helper per le amenities della stanza (Many-to-Many)"""
        if not amenities:
            room_model.amenities = []
            return
        ids = [a.id for a in amenities]
        room_model.amenities = self.db.query(models.RoomAmenityModel).filter(
            models.RoomAmenityModel.id.in_(ids)
        ).all()