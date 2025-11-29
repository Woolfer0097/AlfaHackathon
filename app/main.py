import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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
    
    # Initialize ML model on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize ML model on application startup"""
        try:
            from app.services.ml_service import get_ml_service
            ml_service = get_ml_service()
            logger.info("ML model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}", exc_info=True)
            # Don't fail startup, but log the error
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests with query parameters"""
        query_params = str(request.query_params) if request.query_params else ""
        logger.info(f"{request.method} {request.url.path}{'?' + query_params if query_params else ''}")
        response = await call_next(request)
        if response.status_code == 422:
            logger.warning(f"{request.method} {request.url.path} - Status: {response.status_code} (Validation Error) - Query: {query_params}")
        else:
            logger.info(f"{request.method} {request.url.path} - Status: {response.status_code}")
        return response
    
    # Validation error handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors with detailed logging"""
        query_params = str(request.query_params) if request.query_params else ""
        logger.warning(f"Validation error on {request.method} {request.url.path} - Query: {query_params} - Errors: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body}
        )
    
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

