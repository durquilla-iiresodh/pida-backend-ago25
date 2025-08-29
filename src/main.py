# src/main.py

import json
import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    log.info("Cliente WebSocket conectado.")
    
    country_code = websocket.headers.get('X-Country-Code', None)
    
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            chat_request = ChatRequest(**data)
            
            log.info(f"Recibida petición vía WS. País: {country_code}. Historial con {len(chat_request.history)} mensajes.")

            response_stream = gemini_client.get_chat_response_stream(
                prompt=chat_request.prompt,
                history=chat_request.history,
                country_code=country_code
            )

            async for chunk in response_stream:
                await websocket.send_text(json.dumps({"text": chunk}))
            
            # --- MODIFICACIÓN CLAVE ---
            # Enviamos una señal 'done' simple, sin la respuesta completa.
            await websocket.send_text(json.dumps({"event": "done"}))

    except WebSocketDisconnect:
        log.info("Cliente WebSocket desconectado.")
    except Exception as e:
        log.error(f"Error en la conexión WebSocket: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except Exception:
            pass