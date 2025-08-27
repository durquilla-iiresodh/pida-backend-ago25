from pydantic import BaseModel

class ChatRequest(BaseModel):
    """
    Define la estructura de datos que se espera en una petición al endpoint /chat.
    """
    prompt: str