from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Tuple, Any, Union

from .schemas import ScrapedJob

class ValidationReport(BaseModel):
    total_input: int 
    total_valid: int
    total_invalid: int
    invalid_reasons: List[Dict[str, Any]] = Field(default_factory=list)


def validate_batch(
    jobs: Union[List[Dict], List[ScrapedJob], List[Union[Dict, ScrapedJob]]]
) -> Tuple[List[ScrapedJob], ValidationReport]:
    """
    Validate a batch of jobs (dicts or ScrapedJob objects) and return validated objects.
    
    ETL Context:
    - If input is already ScrapedJob (from transformer), pass through (trusted, already validated)
    - If input is dict (from external source), use model_validate() for robust validation
    - Uses model_validate() instead of ** unpacking to handle both gracefully
    """
    valid_jobs: List[ScrapedJob] = []
    invalid_reasons: List[Dict[str, Any]] = []

    for idx, job_input in enumerate(jobs):
        title = None
        try:
            # Case 1: Already a ScrapedJob object (from transformer)
            if isinstance(job_input, ScrapedJob):
                valid_jobs.append(job_input)
                continue
            
            # Case 2: Dict input - use model_validate for safe construction
            if isinstance(job_input, dict):
                title = job_input.get("title")
                # model_validate() handles type coercion and validation gracefully
                job = ScrapedJob.model_validate(job_input)
                valid_jobs.append(job)
            else:
                raise TypeError(
                    f"Expected dict or ScrapedJob, got {type(job_input).__name__}"
                )

        except (ValidationError, TypeError) as e:
            invalid_reasons.append({
                "row_index": idx,
                "title": title,
                "errors": str(e)
            })

    report = ValidationReport(
        total_input=len(jobs),
        total_valid=len(valid_jobs),
        total_invalid=len(invalid_reasons),
        invalid_reasons=invalid_reasons
    )

    return valid_jobs, report

