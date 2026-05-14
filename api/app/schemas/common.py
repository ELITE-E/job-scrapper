from pydantic import BaseModel, Field
from math import ceil


class PaginationMeta(BaseModel):
    total: int
    page: int
    size: int
    pages: int = Field(default=0, description="Total number of pages")
    has_next: bool
    has_prev: bool
    
    @property
    def computed_pages(self) -> int:
        """Compute total pages if not already set"""
        if self.pages > 0:
            return self.pages
        return ceil(self.total / self.size) if self.size > 0 else 0

class HTTPError(BaseModel):
    detail:str