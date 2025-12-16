from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.config import settings
from typing import List

router = APIRouter(prefix="/api/search", tags=["search"])

# Database setup puntando a Localstack
engine = create_engine(settings.DATABASE_URL)

def get_db():
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def search(location: str = Query(None), db: Session = Depends(get_db)):
    try:
        # Query principale per recuperare gli Hotel
        sql_hotels = """
            SELECT p.* FROM properties p
            WHERE p.status = 'PUBLISHED'
        """
        params = {}
        if location:
            sql_hotels += " AND (p.city ILIKE :loc OR p.name ILIKE :loc)"
            params["loc"] = f"%{location}%"
        
        hotels_result = db.execute(text(sql_hotels), params).mappings().all()
        
        results = []
        
        for h in hotels_result:
            hotel = dict(h)
            hotel_id = hotel["id"]
            
            # Recuperiamo le Stanze per questo hotel
            sql_rooms = "SELECT * FROM rooms WHERE property_id = :pid"
            rooms_items = db.execute(text(sql_rooms), {"pid": hotel_id}).mappings().all()
            hotel["rooms"] = [dict(r) for r in rooms_items]
            
            # Recuperiamo i Media per questo hotel
            sql_media = "SELECT * FROM media WHERE property_id = :pid"
            media_items = db.execute(text(sql_media), {"pid": hotel_id}).mappings().all()
            hotel["media"] = [dict(m) for m in media_items]
            
            # Recuperiamo le Amenities dell'Hotel
            sql_h_amenities = """
                SELECT a.name, a.category 
                FROM property_amenities a
                JOIN property_amenities_link l ON a.id = l.amenity_id
                WHERE l.property_id = :pid
            """
            h_amenities = db.execute(text(sql_h_amenities), {"pid": hotel_id}).mappings().all()
            hotel["amenities"] = [dict(a) for a in h_amenities]
            
            # Per ogni stanza, recuperiamo le sue Amenities specifiche
            for room in hotel["rooms"]:
                sql_r_amenities = """
                    SELECT a.name, a.category 
                    FROM room_amenities a
                    JOIN room_amenities_link l ON a.id = l.amenity_id
                    WHERE l.room_id = :rid
                """
                r_amenities = db.execute(text(sql_r_amenities), {"rid": room["id"]}).mappings().all()
                room["amenities"] = [dict(a) for a in r_amenities]
                
            results.append(hotel)

        return results

    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))