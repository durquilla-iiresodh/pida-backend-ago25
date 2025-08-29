import vertexai
from vertexai.generative_models import GenerativeModel
from src.config import settings, log
from src.core.prompts import PIDA_SYSTEM_PROMPT
from src.modules.pse_client import search_for_sources

# --- CAMBIO: Definimos 'model' fuera del try/except con un valor inicial ---
model = None
log.info(f"--- INICIALIZANDO SDK vertexai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")

try:
    vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    # Asignamos el modelo a la variable que ya existe
    model = GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info(f"--- MODELO '{settings.GEMINI_MODEL_NAME}' INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    # Si falla, el log lo registrará y 'model' permanecerá como None
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR SDK de Vertex AI: {e} ---")


async def get_chat_response(prompt: str, location: str | None) -> str:
    # Esta comprobación ahora funcionará siempre, porque 'model' siempre existirá
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        return "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."

    try:
        log.info(f"Realizando búsqueda en PSE para: '{prompt}'")
        search_context = await search_for_sources(prompt)
        log.info(f"Contexto de búsqueda obtenido.")

        system_instruction = PIDA_SYSTEM_PROMPT
        location_context = f"Contexto de ubicación del usuario: {location}" if location else "Contexto de ubicación del usuario: No proporcionada."
        
        final_prompt = f"{system_instruction}\n\n{location_context}\n\n{search_context}\n\n---\n\nPregunta del usuario: {prompt}"
        
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