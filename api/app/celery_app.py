from celery import Celery

app = Celery(
    "job_aggregator",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

app.config_from_object("celeryconfig")
app.autodiscover_tasks(["app.tasks"])
