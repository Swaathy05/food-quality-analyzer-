"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class AgeGroup(str, Enum):
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    SENIOR = "senior"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserProfile(BaseModel):
    """User health profile schema"""
    user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    allergies: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    health_conditions: List[str] = Field(default_factory=list)
    age_group: Optional[AgeGroup] = None
    activity_level: Optional[ActivityLevel] = None
    preferred_language: str = "en"
    
    @validator('allergies', 'dietary_restrictions', 'health_conditions')
    def clean_lists(cls, v):
        return [item.strip().lower() for item in v if item.strip()]


class NutritionData(BaseModel):
    """Nutrition facts schema"""
    serving_size: Optional[str] = None
    servings_per_container: Optional[float] = None
    calories: Optional[float] = None
    calories_from_fat: Optional[float] = None
    
    # Fats
    total_fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    polyunsaturated_fat: Optional[float] = None
    monounsaturated_fat: Optional[float] = None
    
    # Other nutrients
    cholesterol: Optional[float] = None
    sodium: Optional[float] = None
    total_carbohydrates: Optional[float] = None
    dietary_fiber: Optional[float] = None
    total_sugars: Optional[float] = None
    added_sugars: Optional[float] = None
    protein: Optional[float] = None
    
    # Vitamins and minerals
    vitamin_d: Optional[float] = None
    calcium: Optional[float] = None
    iron: Optional[float] = None
    potassium: Optional[float] = None
    vitamin_a: Optional[float] = None
    vitamin_c: Optional[float] = None
    
    # Additional nutrients
    other_nutrients: Dict[str, float] = Field(default_factory=dict)


class ChemicalInfo(BaseModel):
    """Individual chemical information"""
    name: str
    category: str  # preservative, artificial_color, sweetener, etc.
    risk_level: RiskLevel
    description: str
    health_effects: List[str] = Field(default_factory=list)
    safe_limit: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)


class ChemicalAnalysis(BaseModel):
    """Chemical analysis results"""
    detected_chemicals: List[ChemicalInfo] = Field(default_factory=list)
    risk_summary: Dict[RiskLevel, int] = Field(default_factory=dict)
    overall_risk_level: RiskLevel = RiskLevel.LOW
    safety_score: float = Field(ge=0, le=10)  # 0-10 scale
    recommendations: List[str] = Field(default_factory=list)


class HealthRecommendation(BaseModel):
    """Health recommendation schema"""
    overall_score: float = Field(ge=0, le=10)
    novi_score: float = Field(ge=0, le=100)
    recommendation_type: str  # "consume", "limit", "avoid"
    portion_size: Optional[str] = None
    frequency: Optional[str] = None
    
    # Personalized warnings
    allergen_warnings: List[str] = Field(default_factory=list)
    health_condition_warnings: List[str] = Field(default_factory=list)
    
    # Recommendations
    benefits: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    session_id: str
    timestamp: datetime
    
    # Input data
    extracted_text: str
    ocr_confidence: Optional[float] = None
    
    # Analysis results
    nutrition_data: Optional[NutritionData] = None
    chemical_analysis: ChemicalAnalysis
    health_recommendation: HealthRecommendation
    
    # Processing metadata
    processing_time: float
    model_version: str
    confidence_score: float = Field(ge=0, le=1)


class AnalysisRequest(BaseModel):
    """Analysis request schema"""
    user_profile: Optional[UserProfile] = None
    image_data: Optional[str] = None  # Base64 encoded image
    extracted_text: Optional[str] = None  # Pre-extracted text
    analysis_options: Dict[str, Any] = Field(default_factory=dict)


class FeedbackRequest(BaseModel):
    """User feedback schema"""
    session_id: str
    feedback_type: str = Field(regex="^(accuracy|usefulness|bug_report|general)$")
    rating: Optional[int] = Field(ge=1, le=5)
    comment: Optional[str] = None
    analysis_accuracy: Optional[int] = Field(ge=1, le=5)
    recommendation_usefulness: Optional[int] = Field(ge=1, le=5)


class APIResponse(BaseModel):
    """Standard API response schema"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthMetrics(BaseModel):
    """Health metrics for monitoring"""
    total_analyses: int
    average_processing_time: float
    success_rate: float
    user_satisfaction: float
    common_allergens: List[str]
    risk_distribution: Dict[RiskLevel, int]


class ProductInfo(BaseModel):
    """Product information schema"""
    product_id: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    ingredients: List[str] = Field(default_factory=list)
    nutrition_data: Optional[NutritionData] = None
    verified: bool = False
    data_source: str = "user_upload"