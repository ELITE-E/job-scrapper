from sqlalchemy import select,or_
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from app.models import Job
from app.schemas.job import JobFilters

def build_jobs_query(filters=JobFilters | None):
    query = select(Job).options(
        selectinload(Job.company),
        selectinload(Job.category)
    ).where(Job.is_active == True).order_by(Job.date_posted.desc())

    if not filters:
       
       return query
    
    if filters.category:
        query = query.join(Job.category).where(Category.slug == filters.category)

    if filters.source_site:
        query = query.where(Job.source_site == filters.source_site )

    if filters.is_remote is not None :
        query = query.where(Job.is_remote == filters.is_remote)

      
    if filters.job_type:
        query = query.where(Job.job_type == filters.job_type)

    
    if filters.location:
        v = f"%{filters.location}%"
        query = query.where(
            or_(
                Job.location_city.ilike(v),
                Job.location_state.ilike(v),
                Job.location_country.ilike(v),
            )
        )

    
    if filters.min_salary is not None:
        query = query.where(Job.salary_max >= filters.min_salary)

    if filters.max_salary is not None:
        query = query.where(Job.salary_min <= filters.max_salary)

    
    if filters.search:
        v = f"%{filters.search}%"
        query = query.where(
            or_(
                Job.title.ilike(v),
                Job.description.ilike(v),
            )
        )

    return query