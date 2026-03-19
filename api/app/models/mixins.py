import datetime
import uuid
from typing import Optional

from sqlalchemy.orm import Mapped,mapped_column,declarative_mixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func

@declarative_mixin
class UUIDPrimaryKeyMixin:
    id:Mapped[uuid.UUID]=mapped_column(primary_key=True,
     default=uuid.uuid4)

@declarative_mixin
class TimestampMixin:
    created_at:Mapped[datetime.datetime]=mapped_column(server_default=func.now())
    updated_at:Mapped[Optional[datetime.datetime]]=mapped_column(onupdate=func.now())
