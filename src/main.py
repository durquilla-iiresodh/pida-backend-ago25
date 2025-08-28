import json
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings, log
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

# --- CAMBIO: El endpoint ahora es GET y recibe el prompt como parámetro en la URL ---
@app.get("/chat", tags=["Chat"])
async def chat_handler(prompt: str = Query(..., min_length=1)):
    
    log.info(f"Recibida petición de chat (SSE) con prompt de longitud: {len(prompt)}")
    
    async def stream_generator():
        try:
            # Cada mensaje debe empezar con "data: " y terminar con dos saltos de línea "\n\n"
            start_event = f"data: {json.dumps({'type': 'start'})}\n\n"
            yield start_event

            async for text_chunk in gemini_client.stream_chat_response(prompt):
                chunk_event = f"data: {json.dumps({'type': 'chunk', 'text': text_chunk})}\n\n"
                yield chunk_event
        
        except Exception as e:
            error_event = f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield error_event
            log.error(f"Error durante el streaming SSE: {e}", exc_info=True)
        
        finally:
            # Enviamos un evento especial 'end' para que el cliente sepa que debe cerrar la conexión
            end_event = f"data: {json.dumps({'type': 'end'})}\n\n"
            yield end_event
            log.info("Streaming SSE de chat finalizado.")

    # El media_type 'text/event-stream' es la clave para que la red lo trate como un stream real
    return StreamingResponse(stream_generator(), media_type="text/event-stream")