import os

from celery import Celery
from celery.signals import worker_process_init

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


# Step 8: Initialize OpenTelemetry inside each prefork worker child process
@worker_process_init.connect(weak=False)
def init_worker_tracing(*args, **kwargs):
    """
    Initialize OpenTelemetry tracing inside each Celery prefork worker child process.


    Imports are deliberately inside the function (not at module top) to avoid
    circular imports: celery_app is imported by app.tasks, and evaluating
    app.telemetry at module level would break initialization order.
    """
    from app.telemetry import setup_worker_telemetry
    from opentelemetry.instrumentation.celery import CeleryInstrumentor

    setup_worker_telemetry()
    CeleryInstrumentor().instrument()
