from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.params import Header
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.config import settings
from app.dependencies import UserContext, get_optional_user
from sqlalchemy.orm import sessionmaker

router = APIRouter(prefix="/api/search", tags=["search"])

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@router.get("/")
def search(location: str | None = Query(None), db: Session = Depends(get_db)
        ):
    try:
        BASE_LIMIT = 20
        SEARCH_LIMIT = 50

        # -----------------------------
        # Properties + Owner info
        # -----------------------------
        sql_hotels = """
            SELECT p.id, p.name, p.address, p.city, p.country, p.description, p.created_at,
                   u.id AS owner_id, u.name AS owner_name, u.email AS owner_email
            FROM properties p
            JOIN users u ON p.owner_id = u.id
            WHERE p.status = 'PUBLISHED'
        """
        params = {}

        if location:
            location = location.strip()
            if location:
                if len(location) <= 3:
                    params["loc"] = f"{location}%"
                else:
                    params["loc"] = f"%{location}%"
                sql_hotels += " AND (p.city ILIKE :loc OR p.name ILIKE :loc OR p.address ILIKE :loc OR p.country ILIKE :loc OR p.description ILIKE :loc)"
            sql_hotels += " ORDER BY p.created_at DESC LIMIT :limit"
            params["limit"] = SEARCH_LIMIT
        else:
            sql_hotels += " ORDER BY p.created_at DESC LIMIT :limit"
            params["limit"] = BASE_LIMIT

        hotels = db.execute(text(sql_hotels), params).mappings().all()
        if not hotels:
            return []

        hotel_ids = [h["id"] for h in hotels]

        # -----------------------------
        # Rooms
        # -----------------------------
        sql_rooms = """
            SELECT id, property_id, type, description, price, capacity, is_available, created_at
            FROM rooms
            WHERE property_id = ANY(:hotel_ids)
        """
        rooms = db.execute(text(sql_rooms), {"hotel_ids": hotel_ids}).mappings().all()

        # -----------------------------
        # Media
        # -----------------------------
        sql_media = """
            SELECT id, property_id, file_name, file_type, storage_path, description, inserted_at
            FROM media
            WHERE property_id = ANY(:hotel_ids)
        """
        media = db.execute(text(sql_media), {"hotel_ids": hotel_ids}).mappings().all()

        # -----------------------------
        # Property amenities
        # -----------------------------
        sql_h_amenities = """
            SELECT l.property_id, a.name, a.category
            FROM property_amenities a
            JOIN property_amenities_link l ON a.id = l.amenity_id
            WHERE l.property_id = ANY(:hotel_ids)
        """
        h_amenities = db.execute(text(sql_h_amenities), {"hotel_ids": hotel_ids}).mappings().all()

        # -----------------------------
        # Room amenities
        # -----------------------------
        room_ids = [r["id"] for r in rooms]
        r_amenities = []
        if room_ids:
            sql_r_amenities = """
                SELECT l.room_id, a.name, a.category
                FROM room_amenities a
                JOIN room_amenities_link l ON a.id = l.amenity_id
                WHERE l.room_id = ANY(:room_ids)
            """
            r_amenities = db.execute(text(sql_r_amenities), {"room_ids": room_ids}).mappings().all()

        # -----------------------------
        # Data assembly
        # -----------------------------
        hotels_map = {}
        for h in hotels:
            h = dict(h)
            h["rooms"] = []
            h["media"] = []
            h["amenities"] = []
            h["owner"] = {
                "id": h.pop("owner_id"),
                "name": h.pop("owner_name"),
                "email": h.pop("owner_email")
            }
            hotels_map[h["id"]] = h

        rooms_map = {}
        for r in rooms:
            r = dict(r)
            r["amenities"] = []
            rooms_map[r["id"]] = r
            hotels_map[r["property_id"]]["rooms"].append(r)

        for m in media:
            hotels_map[m["property_id"]]["media"].append(dict(m))

        for a in h_amenities:
            hotels_map[a["property_id"]]["amenities"].append({
                "name": a["name"],
                "category": a["category"]
            })

        for a in r_amenities:
            rooms_map[a["room_id"]]["amenities"].append({
                "name": a["name"],
                "category": a["category"]
            })

        return list(hotels_map.values())

    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
