import uuid
import base64
from typing import Optional
from app.domain import entities
from app.repositories.media_repository import MediaRepository
from app.storage.s3_media_storage import IMediaStorage
from app.schemas import MediaInput

class MediaService:
    def __init__(self, media_repo: MediaRepository, storage: IMediaStorage):
        self.media_repo = media_repo
        self.storage = storage

    def upload_media(self, data: MediaInput) -> entities.Media:
        media_id = str(uuid.uuid4())
        unique_filename = f"{media_id}-{data.file_name}"

        # Decodifica Base64
        b64_str = data.base_64_data
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        file_bytes = base64.b64decode(b64_str)

        # Upload Fisico (S3)
        storage_path = self.storage.store_media(
            file_name=unique_filename,
            file_data=file_bytes,
            content_type=data.file_type.value
        )

        # Creazione Entità Dominio
        new_media = entities.Media(
            id=media_id,
            file_name=data.file_name,
            file_type=data.file_type.value,
            storage_path=storage_path,
            description=data.description
        )

        # Salvataggio DB con Collegamento
        # Passiamo esplicitamente property_id O room_id
        self.media_repo.save(
            new_media, 
            property_id=data.property_id, 
            room_id=data.room_id
        )
        
        return new_media

    def delete_media(self, media_id: str):
        media = self.media_repo.get_by_id(media_id)
        if media:
            # Cancella da S3 (ignora errori se file non esiste più)
            self.storage.delete_media(media.storage_path)
            # Cancella da DB
            self.media_repo.delete(media_id)

    def get_media_by_id(self, media_id: str) -> Optional[entities.Media]:
        return self.media_repo.get_by_id(media_id)
    
    def list_media_by_property(self, property_id: str) -> list[entities.Media]:
        return self.media_repo.list_by_property(property_id)
    
    def list_media_by_room(self, room_id: str) -> list[entities.Media]:
        return self.media_repo.list_by_room(room_id)
    
    def list_all_media(self) -> list[entities.Media]:
        return self.media_repo.list_all()