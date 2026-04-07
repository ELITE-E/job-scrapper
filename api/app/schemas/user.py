from pydantic import ConfigDict,BaseModel,EmailStr,Field
import uuid
from typing import Optional


class UserCreate(BaseModel):
    email:EmailStr
    password:str = Field(min_length=8,max_length=128) 
    full_name: Optional[str] = None  

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name:Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)