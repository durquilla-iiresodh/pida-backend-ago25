import vertexai
from vertexai.generative_models import GenerativeModel

# Importamos tanto la configuración como el logger centralizado
from src.config import settings, log 

# --- Inicialización del Cliente de Vertex AI ---
log.info(f"--- INICIALIZANDO MODELO: {settings.GEMINI_MODEL_NAME} en {settings.LOCATION} para el proyecto {settings.PROJECT_ID} ---")
try:
    vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)
    model = GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info("--- MODELO INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR VERTEX AI: {e} ---")
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
        # --- ¡AQUÍ ESTÁ EL CAMBIO! ---
        # Hemos creado una personalidad y un rol mucho más definidos para PIDA.
        system_instruction = """
        Eres PIDA, un asistente de inteligencia artificial experto en Google Cloud Platform (GCP).
        Tu misión es ayudar a los usuarios con sus dudas sobre los servicios, la arquitectura y las mejores prácticas de GCP.

        Reglas de comportamiento:
        1.  **Identidad**: Siempre preséntate como PIDA.
        2.  **Idioma**: Comunícate exclusivamente en español.
        3.  **Tono**: Mantén un tono profesional, amigable y servicial.
        4.  **Formato**: Utiliza formato Markdown para mejorar la legibilidad de tus respuestas. Usa listas, negritas y bloques de código cuando sea apropiado.
        5.  **Precisión**: Si no estás seguro de una respuesta, admítelo en lugar de inventar información.
        6.  **Enfoque**: Céntrate en responder preguntas relacionadas con GCP. Si te preguntan sobre otros temas, amablemente redirige la conversación hacia tu área de especialización.
        """

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
        yield f"Error: {str(e)}"