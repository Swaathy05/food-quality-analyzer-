"""
Database models and connection management
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from ..config import get_settings

settings = get_settings()

# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User model for storing user profiles"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    
    # Health profile
    allergies = Column(JSON, default=list)
    dietary_restrictions = Column(JSON, default=list)
    health_conditions = Column(JSON, default=list)
    age_group = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    
    # Preferences
    preferred_language = Column(String, default="en")
    notification_preferences = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)


class AnalysisSession(Base):
    """Model for storing analysis sessions"""
    __tablename__ = "analysis_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=True)
    
    # Image and OCR data
    image_filename = Column(String)
    image_hash = Column(String, index=True)  # For deduplication
    extracted_text = Column(Text)
    ocr_confidence = Column(Float, nullable=True)
    
    # Analysis results
    nutrition_data = Column(JSON)
    chemical_analysis = Column(JSON)
    health_score = Column(Float, nullable=True)
    novi_score = Column(Float, nullable=True)
    recommendations = Column(Text)
    
    # Metadata
    processing_time = Column(Float)  # in seconds
    model_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProductDatabase(Base):
    """Model for storing known products"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    brand = Column(String, index=True, nullable=True)
    barcode = Column(String, index=True, nullable=True)
    
    # Nutrition information
    nutrition_facts = Column(JSON)
    ingredients = Column(JSON)
    allergens = Column(JSON)
    
    # Analysis cache
    health_score = Column(Float, nullable=True)
    novi_score = Column(Float, nullable=True)
    chemical_analysis = Column(JSON)
    
    # Metadata
    data_source = Column(String)  # "user_upload", "fda_api", "nutrition_api"
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserFeedback(Base):
    """Model for storing user feedback"""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_id = Column(String, index=True, nullable=True)
    
    feedback_type = Column(String)  # "accuracy", "usefulness", "bug_report"
    rating = Column(Integer, nullable=True)  # 1-5 scale
    comment = Column(Text, nullable=True)
    
    # Context
    analysis_accuracy = Column(Integer, nullable=True)  # 1-5 scale
    recommendation_usefulness = Column(Integer, nullable=True)  # 1-5 scale
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class APIUsage(Base):
    """Model for tracking API usage and rate limiting"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    ip_address = Column(String, index=True)
    endpoint = Column(String)
    
    # Usage metrics
    request_count = Column(Integer, default=1)
    processing_time = Column(Float)
    success = Column(Boolean)
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Database utility functions
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.user_id == user_id).first()


def create_user(db: Session, user_data: Dict[str, Any]) -> User:
    """Create new user"""
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_analysis_session(db: Session, session_data: Dict[str, Any]) -> AnalysisSession:
    """Save analysis session"""
    session = AnalysisSession(**session_data)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_product_by_barcode(db: Session, barcode: str) -> Optional[ProductDatabase]:
    """Get product by barcode"""
    return db.query(ProductDatabase).filter(ProductDatabase.barcode == barcode).first()


def save_user_feedback(db: Session, feedback_data: Dict[str, Any]) -> UserFeedback:
    """Save user feedback"""
    feedback = UserFeedback(**feedback_data)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def log_api_usage(db: Session, usage_data: Dict[str, Any]) -> APIUsage:
    """Log API usage"""
    usage = APIUsage(**usage_data)
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage