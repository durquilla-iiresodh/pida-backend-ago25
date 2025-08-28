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
    version="1.6.0"
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
            yield json.dumps({"type": "start"}) + "\n"
            async for text_chunk in gemini_client.stream_chat_response(chat_request.prompt):
                yield json.dumps({"type": "chunk", "text": text_chunk}) + "\n"
        except Exception as e:
            log.error(f"Error durante el streaming en el handler: {e}", exc_info=True)
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"
        finally:
            yield json.dumps({"type": "end"}) + "\n"
            log.info("Streaming de chat finalizado correctamente.")

    # Añadimos las cabeceras anti-buffering que pueden ayudar
    headers = {
        "Content-Type": "application/x-ndjson",
        "X-Accel-Buffering": "no",
        "Cache-Control": "no-cache",
    }
    return StreamingResponse(stream_generator(), headers=headers)