"""
Analysis API routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import base64
import io
from PIL import Image
import logging
import uuid
from typing import Optional

from ...models import get_db, save_analysis_session, log_api_usage
from ...models.schemas import (
    AnalysisRequest, AnalysisResult, UserProfile, APIResponse, FeedbackRequest
)
from ...services import OCRService, AnalysisService
from ...utils.exceptions import OCRError, AnalysisError, ValidationError
from ...config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Initialize services
ocr_service = OCRService()
analysis_service = AnalysisService()


@router.post("/analyze", response_model=APIResponse)
async def analyze_food_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_profile: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze food nutrition label from uploaded image
    
    Args:
        file: Uploaded image file
        user_profile: JSON string of user health profile (optional)
        db: Database session
        
    Returns:
        Complete analysis result with recommendations
    """
    session_id = str(uuid.uuid4())
    
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise ValidationError("File must be an image")
        
        if file.size > settings.max_file_size:
            raise ValidationError(f"File size exceeds {settings.max_file_size} bytes")
        
        # Read and validate image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Parse user profile if provided
        profile = None
        if user_profile:
            import json
            try:
                profile_data = json.loads(user_profile)
                profile = UserProfile(**profile_data)
            except Exception as e:
                logger.warning(f"Invalid user profile: {str(e)}")
        
        # Extract text using OCR
        logger.info(f"Starting OCR extraction for session {session_id}")
        ocr_result = ocr_service.extract_text(image)
        
        if not ocr_result.text.strip():
            raise OCRError("No text could be extracted from the image")
        
        # Perform comprehensive analysis
        logger.info(f"Starting analysis for session {session_id}")
        analysis_result = await analysis_service.analyze_food_comprehensive(
            extracted_text=ocr_result.text,
            user_profile=profile,
            session_id=session_id
        )
        
        # Save to database in background
        background_tasks.add_task(
            save_analysis_to_db,
            db, session_id, ocr_result, analysis_result, file.filename
        )
        
        return APIResponse(
            success=True,
            message="Analysis completed successfully",
            data=analysis_result.dict()
        )
        
    except (OCRError, AnalysisError, ValidationError) as e:
        logger.error(f"Analysis failed for session {session_id}: {str(e)}")
        return APIResponse(
            success=False,
            message=str(e),
            errors=[str(e)]
        )
    except Exception as e:
        logger.error(f"Unexpected error in analysis {session_id}: {str(e)}", exc_info=True)
        return APIResponse(
            success=False,
            message="Internal server error",
            errors=["Analysis failed due to internal error"]
        )


@router.post("/analyze-text", response_model=APIResponse)
async def analyze_nutrition_text(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze nutrition data from provided text
    
    Args:
        request: Analysis request with text and user profile
        db: Database session
        
    Returns:
        Analysis result
    """
    session_id = str(uuid.uuid4())
    
    try:
        if not request.extracted_text:
            raise ValidationError("Text is required for analysis")
        
        # Perform analysis
        analysis_result = await analysis_service.analyze_food_comprehensive(
            extracted_text=request.extracted_text,
            user_profile=request.user_profile,
            session_id=session_id
        )
        
        # Save to database in background
        background_tasks.add_task(
            save_text_analysis_to_db,
            db, session_id, request.extracted_text, analysis_result
        )
        
        return APIResponse(
            success=True,
            message="Text analysis completed successfully",
            data=analysis_result.dict()
        )
        
    except (AnalysisError, ValidationError) as e:
        logger.error(f"Text analysis failed for session {session_id}: {str(e)}")
        return APIResponse(
            success=False,
            message=str(e),
            errors=[str(e)]
        )
    except Exception as e:
        logger.error(f"Unexpected error in text analysis {session_id}: {str(e)}", exc_info=True)
        return APIResponse(
            success=False,
            message="Internal server error",
            errors=["Analysis failed due to internal error"]
        )


@router.post("/feedback", response_model=APIResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Submit user feedback for an analysis session
    
    Args:
        feedback: User feedback data
        db: Database session
        
    Returns:
        Success response
    """
    try:
        from ...models import save_user_feedback
        
        feedback_data = {
            "session_id": feedback.session_id,
            "feedback_type": feedback.feedback_type,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "analysis_accuracy": feedback.analysis_accuracy,
            "recommendation_usefulness": feedback.recommendation_usefulness
        }
        
        save_user_feedback(db, feedback_data)
        
        return APIResponse(
            success=True,
            message="Feedback submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Feedback submission failed: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to submit feedback",
            errors=[str(e)]
        )


@router.get("/session/{session_id}", response_model=APIResponse)
async def get_analysis_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve analysis session by ID
    
    Args:
        session_id: Analysis session ID
        db: Database session
        
    Returns:
        Analysis session data
    """
    try:
        from ...models import AnalysisSession
        
        session = db.query(AnalysisSession).filter(
            AnalysisSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return APIResponse(
            success=True,
            message="Session retrieved successfully",
            data={
                "session_id": session.session_id,
                "extracted_text": session.extracted_text,
                "nutrition_data": session.nutrition_data,
                "chemical_analysis": session.chemical_analysis,
                "health_score": session.health_score,
                "novi_score": session.novi_score,
                "recommendations": session.recommendations,
                "created_at": session.created_at.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session retrieval failed: {str(e)}")
        return APIResponse(
            success=False,
            message="Failed to retrieve session",
            errors=[str(e)]
        )


@router.get("/validate-image")
async def validate_image_quality(file: UploadFile = File(...)):
    """
    Validate image quality for OCR suitability
    
    Args:
        file: Uploaded image file
        
    Returns:
        Image quality assessment
    """
    try:
        if not file.content_type.startswith('image/'):
            raise ValidationError("File must be an image")
        
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Validate with OCR service
        validation_result = ocr_service.validate_extraction("")
        
        return APIResponse(
            success=True,
            message="Image validation completed",
            data=validation_result
        )
        
    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        return APIResponse(
            success=False,
            message="Image validation failed",
            errors=[str(e)]
        )


# Background task functions
async def save_analysis_to_db(
    db: Session,
    session_id: str,
    ocr_result,
    analysis_result: AnalysisResult,
    filename: str
):
    """Save analysis result to database"""
    try:
        session_data = {
            "session_id": session_id,
            "image_filename": filename,
            "image_hash": ocr_result.image_hash,
            "extracted_text": ocr_result.text,
            "ocr_confidence": ocr_result.confidence,
            "nutrition_data": analysis_result.nutrition_data.dict() if analysis_result.nutrition_data else None,
            "chemical_analysis": analysis_result.chemical_analysis.dict(),
            "health_score": analysis_result.health_recommendation.overall_score,
            "novi_score": analysis_result.health_recommendation.novi_score,
            "recommendations": analysis_result.health_recommendation.dict(),
            "processing_time": analysis_result.processing_time,
            "model_version": analysis_result.model_version
        }
        
        save_analysis_session(db, session_data)
        logger.info(f"Analysis session {session_id} saved to database")
        
    except Exception as e:
        logger.error(f"Failed to save analysis session {session_id}: {str(e)}")


async def save_text_analysis_to_db(
    db: Session,
    session_id: str,
    extracted_text: str,
    analysis_result: AnalysisResult
):
    """Save text analysis result to database"""
    try:
        session_data = {
            "session_id": session_id,
            "extracted_text": extracted_text,
            "nutrition_data": analysis_result.nutrition_data.dict() if analysis_result.nutrition_data else None,
            "chemical_analysis": analysis_result.chemical_analysis.dict(),
            "health_score": analysis_result.health_recommendation.overall_score,
            "novi_score": analysis_result.health_recommendation.novi_score,
            "recommendations": analysis_result.health_recommendation.dict(),
            "processing_time": analysis_result.processing_time,
            "model_version": analysis_result.model_version
        }
        
        save_analysis_session(db, session_data)
        logger.info(f"Text analysis session {session_id} saved to database")
        
    except Exception as e:
        logger.error(f"Failed to save text analysis session {session_id}: {str(e)}")