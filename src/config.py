import logging
import google.cloud.logging
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Configuración del Logging Estructurado ---
# Conecta el logger de Python a Google Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Ahora podemos usar el logger estándar de Python en cualquier parte
# y los logs aparecerán formateados en Google Cloud.
log = logging.getLogger("pida-backend")
log.setLevel(logging.INFO)


class Settings(BaseSettings):
    # Carga las variables desde un archivo .env si existe (para desarrollo local)
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Variables de GCP
    PROJECT_ID: str = "pida-ago25"
    LOCATION: str = "us-central1"

    # Variables del Modelo Gemini
    GEMINI_MODEL_NAME: str = "gemini-1.5-pro-001"
    
    # Configuración del Modelo
    MAX_OUTPUT_TOKENS: int = 8192
    TEMPERATURE: float = 0.7

# Creamos una única instancia que se importará en otros módulos
settings = Settings()

log.info(f"Configuración cargada para el proyecto: {settings.PROJECT_ID}")