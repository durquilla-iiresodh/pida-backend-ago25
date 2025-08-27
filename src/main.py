import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Importar la librería de Vertex AI
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# --- Configuración de la Aplicación ---
app = FastAPI(
    title="PIDA Backend API",
    description="Servicio de backend para el asistente PIDA",
    version="1.0.0"
)

# --- Configuración de CORS ---
# Permite que tu frontend se comunique con este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Puedes restringirlo a tu dominio en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuración de Variables de Entorno ---
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-1.5-pro-001")
PROJECT_ID = "pida-ago25" # Reemplaza con tu nuevo ID de proyecto si es diferente
LOCATION = "us-central1" # Reemplaza con la región de tu nuevo servicio si es diferente

print(f"--- INICIALIZANDO MODELO: {GEMINI_MODEL_NAME} en {LOCATION} ---")

# --- Inicialización del Cliente de Vertex AI ---
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(GEMINI_MODEL_NAME)

# --- Modelos de Datos (Pydantic) ---
class ChatRequest(BaseModel):
    prompt: str

# --- Endpoint de Status ---
@app.get("/", tags=["Status"])
def read_root():
    """Endpoint de estado para verificar que el servicio está en línea."""
    return {"status": "ok", "message": f"PIDA Backend funcionando con el modelo {GEMINI_MODEL_NAME}."}

# --- Endpoint de Chat con Streaming ---
@app.post("/chat", tags=["Chat"])
async def chat_handler(chat_request: ChatRequest):
    
    async def stream_generator():
        try:
            # Evento de inicio para el frontend
            yield json.dumps({"type": "start", "searchMode": "none"}) + "\n"

            # Por ahora, usamos un system prompt muy simple
            system_instruction = "Eres un asistente de IA útil y amigable."

            # Llama a la API de Gemini en modo stream
            stream = model.generate_content(
                [chat_request.prompt],
                generation_config={"max_output_tokens": 8192, "temperature": 0.7},
                system_instruction=system_instruction,
                stream=True
            )
            
            # Envía cada fragmento de texto al frontend
            for chunk in stream:
                if chunk.text:
                    yield json.dumps({"type": "chunk", "text": chunk.text}) + "\n"
        
        except Exception as e:
            print(f"Error durante el streaming: {e}")
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")