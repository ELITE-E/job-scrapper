import re
import logging
from pydantic import ConfigDict,BaseModel,model_validator
from pydantic import Field,field_validator,model_validator
from datetime import date,timedelta
from typing import Optional,List,Dict
from decimal import Decimal
import pandas as pd

logger = logging.getLogger("scrapper.schemas")

ALLOWED_SITES = {
            "indeed",
            "linkedin",
            "zip_recruiter",
            "glassdoor",
            "google"
        }

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

    category_slug : Optional[str] = None

    extras:Dict =Field(default_factory=dict)
    errors:list[str] = Field(default_factory=list)

    model_config=ConfigDict(from_attributes=True)

    #title validator
    @field_validator("title",mode="before")
    @classmethod
    def validate_title(cls,v):
        if v is None:
            raise ValueError("title cannot be None")
        if not isinstance(v,str):
            raise TypeError("Title must be a string")
        
        v = v.strip()

        if not v:
            raise ValueError("title cannot be empty or whitespace")
        
        if len(v) <3:
            raise ValueError("title must be at least 3 characters long")
        return v
    
    #job_url validator
    @field_validator("job_url",mode='before')
    @classmethod
    def validate_job_url(cls,v):
        if not isinstance(v,str):
            raise TypeError("job_url must be a string ")
        
        v = v.strip()

        if not v.startswith(("http://","https://")):
            raise ValueError("job_url must start with http:// or https://")
        return v
    #date_posted validator
    @field_validator("date_posted",mode="before")
    @classmethod
    def validate_date(cls, v, info):
        """
        Validate and normalize date_posted field.
        
        - Allows None values (jobs without posted dates)
        - Accepts date objects directly
        - Attempts to parse strings to dates
        - Allows jobs up to 60 days old (for sponsored/archived jobs)
        - Logs warnings instead of failing for edge cases
        """
        # Case 1: None is acceptable
        if v is None:
            return v

        # Case 2: Already a date object
        if isinstance(v, date):
            parsed_date = v
        # Case 3: String - try to parse it
        elif isinstance(v, str):
            try:
                parsed_date = pd.to_datetime(v).date()
            except Exception as e:
                logger.warning(
                    f"Could not parse date_posted '{v}' for job '{info.data.get('title', 'unknown')}'. "
                    f"Setting to None. Error: {e}"
                )
                return None
        else:
            logger.warning(
                f"Unexpected date_posted type: {type(v).__name__} for job "
                f"'{info.data.get('title', 'unknown')}'. Setting to None."
            )
            return None

        # Case 4: Validate date range (60-day window for sponsored/archived jobs)
        today = date.today()
        earliest = today - timedelta(days=60)  # Allow up to 60 days old
        latest = today + timedelta(days=1)  # Don't allow future dates

        if not (earliest <= parsed_date <= latest):
            logger.warning(
                f"Date '{parsed_date}' outside acceptable range ({earliest} to {latest}). "
                f"Job: '{info.data.get('title', 'unknown')}'. Setting to None."
            )
            # Instead of rejecting, set to None so the job isn't discarded
            return None

        return parsed_date
    #Salary validation
    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_min > self.salary_max:
                #Swap instead of error :usefule when sites flip ranges
                #self.salary_min,self.salary_max =self.salary_max,self.salary_min
                raise ValueError("salary_min must be less than salary_max")
        return self
        
    #site validator
    @field_validator("source_site",mode="before")
    @classmethod
    def validate_source_site(cls,v):
        if not isinstance(v,str):
            raise TypeError("source_site must be a string ")
        
        v_str = str(v).strip().lower()
        cleaned = re.sub(r"[\s\-]+", "_", v_str)
        print(v)

        if cleaned not in ALLOWED_SITES:
            print(f"BUG:'{cleaned}' not in {ALLOWED_SITES}")
            raise ValueError(f"source_site must be one of {ALLOWED_SITES}")
        return cleaned
        
class ScrapeResult(BaseModel):
    site_name: str
    #search_terms:Optional[str] = None
    status: str 

    jobs_found: int = 0
    jobs_new: int = 0
    jobs_updated: int = 0

    errors: List[str] = Field(default_factory=list)
    duration_seconds: float = 0.0

    model_config =ConfigDict(from_attributes=True)

class KeywordEntry(BaseModel):
    term : str
    weight : float = 1.0

class CategoryDefinition(BaseModel):
    name : str
    slug : str
    description : str  = ""
    keywords : List[KeywordEntry] = Field(default_factory=list)
    title_keywords : List[str] = Field(default_factory=list)

class CategorizerSettings(BaseModel):
    title_weight_multiplier : float = 3.0
    min_score_threshold  : float = 2.0
    default_category : str = "other"

class CategorizerConfig(BaseModel):
    settings : CategorizerSettings
    categories : List[CategoryDefinition]

    @model_validator(mode="after")
    def check_unique_slugs(self):
        slugs = [c.slug for c in self.categories]

        if len(slugs) != len(set(slugs)):
            raise ValueError("Duplicate category slugs found ")
        return self