"""
Admin routes for system management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from ...models import get_db, AnalysisSession, User, UserFeedback
from ...models.schemas import APIResponse
from ...config import get_settings

router = APIRouter()
security = HTTPBearer()
settings = get_settings()
logger = logging.getLogger(__name__)


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication token"""
    # In production, implement proper JWT token verification
    if credentials.credentials != "admin-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials


@router.get("/stats", response_model=APIResponse)
async def get_admin_statistics(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_token)
):
    """
    Get comprehensive admin statistics
    
    Returns:
        Detailed system statistics for admin dashboard
    """
    try:
        # Time periods
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Analysis statistics
        total_analyses = db.query(AnalysisSession).count()
        analyses_24h = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= last_24h
        ).count()
        analyses_7d = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= last_7d
        ).count()
        analyses_30d = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= last_30d
        ).count()
        
        # User statistics
        total_users = db.query(User).count()
        new_users_7d = db.query(User).filter(
            User.created_at >= last_7d
        ).count()
        active_users_7d = db.query(User).filter(
            User.updated_at >= last_7d
        ).count()
        
        # Performance statistics
        avg_processing_times = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= last_7d,
            AnalysisSession.processing_time.isnot(None)
        ).with_entities(AnalysisSession.processing_time).all()
        
        avg_processing_time = (
            sum(t[0] for t in avg_processing_times) / len(avg_processing_times)
            if avg_processing_times else 0
        )
        
        # Error analysis
        failed_analyses = db.query(AnalysisSession).filter(
            AnalysisSession.created_at >= last_7d,
            AnalysisSession.health_score.is_(None)
        ).count()
        
        success_rate = (
            (analyses_7d - failed_analyses) / max(analyses_7d, 1)
        ) if analyses_7d > 0 else 0
        
        # Feedback statistics
        feedback_entries = db.query(UserFeedback).filter(
            UserFeedback.created_at >= last_7d
        ).count()
        
        avg_ratings = db.query(UserFeedback).filter(
            UserFeedback.created_at >= last_7d,
            UserFeedback.rating.isnot(None)
        ).with_entities(UserFeedback.rating).all()
        
        avg_rating = (
            sum(r[0] for r in avg_ratings) / len(avg_ratings)
            if avg_ratings else 0
        )
        
        stats = {
            "analysis_stats": {
                "total": total_analyses,
                "last_24h": analyses_24h,
                "last_7d": analyses_7d,
                "last_30d": analyses_30d,
                "success_rate_7d": success_rate,
                "avg_processing_time_7d": avg_processing_time
            },
            "user_stats": {
                "total_users": total_users,
                "new_users_7d": new_users_7d,
                "active_users_7d": active_users_7d,
                "user_retention_rate": active_users_7d / max(total_users, 1)
            },
            "feedback_stats": {
                "total_feedback_7d": feedback_entries,
                "average_rating_7d": avg_rating,
                "feedback_rate_7d": feedback_entries / max(analyses_7d, 1)
            },
            "system_health": {
                "error_rate_7d": failed_analyses / max(analyses_7d, 1),
                "avg_response_time": avg_processing_time
            }
        }
        
        return APIResponse(
            success=True,
            message="Admin statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve admin statistics: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to retrieve statistics",
            errors=[str(e)]
        )


@router.get("/recent-analyses", response_model=APIResponse)
async def get_recent_analyses(
    limit: int = 50,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_token)
):
    """
    Get recent analysis sessions for admin review
    
    Args:
        limit: Maximum number of sessions to return
        db: Database session
        
    Returns:
        List of recent analysis sessions
    """
    try:
        sessions = db.query(AnalysisSession).order_by(
            AnalysisSession.created_at.desc()
        ).limit(limit).all()
        
        session_data = []
        for session in sessions:
            session_data.append({
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "processing_time": session.processing_time,
                "health_score": session.health_score,
                "novi_score": session.novi_score,
                "ocr_confidence": session.ocr_confidence,
                "has_nutrition_data": session.nutrition_data is not None,
                "chemical_count": len(session.chemical_analysis.get("detected_chemicals", [])) if session.chemical_analysis else 0
            })
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(session_data)} recent analyses",
            data=session_data
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve recent analyses: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to retrieve recent analyses",
            errors=[str(e)]
        )


@router.get("/feedback-summary", response_model=APIResponse)
async def get_feedback_summary(
    days: int = 7,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_token)
):
    """
    Get feedback summary for admin review
    
    Args:
        days: Number of days to include in summary
        db: Database session
        
    Returns:
        Feedback summary and insights
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        feedback_entries = db.query(UserFeedback).filter(
            UserFeedback.created_at >= cutoff_date
        ).all()
        
        # Categorize feedback
        feedback_by_type = {}
        ratings_by_type = {}
        
        for feedback in feedback_entries:
            feedback_type = feedback.feedback_type
            
            if feedback_type not in feedback_by_type:
                feedback_by_type[feedback_type] = 0
                ratings_by_type[feedback_type] = []
            
            feedback_by_type[feedback_type] += 1
            
            if feedback.rating:
                ratings_by_type[feedback_type].append(feedback.rating)
        
        # Calculate averages
        avg_ratings_by_type = {}
        for feedback_type, ratings in ratings_by_type.items():
            if ratings:
                avg_ratings_by_type[feedback_type] = sum(ratings) / len(ratings)
        
        # Get recent comments
        recent_comments = [
            {
                "feedback_type": f.feedback_type,
                "rating": f.rating,
                "comment": f.comment,
                "created_at": f.created_at.isoformat()
            }
            for f in feedback_entries[-10:]  # Last 10 comments
            if f.comment
        ]
        
        summary = {
            "period_days": days,
            "total_feedback": len(feedback_entries),
            "feedback_by_type": feedback_by_type,
            "average_ratings_by_type": avg_ratings_by_type,
            "recent_comments": recent_comments
        }
        
        return APIResponse(
            success=True,
            message="Feedback summary retrieved successfully",
            data=summary
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve feedback summary: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to retrieve feedback summary",
            errors=[str(e)]
        )


@router.post("/cleanup", response_model=APIResponse)
async def cleanup_old_data(
    days_to_keep: int = 90,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_token)
):
    """
    Clean up old data from the database
    
    Args:
        days_to_keep: Number of days of data to keep
        db: Database session
        
    Returns:
        Cleanup summary
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Count records to be deleted
        old_sessions = db.query(AnalysisSession).filter(
            AnalysisSession.created_at < cutoff_date
        ).count()
        
        old_feedback = db.query(UserFeedback).filter(
            UserFeedback.created_at < cutoff_date
        ).count()
        
        # Delete old records
        deleted_sessions = db.query(AnalysisSession).filter(
            AnalysisSession.created_at < cutoff_date
        ).delete()
        
        deleted_feedback = db.query(UserFeedback).filter(
            UserFeedback.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        cleanup_summary = {
            "cutoff_date": cutoff_date.isoformat(),
            "deleted_sessions": deleted_sessions,
            "deleted_feedback": deleted_feedback,
            "total_deleted": deleted_sessions + deleted_feedback
        }
        
        logger.info(f"Cleanup completed: {cleanup_summary}")
        
        return APIResponse(
            success=True,
            message="Data cleanup completed successfully",
            data=cleanup_summary
        )
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {str(e)}")
        db.rollback()
        return APIResponse(
            success=False,
            message="Data cleanup failed",
            errors=[str(e)]
        )


@router.get("/system-info", response_model=APIResponse)
async def get_system_info(
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_token)
):
    """
    Get system information for admin
    
    Returns:
        System configuration and status
    """
    try:
        import psutil
        import platform
        
        system_info = {
            "application": {
                "name": settings.app_name,
                "version": settings.app_version,
                "debug_mode": settings.debug,
                "log_level": settings.log_level
            },
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "disk_total_gb": psutil.disk_usage('/').total / (1024**3)
            },
            "configuration": {
                "max_file_size_mb": settings.max_file_size / (1024*1024),
                "rate_limit_per_minute": settings.rate_limit_per_minute,
                "database_url": settings.database_url.split('@')[-1] if '@' in settings.database_url else "sqlite",
                "ocr_language": settings.ocr_language
            }
        }
        
        return APIResponse(
            success=True,
            message="System information retrieved successfully",
            data=system_info
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve system info: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to retrieve system information",
            errors=[str(e)]
        )