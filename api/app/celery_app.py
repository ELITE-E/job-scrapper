from celery import Celery

from app.core.config import settings

app = Celery(
    "job_aggregator",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
)

app.config_from_object("celeryconfig")
app.autodiscover_tasks(["app.tasks"])
