from typing import Optional, List
from sqlalchemy import delete, exists
from sqlalchemy.orm import Session

from app.domain import entities
from app.models import models  
from app.repositories import mappers
from sqlalchemy.orm import selectinload
from app.storage.media_storage_interface import IMediaStorage


class RoomRepository:
    def __init__(self, db: Session, storage: IMediaStorage):
        self.db = db
        self.storage = storage

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
        
        files_to_delete_on_success: List[str] = [] # Percorsi dei file da cancellare dopo il commit

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

            # Sync Media: Raccogliamo i file da cancellare
            deleted_paths = self._sync_media(existing_model, entity.media)
            files_to_delete_on_success.extend(deleted_paths)
            
            self.db.add(existing_model)

        else:
            # INSERT
            new_model = mappers.to_model_room(entity)
            
            # Popoliamo le relazioni manualmente anche in fase di creazione
            self._sync_amenities(new_model, entity.amenities)
            self._sync_media(new_model, entity.media)
            
            self.db.add(new_model)

        self.db.commit()
        
        for path in files_to_delete_on_success:
            self.storage.delete_media(path)
            
        # Ritorniamo l'entità ricaricata dal DB per essere sicuri
        return self.get_by_id(entity.id)

    def delete(self, room_id: str):
        model = self.db.query(models.RoomModel).get(room_id)
        if model:
            # SNAPSHOT MEDIA: Salva i path prima che il DB li cancelli
            paths_to_delete = [m.storage_path for m in model.media]

            # SNAPSHOT AMENITIES
            linked_amenity_ids = [
                link.amenity_id 
                for link in model.amenity_links 
                if not link.amenity.is_global
            ]

            # DB DELETE
            self.db.delete(model)
            self.db.flush()

            # CLEANUP AMENITIES
            if linked_amenity_ids:
                stmt = (
                    delete(models.RoomAmenityModel)
                    .where(models.RoomAmenityModel.id.in_(linked_amenity_ids))
                    .where(models.RoomAmenityModel.is_global == False)
                    .where(
                        ~exists().where(
                            models.RoomAmenityLinkModel.amenity_id == models.RoomAmenityModel.id
                        )
                    )
                )
                self.db.execute(stmt)

            self.db.commit()

            # CLEANUP FILE FISICI
            for path in paths_to_delete:
                if path:
                    self.storage.delete_media(path)
            
        # print("deleted amenities:", linked_amenity_ids)

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
        
        # FASE SNAPSHOT: Capiamo cosa stiamo per rimuovere
        # ID attualmente collegati a questa stanza nel DB
        current_linked_ids = {link.amenity_id for link in model.amenity_links}
        # ID che l'utente vuole salvare (dal frontend)
        incoming_ids = {entity.id for entity in room_amenity_entities}
        
        # Calcoliamo la differenza: ID che c'erano prima ma ora non ci sono più
        ids_to_unlink = current_linked_ids - incoming_ids

        # FASE UPDATE LINKS (Standard)
        # Svuotiamo la lista (SQLAlchemy cancellerà le righe nella tabella 'room_amenity_link')
        model.amenity_links = [] 

        if room_amenity_entities:
            new_links = []
            for am_entity in room_amenity_entities:
                link = models.RoomAmenityLinkModel(
                    room_id=model.id,
                    amenity_id=am_entity.id,
                    custom_description=am_entity.custom_description
                )
                new_links.append(link)
            model.amenity_links = new_links

        # IMPORTANTE: Facciamo un flush per applicare le modifiche ai LINK nel DB
        # Prima di provare a cancellare l'amenity padre, i link figli devono essere spariti.
        self.db.flush()

        # FASE CLEANUP (Garbage Collection)
        # Se abbiamo rimosso dei collegamenti, controlliamo se le amenity "genitore" sono diventate orfane
        if ids_to_unlink:
            # Query di cancellazione sicura:
            # DELETE FROM room_amenities 
            # WHERE id IN (ids_to_unlink) 
            #   AND is_global = FALSE 
            #   AND NOT EXISTS (SELECT 1 FROM room_amenity_links WHERE amenity_id = room_amenities.id)
            
            stmt = (
                delete(models.RoomAmenityModel)
                .where(models.RoomAmenityModel.id.in_(ids_to_unlink)) # Solo quelle che abbiamo appena sganciato
                .where(models.RoomAmenityModel.is_global == False)    # MAI cancellare quelle del catalogo
                .where(
                    ~exists().where(
                        models.RoomAmenityLinkModel.amenity_id == models.RoomAmenityModel.id
                    )
                )
            )
            
            self.db.execute(stmt)
            
        # print("eliminated orphaned amenities:", ids_to_unlink)

    def _sync_media(self, model: models.RoomModel, media_entities: List[entities.Media]) -> List[str]:
        """
        Sync One-to-Many relationship.
        Ritorna una lista di storage_paths che devono essere cancellati DOPO il commit.
        """
        current_media_map = {m.id: m for m in model.media}
        incoming_ids = {m.id for m in media_entities}
        
        # Identifica file da rimuovere
        removed_media = [m for m_id, m in current_media_map.items() if m_id not in incoming_ids]
        paths_to_delete = [m.storage_path for m in removed_media if m.storage_path]

        updated_media_list = []
        for m_entity in media_entities:
            if m_entity.id in current_media_map:
                existing = current_media_map[m_entity.id]
                existing.description = m_entity.description
                updated_media_list.append(existing)
            else:
                new_media = mappers.to_model_media(m_entity, room_id=model.id)
                updated_media_list.append(new_media)
        
        model.media = updated_media_list
        
        # NON cancelliamo qui. Ritorniamo la lista al chiamante.
        return paths_to_delete