from fastapi import APIRouter
from app.router.routes import (health,
                               jobs,
                               auth,
                               categories,
                               users)


api_router = APIRouter()
api_router.include_router(health.router,prefix="/health")
api_router.include_router(jobs.router)

api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(users.router)
