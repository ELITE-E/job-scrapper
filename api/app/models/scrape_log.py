from datetime import datetime
from decimal import Decimal

from .base import Base

from .mixins import UUIDPrimaryKeyMixin,TimestampMixin

from sqlalchemy import String,Text,Numeric,Index
from sqlalchemy.orm import mapped_column,Mapped

class ScrapeLog(Base,
                 UUIDPrimaryKeyMixin,
                 TimestampMixin):
    
    __tablename__="scrape_logs"

    __table_args__ = (
        Index('ix_scrape_logs_started_at', 'started_at'),
        Index('ix_scrape_logs_status', 'status'),
    )

    task_id: Mapped[str | None] = mapped_column(String(255), unique=True) #(Celery task ID)
    site_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)# (success, failed, running)

    jobs_found: Mapped[int] = mapped_column(default=0)
    jobs_new: Mapped[int] = mapped_column(default=0)

    error_message: Mapped[str | None] = mapped_column(Text)
    error_traceback: Mapped[str | None] = mapped_column(Text)
    
    duration_seconds: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
     
    triggered_by: Mapped[str | None] = mapped_column(String(100))

    jobs_duplicates: Mapped[int] = mapped_column(default=0)

    started_at: Mapped[datetime | None]
    completed_at: Mapped[datetime | None]

    def __repr__(self) -> str:
        return (
            f"<ScrapeLog id={self.id} status={self.status} jobs_added={self.jobs_found} site={self.site_name}>"
        )