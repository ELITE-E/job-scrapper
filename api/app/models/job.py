import uuid
from decimal import Decimal
from  datetime import date,datetime

from .base import Base
from .mixins import UUIDPrimaryKeyMixin,TimestampMixin

from sqlalchemy import String,Text,ForeignKey,Numeric,text,Index,func,Date
from sqlalchemy.orm import mapped_column,Mapped,relationship
from sqlalchemy.dialects.postgresql import UUID,JSONB

from typing import Optional

class Job(Base,
          UUIDPrimaryKeyMixin,
          TimestampMixin):
    
    __tablename__="jobs"

    title:Mapped[str]=mapped_column(String(500),nullable=False)
    description:Mapped[str | None]=mapped_column(Text)
    job_url:Mapped[str]=mapped_column(String(2048),nullable=False)



    job_url_hash:Mapped[str]=mapped_column(String(64),unique=True,nullable=False,index=True)
    source_site:Mapped[str]=mapped_column(String(50),nullable=False)
    location_city:Mapped[str | None]=mapped_column(String(255))



    location_state:Mapped[str | None]=mapped_column(String(255))
    location_country:Mapped[str | None]=mapped_column(String(100))
    is_remote:Mapped[bool]=mapped_column(default=False)



    job_type:Mapped[str | None]=mapped_column(String(50))
    salary_min: Mapped[Decimal | None] =mapped_column(Numeric(12, 2))
    salary_max: Mapped[Decimal | None]= mapped_column(Numeric(12, 2))


    salary_currency: Mapped[str | None]= mapped_column(String(10))
    salary_interval: Mapped[str | None]= mapped_column(String(20)) 
    date_posted: Mapped[date | None] = mapped_column(Date)


    date_scraped: Mapped[datetime]= mapped_column(server_default=func.now())
    is_active: Mapped[bool] = mapped_column(default=True)

    extras:Mapped[dict | None]=mapped_column(JSONB,default={})

    company_id:Mapped[uuid.UUID | None]=mapped_column(ForeignKey("companies.id"))
    category_id:Mapped[uuid.UUID | None]=mapped_column(ForeignKey("categories.id"))

    company: Mapped[Optional["Company"]]= relationship(back_populates="jobs")
    category: Mapped[Optional["Category"]]= relationship(back_populates="jobs")

    __table_args__ = (
    Index(
        "ix_jobs_location",
        "location_country", "location_state", "location_city"
    ),
    Index(
        "ix_jobs_search",
        text("to_tsvector('english', title || ' ' || description)"),
        postgresql_using="gin"
    ),
    )
    