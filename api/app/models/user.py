from .base import Base
from .mixins import UUIDPrimaryKeyMixin,TimestampMixin
from sqlalchemy import String
from sqlalchemy.orm import mapped_column,Mapped

class User(Base,
           UUIDPrimaryKeyMixin,
           TimestampMixin):
    __tablename__ = "users"

    
    email:Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True)

    hashed_password:Mapped[str] = mapped_column(
        String(255),
        nullable=False)
    full_name:Mapped[str | None] = mapped_column(String(255))
    is_active:Mapped[bool] = mapped_column(default=True)
    refresh_token:Mapped[str | None] = mapped_column(String,nullable=True)

    