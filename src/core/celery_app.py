from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "worker", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Descobrir tarefas automaticamente nos pacotes especificados
    task_track_started=True,
)

# Auto-discover tasks in src.tasks
celery_app.autodiscover_tasks(["src.tasks"])
