from pydantic import ConfigDict,BaseModel
import uuid
from typing import Optional
class CategoryResponse(BaseModel):

    id: uuid.UUID
    name: str
    slug: str
    description:Optional[str] = None
    job_count: int = 0 
    model_config = ConfigDict(from_attributes=True)