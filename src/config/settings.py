"""
Configuration settings for Food Quality Analyzer
"""
import os
from typing import Optional
from pydantic import BaseSettings, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # API Configuration
    groq_api_key: str
    openai_api_key: Optional[str] = None
    
    # Database Configuration
    database_url: str = "sqlite:///./food_analyzer.db"
    redis_url: Optional[str] = None
    
    # OCR Configuration
    tesseract_path: Optional[str] = None
    ocr_language: str = "eng"
    ocr_config: str = "--oem 3 --psm 6"
    
    # Application Configuration
    app_name: str = "Food Quality Analyzer"
    app_version: str = "2.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set = {".png", ".jpg", ".jpeg", ".webp"}
    upload_folder: str = "uploads"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    
    # External APIs
    nutrition_api_key: Optional[str] = None
    fda_api_key: Optional[str] = None
    
    @validator('groq_api_key')
    def groq_api_key_must_be_set(cls, v):
        if not v:
            raise ValueError('GROQ_API_KEY must be set')
        return v
    
    @validator('secret_key')
    def secret_key_must_be_secure(cls, v):
        if v == "your-secret-key-change-in-production":
            raise ValueError('SECRET_KEY must be changed in production')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Chemical database configuration
HARMFUL_CHEMICALS = {
    "preservatives": {
        "BHA": {"risk_level": "high", "description": "Butylated hydroxyanisole - potential carcinogen"},
        "BHT": {"risk_level": "high", "description": "Butylated hydroxytoluene - potential carcinogen"},
        "sodium_benzoate": {"risk_level": "medium", "description": "May form benzene when combined with vitamin C"},
        "potassium_sorbate": {"risk_level": "low", "description": "Generally recognized as safe"},
    },
    "artificial_colors": {
        "red_40": {"risk_level": "medium", "description": "May cause hyperactivity in children"},
        "yellow_5": {"risk_level": "medium", "description": "May cause allergic reactions"},
        "blue_1": {"risk_level": "medium", "description": "May cause allergic reactions"},
        "caramel_color": {"risk_level": "medium", "description": "May contain 4-methylimidazole"},
    },
    "sweeteners": {
        "aspartame": {"risk_level": "medium", "description": "Avoid if phenylketonuria"},
        "sucralose": {"risk_level": "low", "description": "Generally recognized as safe"},
        "acesulfame_k": {"risk_level": "medium", "description": "Limited long-term studies"},
        "high_fructose_corn_syrup": {"risk_level": "high", "description": "Linked to obesity and diabetes"},
    },
    "emulsifiers": {
        "polysorbate_80": {"risk_level": "medium", "description": "May affect gut microbiome"},
        "carrageenan": {"risk_level": "medium", "description": "May cause digestive inflammation"},
        "lecithin": {"risk_level": "low", "description": "Generally recognized as safe"},
    }
}

# Nutrition scoring weights
NUTRITION_WEIGHTS = {
    "calories": 0.15,
    "total_fat": 0.12,
    "saturated_fat": 0.15,
    "trans_fat": 0.20,
    "cholesterol": 0.10,
    "sodium": 0.15,
    "total_carbs": 0.08,
    "fiber": -0.10,  # Negative weight (good)
    "sugars": 0.15,
    "protein": -0.15,  # Negative weight (good)
    "vitamins": -0.05,  # Negative weight (good)
}