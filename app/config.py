# app/config.py

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENABLE_LOGS: bool = os.getenv("ENABLE_LOGS", "true").lower() in ("true", "1", "t")
    RECORDS_PATH: str = os.getenv("RECORDS_PATH", "records")  # Directory to store audio files

    class Config:
        env_file = ".env"

settings = Settings()
