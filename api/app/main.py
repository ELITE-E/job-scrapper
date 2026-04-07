from fastapi import FastAPI,Request,HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi_pagination import add_pagination

from slowapi import Limiter
from slowapi.util import get_remote_address

from starlette.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from contextlib import asynccontextmanager

from app.core.config import settings
from app.router.main import api_router


redis_client:redis.Redis | None = None

@asynccontextmanager
async def lifespan(app:FastAPI):
    global redis_client

    redis_client = redis.from_url(
        str(settings.REDIS_URL),
        decode_responses=True,  # Automatically decode bytes to strings
        socket_timeout=5.0,     # Connection timeout in seconds
        socket_connect_timeout=5.0
    )

    FastAPICache.init(RedisBackend(redis_client),
                     prefix="/job-cache" )
    yield

    await redis_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan

)
add_pagination(app)
@app.exception_handler(HTTPException)
async def http_exception_handler(request:Request,exc:HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail":exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods = ["GET","POST","PUT","DELETE","OPTIONS"],
        allow_headers=["*"]
    )
app.include_router(api_router,prefix=settings.API_V1_STR)

