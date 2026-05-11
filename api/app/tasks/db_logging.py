from contextlib import contextmanager
from datetime import UTC, datetime
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.scrape_log import ScrapeLog

SYNC_DATABASE_URL = str(settings.SYNC_DATABASE_URL)

sync_engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
SyncSession = sessionmaker(bind=sync_engine)

logger = logging.getLogger(__name__)


@contextmanager
def get_sync_session():
    session = SyncSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def log_scrape_start(task_id: str, site_name: str, triggered_by: str = "beat") -> int:
    with get_sync_session() as session:
        log_entry = ScrapeLog(
            status="STARTED",
            started_at=datetime.now(UTC),
            task_id=task_id,
            triggered_by=triggered_by,
            site_name=site_name,
        )
        session.add(log_entry)
        session.flush()
        session.commit()
        session.refresh(log_entry)
        return int(log_entry.id)


def log_scrape_success(log_id: int, stats: dict) -> None:
    with get_sync_session() as session:
        log_entry = session.get(ScrapeLog, log_id)
        if log_entry is None:
            raise ValueError(f"ScrapeLog id={log_id} not found")

        required_keys = {"jobs_added", "jobs_duplicates"}
        missing_keys = required_keys - stats.keys()
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            logger.error("Missing stats keys for ScrapeLog %s: %s", log_id, missing)
            raise ValueError(f"Missing stats keys: {missing}")

        finished_at = datetime.now(UTC)
        log_entry.status = "SUCCESS"
        log_entry.completed_at = finished_at
        log_entry.jobs_new = stats["jobs_added"]
        log_entry.jobs_duplicates = stats["jobs_duplicates"]

        if log_entry.started_at is not None:
            log_entry.duration_seconds = (
                finished_at - log_entry.started_at
            ).total_seconds()


def log_scrape_failure(log_id: int, error_message: str, error_traceback: str) -> None:
    with get_sync_session() as session:
        log_entry = session.get(ScrapeLog, log_id)
        if log_entry is None:
            raise ValueError(f"ScrapeLog id={log_id} not found")

        finished_at = datetime.now(UTC)
        log_entry.status = "FAILURE"
        log_entry.completed_at = finished_at
        log_entry.error_message = error_message
        log_entry.error_traceback = error_traceback

        if log_entry.started_at is not None:
            log_entry.duration_seconds = (
                finished_at - log_entry.started_at
            ).total_seconds()
