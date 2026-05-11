import os

from celery import Celery

from app.core.config import settings

broker_url = os.getenv("CELERY_BROKER_URL", str(settings.REDIS_URL))
result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)

app = Celery(
    "job_aggregator",
    broker=broker_url,
    backend=result_backend,
)

app.config_from_object("celeryconfig")
app.autodiscover_tasks(["app.tasks"])
