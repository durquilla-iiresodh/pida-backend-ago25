from fastapi import FastAPI

app = FastAPI(
    title="PIDA Backend API",
    description="Servicio de backend para el asistente PIDA",
    version="1.0.0"
)

@app.get("/", tags=["Status"])
def read_root():
    """Endpoint de estado para verificar que el servicio está en línea."""
    return {"status": "ok", "message": "PIDA Backend está funcionando."}

# Aquí incluiremos los routers de otras funcionalidades en el futuro
# from .core import gemini_router
# app.include_router(gemini_router.router)