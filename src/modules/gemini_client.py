# src/modules/gemini_client.py

import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
from src.config import settings, log
from src.core.prompts import PIDA_SYSTEM_PROMPT
from src.modules.pse_client import search_for_sources
from src.models.chat_models import ChatMessage
from typing import List

model = None
log.info(f"--- INICIALIZANDO SDK vertexai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")

try:
    vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    # Pasamos la instrucción del sistema directamente al inicializar el modelo
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
        # El rol 'model' en nuestra app equivale a 'model' en Vertex AI.
        # El rol 'user' en nuestra app equivale a 'user' en Vertex AI.
        vertex_history.append(Content(role=message.role, parts=[Part.from_text(message.content)]))
    return vertex_history

async def get_chat_response(prompt: str, history: List[ChatMessage], country_code: str | None) -> str:
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        return "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."

    try:
        log.info(f"Realizando búsqueda en PSE para: '{prompt}'")
        search_context = await search_for_sources(prompt, num_results=5)
        log.info(f"Contexto de búsqueda obtenido: {search_context[:200]}...")

        location_context = f"Contexto geográfico del usuario (código de país): {country_code}" if country_code else "Contexto geográfico del usuario: Desconocido."

        # Construimos el prompt final que se enviará en este turno
        final_user_prompt = f"{location_context}\n\n{search_context}\n\n---\n\nPregunta del usuario: {prompt}"

        # Preparamos el historial para el SDK
        vertex_history = _prepare_history_for_vertex(history)

        # Iniciamos una sesión de chat con el historial previo
        chat = model.start_chat(history=vertex_history)

        log.info(f"Prompt final enviado al modelo (primeros 500 chars): {final_user_prompt[:500]}")

        # Enviamos el nuevo mensaje (con contexto) a la sesión de chat
        response = chat.send_message(
            [final_user_prompt],
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