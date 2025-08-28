import vertexai
from vertexai.generative_models import GenerativeModel
from src.config import settings, log
# --- NUEVA LÍNEA: Importamos la instrucción desde nuestro nuevo archivo ---
from src.core.prompts import PIDA_SYSTEM_PROMPT

log.info(f"--- INICIALIZANDO SDK vertexai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")
try:
    vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    model = GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info(f"--- MODELO '{settings.GEMINI_MODEL_NAME}' INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR SDK de Vertex AI: {e} ---")
    model = None


async def get_chat_response(prompt: str) -> str:
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        return "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."

    try:
        # --- CAMBIO: Usamos la constante importada ---
        system_instruction = PIDA_SYSTEM_PROMPT
        
        final_prompt = f"{system_instruction}\n\n---\n\nPregunta del usuario: {prompt}"
        
        response = model.generate_content(
            [final_prompt],
            generation_config={
                "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
                "temperature": settings.TEMPERATURE,
            }
        )
        
        return response.text
    
    except Exception as e:
        log.error(f"Error crítico en el cliente de Gemini: {e}", exc_info=True)
        return f"Error: {str(e)}"