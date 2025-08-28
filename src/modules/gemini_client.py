import vertexai
from vertexai.generative_models import GenerativeModel
from src.config import settings, log

# --- Inicialización del Cliente con la librería original y variables correctas ---
log.info(f"--- INICIALIZANDO SDK vertexai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")
try:
    # Ahora usamos los nombres correctos leídos desde el entorno
    vertexai.init(project=settings.GOOGLE_CLOUD_PROJECT, location=settings.GOOGLE_CLOUD_LOCATION)
    model = GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info(f"--- MODELO '{settings.GEMINI_MODEL_NAME}' INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR SDK de Vertex AI: {e} ---")
    model = None


async def stream_chat_response(prompt: str):
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        yield "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."
        return

    try:
        # En esta librería, la instrucción de sistema va dentro de la llamada
        system_instruction = "Eres PIDA, un asistente de IA útil y amigable."
        
        stream = model.generate_content(
            [system_instruction, prompt], # Pasamos la instrucción como parte de los contenidos
            generation_config={
                "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
                "temperature": settings.TEMPERATURE,
            },
            stream=True
        )
        
        for chunk in stream:
            # La librería original a veces devuelve un chunk inicial vacío
            if chunk.text:
                yield chunk.text
    
    except Exception as e:
        log.error(f"Error crítico en el cliente de Gemini durante el streaming: {e}", exc_info=True)
        yield f"Error: {str(e)}"