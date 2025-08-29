import httpx
from src.config import settings, log

async def search_for_sources(query: str, num_results: int = 3) -> str:
    """
    Realiza una búsqueda en el Programmable Search Engine (PSE) de Google.
    Devuelve un string formateado con los resultados para inyectarlo en el prompt.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": settings.PSE_API_KEY,
        "cx": settings.PSE_ID,
        "q": query,
        "num": num_results
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params)
            response.raise_for_status()  # Lanza un error si la petición falla
            results = response.json()

        if "items" not in results or not results["items"]:
            log.warning(f"La búsqueda de PSE para '{query}' no arrojó resultados.")
            return "No se encontraron resultados de búsqueda externos."

        # Formateamos los resultados para que el LLM los entienda fácilmente
        formatted_results = "\n\n### Contexto de Búsqueda Externa:\n"
        for i, item in enumerate(results["items"]):
            title = item.get("title", "Sin Título")
            link = item.get("link", "#")
            snippet = item.get("snippet", "No hay descripción.").replace("\n", " ")
            formatted_results += f"{i+1}. Título: {title}\n"
            formatted_results += f"   Enlace: {link}\n"
            formatted_results += f"   Extracto: {snippet}\n"
        
        return formatted_results

    except httpx.HTTPStatusError as e:
        log.error(f"Error en la API de PSE: {e.response.status_code} - {e.response.text}")
        return "Hubo un error al realizar la búsqueda externa."
    except Exception as e:
        log.error(f"Error inesperado en el cliente de PSE: {e}")
        return "Hubo un error inesperado al realizar la búsqueda externa."