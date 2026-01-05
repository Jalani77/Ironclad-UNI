from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Comma-separated list of admin identities (emails or student IDs)
    ADMIN_IDENTIFIERS: str = "admin@ucla.edu"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
