"""
FastAPI main application with CORS, middleware, and all API routes.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.database import engine
from app.models import Base  # Import Base to ensure all models are registered
from app.api.v1 import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    On startup:
    - Creates database tables (if they don't exist)
    - Logs startup message

    On shutdown:
    - Closes database connections
    """
    # Startup
    logger.info("Starting AI Chat Application backend...")
    logger.info(f"Environment: {settings.DEBUG and 'Development' or 'Production'}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")

    # Create tables (in production, use Alembic migrations instead)
    if settings.DEBUG:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="AI Chat Application API",
    description=(
        "Backend API for AI Chat Application with dual services:\n\n"
        "- **AskAT&T**: General OpenAI chat service\n"
        "- **AskDocs**: Domain-specific RAG chat with vector search and source attribution\n\n"
        "Features:\n"
        "- JWT authentication with role-based access control\n"
        "- Token-by-token Server-Sent Events (SSE) streaming\n"
        "- Conversation persistence and history\n"
        "- Feedback collection per message\n"
        "- Admin panel for user/role/configuration management"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # List of allowed origins from config
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers to the frontend
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests with timing information.
    """
    start_time = time.time()

    # Log request
    logger.info(f"→ {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response with timing
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    logger.info(
        f"← {request.method} {request.url.path} "
        f"[{response.status_code}] {process_time:.2f}ms"
    )

    # Add custom header with processing time
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed error messages.
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler for unexpected errors.
    """
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns application status and version.
    """
    return {
        "status": "healthy",
        "service": "AI Chat Application API",
        "version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production"
    }


# Include API v1 routes
app.include_router(api_router, prefix="/api")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information and documentation links.
    """
    return {
        "message": "AI Chat Application API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn for development
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
