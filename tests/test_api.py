"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import io
from PIL import Image

from src.api.main import app

client = TestClient(app)


class TestAnalysisAPI:
    """Test analysis API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Food Quality Analyzer API"
        assert "version" in data
        assert "status" in data
    
    def test_api_info_endpoint(self):
        """Test API info endpoint"""
        response = client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Food Quality Analyzer"
        assert "features" in data
        assert "endpoints" in data
    
    @patch('src.services.OCRService.extract_text')
    @patch('src.services.AnalysisService.analyze_food_comprehensive')
    def test_analyze_image_endpoint(self, mock_analysis, mock_ocr):
        """Test image analysis endpoint"""
        # Mock OCR result
        mock_ocr_result = Mock()
        mock_ocr_result.text = "Nutrition Facts Calories 250 Total Fat 10g"
        mock_ocr_result.confidence = 0.9
        mock_ocr_result.image_hash = "test_hash"
        mock_ocr.return_value = mock_ocr_result
        
        # Mock analysis result
        mock_analysis_result = Mock()
        mock_analysis_result.dict.return_value = {
            "session_id": "test_session",
            "health_score": 7.5,
            "novi_score": 75.0
        }
        mock_analysis.return_value = mock_analysis_result
        
        # Create test image
        image = Image.new('RGB', (800, 600), color='white')
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Test request
        response = client.post(
            "/api/v1/analysis/analyze",
            files={"file": ("test.png", img_buffer, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_analyze_image_invalid_file(self):
        """Test image analysis with invalid file"""
        response = client.post(
            "/api/v1/analysis/analyze",
            files={"file": ("test.txt", io.StringIO("not an image"), "text/plain")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "File must be an image" in data["message"]
    
    def test_analyze_text_endpoint(self):
        """Test text analysis endpoint"""
        with patch('src.services.AnalysisService.analyze_food_comprehensive') as mock_analysis:
            mock_result = Mock()
            mock_result.dict.return_value = {"session_id": "test", "health_score": 8.0}
            mock_analysis.return_value = mock_result
            
            response = client.post(
                "/api/v1/analysis/analyze-text",
                json={
                    "extracted_text": "Nutrition Facts Calories 200 Total Fat 5g",
                    "user_profile": None
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_feedback_endpoint(self):
        """Test feedback submission endpoint"""
        response = client.post(
            "/api/v1/analysis/feedback",
            json={
                "session_id": "test_session",
                "feedback_type": "accuracy",
                "rating": 5,
                "comment": "Great analysis!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestHealthAPI:
    """Test health check API endpoints"""
    
    def test_health_check(self):
        """Test basic health check"""
        response = client.get("/api/v1/health/check")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "status" in data["data"]
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = client.get("/api/v1/health/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_status_endpoint(self):
        """Test service status endpoint"""
        response = client.get("/api/v1/health/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "services" in data["data"]


class TestAdminAPI:
    """Test admin API endpoints"""
    
    def test_admin_stats_unauthorized(self):
        """Test admin stats without authorization"""
        response = client.get("/api/v1/admin/stats")
        assert response.status_code == 401
    
    def test_admin_stats_authorized(self):
        """Test admin stats with authorization"""
        headers = {"Authorization": "Bearer admin-secret-token"}
        response = client.get("/api/v1/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data


@pytest.fixture
def test_client():
    """Test client fixture"""
    return client