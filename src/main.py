# src/main.py

import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings, log
from src.models.chat_models import ChatRequest
from src.modules import gemini_client

app = FastAPI(title="PIDA Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Status"])
def read_root():
    return {"status": "ok", "message": f"PIDA Backend funcionando con el modelo {settings.GEMINI_MODEL_NAME}."}

@app.post("/chat", tags=["Chat"])
async def chat_handler(chat_request: ChatRequest, request: Request):
    country_code = request.headers.get('X-Country-Code', None)
    log.info(f"Recibida petición de stream. País: {country_code}. Historial con {len(chat_request.history)} mensajes.")
    
    async def stream_generator():
        try:
            response_stream = gemini_client.get_chat_response_stream(
                prompt=chat_request.prompt,
                history=chat_request.history, 
                country_code=country_code
            )
            
            async for chunk_text in response_stream:
                yield f"data: {json.dumps({'text': chunk_text})}\n\n"
        except Exception as e:
            log.error(f"Error en el generador de stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    # --- MODIFICACIÓN CLAVE ---
    # Añadimos cabeceras para deshabilitar el buffering y forzar el streaming real.
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no" # Específico para proxies como Nginx
    }

    # Pasamos las nuevas cabeceras al StreamingResponse.
    # El media_type ahora se define dentro de los headers.
    return StreamingResponse(stream_generator(), headers=headers)