import vertexai
from vertexai.generative_models import GenerativeModel
from src.config import settings, log
from src.core.prompts import PIDA_SYSTEM_PROMPT
from src.modules.pse_client import search_for_sources

model = None
log.info(f"--- INICIALIZANDO SDK vertexai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")

try:
    vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    model = GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info(f"--- MODELO '{settings.GEMINI_MODEL_NAME}' INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR SDK de Vertex AI: {e} ---")

async def get_chat_response(prompt: str, country_code: str | None) -> str:
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        return "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."

    try:
        log.info(f"Realizando búsqueda en PSE para: '{prompt}'")
        # Aseguramos que search_for_sources sea llamado con un número suficiente de resultados
        search_context = await search_for_sources(prompt, num_results=5) # Incrementamos a 5 resultados para dar más opciones
        log.info(f"Contexto de búsqueda obtenido: {search_context[:200]}...") # Log parcial para no saturar

        system_instruction = PIDA_SYSTEM_PROMPT
        location_context = f"Contexto geográfico del usuario (código de país): {country_code}" if country_code else "Contexto geográfico del usuario: Desconocido."
        
        # Construimos el prompt final asegurando que el search_context siempre esté presente
        final_prompt = f"{system_instruction}\n\n{location_context}\n\n{search_context}\n\n---\n\nPregunta del usuario: {prompt}"
        
        log.info(f"Prompt final enviado al modelo (primeros 500 chars): {final_prompt[:500]}")

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