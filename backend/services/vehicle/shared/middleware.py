from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI, origins: list):
    """Setup CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=".*",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_gzip(app: FastAPI):
    """Setup GZip compression"""
    app.add_middleware(GZipMiddleware, minimum_size=1000)


async def catch_exceptions_middleware(request: Request, call_next):
    """Global exception handler"""
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )


async def log_requests_middleware(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Add custom header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )


def setup_middleware(app: FastAPI):
    """Setup all middleware for microservices"""
    setup_cors(app, ["http://localhost:3000", "http://localhost:8000"])
    setup_gzip(app)
    setup_exception_handlers(app)
    app.middleware("http")(log_requests_middleware)


def add_exception_handlers(app: FastAPI):
    """Alias for setup_exception_handlers"""
    setup_exception_handlers(app)
