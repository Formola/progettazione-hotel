import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AWS Config
    AWS_ENDPOINT_URL: str = os.getenv("AWS_ENDPOINT_URL")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Database Config (PostgreSQL su RDS/Localstack)
    DB_HOST: str = os.getenv("DB_HOST", "localstack")
    DB_PORT: str = os.getenv("DB_PORT", "4510")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_NAME: str = os.getenv("DB_NAME", "myappdb")

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()