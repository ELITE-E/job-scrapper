import yaml
from pydantic import BaseModel,Field,field_validator
from typing import List,Optional

class RetryingConfig(BaseModel):
    max_attempt:int = 3
    wait_multiplier:int = 2
    wait_min:int = 4
    wait_max:int = 30


class GlobalConfig(BaseModel):
    delay_between_sites:int = 5
    description_format:str = "markdown"
    hours_old:int = 72
    results_wanted:int = 50


VALID_SITES = {
    "indeed",
    "linkedin",
    "zip_recruiter",
    "glassdoor",
    "google",
    "bayt",
    "naukri",
    "bdjobs",
}

class SiteConfig(BaseModel):
    name:str 
    enabled:bool = True
    search_terms:List[str]

    location:str
    results_wanted:Optional[int] = None
    hours_old:Optional[int] =None

    job_type:Optional[str] = None 
    is_remote:Optional[bool] = None
    proxies:List[str] = []

    delay_beetween_searches:int = 5
    country_indeed:Optional[str]= None
    likedin_fetch_description: bool = False

    @field_validator("name")
    @classmethod
    def validate_site_name(cls,v):
        if v not in VALID_SITES:
            raise ValueError(f"Unsurported site: {v}")
        return v
    

class ScrapperConfig(BaseModel):
    global_:GlobalConfig = Field(alias="global")
    retry:RetryingConfig
    sites:List[SiteConfig]




