import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings, log
from src.models.chat_models import ChatRequest # <-- Se usa el modelo actualizado
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
async def chat_handler(chat_request: ChatRequest):
    log.info(f"Recibida petición de chat con prompt de longitud: {len(chat_request.prompt)}")
    
    try:
        # --- CAMBIO: Pasamos la ubicación recibida a la función del cliente ---
        response_text = await gemini_client.get_chat_response(
            prompt=chat_request.prompt, 
            location=chat_request.location
        )
        return JSONResponse(content={"text": response_text})
    except Exception as e:
        log.error(f"Error en el handler de chat: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})