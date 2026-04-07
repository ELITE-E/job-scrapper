from fastapi import APIRouter
import redis.asyncio as  redis

router = APIRouter()

@router.get("/",tags=["health"])
async def health_check():
    from app.main import redis_client

    status = {"api":"online","redis":"disconnected"}

    if redis_client:
        try:
            await redis_client.ping()
            status["redis"] = "connected"
        except redis.ConnectionError:
            pass
    return status