import vertexai
from vertexai.generative_models import GenerativeModel

# Importamos tanto la configuración como el logger centralizado
from src.config import settings, log 

# --- Inicialización del Cliente de Vertex AI ---
# Se ejecuta una sola vez cuando se carga el módulo
log.info(f"--- INICIALIZANDO MODELO: {settings.GEMINI_MODEL_NAME} en {settings.LOCATION} para el proyecto {settings.PROJECT_ID} ---")
try:
    vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)
    model = GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info("--- MODELO INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR VERTEX AI: {e} ---")
    # En un caso real, esto podría impedir que la app se inicie.
    model = None


async def stream_chat_response(prompt: str):
    """
    Genera una respuesta de chat en streaming utilizando el modelo Gemini.
    Utiliza un generador asíncrono para enviar los trozos de respuesta.
    """
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        yield "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."
        return

    try:
        # Por ahora, usamos un system prompt muy simple
        system_instruction = "Eres un asistente de IA útil y amigable llamado PIDA."

        # Llama a la API de Gemini en modo stream
        stream = model.generate_content(
            [prompt],
            generation_config={
                "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
                "temperature": settings.TEMPERATURE,
            },
            system_instruction=system_instruction,
            stream=True
        )
        
        # Envía cada fragmento de texto
        for chunk in stream:
            if chunk.text:
                yield chunk.text
    
    except Exception as e:
        log.error(f"Error crítico en el cliente de Gemini durante el streaming: {e}", exc_info=True)
        # En caso de error, también lo enviamos como parte del stream
        yield f"Error: {str(e)}"