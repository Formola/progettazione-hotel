from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional

# Questa repository si occupa delle query.
class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    # CQRS (Command Query Responsibility Segregation)
    # Cqrs vuol dire che le operazioni di lettura (Query) sono separate
    # dalle operazioni di scrittura (Command). Qui abbiamo solo Query.
    
    # Ritorna una lista di dizionari con i dati assemblati
    # facciamo esattamente 5 query per ogni hotel (hotel, rooms, media, property amenities, room amenities)
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
                # Logica di ricerca semplice
                params["loc"] = f"%{location}%"
                sql_hotels += " AND (p.city ILIKE :loc OR p.name ILIKE :loc OR p.address ILIKE :loc OR p.country ILIKE :loc OR p.description ILIKE :loc)"
                sql_hotels += " ORDER BY p.created_at DESC LIMIT :limit"
                params["limit"] = SEARCH_LIMIT
            else:
                sql_hotels += " ORDER BY p.created_at DESC LIMIT :limit"
                params["limit"] = BASE_LIMIT

            # Esecuzione Query Hotel
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
            # Media (Property + Rooms)
            # -----------------------------
            # Nota: Recuperiamo tutto ciò che riguarda questi hotel.
            sql_media = """
                SELECT id, property_id, room_id, file_name, file_type, storage_path, description, inserted_at
                FROM media
                WHERE property_id = ANY(:hotel_ids)
            """
            media = self.db.execute(text(sql_media), {"hotel_ids": hotel_ids}).mappings().all()

            # -----------------------------
            # Property Amenities
            # -----------------------------
            # Qui estraiamo anche description (catalogo) e custom_description (link)
            sql_h_amenities = """
                SELECT l.property_id, a.id, a.name, a.category,
                       a.description,          -- Descrizione generica
                       l.custom_description    -- Descrizione custom
                FROM property_amenities a
                JOIN property_amenities_link l ON a.id = l.amenity_id
                WHERE l.property_id = ANY(:hotel_ids)
            """
            h_amenities = self.db.execute(text(sql_h_amenities), {"hotel_ids": hotel_ids}).mappings().all()

            # -----------------------------
            # Room Amenities
            # -----------------------------
            room_ids = [r["id"] for r in rooms]
            r_amenities = []
            if room_ids:
                sql_r_amenities = """
                    SELECT l.room_id, a.id, a.name, a.category,
                           a.description,          -- Descrizione generica
                           l.custom_description    -- Descrizione custom
                    FROM room_amenities a
                    JOIN room_amenities_link l ON a.id = l.amenity_id
                    WHERE l.room_id = ANY(:room_ids)
                """
                r_amenities = self.db.execute(text(sql_r_amenities), {"room_ids": room_ids}).mappings().all()

            # -----------------------------
            # Data Assembly (Manual Mapping)
            # -----------------------------
            
            # Mappa Hotel
            hotels_map = {}
            for h in hotels:
                h_dict = dict(h)
                h_dict["rooms"] = []
                h_dict["media"] = []
                h_dict["amenities"] = []
                # Struttura Owner
                h_dict["owner"] = {
                    "id": h_dict.pop("owner_id"),
                    "name": h_dict.pop("owner_name"),
                    "email": h_dict.pop("owner_email")
                }
                hotels_map[h_dict["id"]] = h_dict

            # Mappa Stanze
            rooms_map = {}
            for r in rooms:
                r_dict = dict(r)
                r_dict["amenities"] = []
                r_dict["media"] = [] # Inizializza lista media per la stanza
                rooms_map[r_dict["id"]] = r_dict

                # Collega stanza all'hotel
                if r_dict["property_id"] in hotels_map:
                    hotels_map[r_dict["property_id"]]["rooms"].append(r_dict)

            # Mappa Media
            for m in media:
                m_dict = dict(m)
                # Se il media ha un room_id ed esiste nella mappa stanze, mettilo lì
                if m_dict.get("room_id") and m_dict["room_id"] in rooms_map:
                    rooms_map[m_dict["room_id"]]["media"].append(m_dict)
                # Altrimenti, se appartiene alla property, mettilo lì
                elif m_dict["property_id"] in hotels_map:
                    hotels_map[m_dict["property_id"]]["media"].append(m_dict)

            # Mappa Amenities Property (Con i nuovi campi)
            for a in h_amenities:
                if a["property_id"] in hotels_map:
                    hotels_map[a["property_id"]]["amenities"].append({
                        "id": a["id"], 
                        "name": a["name"],
                        "category": a["category"],
                        "description": a["description"],       
                        "custom_description": a["custom_description"] 
                    })

            # Mappa Amenities Rooms (Con i nuovi campi)
            for a in r_amenities:
                if a["room_id"] in rooms_map:
                    rooms_map[a["room_id"]]["amenities"].append({
                        "id": a["id"],
                        "name": a["name"],
                        "category": a["category"],
                        "description": a["description"],          
                        "custom_description": a["custom_description"] 
                    })

            return list(hotels_map.values())

        except Exception as e:
            print(f"Database Error in SearchRepository: {e}")
            raise e