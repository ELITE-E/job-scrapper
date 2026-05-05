from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import APIRouter,Depends,HTTPException,Request
from fastapi_pagination import Page,Params
from fastapi_pagination.ext.sqlalchemy import paginate

from fastapi_cache.decorator import cache


from app.dependencies import get_db
from app.schemas.job import JobResponse,JobFilters,JobDetailResponse
from app.services.job_service import build_jobs_query,get_job_by_id_query

from app.core.cache import request_key_builder
from app.schemas.error import HTTPError
from app.schemas.category import CategoryResponse


from app.core.limiter import limiter
from app.models.job import Job
from app.models.category import Category

router = APIRouter()

@cache()
async def get_cache():
  return 


@router.get(
    "/jobs",
    response_model=Page[JobResponse],
     responses={
        422: {"model": HTTPError, "description": "Invalid query parameters"},
        429: {"model": HTTPError, "description": "Rate limit exceeded"},
    },
    )
@limiter.limit("100/minute")
@cache(expire=300,
       key_builder=request_key_builder)
async def get_jobs(
     request:Request,
     filters: JobFilters = Depends(),
     params: Params = Depends(),
    db: AsyncSession = Depends(get_db)):
  query = build_jobs_query(filters)
  return await paginate(db,query,params)


@router.get(
    "/jobs/{job_id}",
    response_model=JobDetailResponse,
     responses={
        404: {"model": HTTPError, "description": "Job not found"},
        422: {"model": HTTPError, "description": "Invalid job ID"},
        },
        )
@limiter.limit("200/minute")
@cache(expire=3600)
async def get_job(
  request:Request,  
  job_id:str,
    db:AsyncSession = Depends(get_db)):
  try:
    job_uuid = UUID(job_id)
  
  except ValueError:
    raise HTTPException(status_code=400,
      detail="Invalid job ID format")
  query = get_job_by_id_query(job_uuid)
  result = await db.execute(query)
  
  job = result.scalar_one_or_none()

  #Print the description
  print(f"API Log: Job ID {job_uuid} has description: {job.description[:50] if job.description else 'None'}")

  if not job:
    raise HTTPException(status_code=404,detail="Job not found")
  return job

@router.get(
    "/categories",
    response_model=list[CategoryResponse],
      responses={
        429: {"model": HTTPError, "description": "Rate limit exceeded"},
    },
    )
@limiter.limit("200/minute")
@cache(expire = 86400)
async def get_categories(
   request: Request,
  db:AsyncSession = Depends(get_db)
):
  
  result = await db.execute(
    select(Category)
      )
  return result.scalars().all()