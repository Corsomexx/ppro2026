import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Půjčovna vybavení Hory a voda"
    PROJECT_VERSION: str = "1.0.0"
    
    # Výchozí fallback na lokální SQLite soubor pro okamžitý start,
    # v Dockeru je předávána proměnná DATABASE_URL na PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./rental.db")
    
    # Automatický seeding při startu, pokud je DB prázdná
    SEED_ON_STARTUP: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
