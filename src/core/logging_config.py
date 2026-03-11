import logging
import sys

from loguru import logger

from src.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Intercerpta logs padrão do Python e redireciona para o Loguru.
    """

    def emit(self, record):
        # Pega o nível correspondente do loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Encontra o chamador de onde o log se originou
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Configura o Loguru para saída estruturada (JSON em produção) e intercepta logs do FastAPI/Uvicorn.
    """
    # Remove handlers padrão do loguru
    logger.remove()

    # Adiciona saída para console com formatação rica
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        serialize=settings.ENVIRONMENT == "production",  # JSON em produção
    )

    # Intercepta logs de outras bibliotecas (uvicorn, fastapi)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "fastapi"):
        _logger = logging.getLogger(name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False

    return logger
