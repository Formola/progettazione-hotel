from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional

class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_properties(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            BASE_LIMIT = 20
            SEARCH_LIMIT = 50

            # -----------------------------
            # Properties + Owner info
            # -----------------------------
            sql_hotels = """
                SELECT p.id, p.name, p.address, p.city, p.country, p.description, p.created_at, p.status,
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

            hotels = self.db.execute(text(sql_hotels), params).mappings().all()
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
            rooms = self.db.execute(text(sql_rooms), {"hotel_ids": hotel_ids}).mappings().all()

            # -----------------------------
            # Media
            # -----------------------------
            sql_media = """
                SELECT id, property_id, file_name, file_type, storage_path, description, inserted_at
                FROM media
                WHERE property_id = ANY(:hotel_ids)
            """
            media = self.db.execute(text(sql_media), {"hotel_ids": hotel_ids}).mappings().all()

            # -----------------------------
            # Property amenities
            # -----------------------------
            sql_h_amenities = """
                SELECT l.property_id, a.id, a.name, a.category
                FROM property_amenities a
                JOIN property_amenities_link l ON a.id = l.amenity_id
                WHERE l.property_id = ANY(:hotel_ids)
            """
            h_amenities = self.db.execute(text(sql_h_amenities), {"hotel_ids": hotel_ids}).mappings().all()

            # -----------------------------
            # Room amenities
            # -----------------------------
            room_ids = [r["id"] for r in rooms]
            r_amenities = []
            if room_ids:
                sql_r_amenities = """
                    SELECT l.room_id, a.id, a.name, a.category
                    FROM room_amenities a
                    JOIN room_amenities_link l ON a.id = l.amenity_id
                    WHERE l.room_id = ANY(:room_ids)
                """
                r_amenities = self.db.execute(text(sql_r_amenities), {"room_ids": room_ids}).mappings().all()

            # -----------------------------
            # Data assembly (Manual Mapping)
            # -----------------------------
            hotels_map = {}
            for h in hotels:
                h_dict = dict(h)
                h_dict["rooms"] = []
                h_dict["media"] = []
                h_dict["amenities"] = []
                # Ristrutturiamo l'owner come oggetto annidato
                h_dict["owner"] = {
                    "id": h_dict.pop("owner_id"),
                    "name": h_dict.pop("owner_name"),
                    "email": h_dict.pop("owner_email")
                }
                hotels_map[h_dict["id"]] = h_dict

            rooms_map = {}
            for r in rooms:
                r_dict = dict(r)
                r_dict["amenities"] = []
                rooms_map[r_dict["id"]] = r_dict

                if r_dict["property_id"] in hotels_map:
                    hotels_map[r_dict["property_id"]]["rooms"].append(r_dict)

            for m in media:
                if m["property_id"] in hotels_map:
                    hotels_map[m["property_id"]]["media"].append(dict(m))

            for a in h_amenities:
                if a["property_id"] in hotels_map:

                    hotels_map[a["property_id"]]["amenities"].append({
                        "id": a.get("id"), 
                        "name": a["name"],
                        "category": a["category"]
                    })

            for a in r_amenities:
                if a["room_id"] in rooms_map:
                    rooms_map[a["room_id"]]["amenities"].append({
                        "id": a.get("id"),
                        "name": a["name"],
                        "category": a["category"]
                    })

            return list(hotels_map.values())

        except Exception as e:
            print(f"Database Error in SearchRepository: {e}")
            raise e