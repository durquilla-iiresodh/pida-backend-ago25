# src/main.py

import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse # MODIFICADO: Importamos StreamingResponse
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
    
    # MODIFICADO: Creamos un generador para el streaming
    async def stream_generator():
        try:
            # Obtenemos el generador de respuesta desde el cliente de Gemini
            response_stream = gemini_client.get_chat_response_stream(
                prompt=chat_request.prompt,
                history=chat_request.history, 
                country_code=country_code
            )
            
            # Iteramos sobre cada fragmento de texto que nos llega
            async for chunk_text in response_stream:
                # Lo envolvemos en un formato de evento de servidor (SSE)
                # El cliente buscará la línea "data:" para obtener el contenido.
                yield f"data: {json.dumps({'text': chunk_text})}\n\n"
        except Exception as e:
            log.error(f"Error en el generador de stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    # Devolvemos un StreamingResponse que ejecutará nuestro generador
    return StreamingResponse(stream_generator(), media_type="text/event-stream")