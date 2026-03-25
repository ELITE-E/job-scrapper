import uuid
from typing import List ,Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.job import Job

from scrapper.schemas import ScrapedJob,ScrapedCompany


async def find_or_create_company(
        company_data:ScrapedCompany,
        session:AsyncSession,
)->uuid.UUID:
    if not company_data or not company_data.name:
        return None 
    
    #Try to find existing company
    stmt= select(Company).where(Company.name === company_data.name).limit(1)
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
        session:AsyncSession,

)->Tuple[int,int]:
    if not jobs:
        return (0,0)
    new_jobs=[]
    new_count= 0
    updated_count = 0

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
            job_type=job.job_type
            source_site=job.source_site,

            location_city=job.location_city,
            location_stte=job.location_state,
            loction_country=job.location_country,

            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,

            salary_interval=job.salary_interval,

            date_posted=job.date_posted,

            extras=job.extras,

            company_id=company_id,

        )
        new_jobs.append(db_job)

        #Bulk insert
        session.add_all(new_jobs)

        await session.commit(new_jobs)

        return (new_count,updated_count)
