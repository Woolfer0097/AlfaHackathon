import logging
from fastapi import APIRouter
from typing import Dict
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy"}

