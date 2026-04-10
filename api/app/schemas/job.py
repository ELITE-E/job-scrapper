from pydantic import BaseModel,ConfigDict,Field
import uuid
from datetime import date,datetime
from typing import Optional,List,Dict

from .common import PaginationMeta

class CompanyBrief(BaseModel):
    name:str
    url:Optional[str] = None
    industry:Optional[str] = None
    logo_url:Optional[str] = None

    model_config=ConfigDict(from_attributes=True)

class CategoryBrief(BaseModel):
    name:str
    slug:str

    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
     id: uuid.UUID
     title: str
     company: Optional[CompanyBrief ] = None
     category: Optional[CategoryBrief] = None

     location_city: Optional[str] = None
     location_state: Optional[str] = None
     location_country: Optional[str] = None

     is_remote: bool
     job_type:Optional[str] = None

     salary_min:Optional[float] = None
     salary_max: Optional[float] = None
     salary_currency:Optional[str] = None
     salary_interval:Optional[str]  = None

     source_site: str
     job_url: str
     date_posted: Optional[date ] = None
     date_scraped: datetime

     model_config = ConfigDict(from_attributes=True)

class JonDetailResponse(JobResponse):
    description:Optional[str] = None
    extras:Dict = {}

class JobListResponse(BaseModel):
    items:List[JobResponse]
    meta:PaginationMeta

class JobFilters(BaseModel):
    category: Optional[str] =  Field(default=None, min_length=2)
    source_site: Optional[str] = None
    job_type: Optional[str] = None

    is_remote: Optional[bool] = None
    location: Optional[str | None] =  Field(default=None, min_length=2)
    search: Optional[str] = None

    min_salary: Optional[float | None] =  Field(default=None, ge=0)
    max_salary: Optional[float | None] =  Field(default=None, ge=0)