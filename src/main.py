import json
from fastapi import FastAPI, Request
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

@app.post("/chat", tags=["Chat"])
async def chat_handler(chat_request: ChatRequest, request: Request):
    # Obtenemos el código del país desde las cabeceras que añade Cloud Run
    country_code = request.headers.get('X-Country-Code', None)
    log.info(f"Recibida petición. País detectado: {country_code}")
    
    try:
        response_text = await gemini_client.get_chat_response(
            prompt=chat_request.prompt, 
            country_code=country_code
        )
        return JSONResponse(content={"text": response_text})
    except Exception as e:
        log.error(f"Error en el handler de chat: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})