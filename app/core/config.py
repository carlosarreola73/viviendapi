import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "API Rest Certificados Vivienda Sinestry-GNP"
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000")
    GOOGLE_CREDENTIALS_JSON: str = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    BQ_DATASET: str = os.getenv("BQ_DATASET", "vivienda_infonavit")
    BQ_TABLE: str = os.getenv("BQ_TABLE", "polizas_vivienda")
    SHARED_DRIVE_ID: str = os.getenv("SHARED_DRIVE_ID", "0APoMNV1l2yBHUk9PVA")

    class Config:
        case_sensitive = True

settings = Settings()
