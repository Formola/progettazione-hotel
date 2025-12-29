# app/services/media_service.py
import uuid
import base64
from typing import Optional

from app.domain import entities
from app.repositories.media_repository import MediaRepository
from app.storage.base import IMediaStorage
from app.schemas import MediaInput

class MediaService:
    def __init__(self, media_repo: MediaRepository, storage: IMediaStorage):
        self.media_repo = media_repo
        self.storage = storage

    def upload_media(self, data: MediaInput) -> entities.Media:
        # Generazione ID e Nome File Univoco
        media_id = str(uuid.uuid4())
        # Es: 550e8400...-vacanza.jpg
        unique_filename = f"{media_id}-{data.file_name}"

        # Decodifica Base64 (Logica Applicativa)
        b64_str = data.base_64_data
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        file_bytes = base64.b64decode(b64_str)

        # Upload Fisico (tramite Interfaccia)
        # Il service non sa se sta usando S3 o LocalStack o Disco
        storage_path = self.storage.store_media(
            file_name=unique_filename,
            file_data=file_bytes,
            content_type=data.file_type.value # Enum -> str
        )

        # Creazione Entità Dominio
        new_media = entities.Media(
            id=media_id,
            file_name=data.file_name,
            file_type=data.file_type.value,
            storage_path=storage_path,
            description=data.description
        )

        # Salvataggio Metadati DB
        self.media_repo.save(new_media)
        
        return new_media

    def get_media(self, media_id: str) -> Optional[entities.Media]:
        return self.media_repo.get_by_id(media_id)

    def delete_media(self, media_id: str):
        media = self.media_repo.get_by_id(media_id)
        if media:
            # Cancella da S3
            self.storage.delete_media(media.storage_path)
            # Cancella da DB
            self.media_repo.delete(media_id)
            
    def get_media_by_id(self, media_id: str) -> Optional[entities.Media]:
        return self.media_repo.get_by_id(media_id)