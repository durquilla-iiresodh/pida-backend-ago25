import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
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

# --- CAMBIO: El endpoint ahora es un POST normal que devuelve JSON ---
@app.post("/chat", tags=["Chat"])
async def chat_handler(chat_request: ChatRequest):
    log.info(f"Recibida petición de chat (no-stream) con prompt de longitud: {len(chat_request.prompt)}")
    
    try:
        # Llamamos a la nueva función y esperamos la respuesta completa
        response_text = await gemini_client.get_chat_response(chat_request.prompt)
        # Devolvemos la respuesta en un objeto JSON
        return JSONResponse(content={"text": response_text})
    except Exception as e:
        log.error(f"Error en el handler de chat: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})