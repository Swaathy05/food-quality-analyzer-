"""
Advanced nutrition data parser with pattern recognition
"""
import re
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

from ..models.schemas import NutritionData

logger = logging.getLogger(__name__)


@dataclass
class ParsedValue:
    """Parsed nutrition value with confidence"""
    value: float
    unit: str
    confidence: float
    source_text: str


class NutritionParser:
    """Advanced parser for nutrition facts from OCR text"""
    
    def __init__(self):
        self.patterns = self._build_patterns()
        self.unit_conversions = self._build_unit_conversions()
    
    def parse(self, text: str) -> Optional[NutritionData]:
        """
        Parse nutrition data from OCR text
        
        Args:
            text: OCR extracted text
            
        Returns:
            NutritionData object or None if parsing fails
        """
        try:
            if not text or len(text.strip()) < 10:
                return None
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Extract nutrition values
            nutrition_values = self._extract_nutrition_values(cleaned_text)
            
            if not nutrition_values:
                logger.warning("No nutrition values found in text")
                return None
            
            # Convert to NutritionData object
            nutrition_data = self._build_nutrition_data(nutrition_values)
            
            logger.info(f"Successfully parsed {len(nutrition_values)} nutrition values")
            return nutrition_data
            
        except Exception as e:
            logger.error(f"Nutrition parsing failed: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize OCR text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Fix common OCR errors
        text = text.replace('|', 'I')
        text = text.replace('0', 'O')  # In some contexts
        text = text.replace('rng', 'mg')
        text = text.replace('rag', 'mg')
        text = text.replace('9', 'g')  # When followed by space
        
        # Normalize units
        text = re.sub(r'\bmcg\b', 'μg', text, flags=re.IGNORECASE)
        text = re.sub(r'\biu\b', 'IU', text, flags=re.IGNORECASE)
        
        return text
    
    def _build_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for nutrition value extraction"""
        return {
            'calories': [
                r'calories?\s*(\d+)',
                r'energy\s*(\d+)\s*kcal',
                r'(\d+)\s*cal(?:ories?)?'
            ],
            'total_fat': [
                r'total\s*fat\s*(\d+(?:\.\d+)?)\s*g',
                r'fat\s*(\d+(?:\.\d+)?)\s*g',
                r'total\s*fat\s*(\d+(?:\.\d+)?)'
            ],
            'saturated_fat': [
                r'saturated\s*fat\s*(\d+(?:\.\d+)?)\s*g',
                r'saturated\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'trans_fat': [
                r'trans\s*fat\s*(\d+(?:\.\d+)?)\s*g',
                r'trans\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'cholesterol': [
                r'cholesterol\s*(\d+(?:\.\d+)?)\s*mg',
                r'cholesterol\s*(\d+(?:\.\d+)?)'
            ],
            'sodium': [
                r'sodium\s*(\d+(?:\.\d+)?)\s*mg',
                r'sodium\s*(\d+(?:\.\d+)?)',
                r'salt\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'total_carbohydrates': [
                r'total\s*carbohydrate\s*(\d+(?:\.\d+)?)\s*g',
                r'carbohydrate\s*(\d+(?:\.\d+)?)\s*g',
                r'carbs\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'dietary_fiber': [
                r'dietary\s*fiber\s*(\d+(?:\.\d+)?)\s*g',
                r'fiber\s*(\d+(?:\.\d+)?)\s*g',
                r'fibre\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'total_sugars': [
                r'total\s*sugars?\s*(\d+(?:\.\d+)?)\s*g',
                r'sugars?\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'added_sugars': [
                r'added\s*sugars?\s*(\d+(?:\.\d+)?)\s*g',
                r'includes\s*(\d+(?:\.\d+)?)\s*g\s*added\s*sugars?'
            ],
            'protein': [
                r'protein\s*(\d+(?:\.\d+)?)\s*g',
                r'protein\s*(\d+(?:\.\d+)?)'
            ],
            'vitamin_d': [
                r'vitamin\s*d\s*(\d+(?:\.\d+)?)\s*(?:μg|mcg|iu)',
                r'vitamin\s*d\s*(\d+(?:\.\d+)?)'
            ],
            'calcium': [
                r'calcium\s*(\d+(?:\.\d+)?)\s*mg',
                r'calcium\s*(\d+(?:\.\d+)?)'
            ],
            'iron': [
                r'iron\s*(\d+(?:\.\d+)?)\s*mg',
                r'iron\s*(\d+(?:\.\d+)?)'
            ],
            'potassium': [
                r'potassium\s*(\d+(?:\.\d+)?)\s*mg',
                r'potassium\s*(\d+(?:\.\d+)?)'
            ]
        }
    
    def _build_unit_conversions(self) -> Dict[str, float]:
        """Build unit conversion factors to standard units"""
        return {
            # Weight conversions to grams
            'kg': 1000.0,
            'g': 1.0,
            'mg': 0.001,
            'μg': 0.000001,
            'mcg': 0.000001,
            
            # Volume conversions to ml
            'l': 1000.0,
            'ml': 1.0,
            'fl oz': 29.5735,
            'cup': 236.588,
            'tbsp': 14.7868,
            'tsp': 4.92892,
            
            # Energy conversions to kcal
            'kcal': 1.0,
            'cal': 0.001,
            'kj': 0.239006,
            'j': 0.000239006,
            
            # Special units
            'iu': 1.0,  # International Units (context dependent)
            '%': 1.0    # Percentage
        }
    
    def _extract_nutrition_values(self, text: str) -> Dict[str, ParsedValue]:
        """Extract nutrition values using pattern matching"""
        nutrition_values = {}
        
        for nutrient, patterns in self.patterns.items():
            best_match = None
            best_confidence = 0.0
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    try:
                        value_str = match.group(1)
                        value = float(value_str)
                        
                        # Calculate confidence based on pattern specificity and context
                        confidence = self._calculate_match_confidence(match, text, pattern)
                        
                        if confidence > best_confidence:
                            # Extract unit if present
                            unit = self._extract_unit(match.group(0))
                            
                            best_match = ParsedValue(
                                value=value,
                                unit=unit,
                                confidence=confidence,
                                source_text=match.group(0)
                            )
                            best_confidence = confidence
                            
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Failed to parse match {match.group(0)}: {str(e)}")
                        continue
            
            if best_match:
                nutrition_values[nutrient] = best_match
        
        return nutrition_values
    
    def _calculate_match_confidence(self, match: re.Match, text: str, pattern: str) -> float:
        """Calculate confidence score for a pattern match"""
        base_confidence = 0.7
        
        # Bonus for more specific patterns
        if 'total' in pattern.lower():
            base_confidence += 0.1
        if 'dietary' in pattern.lower():
            base_confidence += 0.1
        
        # Context analysis
        match_text = match.group(0).lower()
        surrounding_text = text[max(0, match.start()-50):match.end()+50].lower()
        
        # Bonus for nutrition facts context
        nutrition_keywords = ['nutrition', 'facts', 'serving', 'daily', 'value', '%']
        context_bonus = sum(0.05 for keyword in nutrition_keywords if keyword in surrounding_text)
        
        # Penalty for unlikely values
        try:
            value = float(match.group(1))
            if value > 10000:  # Unlikely nutrition value
                base_confidence -= 0.2
            elif value == 0:
                base_confidence -= 0.1
        except (ValueError, IndexError):
            pass
        
        return min(1.0, base_confidence + context_bonus)
    
    def _extract_unit(self, match_text: str) -> str:
        """Extract unit from matched text"""
        # Common nutrition units
        units = ['g', 'mg', 'μg', 'mcg', 'kcal', 'cal', 'iu', '%']
        
        match_lower = match_text.lower()
        for unit in units:
            if unit.lower() in match_lower:
                return unit
        
        return 'g'  # Default unit
    
    def _build_nutrition_data(self, values: Dict[str, ParsedValue]) -> NutritionData:
        """Build NutritionData object from parsed values"""
        data = {}
        
        # Map parsed values to NutritionData fields
        field_mapping = {
            'calories': 'calories',
            'total_fat': 'total_fat',
            'saturated_fat': 'saturated_fat',
            'trans_fat': 'trans_fat',
            'cholesterol': 'cholesterol',
            'sodium': 'sodium',
            'total_carbohydrates': 'total_carbohydrates',
            'dietary_fiber': 'dietary_fiber',
            'total_sugars': 'total_sugars',
            'added_sugars': 'added_sugars',
            'protein': 'protein',
            'vitamin_d': 'vitamin_d',
            'calcium': 'calcium',
            'iron': 'iron',
            'potassium': 'potassium'
        }
        
        for parsed_key, data_key in field_mapping.items():
            if parsed_key in values:
                parsed_value = values[parsed_key]
                # Convert to standard units if needed
                converted_value = self._convert_to_standard_unit(
                    parsed_value.value, parsed_value.unit, data_key
                )
                data[data_key] = converted_value
        
        # Extract serving information
        serving_info = self._extract_serving_info(values)
        if serving_info:
            data.update(serving_info)
        
        return NutritionData(**data)
    
    def _convert_to_standard_unit(self, value: float, unit: str, nutrient: str) -> float:
        """Convert value to standard unit for the nutrient"""
        # Most nutrients are already in standard units (g, mg)
        # Special conversions can be added here
        
        if nutrient == 'sodium' and unit == 'g':
            return value * 1000  # Convert g to mg for sodium
        
        return value
    
    def _extract_serving_info(self, values: Dict[str, ParsedValue]) -> Dict[str, Any]:
        """Extract serving size and servings per container"""
        serving_info = {}
        
        # This would need more sophisticated parsing
        # For now, return empty dict
        
        return serving_info
    
    def validate_nutrition_data(self, nutrition_data: NutritionData) -> Dict[str, Any]:
        """Validate parsed nutrition data for reasonableness"""
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for reasonable ranges
        if nutrition_data.calories and nutrition_data.calories > 2000:
            validation_result['warnings'].append("Very high calorie content")
        
        if nutrition_data.sodium and nutrition_data.sodium > 2000:
            validation_result['warnings'].append("Very high sodium content")
        
        if nutrition_data.total_fat and nutrition_data.total_fat > 100:
            validation_result['warnings'].append("Unusually high fat content")
        
        # Check for consistency
        if (nutrition_data.saturated_fat and nutrition_data.total_fat and 
            nutrition_data.saturated_fat > nutrition_data.total_fat):
            validation_result['errors'].append("Saturated fat cannot exceed total fat")
            validation_result['is_valid'] = False
        
        if (nutrition_data.added_sugars and nutrition_data.total_sugars and
            nutrition_data.added_sugars > nutrition_data.total_sugars):
            validation_result['errors'].append("Added sugars cannot exceed total sugars")
            validation_result['is_valid'] = False
        
        return validation_result