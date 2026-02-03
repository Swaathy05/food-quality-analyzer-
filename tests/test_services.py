"""
Service layer tests
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np

from src.services import OCRService, AnalysisService
from src.models.schemas import UserProfile, NutritionData, ChemicalAnalysis
from src.utils.exceptions import OCRError, AnalysisError


class TestOCRService:
    """Test OCR service functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ocr_service = OCRService()
        self.test_image = Image.new('RGB', (800, 600), color='white')
    
    @patch('pytesseract.image_to_string')
    def test_extract_text_success(self, mock_tesseract):
        """Test successful text extraction"""
        mock_tesseract.return_value = "Nutrition Facts\nCalories 250\nTotal Fat 10g"
        
        result = self.ocr_service.extract_text(self.test_image)
        
        assert result.text is not None
        assert len(result.text) > 0
        assert result.confidence >= 0
        assert result.processing_time > 0
        assert result.method_used is not None
    
    @patch('pytesseract.image_to_string')
    def test_extract_text_empty_result(self, mock_tesseract):
        """Test OCR with empty result"""
        mock_tesseract.return_value = ""
        
        result = self.ocr_service.extract_text(self.test_image)
        
        assert result.text == ""
        assert result.confidence >= 0
    
    @patch('pytesseract.image_to_string')
    def test_extract_text_error(self, mock_tesseract):
        """Test OCR error handling"""
        mock_tesseract.side_effect = Exception("Tesseract error")
        
        with pytest.raises(OCRError):
            self.ocr_service.extract_text(self.test_image)
    
    def test_validate_extraction(self):
        """Test text validation"""
        # Valid nutrition text
        valid_text = "Nutrition Facts Calories 250 Total Fat 10g Protein 5g"
        result = self.ocr_service.validate_extraction(valid_text)
        assert result['is_valid'] is True
        assert result['confidence'] > 0
        
        # Invalid text
        invalid_text = "Random text with no nutrition info"
        result = self.ocr_service.validate_extraction(invalid_text)
        assert result['is_valid'] is False
        assert len(result['issues']) > 0


class TestAnalysisService:
    """Test analysis service functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.analysis_service = AnalysisService()
        self.test_text = "Nutrition Facts Calories 250 Total Fat 10g Sodium 600mg"
        self.test_profile = UserProfile(
            allergies=["gluten"],
            dietary_restrictions=["low sodium"],
            health_conditions=["diabetes"]
        )
    
    @patch('src.services.analysis_service.AnalysisService._get_ai_recommendations')
    @patch('src.utils.nutrition_parser.NutritionParser.parse')
    @patch('src.utils.chemical_detector.ChemicalDetector.detect_chemicals')
    async def test_analyze_food_comprehensive(self, mock_chemicals, mock_nutrition, mock_ai):
        """Test comprehensive food analysis"""
        # Mock nutrition data
        mock_nutrition.return_value = NutritionData(
            calories=250,
            total_fat=10,
            sodium=600
        )
        
        # Mock chemical analysis
        mock_chemicals.return_value = []
        
        # Mock AI recommendations
        mock_ai.return_value = {
            "benefits": ["Provides energy"],
            "risks": ["High sodium"],
            "alternatives": ["Low sodium version"],
            "tips": ["Consume in moderation"],
            "portion_size": "1 serving",
            "frequency": "Occasionally"
        }
        
        result = await self.analysis_service.analyze_food_comprehensive(
            extracted_text=self.test_text,
            user_profile=self.test_profile,
            session_id="test_session"
        )
        
        assert result is not None
        assert result.session_id == "test_session"
        assert result.nutrition_data is not None
        assert result.chemical_analysis is not None
        assert result.health_recommendation is not None
        assert result.processing_time > 0
    
    def test_calculate_nutrition_score(self):
        """Test nutrition score calculation"""
        # Good nutrition
        good_nutrition = NutritionData(
            calories=200,
            total_fat=5,
            sodium=300,
            dietary_fiber=5,
            protein=15
        )
        score = self.analysis_service._calculate_nutrition_score(good_nutrition)
        assert score >= 6.0
        
        # Poor nutrition
        poor_nutrition = NutritionData(
            calories=500,
            total_fat=25,
            sodium=1200,
            total_sugars=30,
            trans_fat=2
        )
        score = self.analysis_service._calculate_nutrition_score(poor_nutrition)
        assert score <= 5.0
    
    def test_calculate_novi_score(self):
        """Test NOVI score calculation"""
        nutrition = NutritionData(calories=250, dietary_fiber=6, protein=20)
        chemical_analysis = ChemicalAnalysis()
        
        score = self.analysis_service._calculate_novi_score(nutrition, chemical_analysis)
        assert 0 <= score <= 100
    
    def test_check_allergens(self):
        """Test allergen checking"""
        text = "Contains wheat, soy, and milk ingredients"
        profile = UserProfile(allergies=["wheat", "soy"])
        
        warnings = self.analysis_service._check_allergens(text, profile)
        assert len(warnings) >= 2  # Should detect wheat and soy
    
    def test_check_health_conditions(self):
        """Test health condition warnings"""
        nutrition = NutritionData(
            total_sugars=25,
            sodium=800,
            saturated_fat=8
        )
        profile = UserProfile(health_conditions=["diabetes", "hypertension"])
        
        warnings = self.analysis_service._check_health_conditions(nutrition, profile)
        assert len(warnings) > 0  # Should have warnings for high sugar and sodium


class TestNutritionParser:
    """Test nutrition parsing functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        from src.utils.nutrition_parser import NutritionParser
        self.parser = NutritionParser()
    
    def test_parse_nutrition_data(self):
        """Test nutrition data parsing"""
        text = """
        Nutrition Facts
        Serving Size 1 cup (240ml)
        Calories 250
        Total Fat 10g
        Saturated Fat 3g
        Sodium 600mg
        Total Carbohydrate 30g
        Dietary Fiber 5g
        Total Sugars 15g
        Protein 8g
        """
        
        result = self.parser.parse(text)
        
        assert result is not None
        assert result.calories == 250
        assert result.total_fat == 10
        assert result.saturated_fat == 3
        assert result.sodium == 600
        assert result.protein == 8
    
    def test_parse_empty_text(self):
        """Test parsing empty text"""
        result = self.parser.parse("")
        assert result is None
    
    def test_parse_invalid_text(self):
        """Test parsing invalid text"""
        result = self.parser.parse("This is not a nutrition label")
        assert result is None
    
    def test_validate_nutrition_data(self):
        """Test nutrition data validation"""
        # Valid data
        valid_data = NutritionData(
            calories=250,
            total_fat=10,
            saturated_fat=3,
            total_sugars=15,
            added_sugars=10
        )
        result = self.parser.validate_nutrition_data(valid_data)
        assert result['is_valid'] is True
        
        # Invalid data (saturated fat > total fat)
        invalid_data = NutritionData(
            total_fat=5,
            saturated_fat=10  # This is invalid
        )
        result = self.parser.validate_nutrition_data(invalid_data)
        assert result['is_valid'] is False
        assert len(result['errors']) > 0


class TestChemicalDetector:
    """Test chemical detection functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        from src.utils.chemical_detector import ChemicalDetector
        self.detector = ChemicalDetector()
    
    def test_detect_chemicals(self):
        """Test chemical detection"""
        text = "Ingredients: Water, High Fructose Corn Syrup, BHA, Red 40, Sodium Benzoate"
        
        chemicals = self.detector.detect_chemicals(text)
        
        assert len(chemicals) > 0
        chemical_names = [c.name.lower() for c in chemicals]
        assert any("bha" in name for name in chemical_names)
        assert any("red" in name for name in chemical_names)
    
    def test_detect_no_chemicals(self):
        """Test detection with no chemicals"""
        text = "Ingredients: Water, Organic Cane Sugar, Natural Flavors"
        
        chemicals = self.detector.detect_chemicals(text)
        
        # Should detect few or no harmful chemicals
        assert len(chemicals) <= 1
    
    def test_pattern_based_detection(self):
        """Test pattern-based chemical detection"""
        text = "Contains E100, FD&C Red 40, and Monosodium Glutamate"
        
        matches = self.detector._pattern_based_detection(text.lower())
        
        assert len(matches) > 0
    
    def test_keyword_based_detection(self):
        """Test keyword-based detection"""
        text = "Contains aspartame and carrageenan"
        
        matches = self.detector._keyword_based_detection(text.lower())
        
        assert len(matches) >= 2  # Should detect both chemicals


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    mock = Mock()
    mock.invoke.return_value.content = '{"benefits": ["test"], "risks": ["test"]}'
    return mock