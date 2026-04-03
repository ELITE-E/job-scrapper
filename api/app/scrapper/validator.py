from pydantic import BaseModel,Field,ValidationError
from typing import List,Dict,Tuple,Any

from .schemas import ScrapedJob

class ValidationReport(BaseModel):
    total_input: int 
    total_valid: int
    total_invalid : int
    invalid_reasons: List[Dict[str,Any]] = Field(default_factory=list)


def validate_batch(jobs:List[Dict])->Tuple[List[ScrapedJob],ValidationReport]:

    valid_jobs : List[ScrapedJob] = []
    invalid_reasons: List[Dict[str,Any]] = []

    for idx ,job_dict in enumerate(jobs):
        try:
            job = ScrapedJob(**job_dict)
            valid_jobs.append(job)

        except ValidationError as e:
            invalid_reasons.append({
                "row_index":idx,
                "title":job_dict.get("title"),
                "errors":e.errors()
            })

    report= ValidationReport(
        total_input=len(jobs),
        total_valid=len(valid_jobs),
        total_invalid=len(invalid_reasons),
        invalid_reasons= invalid_reasons
            )

    return valid_jobs,report

