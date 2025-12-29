from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain import entities
from app.models import models  
from app.repositories import mappers

class RoomRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, room_id: str) -> Optional[entities.Room]:
        model = self.db.query(models.RoomModel).filter(models.RoomModel.id == room_id).first()
        if not model:
            return None
        return mappers.to_domain_room(model)

    def save(self, entity: entities.Room) -> entities.Room:
        # Recupera il modello esistente
        existing_model = self.db.query(models.RoomModel).get(entity.id)

        if existing_model:
            # UPDATE
            # Campi Scalari
            existing_model.price = entity.price
            existing_model.capacity = entity.capacity
            existing_model.type = entity.type.value
            existing_model.description = entity.description
            existing_model.is_available = entity.is_available

            # Sync Amenities (Many-to-Many)
            self._sync_amenities(existing_model, entity.amenities)

            # Sync Media (One-to-Many)
            self._sync_media(existing_model, entity.media)

            self.db.add(existing_model)

        else:
            # INSERT
            new_model = mappers.to_model_room(entity)
            
            # Popoliamo le relazioni manualmente anche in fase di creazione
            self._sync_amenities(new_model, entity.amenities)
            self._sync_media(new_model, entity.media)
            
            self.db.add(new_model)

        self.db.commit()
        # Ritorniamo l'entità ricaricata dal DB per essere sicuri
        return self.get_by_id(entity.id)

    def delete(self, room_id: str):
        model = self.db.query(models.RoomModel).get(room_id)
        if model:
            self.db.delete(model)
            self.db.commit()

    # =================================================================
    # HELPER PRIVATI DI SINCRONIZZAZIONE
    # =================================================================

    def _sync_amenities(self, model: models.RoomModel, amenity_entities: List[entities.RoomAmenity]):
        """
        Gestisce la relazione Many-to-Many con room_amenities.
        Sostituisce la lista corrente con quella nuova.
        """
        if not amenity_entities:
            model.amenities = []
            return

        ids = [a.id for a in amenity_entities]
        # Recupera gli oggetti ORM reali dal DB
        amenity_models = self.db.query(models.RoomAmenityModel).filter(
            models.RoomAmenityModel.id.in_(ids)
        ).all()
        
        model.amenities = amenity_models

    def _sync_media(self, model: models.RoomModel, media_entities: List[entities.Media]):
        """
        Gestisce la relazione One-to-Many con i Media della stanza.
        Logica: Aggiorna esistenti, Crea nuovi, Rimuove orfani.
        """
        # Mappa dei media esistenti nel DB per questa stanza {id: oggetto_orm}
        db_media_map = {m.id: m for m in model.media}
        
        updated_media_list = []

        for m_entity in media_entities:
            if m_entity.id in db_media_map:
                # UPDATE: Il media esiste, aggiorniamo solo i metadati (es. descrizione)
                existing_media = db_media_map[m_entity.id]
                existing_media.description = m_entity.description
                # file_name e path di solito non cambiano durante un update stanza, 
                updated_media_list.append(existing_media)
            else:
                # 2. INSERT: Nuovo media aggiunto alla lista
                new_media = mappers.to_model_media(m_entity, room_id=model.id)
                updated_media_list.append(new_media)
        
        # DELETE (Orphan Removal): Assegnando la nuova lista, SQLAlchemy
        # rimuoverà dal DB i media che erano in db_media_map ma non in updated_media_list.
        # (Richiede cascade="all, delete-orphan" nella relazione in RoomModel)
        model.media = updated_media_list