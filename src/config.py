import logging
import google.cloud.logging
from pydantic_settings import BaseSettings, SettingsConfigDict

client = google.cloud.logging.Client()
client.setup_logging()
log = logging.getLogger("pida-backend")
log.setLevel(logging.INFO)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    
    # --- PARÁMETROS DEL MODELO ACTUALIZADOS ---
    MAX_OUTPUT_TOKENS: int = 16384
    TEMPERATURE: float = 0.5
    TOP_P: float = 0.95

settings = Settings()
log.info(f"Configuración cargada para el proyecto: {settings.GOOGLE_CLOUD_PROJECT}")