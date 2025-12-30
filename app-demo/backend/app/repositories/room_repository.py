from typing import Optional, List
from sqlalchemy.orm import Session

from app.domain import entities
from app.models import models  
from app.repositories import mappers
from sqlalchemy.orm import selectinload


class RoomRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, room_id: str) -> Optional[entities.Room]:
        stmt = (
            self.db.query(models.RoomModel)
            .options(
                # Carichiamo i LINK e, dentro i link, le AMENITIES
                selectinload(models.RoomModel.amenity_links).joinedload(models.RoomAmenityLinkModel.amenity),
                selectinload(models.RoomModel.media)
            )
            .filter(models.RoomModel.id == room_id)
        )
        model = stmt.first()
        return mappers.to_domain_room(model) if model else None
    
    def get_by_property_id(self, property_id: str) -> List[entities.Room]:
        
        """
        OTTIMIZZAZIONE PERFORMANCE (selectinload):
        
        Usiamo `selectinload` per evitare il problema "N+1 Query".
        
        Esempio su 50 stanze:
        - Lazy Loading (Default): 1 query (rooms) + 50 (amenities) + 50 (media) = 101 query.
        - Eager Loading (selectinload): 
          1. Query Rooms
          2. Query Amenities (WHERE room_id IN (...))
          3. Query Media (WHERE room_id IN (...))
          Totale = 3 query.
        """
        
        
        stmt = (
            self.db.query(models.RoomModel)
            .options(
                selectinload(models.RoomModel.amenity_links).joinedload(models.RoomAmenityLinkModel.amenity),
                selectinload(models.RoomModel.media)
            )
            .filter(models.RoomModel.property_id == property_id)
        )
        
        models_list = stmt.all()
        return [mappers.to_domain_room(m) for m in models_list]

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
    
    ## EVITNANO DIFFING
    ## ossia: non dobbiamo confrontare cosa è cambiato,
    ## ma semplicemente riallineare lo stato del DB
    ## a quello dell'entità passata.
    ## se non svuotassimo le liste, dovremmo fare un diffing manuale
    ## per capire cosa aggiungere, cosa rimuovere, cosa aggiornare.
    ## esempio: se un'amenity è stata rimossa, 

    def _sync_amenities(self, model: models.RoomModel, room_amenity_entities: List[entities.RoomAmenity]):
        """
        Handles the Many-to-Many relationship with Room Amenities via the link table.
        """
        # Clear the current list of links (it will be recreated)
        # Note: thanks to cascade="all, delete-orphan", removing from the list deletes from the DB
        model.amenity_links = [] 

        if not room_amenity_entities:
            return

        new_links = []
        for am_entity in room_amenity_entities:
            # Creiamo il Link Model esplicitamente
            link = models.RoomAmenityLinkModel(
                room_id=model.id,
                amenity_id=am_entity.id,
                custom_description=am_entity.custom_description
            )
            new_links.append(link)
        
        model.amenity_links = new_links

    def _sync_media(self, model: models.RoomModel, media_entities: List[entities.Media]):
        """
        Sync One-to-Many relationship with Media.
        Handles Inserts, Updates, and Deletes of Media associated with the Room.
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
                # INSERT: Nuovo media aggiunto alla lista
                new_media = mappers.to_model_media(m_entity, room_id=model.id)
                updated_media_list.append(new_media)
        
        # DELETE (Orphan Removal): Assegnando la nuova lista, SQLAlchemy
        # rimuoverà dal DB i media che erano in db_media_map ma non in updated_media_list.
        model.media = updated_media_list