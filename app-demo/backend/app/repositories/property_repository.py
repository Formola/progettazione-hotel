from sqlalchemy import delete, exists
from sqlalchemy.orm import Session, selectinload, joinedload
from typing import List, Optional
from app.domain import entities
from app.models import models
from app.repositories import mappers

## INTERFACCIA REPOSITORY SERVE SOLO SE IN FUTURO VOGLIAMO
## USARE DIVERSI DATABASE.

# class PropertyRepositoryInterface(ABC):
    
#     db: Session
    
#     def save(self, entity: entities.Property) -> entities.Property:
#         pass

#     def get_by_id(self, property_id: str) -> Optional[entities.Property]:
#         pass

#     def get_by_owner_id(self, owner_id: str) -> List[entities.Property]:
#         pass

#     def delete(self, property_id: str):
#         pass

class PropertyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, property_id: str) -> Optional[entities.Property]:
        stmt = (
            self.db.query(models.PropertyModel)
            .options(
                # Carica Amenities e Media della Proprietà
                selectinload(models.PropertyModel.amenity_links).joinedload(models.PropertyAmenityLinkModel.amenity),
                selectinload(models.PropertyModel.media),
                
                # Carica le stanze (READ-ONLY context qui)
                selectinload(models.PropertyModel.rooms).options(
                    selectinload(models.RoomModel.amenity_links).joinedload(models.RoomAmenityLinkModel.amenity),
                    selectinload(models.RoomModel.media)
                )
            )
            .filter(models.PropertyModel.id == property_id)
        )
        model = stmt.first()
        return mappers.to_domain_property(model) if model else None
    
    def get_by_owner_id(self, owner_id: str) -> List[entities.Property]:
        stmt = (
            self.db.query(models.PropertyModel)
            .filter(models.PropertyModel.owner_id == owner_id)
            .options(
                selectinload(models.PropertyModel.amenity_links).joinedload(models.PropertyAmenityLinkModel.amenity),
                selectinload(models.PropertyModel.media),
                selectinload(models.PropertyModel.rooms).options(
                    selectinload(models.RoomModel.amenity_links).joinedload(models.RoomAmenityLinkModel.amenity),
                    selectinload(models.RoomModel.media)
                )
            )
        )
        models_list = stmt.all()
        return [mappers.to_domain_property(m) for m in models_list]
    
    def delete(self, property_id: str):
        model = self.db.query(models.PropertyModel).get(property_id)
        if model:
            # Recuperiamo gli ID delle amenities custom collegate a questa proprietà
            # che potrebbero diventare orfane dopo la cancellazione
            linked_amenity_ids = [
                link.amenity_id 
                for link in model.amenity_links 
                if not link.amenity.is_global
            ]

            # Cancella la proprietà (e a cascata i link)
            self.db.delete(model)
            
            # Facciamo flush per applicare la cancellazione dei link
            self.db.flush()

            # Clean up: Cancelliamo le amenities che ora sono orfane
            if linked_amenity_ids:
                stmt = (
                    delete(models.PropertyAmenityModel)
                    .where(models.PropertyAmenityModel.id.in_(linked_amenity_ids))
                    .where(models.PropertyAmenityModel.is_global == False)
                    .where(
                        ~exists().where(
                            models.PropertyAmenityLinkModel.amenity_id == models.PropertyAmenityModel.id
                        )
                    )
                )
                self.db.execute(stmt)

            self.db.commit()

    def save(self, entity: entities.Property) -> entities.Property:
        existing_model = self.db.query(models.PropertyModel).get(entity.id)

        if not existing_model:
            # INSERT: Creiamo la proprietà base
            new_model = mappers.to_model_property(entity)
            
            # Sync SOLO Amenities e Media della Proprietà
            self._sync_amenities(new_model, entity.amenities)
            self._sync_media_insert(new_model, entity.media)
            
            # NOTA: Ignoriamo entity.rooms durante la creazione della proprietà.
            # Le stanze verranno create successivamente tramite room_service.add_room
            
            self.db.add(new_model)
        else:
            # UPDATE
            existing_model.name = entity.name
            existing_model.description = entity.description
            existing_model.address = entity.address
            existing_model.city = entity.city
            existing_model.country = entity.country
            existing_model.status = entity.status.value

            # Sync Amenities
            self._sync_amenities(existing_model, entity.amenities)

            # Sync Media
            self._sync_media_update(existing_model, entity.media)
            
            # NOTA: Non tocchiamo existing_model.rooms qui. 
            # Le stanze si gestiscono dal loro endpoint dedicato.

        self.db.commit()
        return self.get_by_id(entity.id)

    # =================================================================
    # HELPER PRIVATI (Solo scope Property)
    # =================================================================

    def _sync_amenities(self, model: models.PropertyModel, property_amenity_entities: List[entities.PropertyAmenity]):
        """
        Gestisce la relazione Many-to-Many e pulisce le Custom Amenities orfane.
        """
        current_linked_ids = {link.amenity_id for link in model.amenity_links}
        incoming_ids = {entity.id for entity in property_amenity_entities}
        ids_to_unlink = current_linked_ids - incoming_ids

        model.amenity_links = [] # Reset links

        if property_amenity_entities:
            new_links = []
            for a_entity in property_amenity_entities:
                link = models.PropertyAmenityLinkModel(
                    property_id=model.id,
                    amenity_id=a_entity.id,
                    custom_description=a_entity.custom_description
                )
                new_links.append(link)
            model.amenity_links = new_links

        self.db.flush()

        # Garbage Collection Custom Amenities
        if ids_to_unlink:
            stmt = (
                delete(models.PropertyAmenityModel)
                .where(models.PropertyAmenityModel.id.in_(ids_to_unlink))
                .where(models.PropertyAmenityModel.is_global == False)
                .where(
                    ~exists().where(
                        models.PropertyAmenityLinkModel.amenity_id == models.PropertyAmenityModel.id
                    )
                )
            )
            self.db.execute(stmt)

    def _sync_media_insert(self, model: models.PropertyModel, media_entities: List[entities.Media]):
        for m_entity in media_entities:
            m_model = mappers.to_model_media(m_entity, property_id=model.id)
            model.media.append(m_model)

    def _sync_media_update(self, model: models.PropertyModel, media_entities: List[entities.Media]):
        db_media_map = {m.id: m for m in model.media}
        updated_media_list = []

        for m_entity in media_entities:
            if m_entity.id in db_media_map:
                existing = db_media_map[m_entity.id]
                existing.description = m_entity.description
                updated_media_list.append(existing)
            else:
                new_media = mappers.to_model_media(m_entity, property_id=model.id)
                updated_media_list.append(new_media)
        
        model.media = updated_media_list