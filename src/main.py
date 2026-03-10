from fastapi import FastAPI

from src.api.v1.router import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/healthcheck", tags=["Health"])
async def health_check():
    """
    Endpoint para verificação de integridade do sistema.
    Baseado na Sprint 01.
    """
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
