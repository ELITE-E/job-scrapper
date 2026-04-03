import uuid
from typing import List ,Tuple
import logging


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, Category,Company

from app.scrapper.schemas import ScrapedJob,ScrapedCompany

logger = logging.getLogger(__name__)

async def find_or_create_company(
        company_data:ScrapedCompany,
        session:AsyncSession,
)->uuid.UUID | None:
    if not company_data or not company_data.name:
        return None 
    
    #Try to find existing company
    stmt= select(Company).where(Company.name == company_data.name).limit(1)
    result = await session.execute(stmt)
    company = result.scalar_one_or_none()

    if company :
        #Only fill missing fileds
        updated = False

        if not company.logo_url and company_data.logo_url:
            company.logo_url= company_data.logo_url
            updated=True

        if not company.url and company_data.url:
            company.url = company_data.url
            updated=True

        if not company.industry and company_data.industry:
            company.industry = company_data.industry
            updated= True

        if not company.description and company_data.description:
            company.description = company_data.description
            updated = True

        if not company.employees_label and company_data.employees_label:
            company.employees_label=company_data.employees_label
            updated=True 

        if updated:
            session.add(company)
        return company.id
    
    #Creates a new company
    new_company = Company(
            id = uuid.uuid4(),
            name= company_data.name,
            url = company_data.url,
            logo_url = company_data.logo_url, 
            industry = company_data.industry,
            description=company_data.description,
            employees_label=company_data.employees_label  
               )
    
    session.add(new_company)

    return new_company.id

async def persist_jobs(
        jobs:List[ScrapedJob],
        session:AsyncSession,)->Tuple[int,int]:
    if not jobs:
        return (0,0)
    new_jobs=[]
    new_count= 0
    updated_count = 0


    try:
        result= await session.execute(select(Category.id,Category.slug))
        category_map = {slug:id for id,slug in result.all()}

        for job in jobs:

        #Resolve company FK
            company_id = None
            if job.company:
                company_id = await find_or_create_company(job.company,session=session)
        #Job ORM obj
            db_job=Job(
                title=job.title,
                description=job.description,
                job_url=job.job_url,

                job_url_hash=job.job_url_hash,
                job_type=job.job_type,
                source_site=job.source_site,

                location_city=job.location_city,
                location_state=job.location_state,
                location_country=job.location_country,

                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,

                salary_interval=job.salary_interval,

                date_posted=job.date_posted,

                extras=job.extras,

                company_id=company_id,

        )
            
            #Category resolution
            if job.category_slug:
                category_id = category_map.get(job.category_slug)

                if category_id:
                    db_job.category_id = category_id
                else:
                    logger.warning(
                        f"Unknown category slug : {job.category_slug}"
                    )
            new_jobs.append(db_job)

        #Bulk insert
        session.add_all(new_jobs)

        await session.commit()

        new_count = len(new_jobs)

    except Exception as e:
        await session.rollback()
        raise e

    return (new_count,updated_count)
