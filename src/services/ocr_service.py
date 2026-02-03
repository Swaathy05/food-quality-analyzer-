"""
Advanced OCR service with multiple engines and preprocessing
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import logging
from typing import Tuple, Optional, Dict, Any
import hashlib
import time
from dataclasses import dataclass

from ..config import get_settings
from ..utils.image_processing import ImageProcessor
from ..utils.exceptions import OCRError, ImageProcessingError

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class OCRResult:
    """OCR result with confidence and metadata"""
    text: str
    confidence: float
    processing_time: float
    method_used: str
    image_hash: str
    preprocessing_applied: list


class OCRService:
    """Advanced OCR service with multiple engines and preprocessing techniques"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self._setup_tesseract()
    
    def _setup_tesseract(self):
        """Setup Tesseract configuration"""
        if settings.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path
    
    def extract_text(self, image: Image.Image, enhance_image: bool = True) -> OCRResult:
        """
        Extract text from image using multiple OCR techniques
        
        Args:
            image: PIL Image object
            enhance_image: Whether to apply image enhancement
            
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()
        
        try:
            # Generate image hash for caching
            image_hash = self._generate_image_hash(image)
            
            # Apply preprocessing
            processed_images = self._preprocess_image(image, enhance_image)
            
            # Try multiple OCR approaches
            best_result = self._try_multiple_ocr_methods(processed_images)
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=best_result['text'],
                confidence=best_result['confidence'],
                processing_time=processing_time,
                method_used=best_result['method'],
                image_hash=image_hash,
                preprocessing_applied=best_result['preprocessing']
            )
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise OCRError(f"Failed to extract text from image: {str(e)}")
    
    def _generate_image_hash(self, image: Image.Image) -> str:
        """Generate hash for image caching"""
        image_bytes = image.tobytes()
        return hashlib.md5(image_bytes).hexdigest()
    
    def _preprocess_image(self, image: Image.Image, enhance: bool) -> Dict[str, Tuple[np.ndarray, list]]:
        """
        Apply various preprocessing techniques
        
        Returns:
            Dictionary of processed images with their preprocessing steps
        """
        processed_images = {}
        
        try:
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Original image
            processed_images['original'] = (opencv_image, ['none'])
            
            # Grayscale conversion
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            processed_images['grayscale'] = (gray, ['grayscale'])
            
            if enhance:
                # Enhanced preprocessing techniques
                processed_images.update(self._advanced_preprocessing(gray))
            
            return processed_images
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise ImageProcessingError(f"Failed to preprocess image: {str(e)}")
    
    def _advanced_preprocessing(self, gray_image: np.ndarray) -> Dict[str, Tuple[np.ndarray, list]]:
        """Apply advanced preprocessing techniques"""
        processed = {}
        
        # Gaussian blur + threshold
        blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
        _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed['gaussian_otsu'] = (thresh1, ['grayscale', 'gaussian_blur', 'otsu_threshold'])
        
        # Adaptive threshold
        adaptive_thresh = cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        processed['adaptive'] = (adaptive_thresh, ['grayscale', 'adaptive_threshold'])
        
        # Morphological operations
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
        processed['morphological'] = (morph, ['grayscale', 'gaussian_blur', 'otsu_threshold', 'morphological_close'])
        
        # Noise removal
        denoised = cv2.medianBlur(gray_image, 3)
        _, thresh_denoised = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed['denoised'] = (thresh_denoised, ['grayscale', 'median_blur', 'otsu_threshold'])
        
        # Edge enhancement
        edges = cv2.Canny(gray_image, 50, 150)
        processed['edges'] = (edges, ['grayscale', 'canny_edges'])
        
        return processed
    
    def _try_multiple_ocr_methods(self, processed_images: Dict[str, Tuple[np.ndarray, list]]) -> Dict[str, Any]:
        """Try multiple OCR methods and return the best result"""
        results = []
        
        # Different Tesseract configurations
        configs = [
            {
                'name': 'nutrition_optimized',
                'config': '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,()%:-+ '
            },
            {
                'name': 'single_block',
                'config': '--oem 3 --psm 8'
            },
            {
                'name': 'single_line',
                'config': '--oem 3 --psm 7'
            },
            {
                'name': 'default',
                'config': '--oem 3 --psm 6'
            }
        ]
        
        for image_name, (image, preprocessing) in processed_images.items():
            for config in configs:
                try:
                    # Extract text
                    text = pytesseract.image_to_string(image, config=config['config'])
                    
                    # Get confidence
                    confidence = self._calculate_confidence(image, config['config'])
                    
                    # Clean text
                    cleaned_text = self._clean_extracted_text(text)
                    
                    if cleaned_text.strip():  # Only consider non-empty results
                        results.append({
                            'text': cleaned_text,
                            'confidence': confidence,
                            'method': f"{image_name}_{config['name']}",
                            'preprocessing': preprocessing
                        })
                        
                except Exception as e:
                    logger.warning(f"OCR method {config['name']} on {image_name} failed: {str(e)}")
                    continue
        
        if not results:
            raise OCRError("All OCR methods failed to extract text")
        
        # Return the result with highest confidence
        best_result = max(results, key=lambda x: x['confidence'])
        logger.info(f"Best OCR result: {best_result['method']} with confidence {best_result['confidence']:.2f}")
        
        return best_result
    
    def _calculate_confidence(self, image: np.ndarray, config: str) -> float:
        """Calculate OCR confidence score"""
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence for words with confidence > 0
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                return sum(confidences) / len(confidences) / 100.0  # Normalize to 0-1
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Could not calculate confidence: {str(e)}")
            return 0.5  # Default confidence
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common OCR artifacts
        text = text.replace('|', 'I')  # Common misread
        text = text.replace('0', 'O')  # In some contexts
        
        # Fix common nutrition label patterns
        text = self._fix_nutrition_patterns(text)
        
        return text.strip()
    
    def _fix_nutrition_patterns(self, text: str) -> str:
        """Fix common patterns in nutrition labels"""
        import re
        
        # Fix "mg" patterns
        text = re.sub(r'(\d+)\s*rng', r'\1mg', text)
        text = re.sub(r'(\d+)\s*rag', r'\1mg', text)
        
        # Fix "g" patterns
        text = re.sub(r'(\d+)\s*9\b', r'\1g', text)
        
        # Fix percentage patterns
        text = re.sub(r'(\d+)\s*%', r'\1%', text)
        
        # Fix calorie patterns
        text = re.sub(r'Calories?\s*(\d+)', r'Calories \1', text, flags=re.IGNORECASE)
        
        return text
    
    def validate_extraction(self, text: str) -> Dict[str, Any]:
        """Validate extracted text quality"""
        validation_result = {
            'is_valid': False,
            'confidence': 0.0,
            'issues': [],
            'suggestions': []
        }
        
        if not text or len(text.strip()) < 10:
            validation_result['issues'].append("Text too short")
            validation_result['suggestions'].append("Try a clearer image")
            return validation_result
        
        # Check for nutrition-related keywords
        nutrition_keywords = [
            'calories', 'fat', 'protein', 'carbohydrate', 'sodium', 'sugar',
            'vitamin', 'mineral', 'serving', 'nutrition', 'facts'
        ]
        
        found_keywords = sum(1 for keyword in nutrition_keywords 
                           if keyword.lower() in text.lower())
        
        if found_keywords >= 3:
            validation_result['is_valid'] = True
            validation_result['confidence'] = min(found_keywords / len(nutrition_keywords), 1.0)
        else:
            validation_result['issues'].append("Few nutrition-related terms found")
            validation_result['suggestions'].append("Ensure image shows nutrition facts label")
        
        # Check for numeric values
        import re
        numbers = re.findall(r'\d+', text)
        if len(numbers) < 5:
            validation_result['issues'].append("Few numeric values detected")
            validation_result['suggestions'].append("Ensure nutrition values are clearly visible")
        
        return validation_result