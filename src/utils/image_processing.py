"""
Advanced image processing utilities for OCR optimization
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging
from typing import Tuple, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of image processing operation"""
    image: np.ndarray
    method: str
    confidence: float
    metadata: dict


class ImageProcessor:
    """Advanced image processing for nutrition label OCR"""
    
    def __init__(self):
        self.processing_methods = [
            self._basic_preprocessing,
            self._adaptive_threshold,
            self._morphological_processing,
            self._edge_enhancement,
            self._noise_reduction,
            self._contrast_enhancement
        ]
    
    def process_image(self, image: Image.Image) -> List[ProcessingResult]:
        """
        Apply multiple processing techniques to optimize for OCR
        
        Args:
            image: PIL Image object
            
        Returns:
            List of processed images with metadata
        """
        results = []
        
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        for method in self.processing_methods:
            try:
                result = method(opencv_image)
                if result:
                    results.append(result)
            except Exception as e:
                logger.warning(f"Processing method failed: {str(e)}")
                continue
        
        return results
    
    def _basic_preprocessing(self, image: np.ndarray) -> ProcessingResult:
        """Basic preprocessing: grayscale + threshold"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return ProcessingResult(
            image=thresh,
            method="basic_preprocessing",
            confidence=0.7,
            metadata={"steps": ["grayscale", "otsu_threshold"]}
        )
    
    def _adaptive_threshold(self, image: np.ndarray) -> ProcessingResult:
        """Adaptive thresholding for varying lighting conditions"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Gaussian adaptive threshold
        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return ProcessingResult(
            image=adaptive,
            method="adaptive_threshold",
            confidence=0.8,
            metadata={"block_size": 11, "C": 2}
        )
    
    def _morphological_processing(self, image: np.ndarray) -> ProcessingResult:
        """Morphological operations to clean up text"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Define kernel
        kernel = np.ones((2, 2), np.uint8)
        
        # Apply morphological operations
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        return ProcessingResult(
            image=closing,
            method="morphological_processing",
            confidence=0.75,
            metadata={"kernel_size": (2, 2), "operations": ["opening", "closing"]}
        )
    
    def _edge_enhancement(self, image: np.ndarray) -> ProcessingResult:
        """Edge enhancement for better text detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Unsharp masking
        unsharp = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        
        # Threshold
        _, thresh = cv2.threshold(unsharp, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return ProcessingResult(
            image=thresh,
            method="edge_enhancement",
            confidence=0.8,
            metadata={"blur_kernel": (3, 3), "unsharp_weight": 1.5}
        )
    
    def _noise_reduction(self, image: np.ndarray) -> ProcessingResult:
        """Noise reduction while preserving text"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Non-local means denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Threshold
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return ProcessingResult(
            image=thresh,
            method="noise_reduction",
            confidence=0.85,
            metadata={"h": 10, "template_window": 7, "search_window": 21}
        )
    
    def _contrast_enhancement(self, image: np.ndarray) -> ProcessingResult:
        """Contrast enhancement using CLAHE"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create CLAHE object
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Threshold
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return ProcessingResult(
            image=thresh,
            method="contrast_enhancement",
            confidence=0.8,
            metadata={"clip_limit": 2.0, "tile_grid": (8, 8)}
        )
    
    def detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect text regions in the image
        
        Returns:
            List of bounding boxes (x, y, w, h)
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area and aspect ratio
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size and aspect ratio
                if w > 20 and h > 10 and w < image.shape[1] * 0.8:
                    aspect_ratio = w / h
                    if 0.2 < aspect_ratio < 10:  # Reasonable aspect ratio for text
                        text_regions.append((x, y, w, h))
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Text region detection failed: {str(e)}")
            return []
    
    def crop_text_regions(self, image: np.ndarray, regions: List[Tuple[int, int, int, int]]) -> List[np.ndarray]:
        """
        Crop text regions from image
        
        Args:
            image: Input image
            regions: List of bounding boxes
            
        Returns:
            List of cropped image regions
        """
        cropped_regions = []
        
        for x, y, w, h in regions:
            try:
                # Add padding
                padding = 5
                x_start = max(0, x - padding)
                y_start = max(0, y - padding)
                x_end = min(image.shape[1], x + w + padding)
                y_end = min(image.shape[0], y + h + padding)
                
                cropped = image[y_start:y_end, x_start:x_end]
                
                if cropped.size > 0:
                    cropped_regions.append(cropped)
                    
            except Exception as e:
                logger.warning(f"Failed to crop region {x}, {y}, {w}, {h}: {str(e)}")
                continue
        
        return cropped_regions
    
    def enhance_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Apply final enhancements specifically for OCR
        
        Args:
            image: Preprocessed image
            
        Returns:
            OCR-optimized image
        """
        try:
            # Ensure binary image
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply final threshold
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Dilate slightly to connect broken characters
            kernel = np.ones((1, 1), np.uint8)
            dilated = cv2.dilate(binary, kernel, iterations=1)
            
            return dilated
            
        except Exception as e:
            logger.error(f"OCR enhancement failed: {str(e)}")
            return image
    
    def calculate_image_quality(self, image: np.ndarray) -> float:
        """
        Calculate image quality score for OCR suitability
        
        Returns:
            Quality score (0-1, higher is better)
        """
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Calculate various quality metrics
            
            # 1. Contrast (standard deviation)
            contrast = np.std(gray) / 255.0
            
            # 2. Sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian) / 10000.0  # Normalize
            
            # 3. Brightness (mean intensity)
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2  # Prefer mid-range brightness
            
            # 4. Noise level (estimate)
            noise = np.std(cv2.GaussianBlur(gray, (5, 5), 0) - gray)
            noise_score = max(0, 1.0 - noise / 50.0)
            
            # Combine scores
            quality_score = (
                contrast * 0.3 +
                min(sharpness, 1.0) * 0.3 +
                brightness_score * 0.2 +
                noise_score * 0.2
            )
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception as e:
            logger.error(f"Quality calculation failed: {str(e)}")
            return 0.5  # Default quality score