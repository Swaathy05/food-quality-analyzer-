"""
Custom exceptions for the Food Quality Analyzer
"""


class FoodAnalyzerError(Exception):
    """Base exception for Food Quality Analyzer"""
    pass


class OCRError(FoodAnalyzerError):
    """Exception raised for OCR-related errors"""
    pass


class ImageProcessingError(FoodAnalyzerError):
    """Exception raised for image processing errors"""
    pass


class AnalysisError(FoodAnalyzerError):
    """Exception raised for analysis-related errors"""
    pass


class AIServiceError(FoodAnalyzerError):
    """Exception raised for AI service errors"""
    pass


class DatabaseError(FoodAnalyzerError):
    """Exception raised for database-related errors"""
    pass


class ValidationError(FoodAnalyzerError):
    """Exception raised for validation errors"""
    pass


class RateLimitError(FoodAnalyzerError):
    """Exception raised when rate limit is exceeded"""
    pass


class AuthenticationError(FoodAnalyzerError):
    """Exception raised for authentication errors"""
    pass