# src/main.py

import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings, log
from src.models.chat_models import ChatRequest
from src.modules import pse_client, gemini_client

app = FastAPI(title="PIDA Backend API - Logic Only")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite el acceso desde tu VM
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Status"])
def read_root():
    return {"status": "ok", "message": f"PIDA Backend de Lógica funcionando."}

@app.post("/prepare-prompt", tags=["Prompt Preparation"])
async def prepare_prompt_handler(chat_request: ChatRequest, request: Request):
    try:
        country_code = request.headers.get('X-Country-Code', None)
        log.info(f"Recibida petición para preparar prompt. País: {country_code}")

        # 1. Realizar la búsqueda de fuentes
        search_context = await pse_client.search_for_sources(chat_request.prompt, num_results=5)
        
        # 2. Construir el prompt final para Gemini
        location_context = f"Contexto geográfico: {country_code}" if country_code else "Contexto geográfico: Desconocido."
        final_prompt = f"{location_context}\n\n{search_context}\n\n---\n\nPregunta: {chat_request.prompt}"

        # 3. Formatear el historial para la API de Gemini
        history_for_gemini = gemini_client._prepare_history_for_vertex(chat_request.history)
        
        return JSONResponse(content={
            "final_prompt": final_prompt,
            "history_for_gemini": history_for_gemini
        })

    except Exception as e:
        log.error(f"Error preparando el prompt: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})