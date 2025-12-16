from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search
from app.config import settings

app = FastAPI(title="HotelManager API")

# Lista degli indirizzi autorizzati (il tuo frontend)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Autorizza il frontend
    allow_credentials=True,
    allow_methods=["*"], # Autorizza tutti i metodi (GET, POST, etc.)
    allow_headers=["*"], # Autorizza tutti gli header
)

# Includiamo slo il router della ricerca per ora
app.include_router(search.router)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": settings.DB_HOST,
        "region": settings.AWS_REGION
    }