from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    prompt: str
    # Nuevo campo opcional para la ubicación
    location: Optional[str] = None