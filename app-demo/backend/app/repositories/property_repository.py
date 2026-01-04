from sqlalchemy import delete, exists
from sqlalchemy.orm import Session, selectinload, joinedload
from typing import List, Optional
from app.domain import entities
from app.models import models
from app.repositories import mappers
from app.storage.media_storage_interface import IMediaStorage

class PropertyRepository:
    def __init__(self, db: Session, storage: IMediaStorage):
        self.db = db
        self.storage = storage

    def get_by_id(self, property_id: str) -> Optional[entities.Property]:
        stmt = (
            self.db.query(models.PropertyModel)
            .options(
                selectinload(models.PropertyModel.amenity_links).joinedload(models.PropertyAmenityLinkModel.amenity),
                selectinload(models.PropertyModel.media),
                selectinload(models.PropertyModel.rooms).options(
                    selectinload(models.RoomModel.amenity_links).joinedload(models.RoomAmenityLinkModel.amenity),
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
        
        paths_to_delete_on_success: List[str] = [] # Accumulatore per file fisici

        if model:
            # Raccogli TUTTI i media (della Property e delle sue Rooms)
            paths_to_delete_on_success.extend([m.storage_path for m in model.media if m.storage_path])
            for room in model.rooms:
                paths_to_delete_on_success.extend([m.storage_path for m in room.media if m.storage_path])

            # Identifica Amenities Custom che diverranno orfane
            prop_custom_ids = [l.amenity_id for l in model.amenity_links if not l.amenity.is_global]
            room_custom_ids = []
            for r in model.rooms:
                room_custom_ids.extend([l.amenity_id for l in r.amenity_links if not l.amenity.is_global])

            # DELETE Principale (Cascade cancellerà rooms, media rows, amenity_links)
            self.db.delete(model)
            self.db.flush() 

            # CLEANUP AMENITIES ORFANE (Property)
            if prop_custom_ids:
                stmt = delete(models.PropertyAmenityModel).where(
                    models.PropertyAmenityModel.id.in_(prop_custom_ids),
                    models.PropertyAmenityModel.is_global == False,
                    ~exists().where(models.PropertyAmenityLinkModel.amenity_id == models.PropertyAmenityModel.id)
                )
                self.db.execute(stmt)

            # CLEANUP AMENITIES ORFANE (Rooms)
            if room_custom_ids:
                stmt = delete(models.RoomAmenityModel).where(
                    models.RoomAmenityModel.id.in_(room_custom_ids),
                    models.RoomAmenityModel.is_global == False,
                    ~exists().where(models.RoomAmenityLinkModel.amenity_id == models.RoomAmenityModel.id)
                )
                self.db.execute(stmt)

            # COMMIT DEL DB
            self.db.commit()
        
        # CANCELLAZIONE FISICA (Solo se commit è andato a buon fine)
        for path in paths_to_delete_on_success:
            self.storage.delete_media(path)
        

    def save(self, entity: entities.Property) -> entities.Property:
        existing_model = self.db.query(models.PropertyModel).get(entity.id)
        
        files_to_delete_on_success: List[str] = []

        if not existing_model:
            # INSERT
            new_model = mappers.to_model_property(entity)
            self._sync_amenities(new_model, entity.amenities)
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

            self._sync_amenities(existing_model, entity.amenities)
            
            # Sync Media (Raccogli file da cancellare, ma non cancellare ancora)
            deleted_paths = self._sync_media_update(existing_model, entity.media)
            files_to_delete_on_success.extend(deleted_paths)

        # COMMIT
        self.db.commit()
        
        # CANCELLAZIONE FISICA
        for path in files_to_delete_on_success:
            self.storage.delete_media(path)
            
        return self.get_by_id(entity.id)

    # =================================================================
    # HELPER PRIVATI
    # =================================================================

    def _sync_amenities(self, model: models.PropertyModel, property_amenity_entities: List[entities.PropertyAmenity]):
        current_linked_ids = {link.amenity_id for link in model.amenity_links}
        incoming_ids = {entity.id for entity in property_amenity_entities}
        ids_to_unlink = current_linked_ids - incoming_ids

        model.amenity_links = [] 

        if property_amenity_entities:
            new_links = []
            for a_entity in property_amenity_entities:
                link = models.PropertyAmenityLinkModel(
                    property_id=model.id,
                    amenity_id=a_entity.id,
                    custom_description=a_entity.custom_description
                )
                new_links.append(link)
            model.amenity_links = new_links

        self.db.flush()

        if ids_to_unlink:
            stmt = (
                delete(models.PropertyAmenityModel)
                .where(models.PropertyAmenityModel.id.in_(ids_to_unlink))
                .where(models.PropertyAmenityModel.is_global == False)
                .where(
                    ~exists().where(
                        models.PropertyAmenityLinkModel.amenity_id == models.PropertyAmenityModel.id
                    )
                )
            )
            self.db.execute(stmt)

    def _sync_media_insert(self, model: models.PropertyModel, media_entities: List[entities.Media]):
        for m_entity in media_entities:
            m_model = mappers.to_model_media(m_entity, property_id=model.id)
            model.media.append(m_model)

    def _sync_media_update(self, model: models.PropertyModel, media_entities: List[entities.Media]) -> List[str]:
        """
        Sync Media. Ritorna lista di file paths da cancellare (Safe Delete).
        """
        db_media_map = {m.id: m for m in model.media}
        updated_media_list = []
        paths_to_delete = []

        # Identifica rimossi
        incoming_ids = {m.id for m in media_entities}
        for m_id, m_orm in db_media_map.items():
            if m_id not in incoming_ids:
                if m_orm.storage_path:
                    paths_to_delete.append(m_orm.storage_path)

        # Aggiorna DB Objects
        for m_entity in media_entities:
            if m_entity.id in db_media_map:
                existing = db_media_map[m_entity.id]
                existing.description = m_entity.description
                updated_media_list.append(existing)
            else:
                new_media = mappers.to_model_media(m_entity, property_id=model.id)
                updated_media_list.append(new_media)
        
        model.media = updated_media_list
        
        # Ritorniamo la lista per cancellazione differita
        return paths_to_delete