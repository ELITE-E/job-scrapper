import hashlib
from typing import List 

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from scrapper.schemas import ScrapedJob

def compute_hash(job_url:str)->str:
    return hashlib.sha256(job_url.encode()).hexdigest

async def filter_new_jobs(
        jobs:List[ScrapedJob],
        session:AsyncSession,
)->List[ScrapedJob]:
    #Edge case - Empty input
    if not jobs:
        return []
    
    #extract hashes
    hashes = [job.job_url_hash for job in jobs]

    #Batch query existing hashes
    stmt = select(Job.job_url_hash).where(Job.job_url_hash.in_(hashes))
    result = await session.execute(stmt)

    existing_hashes = set(result.scalars().all())
    
    #Filter out existing jobs
    new_jobs = [job for job in jobs if job.job_url_hash not in existing_hashes]

    return new_jobs