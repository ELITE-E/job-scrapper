from fastapi import APIRouter

router = APIRouter()

router.get("/auth",tags="Authentication")