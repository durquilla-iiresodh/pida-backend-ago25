import vertexai
from vertexai.generative_models import GenerativeModel
from src.config import settings, log
from src.core.prompts import PIDA_SYSTEM_PROMPT

log.info(f"--- INICIALIZANDO SDK vertexai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")
try:
    vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    model = GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info(f"--- MODELO '{settings.GEMINI_MODEL_NAME}' INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR SDK de Vertex AI: {e} ---")
    model = None

# --- CAMBIO: La función ahora acepta la ubicación ---
async def get_chat_response(prompt: str, location: str | None) -> str:
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        return "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."

    try:
        system_instruction = PIDA_SYSTEM_PROMPT
        
        # --- CAMBIO: Añadimos la ubicación al contexto si existe ---
        location_context = f"Contexto de ubicación del usuario: {location}" if location else "Contexto de ubicación del usuario: No proporcionada."
        
        final_prompt = f"{system_instruction}\n\n{location_context}\n\n---\n\nPregunta del usuario: {prompt}"
        
        response = model.generate_content(
            [final_prompt],
            generation_config={
                "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
                "temperature": settings.TEMPERATURE,
                "top_p": settings.TOP_P,
            }
        )
        
        return response.text
    
    except Exception as e:
        log.error(f"Error crítico en el cliente de Gemini: {e}", exc_info=True)
        return f"Error: {str(e)}"