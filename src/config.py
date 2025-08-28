import logging
import google.cloud.logging
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Configuración del Logging Estructurado ---
client = google.cloud.logging.Client()
client.setup_logging()

log = logging.getLogger("pida-backend")
log.setLevel(logging.INFO)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Lee estas variables directamente del entorno establecido en Cloud Run
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str

    # --- CORRECCIÓN FINAL: Usando el modelo correcto y disponible ---
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"

    # Configuración del Modelo
    MAX_OUTPUT_TOKENS: int = 8192
    TEMPERATURE: float = 0.7

# Creamos una única instancia que se importará en otros módulos
settings = Settings()

log.info(f"Configuración cargada para el proyecto: {settings.GOOGLE_CLOUD_PROJECT}")