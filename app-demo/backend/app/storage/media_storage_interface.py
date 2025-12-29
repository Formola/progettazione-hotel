from abc import ABC, abstractmethod
from inspect import _void

class IMediaStorage(ABC):
    @abstractmethod
    def store_media(self, file_name: str, file_data: bytes, content_type: str) -> str:
        """
        Salva i bytes del file e ritorna l'URL pubblico/percorso.
        """
        pass

    @abstractmethod
    def delete_media(self, storage_path: str) -> _void:
        """
        Cancella il file dato il suo percorso/URL.
        """
        pass