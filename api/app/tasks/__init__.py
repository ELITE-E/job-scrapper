import asyncio
import logging
import traceback

from opentelemetry import trace
from opentelemetry.trace import StatusCode
from redis import Redis

from app.celery_app import app
from app.core.config import settings
from app.tasks.db_logging import (
    log_scrape_failure,
    log_scrape_start,
    log_scrape_success,
)
from app.scrapper import run_full_scrape

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


@app.task(
    bind=True,
    name="app.tasks.scrape_jobs_task",
    max_retries=3,
    default_retry_delay=300,
    soft_time_limit=3600,
    time_limit=7200,
)
def scrape_jobs_task(self, triggered_by="beat"):
    logger.info(
        "[scrape_jobs_task] Starting. Attempt %s of %s",
        self.request.retries + 1,
        self.max_retries + 1,
    )

    lock_acquired = False
    redis_client = None
    try:
        redis_client = Redis.from_url(
            str(settings.REDIS_URL),
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        lock_acquired = redis_client.set("scrape_lock", "1", ex=21600, nx=True)
        if not lock_acquired:
            logger.info("[scrape_jobs_task] Lock exists; skipping run")
    except Exception as lock_err:
        logger.warning(
            "[scrape_jobs_task] Lock unavailable; continuing without lock: %s",
            lock_err,
        )
        redis_client = None

    log_id = None
    try:
        if lock_acquired or redis_client is None:
            log_id = log_scrape_start(
                task_id=self.request.id,
                site_name="all",
                triggered_by=triggered_by,
            )
    except Exception as db_err:
        logger.warning("[scrape_jobs_task] Could not write start log: %s", db_err)

    if redis_client is not None and not lock_acquired:
        stats = {
            "jobs_added": 0,
            "jobs_duplicates": 0,
        }
        logger.info("[scrape_jobs_task] Skipped due to lock")
        if log_id is not None:
            log_scrape_success(log_id, stats)
        return stats

    try:
        with tracer.start_as_current_span("run_full_scrape") as span:
            span.set_attribute("scraper.triggered_by", triggered_by)
            span.set_attribute("scraper.task_id", self.request.id or "unknown")
            span.set_attribute("scraper.retry_count", self.request.retries)
            
            results = asyncio.run(run_full_scrape())
            jobs_added = sum(result.jobs_new for result in results)
            jobs_duplicates = sum(result.jobs_duplicates for result in results)
            stats = {
                "jobs_added": jobs_added,
                "jobs_duplicates": jobs_duplicates,
            }
            
            span.set_attribute("scraper.jobs_added", jobs_added)
            span.set_attribute("scraper.jobs_duplicates", jobs_duplicates)
            
            logger.info("[scrape_jobs_task] Completed. Stats: %s", stats)

            if log_id is not None:
                log_scrape_success(log_id, stats)

            return stats
    except Exception as exc:
        traceback_str = traceback.format_exc()
        
        # Phase 9: Detect rate limit hits
        error_msg = str(exc).lower()
        if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
            logger.warning(
                "[scrape_jobs_task] 🔴 RATE LIMIT HIT detected. "
                "Celery will retry in %s seconds. Attempt %s of %s",
                self.default_retry_delay,
                self.request.retries + 1,
                self.max_retries + 1,
            )
        
        logger.error("[scrape_jobs_task] Failed: %s\n%s", exc, traceback_str)
        
        # Record the exception in the current span
        current_span = trace.get_current_span()
        current_span.set_status(StatusCode.ERROR, str(exc))
        current_span.record_exception(exc)

        if log_id is not None:
            log_scrape_failure(log_id, str(exc), traceback_str)

        raise self.retry(exc=exc)
    finally:
        if lock_acquired and redis_client is not None:
            try:
                redis_client.delete("scrape_lock")
            except Exception:
                logger.warning("[scrape_jobs_task] Failed to release lock")
