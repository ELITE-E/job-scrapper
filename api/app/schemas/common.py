from pydantic import BaseModel


class PaginationMeta(BaseModel):
    total:int
    page:int
    size:int
    has_next:bool
    has_prev:bool

class HTTPError(BaseModel):
    detail:str