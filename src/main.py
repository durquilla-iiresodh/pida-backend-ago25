import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Importaciones de nuestros módulos, modelos y ahora el logger
from src.config import settings, log
from src.models.chat_models import ChatRequest
from src.modules import gemini_client

# --- Configuración de la Aplicación ---
app = FastAPI(
    title="PIDA Backend API",
    description="Servicio de backend para el asistente PIDA con arquitectura modular.",
    version="1.2.0" # Incrementamos la versión
)

# --- Configuración de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint de Status ---
@app.get("/", tags=["Status"])
def read_root():
    """Endpoint de estado para verificar que el servicio está en línea."""
    log.info("Health check endpoint invocado.")
    return {
        "status": "ok",
        "message": f"PIDA Backend funcionando con el modelo {settings.GEMINI_MODEL_NAME}."
    }

# --- Endpoint de Chat con Streaming ---
@app.post("/chat", tags=["Chat"])
async def chat_handler(chat_request: ChatRequest):
    
    log.info(f"Recibida petición de chat con prompt de longitud: {len(chat_request.prompt)}")
    
    async def stream_generator():
        try:
            # Evento de inicio para el frontend
            yield json.dumps({"type": "start", "searchMode": "none"}) + "\n"

            # Delegamos TODA la lógica a nuestro módulo cliente de Gemini
            async for text_chunk in gemini_client.stream_chat_response(chat_request.prompt):
                yield json.dumps({"type": "chunk", "text": text_chunk}) + "\n"
        
        except Exception as e:
            # Usamos exc_info=True para capturar el stack trace completo en los logs de GCP
            log.error(f"Error durante el streaming en el handler: {e}", exc_info=True)
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"
        
        finally:
            # Evento de fin para el frontend
            log.info("Streaming de chat finalizado correctamente.")
            yield json.dumps({"type": "end"}) + "\n"

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")