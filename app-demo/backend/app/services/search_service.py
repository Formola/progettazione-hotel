from typing import Any, Dict, List, Optional
from app.domain import entities # <--- Importa entities
from app.repositories.search_repository import SearchRepository

class SearchService:
    def __init__(self, search_repo: SearchRepository):
        self.search_repo = search_repo

    # Ritorna una lista di Entità di Dominio, non Dizionari
    def search(self, location: str = None) -> List[Dict[str, Any]]:
        return self.search_repo.search_properties(location)