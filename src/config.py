import logging
import google.cloud.logging
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Configuración del Logging Estructurado ---
client = google.cloud.logging.Client()
client.setup_logging()

log = logging.getLogger("pida-backend")
log.setLevel(logging.INFO)


class Settings(BaseSettings):
    # Carga las variables desde un archivo .env si existe (para desarrollo local)
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Variables de GCP
    PROJECT_ID: str = "pida-ago25"
    LOCATION: str = "us-central1"

    # --- ¡CAMBIO FINAL! ---
    # Usamos el ID oficial de Gemini 2.5 Flash para Vertex AI
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    
    # Configuración del Modelo
    MAX_OUTPUT_TOKENS: int = 8192
    TEMPERATURE: float = 0.7 # El nuevo modelo soporta hasta 2.0, pero 0.7 es un buen punto de partida.

# Creamos una única instancia que se importará en otros módulos
settings = Settings()

log.info(f"Configuración cargada para el proyecto: {settings.PROJECT_ID} usando el modelo {settings.GEMINI_MODEL_NAME}")