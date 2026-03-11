import sentry_sdk
from fastapi import FastAPI

from src.api.v1.router import api_router
from src.core.config import settings
from src.core.logging_config import setup_logging
from src.core.middlewares.tenant import TenantMiddleware

# Iniciar Logging
setup_logging()

# Iniciar Sentry se DSN estiver presente
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Adicionar Middlewares
app.add_middleware(TenantMiddleware)


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


@app.get("/test-error", tags=["Debug"])
async def trigger_error():
    """
    Endpoint para testar captura de erros pelo Sentry e Logs.
    """
    division_by_zero = 1 / 0
    return {"result": division_by_zero}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
