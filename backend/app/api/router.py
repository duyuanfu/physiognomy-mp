from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.analyze import router as analyze_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="", tags=["System"])
api_router.include_router(analyze_router, prefix="", tags=["Analysis"])
