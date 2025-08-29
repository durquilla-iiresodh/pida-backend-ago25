import vertexai
from vertexai.generative_models import GenerativeModel
from src.config import settings, log
from src.core.prompts import PIDA_SYSTEM_PROMPT
# --- NUEVA LÍNEA: Importamos nuestro cliente de búsqueda ---
from src.modules.pse_client import search_for_sources


log.info(f"--- INICIALIZANDO SDK vertexai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")
# ... (bloque try/except de inicialización sin cambios) ...


async def get_chat_response(prompt: str, location: str | None) -> str:
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        return "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."

    try:
        # --- NUEVO: Realizamos la búsqueda externa ANTES de llamar a Gemini ---
        log.info(f"Realizando búsqueda en PSE para: '{prompt}'")
        search_context = await search_for_sources(prompt)
        log.info(f"Contexto de búsqueda obtenido.")

        system_instruction = PIDA_SYSTEM_PROMPT
        location_context = f"Contexto de ubicación del usuario: {location}" if location else "Contexto de ubicación del usuario: No proporcionada."
        
        # --- CAMBIO: Inyectamos el contexto de búsqueda en el prompt final ---
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