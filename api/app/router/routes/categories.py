from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache 

from app.dependencies import get_db
from app.schemas.category import CategoryResponse
from app.services.category_service import get_categories_with_count

router = APIRouter()

router.get("/categories",tags="Categories",response_model=list[CategoryResponse])
@cache(expire=86400)
async def get_categories(db:AsyncSession = Depends(get_db)):
    categories = get_categories_with_count
    return await categories(db)