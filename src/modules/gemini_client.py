# src/modules/gemini_client.py

import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
from src.config import settings, log
from src.core.prompts import PIDA_SYSTEM_PROMPT
from src.modules.pse_client import search_for_sources
from src.models.chat_models import ChatMessage
from typing import List, AsyncGenerator

model = None
log.info(f"--- INICIALIZANDO SDK vertexai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")

try:
    vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    model = GenerativeModel(
        settings.GEMINI_MODEL_NAME,
        system_instruction=PIDA_SYSTEM_PROMPT
    )
    log.info(f"--- MODELO '{settings.GEMINI_MODEL_NAME}' INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR SDK de Vertex AI: {e} ---")

def _prepare_history_for_vertex(history: List[ChatMessage]) -> List[Content]:
    """Convierte nuestro historial de Pydantic al formato que espera Vertex AI SDK."""
    vertex_history = []
    for message in history:
        vertex_history.append(Content(role=message.role, parts=[Part.from_text(message.content)]))
    return vertex_history

# MODIFICADO: Ahora es un generador asíncrono que devuelve un stream de strings
async def get_chat_response_stream(prompt: str, history: List[ChatMessage], country_code: str | None) -> AsyncGenerator[str, None]:
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        yield "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."
        return

    try:
        log.info(f"Realizando búsqueda en PSE para: '{prompt}'")
        search_context = await search_for_sources(prompt, num_results=5)
        log.info(f"Contexto de búsqueda obtenido: {search_context[:200]}...")

        location_context = f"Contexto geográfico del usuario (código de país): {country_code}" if country_code else "Contexto geográfico del usuario: Desconocido."
        final_user_prompt = f"{location_context}\n\n{search_context}\n\n---\n\nPregunta del usuario: {prompt}"

        vertex_history = _prepare_history_for_vertex(history)
        chat = model.start_chat(history=vertex_history)

        log.info(f"Prompt final enviado al modelo (primeros 500 chars): {final_user_prompt[:500]}")

        # MODIFICADO: Se añade stream=True para obtener la respuesta en fragmentos
        response_stream = chat.send_message(
            [final_user_prompt],
            stream=True,
            generation_config={
                "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
                "temperature": settings.TEMPERATURE,
                "top_p": settings.TOP_P,
            }
        )
        
        # MODIFICADO: Iteramos sobre los fragmentos y los 'cedemos' (yield) uno por uno
        async for chunk in response_stream:
            yield chunk.text
    
    except Exception as e:
        log.error(f"Error crítico en el cliente de Gemini: {e}", exc_info=True)
        yield f"Error: {str(e)}"