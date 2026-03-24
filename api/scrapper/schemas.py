from pydantic_settings import ConfigDict,BaseModel
from pydantic import Field
from datetime import date 
from typing import Optional,List,Dict
from decimal import Decimal
class ScrapedCompany(BaseModel):
    name:str
    url:Optional[str] =None
    logo_url:Optional[str] =None
    industry:Optional[str] = None 

    description:Optional[str] = None 
    employees_label:Optional[str] = None

    model_config=ConfigDict(from_attributes=True)

class ScrapedJob(BaseModel):
    title:str
    company:ScrapedCompany | None = None
    job_url:str

    job_url_hash:str
    source_site:str
    location_city:Optional[str]= None
    location_state:Optional[str] = None

    location_country:Optional[str] = None
    is_remote:bool =False
    description:Optional[str] = None

    job_type:Optional[str] = None 
    salary_min:Optional[Decimal] = None 
    salary_max:Optional[Decimal] = None

    salary_currency:Optional[str] = None 
    salary_interval:Optional[str] = None
    date_posted:Optional[date] = None 

    extras:Dict =Field(default_factory=dict)
    errors:list[str] = Field(default_factory=list)

    model_config=ConfigDict(from_attributes=True)

class ScrapeResult(BaseModel):
    site_name: str
    search_term:Optional[str] = None
    status: str 

    jobs_found: int = 0
    jobs_new: int = 0
    jobs_updated: int = 0

    errors: List[str] = Field(default_factory=list)
    duration_seconds: float = 0.0

    model_config =ConfigDict(from_attributes=True)