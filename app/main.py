import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api import api_router

# Setup logging before creating app
setup_logging()
logger = get_logger(__name__)


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests"""
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} - Status: {response.status_code}")
        return response
    
    # Exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler with logging"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Root endpoint
    @app.get("/")
    async def root():
        logger.debug("Root endpoint accessed")
        return {"message": "ML API is running", "docs": "/docs"}
    
    # Include API router
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    logger.info("Application initialized successfully")
    
    return app


app = create_application()

