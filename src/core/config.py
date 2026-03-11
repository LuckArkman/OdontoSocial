import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class FastAPIAppSettings(BaseSettings):
    """
    Configurações globais da aplicação FastAPI para o projeto OdontoSocial.
    Utiliza Pydantic V2 para validação e tipagem.
    """

    PROJECT_NAME: str = "OdontoSocial - Agente IA de Prospecção"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Celery & Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    )

    # Configurações de Ambiente
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "provisory_secret_key_for_dev_only")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Observabilidade
    SENTRY_DSN: str | None = os.getenv("SENTRY_DSN")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Banco de Dados
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "odontosocial")
    SQLALCHEMY_DATABASE_URI: str | None = os.getenv("DATABASE_URL")

    @property
    def database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> FastAPIAppSettings:
    return FastAPIAppSettings()


settings = get_settings()
