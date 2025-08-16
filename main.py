from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import uvicorn
import os
from contextlib import asynccontextmanager

from config.settings import settings
from app.api.v1 import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting FastAPI application")
    try:
        # Initialize services here if needed
        pass
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Math Homework Backend",
        description="FastAPI backend for processing mathematics homework problems",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for production
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
        )
    
    # Include API routes
    app.include_router(api_router, prefix=settings.api_prefix)
    
    # Mount static files for local storage
    storage_dir = "./storage/files"
    os.makedirs(storage_dir, exist_ok=True)
    app.mount("/storage/files", StaticFiles(directory=storage_dir), name="storage")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "environment": settings.environment,
            "version": "1.0.0"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        response = {
            "message": "Math Homework Backend API",
            "docs": "/docs",
            "health": "/health",
            "environment": settings.environment
        }
        
        # Add development info
        if settings.environment == "development":
            response.update({
                "🔓 auth_bypass": "Authentication not required in dev mode",
                "🧪 dev_endpoints": {
                    "test_auth": "/v1/problems/dev/auth-test",
                    "create_test_problem": "/v1/problems/dev/test"
                },
                "💡 tips": [
                    "No Authorization header needed for dev endpoints",
                    "Use 'dev', 'test', or 'bypass' as Bearer token if needed",
                    "All Firebase operations are mocked"
                ]
            })
        
        return response
    
    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
