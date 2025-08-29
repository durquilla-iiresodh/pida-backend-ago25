import httpx
from bs4 import BeautifulSoup
from src.config import settings, log

async def _fetch_and_parse_url(url: str, client: httpx.AsyncClient) -> str:
    """Función auxiliar para descargar y extraer el texto de una URL."""
    try:
        # Añadimos un user-agent para simular un navegador y evitar bloqueos
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = await client.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        
        # Usamos BeautifulSoup con lxml para parsear el HTML y extraer el texto
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extraemos el texto de los párrafos y lo unimos
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        content = " ".join(paragraphs).replace("\n", " ").strip()
        
        # Devolvemos los primeros 5000 caracteres para no exceder el límite de contexto
        return content[:5000]
    except Exception as e:
        log.warning(f"No se pudo obtener el contenido de la URL {url}: {e}")
        return "No se pudo extraer contenido de esta fuente."

async def search_for_sources(query: str, num_results: int = 3) -> str:
    """
    Realiza una búsqueda en el PSE y ahora también extrae el contenido de las páginas.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": settings.PSE_API_KEY, "cx": settings.PSE_ID, "q": query, "num": num_results}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params)
            response.raise_for_status()
            results = response.json()

        if "items" not in results or not results["items"]:
            log.warning(f"La búsqueda de PSE para '{query}' no arrojó resultados.")
            return "No se encontraron resultados de búsqueda externos."

        formatted_results = "\n\n### Contexto de Búsqueda Externa:\n"
        for i, item in enumerate(results["items"]):
            title = item.get("title", "Sin Título")
            link = item.get("link", "#")
            
            # --- CAMBIO CLAVE: Obtenemos el contenido completo de la página ---
            page_content = await _fetch_and_parse_url(link, client)
            
            formatted_results += f"{i+1}. Título: {title}\n"
            formatted_results += f"   Enlace: {link}\n"
            # Le pasamos el contenido completo en lugar del extracto
            formatted_results += f"   Contenido de la Página: {page_content}\n"
        
        return formatted_results

    except Exception as e:
        log.error(f"Error inesperado en el cliente de PSE: {e}")
        return "Hubo un error al realizar la búsqueda externa."