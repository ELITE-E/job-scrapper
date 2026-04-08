from fastapi import APIRouter
from app.router.routes import (health,
                               jobs,
                               auth,
                               categories,
                               users)


api_router = APIRouter()

api_router.include_router(health.router,prefix="/health")
api_router.include_router(jobs.router,prefix="/api/v1")
api_router.include_router(auth.router,prefix="/api/v1")

api_router.include_router(categories.router,prefix="/api/v1")
api_router.include_router(users.router,prefix="/api/v1")
