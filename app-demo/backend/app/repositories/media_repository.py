from typing import Optional
from sqlalchemy.orm import Session
from app.domain import entities
from app.models import models
from app.repositories import mappers

class MediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, media_id: str) -> Optional[entities.Media]:
        model = self.db.query(models.MediaModel).get(media_id)
        if not model:
            return None
        return mappers.to_domain_media(model)

    def save(self, entity: entities.Media, property_id: str = None, room_id: str = None):
        """
        Saves or updates a Media entity in the database.
            - If the media with the given ID exists, it updates its fields.
            - If it does not exist, it creates a new record.
        """
        model = self.db.query(models.MediaModel).get(entity.id)
        
        if model:
            # Update (es. cambio descrizione)
            model.description = entity.description
            model.file_name = entity.file_name
        else:
            # Insert
            model = models.MediaModel(
                id=entity.id,
                file_name=entity.file_name,
                file_type=entity.file_type,
                storage_path=entity.storage_path,
                description=entity.description,
                property_id=property_id,
                room_id=room_id
            )
            self.db.add(model)
        
        self.db.commit()

    def delete(self, media_id: str):
        model = self.db.query(models.MediaModel).get(media_id)
        if model:
            self.db.delete(model)
            self.db.commit()