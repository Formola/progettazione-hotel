from abc import ABC, abstractmethod

class IMediaStorage(ABC):
    @abstractmethod
    def store_media(self, file_name: str, file_data: bytes, content_type: str) -> str:
        """
        Save the media file and return its storage path/URL.
        """
        pass

    @abstractmethod
    def delete_media(self, storage_path: str):
        """
        Delete the media file from storage given its storage path/URL.
        """
        pass