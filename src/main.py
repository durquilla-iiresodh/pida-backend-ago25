# src/main.py

import json
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

# --- ENDPOINT DE WEBSOCKET ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    log.info("Cliente WebSocket conectado.")
    
    # Obtenemos el código de país de las cabeceras durante la conexión inicial
    country_code = websocket.headers.get('X-Country-Code', None)
    
    try:
        while True:
            # 1. Espera a recibir un mensaje del cliente
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            # Usamos Pydantic para validar los datos recibidos
            chat_request = ChatRequest(**data)
            
            log.info(f"Recibida petición vía WS. País: {country_code}. Historial con {len(chat_request.history)} mensajes.")

            # 2. Obtiene el stream de Gemini
            response_stream = gemini_client.get_chat_response_stream(
                prompt=chat_request.prompt,
                history=chat_request.history,
                country_code=country_code
            )

            # 3. Envía cada fragmento al cliente a través del WebSocket
            full_response = ""
            async for chunk in response_stream:
                full_response += chunk
                # Enviamos cada fragmento como un evento de texto
                await websocket.send_text(json.dumps({"text": chunk}))
            
            # 4. Envía un mensaje final para indicar que el stream ha terminado
            await websocket.send_text(json.dumps({"event": "done", "full_response": full_response}))

    except WebSocketDisconnect:
        log.info("Cliente WebSocket desconectado.")
    except Exception as e:
        log.error(f"Error en la conexión WebSocket: {e}", exc_info=True)
        # Intenta enviar un mensaje de error si la conexión aún está abierta
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except Exception:
            pass # La conexión ya podría estar cerrada