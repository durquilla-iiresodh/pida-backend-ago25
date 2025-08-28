import google.generativeai as genai
from src.config import settings, log

# --- Inicialización del Cliente ---
log.info(f"--- INICIALIZANDO SDK google-genai para el modelo '{settings.GEMINI_MODEL_NAME}' ---")
try:
    model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info(f"--- MODELO '{settings.GEMINI_MODEL_NAME}' INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR EL SDK de Gen AI: {e} ---")
    model = None


async def stream_chat_response(prompt: str):
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        yield "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."
        return

    try:
        system_instruction = """
        Eres PIDA, un asistente de inteligencia artificial experto en Google Cloud Platform (GCP).
        Tu misión es ayudar a los usuarios con sus dudas sobre los servicios, la arquitectura y las mejores prácticas de GCP.
        """

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=settings.MAX_OUTPUT_TOKENS,
            temperature=settings.TEMPERATURE
        )

        stream = model.generate_content(
            contents=[prompt],
            generation_config=generation_config,
            system_instruction=system_instruction,
            stream=True
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        log.error(f"Error crítico en el cliente de Gemini durante el streaming: {e}", exc_info=True)
        yield f"Error: {str(e)}"