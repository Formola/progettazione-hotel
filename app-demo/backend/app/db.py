from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # <--- 1. Importa questo
from app.config import settings

# Crea l'engine
engine = create_engine(settings.DATABASE_URL)

# Crea la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea la classe Base da cui erediteranno tutti i modelli
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()