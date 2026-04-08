from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import APIRouter,Depends,HTTPException
from fastapi_pagination import Page,Params
from fastapi_pagination.ext.sqlalchemy import paginate

from fastapi_cache.decorator import cache

from app.dependencies import get_db
from app.schemas.job import JobResponse,JobFilters
from app.services.category_service import build_jobs_query

from app.core.cache import request_key_builder

router = APIRouter()

@cache()
async def get_cache():
  return 


@router.get("/jobs",response_model=Page[JobResponse])
@cache(expire=300,
       key_builder=request_key_builder)
async def get_jobs(filters: JobFilters = Depends(), params: Params = Depends(), db: AsyncSession = Depends(get_db)):
  query = build_jobs_query(filters)
  return await paginate(db,query,params)


@router.get("/jobs/{job_id}",response_model=JobResponse)
@cache(expire=3600)
async def get_job(  job_id:int,
    db:AsyncSession = Depends(get_db)):
  
  result = await db.execute(
    select(Job).where(Job.id == job_id)
  )
  job = result.scalar_one_or_none()

  if not job:
    raise HTTPException(status_code=404,detail="Job not found")
  return job

@router.get("/categories")
@cache(expire = 86400)
async def get_categories(
  db:AsyncSession = Depends(get_db)
):
  
  result = await db.execute(
    select(Category)
      )
  return result.scalars().all()