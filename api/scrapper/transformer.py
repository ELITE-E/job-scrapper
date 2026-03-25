import hashlib 
import logging 
from datetime import date
from typing import List,Dict,Any

import pandas as pd 
import numpy as np
from pydantic import ValidationError

from scrapper.schemas import ScrapedJob,ScrapedCompany

logger = logging.getLogger("scrapper.transformer")

CORE_COLUMNS={
    "title",
    "company",
    "company_url",
    "job_url",
    "site",
    "city",
    "state",
    "country",
    "is_remote",
    "description",
    "job_type",
    "min_amount",
    "max_amount",
    "currency",
    "interval",
    "date_posted"
}

def parse_date(value)->date | None:
    if not value :
        return  None
    try:
        pd.to_datetime(value).date()
    except Exception:
        return None

def normalize_job_type(value:str | None )->str | None:
    if not value:
        return None 
    
    if isinstance(value,str):
        #Hnadle "JobType.FULLTIME"
        if "." in value:
            value=value.split(".")[-1]

            return value.lower()
        
        return None
    
def normalize_bool(value)->bool:
    if value in (True,"true","True",1):
        return True
    
    return False

def transform_dataframe(df:pd.DataFrame)->List[ScrapedJob]:
    if df is None or df.empty:
        return []
    
    df = df.replace({np.nan:None})

    records = df.to_dict(orient="records")

    results: List[ScrapedJob] = []

    for idx,row in enumerate(records):
        try:
            if not row.get("title") or not row.get("job_url"):
                logger.warning(f"Skipping row {idx}:missing title or job_url")

                continue
            job_url=row["job_url"]
            job_url_hash=hashlib.sha256(job_url.encode()).hexdigest

            company = None
            if row.get("company"):
                company = ScrapedCompany(
                    name=row.get("company"),
                    url=row.get("company_url"),
                )
            
            extras: Dict[str,Any]={
                k:v for k,v in row.items()
                if k not in CORE_COLUMNS and v is not None
            }

            job = ScrapedJob(
                title=row.get("title"),
                company=company,
                job_url=job_url,

                job_url_hash=job_url_hash,
                source_site=row.get("site"),
                location_city=row.get("city"),

                location_state=row.get("state"),
                location_country=row.get("country"),
                is_remote=normalize_bool(row.get("is_remote")),

                description=row.get("description"),
                job_type=normalize_job_type(row.get("job_type")),

                salary_min=row.get("min_amount"),
                salary_max=row.get("max_amount"),
                salary_currency=row.get("currency"),

                salary_interval=row.get("interval"),
                date_posted=parse_date(row.get("date_posted")),
                extras = extras
            )

            results.append(job)

        except ValidationError as e:
            logger.error(f"Validation error on row {idx}: {e}")
            continue

        except Exception as e:
            logger.exception(f"Unexpected error on row {idx}: {e}")
            continue

    return results

