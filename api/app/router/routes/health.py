from fastapi import APIRouter,status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as  redis

from app.dependencies import get_db

router = APIRouter()

@router.get("/",tags=["health"])
async def health_check(
    db : AsyncSession = Depends(get_db)
):
    from app.main import redis_client

    health_status = {"db":"online",
                     "redis":"ok",
                     "status":"ok"}
    
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        health_status["database"] = "down"
        health_status["status"] = "fail"

    if redis_client:
        try:
            await redis_client.ping()
            status["redis"] = "connected"
        except Exception:
            health_status["redis"] = "down"
            health_status["status"] = 'fail'  
        if health_status["status"] =="fail":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_status
            )
        return health_status