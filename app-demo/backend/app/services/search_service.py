from typing import List, Dict, Any
from app.repositories.search_repository import SearchRepository

class SearchService:
    def __init__(self, search_repo: SearchRepository):
        self.search_repo = search_repo

    def search(self, location: str = None) -> List[Dict[str, Any]]:
        return self.search_repo.search_properties(location)