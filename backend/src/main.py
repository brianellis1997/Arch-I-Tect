"""
Main FastAPI application entry point for Arch-I-Tect.

This module initializes and configures the FastAPI application with all
necessary middleware, routes, and exception handlers.
"""
from dotenv import load_dotenv
load_dotenv()

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from dotenv import load_dotenv

from api.routes import router as api_router
from api.middleware import setup_middleware
from utils.validators import validate_environment

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None
    """
    # Startup
    logger.info("Starting Arch-I-Tect API...")
    
    # Validate environment configuration
    try:
        validate_environment()
        logger.info("Environment configuration validated successfully")
    except ValueError as e:
        logger.error(f"Environment validation failed: {e}")
        raise
    
    # Create necessary directories
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    logger.info(f"Upload directory ensured at: {upload_dir.absolute()}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Arch-I-Tect API...")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="Arch-I-Tect API",
        description="Convert cloud architecture diagrams to Infrastructure as Code",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        """Root endpoint for health checking."""
        return {
            "message": "Welcome to Arch-I-Tect API",
            "version": "0.1.0",
            "status": "operational"
        }
    
    @app.get("/health")
    async def health_check():
        """Detailed health check endpoint."""
        return {
            "status": "healthy",
            "llm_provider": os.getenv("LLM_PROVIDER", "not_configured"),
            "max_image_size_mb": os.getenv("MAX_IMAGE_SIZE_MB", "10"),
        }
    
    return app


# Create the application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )