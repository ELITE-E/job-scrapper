import uuid
from decimal import Decimal
from typing import Optional

from .base import Base

from .mixins import UUIDPrimaryKeyMixin,TimestampMixin

from sqlalchemy import String,Numeric,ForeignKey
from sqlalchemy.orm import mapped_column,Mapped,relationship

class JobCategoryKeyword(Base,
                         UUIDPrimaryKeyMixin,
                         TimestampMixin):
    
    __tablename__="job_category_keywords"

    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=1.0)

    category: Mapped[Optional["Category"]] = relationship(back_populates="keywords")