import google.generativeai as genai
from src.config import settings, log

# --- Configuración e Inicialización del Cliente ---
# La nueva librería se configura una sola vez y se conecta a Vertex AI
# gracias a las variables de entorno que definiremos en el despliegue.
log.info(f"--- INICIALIZANDO SDK google-genai para Vertex AI en el proyecto {settings.PROJECT_ID} ---")
try:
    genai.configure(
        project=settings.PROJECT_ID,
        location=settings.LOCATION,
    )
    model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
    log.info(f"--- MODELO '{settings.GEMINI_MODEL_NAME}' INICIALIZADO CORRECTAMENTE ---")
except Exception as e:
    log.critical(f"--- ERROR CRÍTICO AL INICIALIZAR EL SDK de Gen AI: {e} ---")
    model = None


async def stream_chat_response(prompt: str):
    """
    Genera una respuesta de chat en streaming utilizando el modelo Gemini
    a través del nuevo SDK google-genai.
    """
    if not model:
        log.error("El modelo Gemini no está disponible. Revisa los logs de inicialización.")
        yield "Error: El modelo de IA no pudo ser cargado. Contacte al administrador."
        return

    try:
        system_instruction = """
        Eres PIDA, un asistente de inteligencia artificial experto en Google Cloud Platform (GCP).
        Tu misión es ayudar a los usuarios con sus dudas sobre los servicios, la arquitectura y las mejores prácticas de GCP.
        Reglas de comportamiento:
        1.  **Identidad**: Siempre preséntate como PIDA.
        2.  **Idioma**: Comunícate exclusivamente en español.
        3.  **Tono**: Mantén un tono profesional, amigable y servicial.
        4.  **Formato**: Utiliza formato Markdown para mejorar la legibilidad. Usa listas, negritas y bloques de código.
        5.  **Precisión**: Si no estás seguro de una respuesta, admítelo.
        6.  **Enfoque**: Céntrate en responder preguntas relacionadas con GCP.
        """
        
        # La nueva sintaxis pasa la configuración en un objeto 'generation_config'
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