from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.dependencies import get_db
from app.schemas.error import HTTPError

router = APIRouter()

@router.get(
        "/",
        tags=["health"],
        responses={
            503: {"model": HTTPError, "description": "Service unavailable"},
        },
)
async def health_check(
    db: AsyncSession = Depends(get_db)
):
    from app.main import redis_client

    health_status = {
        "db": "online",
        "redis": "ok",
        "status": "ok"
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        health_status["db"] = "down"
        health_status["status"] = "fail"

    # Check redis
    if redis_client:
        try:
            await redis_client.ping()
            health_status["redis"] = "connected"
        except Exception as e:
            health_status["redis"] = "down"
            health_status["status"] = "fail"
    else:
        health_status["redis"] = "unavailable"
    
    # Return appropriate status code
    if health_status["status"] == "fail":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=health_status
    )