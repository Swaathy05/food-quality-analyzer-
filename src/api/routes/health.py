"""
Health check and monitoring routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from ...models import get_db, AnalysisSession, User, UserFeedback
from ...models.schemas import APIResponse, HealthMetrics
from ...config import get_settings
from ..middleware import get_metrics

router = APIRouter()
settings = get_settings()


@router.get("/check", response_model=APIResponse)
async def health_check():
    """
    Basic health check endpoint
    
    Returns:
        System health status
    """
    try:
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": settings.app_version,
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "disk_usage": f"{disk.percent}%",
                "available_memory": f"{memory.available / (1024**3):.2f} GB"
            }
        }
        
        # Determine overall health
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_status["status"] = "degraded"
        
        return APIResponse(
            success=True,
            message="Health check completed",
            data=health_status
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Health check failed",
            errors=[str(e)]
        )


@router.get("/metrics", response_model=APIResponse)
async def get_application_metrics(db: Session = Depends(get_db)):
    """
    Get comprehensive application metrics
    
    Returns:
        Application performance and usage metrics
    """
    try:
        # Get middleware metrics
        middleware_metrics = get_metrics()
        
        # Get database metrics
        db_metrics = await get_database_metrics(db)
        
        # Get system metrics
        system_metrics = get_system_metrics()
        
        # Combine all metrics
        all_metrics = {
            "timestamp": datetime.now().isoformat(),
            "application": middleware_metrics,
            "database": db_metrics,
            "system": system_metrics
        }
        
        return APIResponse(
            success=True,
            message="Metrics retrieved successfully",
            data=all_metrics
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Failed to retrieve metrics",
            errors=[str(e)]
        )


@router.get("/analytics", response_model=APIResponse)
async def get_analytics_dashboard(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get analytics data for dashboard
    
    Args:
        days: Number of days to include in analytics
        db: Database session
        
    Returns:
        Analytics dashboard data
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Analysis statistics
        total_analyses = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= cutoff_date
        ).count()
        
        successful_analyses = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= cutoff_date,
            AnalysisSession.health_score.isnot(None)
        ).count()
        
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(
            User.updated_at >= cutoff_date
        ).count()
        
        # Feedback statistics
        feedback_count = db.query(UserFeedback).filter(
            UserFeedback.created_at >= cutoff_date
        ).count()
        
        avg_rating = db.query(UserFeedback).filter(
            UserFeedback.created_at >= cutoff_date,
            UserFeedback.rating.isnot(None)
        ).with_entities(UserFeedback.rating).all()
        
        average_rating = sum(r[0] for r in avg_rating) / len(avg_rating) if avg_rating else 0
        
        # Performance metrics
        avg_processing_time = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= cutoff_date,
            AnalysisSession.processing_time.isnot(None)
        ).with_entities(AnalysisSession.processing_time).all()
        
        avg_time = sum(t[0] for t in avg_processing_time) / len(avg_processing_time) if avg_processing_time else 0
        
        analytics_data = {
            "period_days": days,
            "analysis_stats": {
                "total_analyses": total_analyses,
                "successful_analyses": successful_analyses,
                "success_rate": successful_analyses / max(total_analyses, 1),
                "average_processing_time": avg_time
            },
            "user_stats": {
                "total_users": total_users,
                "active_users": active_users,
                "activity_rate": active_users / max(total_users, 1)
            },
            "feedback_stats": {
                "total_feedback": feedback_count,
                "average_rating": average_rating,
                "feedback_rate": feedback_count / max(total_analyses, 1)
            }
        }
        
        return APIResponse(
            success=True,
            message="Analytics retrieved successfully",
            data=analytics_data
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Failed to retrieve analytics",
            errors=[str(e)]
        )


@router.get("/status", response_model=APIResponse)
async def get_service_status():
    """
    Get detailed service status
    
    Returns:
        Detailed status of all services
    """
    try:
        from ...services import OCRService, AnalysisService
        
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "services": {
                "ocr_service": await check_ocr_service(),
                "analysis_service": await check_analysis_service(),
                "database": await check_database_connection(),
            },
            "configuration": {
                "debug_mode": settings.debug,
                "rate_limit": settings.rate_limit_per_minute,
                "max_file_size": settings.max_file_size
            }
        }
        
        # Determine overall status
        all_services_healthy = all(
            service["status"] == "healthy" 
            for service in status_data["services"].values()
        )
        
        status_data["overall_status"] = "healthy" if all_services_healthy else "degraded"
        
        return APIResponse(
            success=True,
            message="Service status retrieved",
            data=status_data
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            message="Failed to get service status",
            errors=[str(e)]
        )


# Helper functions
async def get_database_metrics(db: Session) -> Dict[str, Any]:
    """Get database-related metrics"""
    try:
        total_sessions = db.query(AnalysisSession).count()
        total_users = db.query(User).count()
        total_feedback = db.query(UserFeedback).count()
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_sessions = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= recent_cutoff
        ).count()
        
        return {
            "total_analysis_sessions": total_sessions,
            "total_users": total_users,
            "total_feedback_entries": total_feedback,
            "recent_sessions_24h": recent_sessions,
            "database_status": "connected"
        }
        
    except Exception as e:
        return {
            "database_status": "error",
            "error": str(e)
        }


def get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_usage_percent": disk.percent,
            "disk_free_gb": disk.free / (1024**3),
            "uptime_seconds": time.time() - psutil.boot_time()
        }
        
    except Exception as e:
        return {
            "system_status": "error",
            "error": str(e)
        }


async def check_ocr_service() -> Dict[str, Any]:
    """Check OCR service health"""
    try:
        import pytesseract
        
        # Test Tesseract availability
        version = pytesseract.get_tesseract_version()
        
        return {
            "status": "healthy",
            "tesseract_version": str(version),
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }


async def check_analysis_service() -> Dict[str, Any]:
    """Check analysis service health"""
    try:
        # Test AI model availability
        from ...services import AnalysisService
        
        service = AnalysisService()
        
        if service.primary_llm:
            model_status = "primary_available"
        elif service.fallback_llm:
            model_status = "fallback_available"
        else:
            model_status = "no_models_available"
        
        return {
            "status": "healthy" if model_status != "no_models_available" else "degraded",
            "model_status": model_status,
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }


async def check_database_connection() -> Dict[str, Any]:
    """Check database connection health"""
    try:
        from ...models.database import SessionLocal
        
        db = SessionLocal()
        
        # Simple query to test connection
        result = db.execute("SELECT 1").fetchone()
        db.close()
        
        return {
            "status": "healthy",
            "connection": "active",
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "connection": "failed",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }