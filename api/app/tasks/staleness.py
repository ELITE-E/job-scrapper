"""
Staleness checker task for Celery.
Marks old jobs as inactive based on date_scraped.
Runs daily via Celery Beat.
"""

import logging
from datetime import datetime, timedelta, timezone
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.celery_app import app
from app.core.config import settings
from app.models import Job

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


async def mark_stale_jobs_async(stale_days: int = 30) -> dict:
    """
    Mark jobs as inactive if they were scraped more than `stale_days` ago.
    
    Args:
        stale_days: Number of days to consider a job stale (default: 30)
    
    Returns:
        Dictionary with statistics: {marked_stale_count, skipped_count}
    """
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Calculate threshold date: now - stale_days
            stale_threshold = datetime.now(timezone.utc) - timedelta(days=stale_days)
            
            # Query jobs that are:
            # 1. Currently active (is_active=True)
            # 2. Older than stale_threshold (date_scraped < threshold)
            stmt = (
                update(Job)
                .where(
                    (Job.is_active == True) &
                    (Job.date_scraped < stale_threshold)
                )
                .values(is_active=False)
            )
            
            result = await session.execute(stmt)
            marked_stale_count = result.rowcount
            
            await session.commit()
            
            logger.info(
                f"[mark_stale_jobs] Marked {marked_stale_count} jobs as inactive "
                f"(scraped before {stale_threshold.isoformat()})"
            )
            
            return {
                "marked_stale_count": marked_stale_count,
                "stale_threshold_days": stale_days,
            }
    
    except Exception as e:
        logger.error(f"[mark_stale_jobs] Error marking stale jobs: {e}", exc_info=True)
        raise
    
    finally:
        await engine.dispose()


@app.task(
    bind=True,
    name="app.tasks.mark_stale_jobs_task",
    max_retries=2,
    default_retry_delay=600,
)
def mark_stale_jobs_task(self, stale_days: int = 30, triggered_by: str = "beat"):
    """
    Celery task to mark old jobs as inactive.
    Scheduled to run daily at 3 AM UTC.
    
    Args:
        stale_days: Number of days to consider a job stale (default: 30)
        triggered_by: Source of trigger ("beat" for scheduler, or manual)
    """
    logger.info(
        f"[mark_stale_jobs_task] Starting. Triggered by: {triggered_by}. "
        f"Stale threshold: {stale_days} days"
    )
    
    try:
        with tracer.start_as_current_span("mark_stale_jobs") as span:
            span.set_attribute("staleness.triggered_by", triggered_by)
            span.set_attribute("staleness.stale_days", stale_days)
            
            # Run async operation from sync Celery task
            import asyncio
            result = asyncio.run(mark_stale_jobs_async(stale_days))
            
            span.set_attribute("staleness.marked_count", result["marked_stale_count"])
            
            logger.info(f"[mark_stale_jobs_task] Completed. Result: {result}")
            
            return result
    
    except Exception as exc:
        logger.error(
            f"[mark_stale_jobs_task] Failed (attempt {self.request.retries + 1}): {exc}",
            exc_info=True
        )
        
        current_span = trace.get_current_span()
        current_span.set_status(StatusCode.ERROR, str(exc))
        current_span.record_exception(exc)
        
        # Retry with exponential backoff
        raise self.retry(exc=exc)
