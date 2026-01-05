from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Default to local Postgres (matches docker-compose + setup.sh).
    # Can be overridden via backend/.env or environment variables.
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/degree_audit"
    # Kept for compatibility even when auth is disabled.
    SECRET_KEY: str = "dev-insecure-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Comma-separated list of admin identities (emails or student IDs)
    ADMIN_IDENTIFIERS: str = "admin@ucla.edu"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
