from fastapi import APIRouter
from app.api.v1 import health, clients, metrics, predictions, recommendations

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(clients.router, tags=["clients"])
api_router.include_router(metrics.router, tags=["metrics"])
api_router.include_router(predictions.router, tags=["predictions"])
api_router.include_router(recommendations.router, tags=["recommendations"])
