import uuid
from sqlalchemy.orm import Session
from app.models import models
from app.domain import entities
from app.repositories import mappers

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_cognito_id(self, cognito_uuid: str) -> entities.User | None:
        model = self.db.query(models.UserModel).filter(models.UserModel.cognito_uuid == cognito_uuid).first()
        return mappers.to_domain_user(model) if model else None

    def create_from_cognito(self, cognito_uuid: str, email: str, name: str) -> entities.User:
        # Generiamo un ID interno per il DB
        internal_id = str(uuid.uuid4())
        
        user_model = models.UserModel(
            id=internal_id,
            cognito_uuid=cognito_uuid,
            email=email,
            name=name
        )
        self.db.add(user_model)
        self.db.commit()
        self.db.refresh(user_model)
        
        return mappers.to_domain_user(user_model)