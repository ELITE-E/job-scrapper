from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Category,Job

async def get_categories_with_count(db:AsyncSession):
    result = await db.execute(
        select(
            Category,
            func.count(Job.id).label("job_count")
        ).outerjoin(
            Job,
            (Job.category_id == Category.id)&(Job.is_active == True)
        ).group_by(
            Category.id
        ).order_by(
            func.count(Job.id).desc()
        )
    )

    return [
        {
            **category.__dict__,
            "job_count":job_count
        }

        for category,job_count in result.all()
    ]