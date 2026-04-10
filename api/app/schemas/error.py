from pydantic import BaseModel

class HTTPError(BaseModel):
    status: int
    message: str
    path: str | None = None