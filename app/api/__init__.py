from fastapi import APIRouter
from app.api.v1 import prediction, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(prediction.router, prefix="/predictions", tags=["predictions"])

