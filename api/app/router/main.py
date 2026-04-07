from fastapi import APIRouter
from app.router.routes import (health,
                               jobs)


api_router = APIRouter()
api_router.include_router(health.router,prefix="/health")
api_router.include_router(jobs.router,prefix="/jobs")