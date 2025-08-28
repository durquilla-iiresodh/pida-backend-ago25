import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings, log
from src.models.chat_models import ChatRequest
from src.modules import gemini_client

app = FastAPI(
    title="PIDA Backend API",
    description="Servicio de backend para el asistente PIDA con arquitectura modular.",
    version="1.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Status"])
def read_root():
    return {
        "status": "ok",
        "message": f"PIDA Backend funcionando con el modelo {settings.GEMINI_MODEL_NAME}."
    }

@app.post("/chat", tags=["Chat"])
async def chat_handler(chat_request: ChatRequest):
    
    async def stream_generator():
        try:
            # --- CAMBIO A FORMATO SSE ---
            # Cada mensaje debe empezar con "data: " y terminar con dos saltos de línea "\n\n"
            start_event = f"data: {json.dumps({'type': 'start', 'searchMode': 'none'})}\n\n"
            yield start_event

            async for text_chunk in gemini_client.stream_chat_response(chat_request.prompt):
                chunk_event = f"data: {json.dumps({'type': 'chunk', 'text': text_chunk})}\n\n"
                yield chunk_event
        
        except Exception as e:
            error_event = f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield error_event
            log.error(f"Error durante el streaming en el handler: {e}", exc_info=True)
        
        finally:
            end_event = f"data: {json.dumps({'type': 'end'})}\n\n"
            yield end_event
            log.info("Streaming de chat finalizado correctamente.")

    # --- CAMBIO A FORMATO SSE ---
    # Cambiamos el media_type a 'text/event-stream'
    return StreamingResponse(stream_generator(), media_type="text/event-stream")