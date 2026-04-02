import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from api.app.config import settings
from api.app.models import Category, Company, Job, JobCategoryKeyword
from api.app.database import async_session_maker
from api.app.scrapper.categorizer import load_categorizer_config

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


async def seed_categories(session):
    config = load_categorizer_config()
    async with async_session_maker as session:
        result = await session.execute(select(Category))

        existing_categories = {
            cat.slug: cat for cat in result.scalars().all()
        }
        for cat in config.categories:
            
            if cat.slug in existing_categories:
                db_category = existing_categories[cat.slug]
            else:
                db_category = Category(
                name = cat.name,
                slug = cat.slug,
                description = cat.description
            )
            session.add(db_category)
            await session.flush()

        for kw in cat.keywords:
            keyword = JobCategoryKeyword(
                category_id = db_category.id,
                term = kw.term,
                weight = kw.weight,
            )
            session.add(keyword)

    await session.commit()


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
            await seed_categories(session)
            await seed_companies(session)
            await seed_jobs(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())