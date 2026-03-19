from .base import Base

from .mixins import UUIDPrimaryKeyMixin,TimestampMixin
from sqlalchemy import String,Text
from sqlalchemy.orm import mapped_column,Mapped,relationship

class Company(Base,
              UUIDPrimaryKeyMixin,
              TimestampMixin):
    __tablename__="companies"

    name:Mapped[str]=mapped_column(String(500),nullable=False,unique=True)
    url:Mapped[str | None]=mapped_column(String(2048))

    logo_url:Mapped[str | None]=mapped_column(String(225))
    industry:Mapped[str | None]=mapped_column(String(225))

    description:Mapped[str | None]=mapped_column(Text)
    employees_label:Mapped[str | None]=mapped_column(String(100))

    jobs:Mapped[list["Job"]]=relationship(back_populates="company")