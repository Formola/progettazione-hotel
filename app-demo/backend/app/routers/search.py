from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.params import Header
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.config import settings
from app.domain import entities
from app import dependencies as deps
from app.services.search_service import SearchService
from app.schemas import PropertySearchResponse

router = APIRouter(prefix="/api/search", tags=["search"])
        
@router.get("/", response_model=List[PropertySearchResponse])
def search_properties(
    location: Optional[str] = Query(None),
    service: SearchService = Depends(deps.get_search_service),
    user: Optional[entities.User] = Depends(deps.get_optional_user)
):
    # Log opzionale
    caller = user.email if user else "Guest"
    print(f"Search performed by: {caller} [Location: {location}]")

    # Chiamata al service (che chiama il repo SQL)
    results = service.search(location)
    
    return results