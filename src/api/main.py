"""
FastAPI main application with production-ready features
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from ..config import get_settings
from ..models.database import create_tables
from .routes import analysis, health, admin
from .middleware import RateLimitMiddleware, LoggingMiddleware, SecurityMiddleware
from ..utils.exceptions import FoodAnalyzerError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Food Quality Analyzer API")
    create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Food Quality Analyzer API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered food quality and chemical analysis system",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["yourdomain.com", "*.yourdomain.com"]
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityMiddleware)


# Global exception handler
@app.exception_handler(FoodAnalyzerError)
async def food_analyzer_exception_handler(request: Request, exc: FoodAnalyzerError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": str(exc),
            "error_type": exc.__class__.__name__
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_type": "HTTPException"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_type": "InternalServerError"
        }
    )


# Include routers
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Food Quality Analyzer API",
        "version": settings.app_version,
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI-powered food quality and chemical analysis",
        "features": [
            "OCR text extraction from nutrition labels",
            "Chemical detection and risk assessment",
            "Personalized health recommendations",
            "NOVI nutrition scoring",
            "Allergen detection",
            "Health condition warnings"
        ],
        "endpoints": {
            "analyze": "/api/v1/analysis/analyze",
            "health_check": "/api/v1/health/check",
            "metrics": "/api/v1/health/metrics"
        }
    }