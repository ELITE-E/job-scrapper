import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.models import Category, Company, Job, JobCategoryKeyword
from app.database import async_session_maker
from app.scrapper.categorizer import load_categorizer_config

# Use the backward-compatible get_db_url() method
DATABASE_URL = settings.get_db_url()

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


COMPANIES = [
    {"name": "Acme Corp"},
    {"name": "TechStart Inc"},
]

JOBS = [
    {
        "title": "Backend Developer",
        "description": "Work with FastAPI and PostgreSQL",
        "job_url": "https://example.com/job1",
        "job_url_hash": "hash1",
        "source_site": "example",
        "location_city": "Nairobi",
        "location_country": "Kenya",
        "salary_min": 1000,
        "salary_max": 3000,
        "extras": {"experience": "2+ years"},
    },
    {
        "title": "Frontend Engineer",
        "description": "React + TypeScript",
        "job_url": "https://example.com/job2",
        "job_url_hash": "hash2",
        "source_site": "example",
        "location_city": "Remote",
        "location_country": "Global",
        "salary_min": 1200,
        "salary_max": 3500,
        "extras": {"framework": "React"},
    },
]


async def seed_companies(session):
    for comp in COMPANIES:
        stmt = insert(Company).values(**comp).on_conflict_do_nothing(
            index_elements=["name"]
        )
        await session.execute(stmt)


async def seed_jobs(session):
    for job in JOBS:
        stmt = insert(Job).values(**job).on_conflict_do_nothing(
            index_elements=["job_url_hash"]
        )
        await session.execute(stmt)


async def main():
    async with SessionLocal() as session:
        async with session.begin():
           # await seed_categories(session)-->Moved to new script
            await seed_companies(session)
            await seed_jobs(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())