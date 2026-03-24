from datetime import datetime
from decimal import Decimal

from .base import Base

from .mixins import UUIDPrimaryKeyMixin,TimestampMixin

from sqlalchemy import String,Text,Numeric
from sqlalchemy.orm import mapped_column,Mapped

class ScrapeLogs(Base,
                 UUIDPrimaryKeyMixin,
                 TimestampMixin):
    
    __tablename__="scrape_logs"

    task_id: Mapped[str | None] = mapped_column(String(255), unique=True) #(Celery task ID)
    site_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)# (success, failed, running)

    search_term: Mapped[str | None] = mapped_column(String(255))
    jobs_found: Mapped[int] = mapped_column(default=0)
    jobs_new: Mapped[int] = mapped_column(default=0)

    jobs_updated: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_seconds: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    started_at: Mapped[datetime | None]
    completed_at: Mapped[datetime | None]