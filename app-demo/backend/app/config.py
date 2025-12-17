import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- AWS BASIC ---
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: str = os.getenv("AWS_ENDPOINT_URL") # Es: http://localstack:4566

    # --- COGNITO (Backend to AWS) --- Non useremo Cognito nel backend.
    # Nota: Qui non usiamo il prefisso PUBLIC_ perché siamo nel backend
    # COGNITO_USER_POOL_ID: str = os.getenv("COGNITO_USER_POOL_ID")
    # COGNITO_CLIENT_ID: str = os.getenv("COGNITO_CLIENT_ID")

    # --- STORAGE (S3) ---
    S3_MEDIA_BUCKET: str = os.getenv("S3_MEDIA_BUCKET")
    # CLOUDFRONT_DOMAIN: str = os.getenv("CLOUDFRONT_DOMAIN", "")

    # --- DATABASE ---
    DB_HOST: str = os.getenv("DB_HOST", "localstack")
    DB_PORT: str = os.getenv("DB_PORT", "4510")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "myappdb")

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Questo permette a Pydantic di leggere dal file .env se presente (utile per debug senza docker)
    class Config:
        env_file = ".env"
        extra = "ignore" # Ignora variabili extra nel .env che non sono definite qui

settings = Settings()