"""
Middleware configuration for the Arch-I-Tect API.

This module handles request/response logging, error handling, and 
performance monitoring middleware.
"""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def setup_middleware(app: FastAPI) -> None:
    """
    Configure all middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Add rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    @app.middleware("http")
    async def add_request_id(request: Request, call_next: Callable) -> Response:
        """
        Add a unique request ID to each request for tracing.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or endpoint handler
            
        Returns:
            Response: HTTP response with request ID header
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable) -> Response:
        """
        Log all incoming requests and their responses.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or endpoint handler
            
        Returns:
            Response: HTTP response
        """
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started | Method: {request.method} | "
            f"Path: {request.url.path} | ID: {getattr(request.state, 'request_id', 'unknown')}"
        )
        
        try:
            response = await call_next(request)
            
            # Calculate request duration
            duration = round(time.time() - start_time, 3)
            
            # Log response
            logger.info(
                f"Request completed | Method: {request.method} | "
                f"Path: {request.url.path} | Status: {response.status_code} | "
                f"Duration: {duration}s | ID: {getattr(request.state, 'request_id', 'unknown')}"
            )
            
            # Add timing header
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            duration = round(time.time() - start_time, 3)
            logger.error(
                f"Request failed | Method: {request.method} | "
                f"Path: {request.url.path} | Error: {str(e)} | "
                f"Duration: {duration}s | ID: {getattr(request.state, 'request_id', 'unknown')}"
            )
            raise
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """
        Handle ValueError exceptions with proper error responses.
        
        Args:
            request: HTTP request that caused the error
            exc: ValueError exception instance
            
        Returns:
            JSONResponse: Formatted error response
        """
        logger.warning(f"ValueError: {str(exc)} | Path: {request.url.path}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid input",
                "detail": str(exc),
                "request_id": getattr(request.state, 'request_id', 'unknown')
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle all unhandled exceptions with a generic error response.
        
        Args:
            request: HTTP request that caused the error
            exc: Exception instance
            
        Returns:
            JSONResponse: Formatted error response
        """
        logger.exception(
            f"Unhandled exception | Path: {request.url.path} | "
            f"ID: {getattr(request.state, 'request_id', 'unknown')}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later.",
                "request_id": getattr(request.state, 'request_id', 'unknown')
            }
        )