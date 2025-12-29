from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search, properties
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
app.include_router(properties.router)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": settings.DB_HOST,
        "region": settings.AWS_REGION
    }
    
@app.get("/auth/me")
def test_headers(
    x_user_id: str = Header(None, alias="x-user-cognito-sub"),
    x_user_email: str = Header(None, alias="x-user-email"),
    x_user_role: str = Header(None, alias="x-user-role")
):
    return {
        "received_id": x_user_id,
        "received_email": x_user_email,
        "received_role": x_user_role
    }