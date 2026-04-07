from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page,Params
from fastapi_pagination.ext.sqlalchemy import paginate

from app.dependencies import get_db
from app.schemas.job import JobResponse
from app.services.category_service import build_jobs_query

router = APIRouter()

@router.get("/jobs",response_model=Page[JobResponse])
async def get_jobs(
    params:Params = Depends(),
    db:AsyncSession = Depends(get_db)
):

  query = build_jobs_query()

  return await paginate(db,query,params)
