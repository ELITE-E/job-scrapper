from .base import Base

from .mixins import UUIDPrimaryKeyMixin,TimestampMixin

from sqlalchemy import String,Text
from sqlalchemy.orm import mapped_column,Mapped,relationship


class Category(Base,
                 UUIDPrimaryKeyMixin,
                 TimestampMixin):
    
    __tablename__="categories"

    name:Mapped[str]=mapped_column(String(100),nullable=False)
    slug:Mapped[str]=mapped_column(String(100),unique=True,nullable=False)
    description:Mapped[str | None]=mapped_column(Text)


    jobs:Mapped[list["Job"]]=relationship(back_populates="category")
    keywords:Mapped[list["JobCategoryKeyword"]]=relationship(back_populates="category")
    

