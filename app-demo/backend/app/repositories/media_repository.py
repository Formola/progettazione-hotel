from typing import Optional
from sqlalchemy.orm import Session
from app.domain import entities
from app.models import models
from app.repositories import mappers
from app.storage.media_storage_interface import IMediaStorage

class MediaRepository:
    def __init__(self, db: Session, storage: IMediaStorage):
        self.db = db
        self.storage = storage

    def get_by_id(self, media_id: str) -> Optional[entities.Media]:
        model = self.db.query(models.MediaModel).get(media_id)
        if not model:
            return None
        return mappers.to_domain_media(model)

    def save(self, entity: entities.Media, property_id: str = None, room_id: str = None):
        """
        Save or update a Media entity in the database.
        Either property_id or room_id should be provided to link the media.
        """
        model = self.db.query(models.MediaModel).get(entity.id)
        
        if model:
            # UPDATE: Aggiorna solo i metadati modificabili
            model.description = entity.description
            # Nota: Non aggiorniamo property_id/room_id qui di solito, 
            # un media nasce e muore associato alla stessa entità.
        else:
            # INSERT: Crea il record con i collegamenti
            model = models.MediaModel(
                id=entity.id,
                file_name=entity.file_name,
                file_type=entity.file_type,
                storage_path=entity.storage_path,
                description=entity.description,
                
                # Qui SQLAlchemy gestisce i NULL se uno dei due è None
                property_id=property_id, 
                room_id=room_id
            )
            self.db.add(model)
        
        self.db.commit()

    def delete(self, media_id: str):
        model = self.db.query(models.MediaModel).get(media_id)
        if model:
            
            path_to_delete = model.storage_path
            
            self.db.delete(model)
            self.db.commit()
            
            if path_to_delete:
                self.storage.delete_media(path_to_delete)
            
            
    def list_by_property(self, property_id: str) -> list[entities.Media]:
        models_list = self.db.query(models.MediaModel).filter_by(property_id=property_id).all()
        return [mappers.to_domain_media(m) for m in models_list]
    
    def list_by_room(self, room_id: str) -> list[entities.Media]:
        models_list = self.db.query(models.MediaModel).filter_by(room_id=room_id).all()
        return [mappers.to_domain_media(m) for m in models_list]
    
    def list_all(self) -> list[entities.Media]:
        models_list = self.db.query(models.MediaModel).all()
        return [mappers.to_domain_media(m) for m in models_list]
    