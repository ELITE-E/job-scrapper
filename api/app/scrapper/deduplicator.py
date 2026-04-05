import hashlib
from typing import List, Union, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.scrapper.schemas import ScrapedJob


def _normalize_session(
    session: Union[AsyncSession, Sequence[AsyncSession]],
) -> AsyncSession:
    """
    Type guard: Accept a single AsyncSession or unwrap a single-item list.
    Prevents errors when session is accidentally passed as [<AsyncSession>].
    """
    if isinstance(session, AsyncSession):
        return session

    if isinstance(session, (list, tuple)) and not isinstance(session, (str, bytes)):
        if len(session) == 1 and isinstance(session[0], AsyncSession):
            return session[0]
        raise TypeError(
            "session must be an AsyncSession or single-item list/tuple containing AsyncSession"
        )

    raise TypeError("session must be an AsyncSession")


def compute_hash(job_url: str) -> str:
    return hashlib.sha256(job_url.encode()).hexdigest()


async def filter_new_jobs(
    jobs: List[ScrapedJob],
    session: Union[AsyncSession, Sequence[AsyncSession]],
) -> List[ScrapedJob]:
    """Filter jobs that don't already exist in the database."""
    if not jobs:
        return []
    
    # Type guard: unwrap if session accidentally passed as list
    session = _normalize_session(session)

    #extract hashes
    hashes = [job.job_url_hash for job in jobs]

    #Batch query existing hashes
    stmt = select(Job.job_url_hash).where(Job.job_url_hash.in_(hashes))
    result = await session.execute(stmt)

    existing_hashes = set(result.scalars().all())
    
    #Filter out existing jobs
    new_jobs = [job for job in jobs if job.job_url_hash not in existing_hashes]

    return new_jobs