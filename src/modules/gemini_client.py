# src/gemini_client.py

from vertexai.generative_models import Content
from src.models.chat_models import ChatMessage
from typing import List

def _prepare_history_for_vertex(history: List[ChatMessage]) -> List[Content]:
    """Convierte nuestro historial de Pydantic al formato que espera la API de Gemini."""
    vertex_history = []
    for message in history:
        # El formato esperado es una lista de diccionarios
        vertex_history.append({"role": message.role, "parts": [{"text": message.content}]})
    return vertex_history