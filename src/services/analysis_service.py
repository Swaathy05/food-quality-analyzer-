"""
Advanced food analysis service with AI-powered insights
"""
import logging
import time
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import openai

from ..config import get_settings, HARMFUL_CHEMICALS, NUTRITION_WEIGHTS
from ..models.schemas import (
    UserProfile, NutritionData, ChemicalAnalysis, ChemicalInfo,
    HealthRecommendation, AnalysisResult, RiskLevel
)
from ..utils.exceptions import AnalysisError, AIServiceError
from ..utils.nutrition_parser import NutritionParser
from ..utils.chemical_detector import ChemicalDetector

logger = logging.getLogger(__name__)
settings = get_settings()


class AnalysisService:
    """Advanced food analysis service with multiple AI models and comprehensive analysis"""
    
    def __init__(self):
        self.settings = settings
        self.nutrition_parser = NutritionParser()
        self.chemical_detector = ChemicalDetector()
        self._setup_ai_models()
    
    def _setup_ai_models(self):
        """Setup AI models with fallback options"""
        self.primary_llm = None
        self.fallback_llm = None
        
        try:
            # Primary model (Groq)
            if self.settings.groq_api_key:
                self.primary_llm = ChatGroq(
                    temperature=0,
                    groq_api_key=self.settings.groq_api_key,
                    model_name="llama-3.1-70b-versatile"
                )
                logger.info("Groq LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Groq LLM: {str(e)}")
        
        try:
            # Fallback model (OpenAI)
            if self.settings.openai_api_key:
                openai.api_key = self.settings.openai_api_key
                self.fallback_llm = "openai"
                logger.info("OpenAI fallback initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI fallback: {str(e)}")
    
    async def analyze_food_comprehensive(
        self, 
        extracted_text: str, 
        user_profile: Optional[UserProfile] = None,
        session_id: str = None
    ) -> AnalysisResult:
        """
        Perform comprehensive food analysis
        
        Args:
            extracted_text: OCR extracted text from nutrition label
            user_profile: User's health profile
            session_id: Analysis session ID
            
        Returns:
            Complete analysis result
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting comprehensive analysis for session {session_id}")
            
            # Step 1: Parse nutrition data
            nutrition_data = await self._parse_nutrition_data(extracted_text)
            
            # Step 2: Detect and analyze chemicals
            chemical_analysis = await self._analyze_chemicals(extracted_text)
            
            # Step 3: Generate health recommendations
            health_recommendation = await self._generate_health_recommendations(
                nutrition_data, chemical_analysis, user_profile, extracted_text
            )
            
            # Step 4: Calculate confidence score
            confidence_score = self._calculate_overall_confidence(
                nutrition_data, chemical_analysis, extracted_text
            )
            
            processing_time = time.time() - start_time
            
            result = AnalysisResult(
                session_id=session_id or f"analysis_{int(time.time())}",
                timestamp=datetime.now(),
                extracted_text=extracted_text,
                nutrition_data=nutrition_data,
                chemical_analysis=chemical_analysis,
                health_recommendation=health_recommendation,
                processing_time=processing_time,
                model_version=self.settings.app_version,
                confidence_score=confidence_score
            )
            
            logger.info(f"Analysis completed in {processing_time:.2f}s with confidence {confidence_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {str(e)}")
            raise AnalysisError(f"Analysis failed: {str(e)}")
    
    async def _parse_nutrition_data(self, text: str) -> Optional[NutritionData]:
        """Parse nutrition data from extracted text"""
        try:
            return self.nutrition_parser.parse(text)
        except Exception as e:
            logger.warning(f"Nutrition parsing failed: {str(e)}")
            return None
    
    async def _analyze_chemicals(self, text: str) -> ChemicalAnalysis:
        """Analyze chemicals and additives in the product"""
        try:
            detected_chemicals = self.chemical_detector.detect_chemicals(text)
            
            # Calculate risk summary
            risk_summary = {level: 0 for level in RiskLevel}
            for chemical in detected_chemicals:
                risk_summary[chemical.risk_level] += 1
            
            # Determine overall risk level
            overall_risk = self._calculate_overall_risk(detected_chemicals)
            
            # Calculate safety score (0-10, higher is safer)
            safety_score = self._calculate_safety_score(detected_chemicals)
            
            # Generate recommendations
            recommendations = self._generate_chemical_recommendations(detected_chemicals)
            
            return ChemicalAnalysis(
                detected_chemicals=detected_chemicals,
                risk_summary=risk_summary,
                overall_risk_level=overall_risk,
                safety_score=safety_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Chemical analysis failed: {str(e)}")
            return ChemicalAnalysis()  # Return empty analysis
    
    async def _generate_health_recommendations(
        self,
        nutrition_data: Optional[NutritionData],
        chemical_analysis: ChemicalAnalysis,
        user_profile: Optional[UserProfile],
        extracted_text: str
    ) -> HealthRecommendation:
        """Generate personalized health recommendations using AI"""
        
        try:
            # Calculate base scores
            overall_score = self._calculate_nutrition_score(nutrition_data)
            novi_score = self._calculate_novi_score(nutrition_data, chemical_analysis)
            
            # Generate AI-powered recommendations
            ai_recommendations = await self._get_ai_recommendations(
                nutrition_data, chemical_analysis, user_profile, extracted_text
            )
            
            # Check for allergens and health condition warnings
            allergen_warnings = self._check_allergens(extracted_text, user_profile)
            health_warnings = self._check_health_conditions(nutrition_data, user_profile)
            
            # Determine recommendation type
            recommendation_type = self._determine_recommendation_type(
                overall_score, chemical_analysis.overall_risk_level, user_profile
            )
            
            return HealthRecommendation(
                overall_score=overall_score,
                novi_score=novi_score,
                recommendation_type=recommendation_type,
                allergen_warnings=allergen_warnings,
                health_condition_warnings=health_warnings,
                **ai_recommendations
            )
            
        except Exception as e:
            logger.error(f"Health recommendation generation failed: {str(e)}")
            return HealthRecommendation(
                overall_score=5.0,
                novi_score=50.0,
                recommendation_type="limit"
            )
    
    async def _get_ai_recommendations(
        self,
        nutrition_data: Optional[NutritionData],
        chemical_analysis: ChemicalAnalysis,
        user_profile: Optional[UserProfile],
        extracted_text: str
    ) -> Dict[str, Any]:
        """Get AI-powered recommendations"""
        
        prompt = self._build_analysis_prompt(
            nutrition_data, chemical_analysis, user_profile, extracted_text
        )
        
        try:
            # Try primary LLM first
            if self.primary_llm:
                response = await self._query_groq_llm(prompt)
            elif self.fallback_llm:
                response = await self._query_openai_llm(prompt)
            else:
                raise AIServiceError("No AI models available")
            
            return self._parse_ai_response(response)
            
        except Exception as e:
            logger.error(f"AI recommendation generation failed: {str(e)}")
            return self._get_fallback_recommendations(nutrition_data, chemical_analysis)
    
    def _build_analysis_prompt(
        self,
        nutrition_data: Optional[NutritionData],
        chemical_analysis: ChemicalAnalysis,
        user_profile: Optional[UserProfile],
        extracted_text: str
    ) -> str:
        """Build comprehensive analysis prompt"""
        
        prompt_template = PromptTemplate.from_template("""
        You are a professional nutritionist and food safety expert. Analyze this food product and provide comprehensive recommendations.

        ### EXTRACTED NUTRITION LABEL TEXT:
        {extracted_text}

        ### PARSED NUTRITION DATA:
        {nutrition_data}

        ### DETECTED CHEMICALS:
        {chemical_analysis}

        ### USER HEALTH PROFILE:
        {user_profile}

        ### ANALYSIS REQUIREMENTS:
        Provide a detailed analysis in JSON format with the following structure:
        {{
            "benefits": ["list of health benefits"],
            "risks": ["list of potential health risks"],
            "alternatives": ["list of healthier alternatives"],
            "tips": ["list of consumption tips"],
            "portion_size": "recommended portion size",
            "frequency": "recommended consumption frequency"
        }}

        ### ANALYSIS GUIDELINES:
        1. Consider the user's specific health profile (allergies, conditions, restrictions)
        2. Evaluate both nutritional content and chemical additives
        3. Provide evidence-based recommendations
        4. Be specific about portion sizes and frequency
        5. Suggest realistic alternatives
        6. Consider the overall dietary context

        ### RESPONSE FORMAT:
        Return only valid JSON without any additional text or formatting.
        """)
        
        return prompt_template.format(
            extracted_text=extracted_text[:1000],  # Limit text length
            nutrition_data=nutrition_data.dict() if nutrition_data else "Not available",
            chemical_analysis={
                "detected_chemicals": [c.dict() for c in chemical_analysis.detected_chemicals],
                "overall_risk": chemical_analysis.overall_risk_level.value,
                "safety_score": chemical_analysis.safety_score
            },
            user_profile=user_profile.dict() if user_profile else "Not provided"
        )
    
    async def _query_groq_llm(self, prompt: str) -> str:
        """Query Groq LLM"""
        try:
            response = self.primary_llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Groq LLM query failed: {str(e)}")
            raise AIServiceError(f"Groq LLM error: {str(e)}")
    
    async def _query_openai_llm(self, prompt: str) -> str:
        """Query OpenAI LLM as fallback"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI LLM query failed: {str(e)}")
            raise AIServiceError(f"OpenAI LLM error: {str(e)}")
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._parse_text_response(response)
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {str(e)}")
            return self._get_default_recommendations()
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        # Simple text parsing logic
        return {
            "benefits": ["Provides essential nutrients"],
            "risks": ["May contain additives"],
            "alternatives": ["Look for organic alternatives"],
            "tips": ["Consume in moderation"],
            "portion_size": "Follow serving size on label",
            "frequency": "Occasionally"
        }
    
    def _get_fallback_recommendations(
        self, 
        nutrition_data: Optional[NutritionData], 
        chemical_analysis: ChemicalAnalysis
    ) -> Dict[str, Any]:
        """Get fallback recommendations when AI fails"""
        recommendations = {
            "benefits": [],
            "risks": [],
            "alternatives": [],
            "tips": [],
            "portion_size": "Follow serving size on label",
            "frequency": "Occasionally"
        }
        
        # Add basic recommendations based on analysis
        if chemical_analysis.overall_risk_level == RiskLevel.HIGH:
            recommendations["risks"].append("Contains high-risk chemical additives")
            recommendations["frequency"] = "Rarely or avoid"
        
        if nutrition_data and nutrition_data.sodium and nutrition_data.sodium > 600:
            recommendations["risks"].append("High sodium content")
            recommendations["tips"].append("Drink plenty of water")
        
        return recommendations
    
    def _get_default_recommendations(self) -> Dict[str, Any]:
        """Get default recommendations"""
        return {
            "benefits": ["Check nutrition label for specific benefits"],
            "risks": ["Consume as part of balanced diet"],
            "alternatives": ["Consider whole food alternatives"],
            "tips": ["Read ingredient list carefully"],
            "portion_size": "Follow serving size on label",
            "frequency": "In moderation"
        }
    
    def _calculate_nutrition_score(self, nutrition_data: Optional[NutritionData]) -> float:
        """Calculate nutrition score (0-10, higher is better)"""
        if not nutrition_data:
            return 5.0
        
        score = 7.0  # Base score
        
        # Adjust based on nutrition values
        if nutrition_data.sodium and nutrition_data.sodium > 600:
            score -= 1.0
        if nutrition_data.total_sugars and nutrition_data.total_sugars > 15:
            score -= 1.0
        if nutrition_data.saturated_fat and nutrition_data.saturated_fat > 5:
            score -= 0.5
        if nutrition_data.trans_fat and nutrition_data.trans_fat > 0:
            score -= 2.0
        
        # Positive adjustments
        if nutrition_data.dietary_fiber and nutrition_data.dietary_fiber > 3:
            score += 0.5
        if nutrition_data.protein and nutrition_data.protein > 10:
            score += 0.5
        
        return max(0.0, min(10.0, score))
    
    def _calculate_novi_score(
        self, 
        nutrition_data: Optional[NutritionData], 
        chemical_analysis: ChemicalAnalysis
    ) -> float:
        """Calculate NOVI (Nutrition Quality Index) score"""
        base_score = 50.0
        
        if nutrition_data:
            # Adjust based on nutrition
            if nutrition_data.dietary_fiber and nutrition_data.dietary_fiber > 5:
                base_score += 10
            if nutrition_data.protein and nutrition_data.protein > 15:
                base_score += 10
            if nutrition_data.sodium and nutrition_data.sodium > 800:
                base_score -= 15
            if nutrition_data.total_sugars and nutrition_data.total_sugars > 20:
                base_score -= 15
        
        # Adjust based on chemicals
        risk_penalties = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: -5,
            RiskLevel.HIGH: -15,
            RiskLevel.CRITICAL: -25
        }
        
        base_score += risk_penalties.get(chemical_analysis.overall_risk_level, 0)
        
        return max(0.0, min(100.0, base_score))
    
    def _calculate_overall_risk(self, chemicals: List[ChemicalInfo]) -> RiskLevel:
        """Calculate overall risk level from detected chemicals"""
        if not chemicals:
            return RiskLevel.LOW
        
        risk_scores = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        
        max_risk = max(risk_scores[chemical.risk_level] for chemical in chemicals)
        
        for level, score in risk_scores.items():
            if score == max_risk:
                return level
        
        return RiskLevel.LOW
    
    def _calculate_safety_score(self, chemicals: List[ChemicalInfo]) -> float:
        """Calculate safety score (0-10, higher is safer)"""
        if not chemicals:
            return 9.0
        
        base_score = 8.0
        
        risk_penalties = {
            RiskLevel.LOW: 0.5,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.HIGH: 2.0,
            RiskLevel.CRITICAL: 3.0
        }
        
        for chemical in chemicals:
            base_score -= risk_penalties.get(chemical.risk_level, 0)
        
        return max(0.0, min(10.0, base_score))
    
    def _generate_chemical_recommendations(self, chemicals: List[ChemicalInfo]) -> List[str]:
        """Generate recommendations based on detected chemicals"""
        recommendations = []
        
        if not chemicals:
            recommendations.append("No concerning chemicals detected")
            return recommendations
        
        high_risk_chemicals = [c for c in chemicals if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        
        if high_risk_chemicals:
            recommendations.append("Contains high-risk chemical additives - consider alternatives")
            recommendations.append("Limit consumption frequency")
        
        preservatives = [c for c in chemicals if c.category == "preservatives"]
        if preservatives:
            recommendations.append("Contains preservatives - check expiration dates")
        
        artificial_colors = [c for c in chemicals if c.category == "artificial_colors"]
        if artificial_colors:
            recommendations.append("Contains artificial colors - may cause reactions in sensitive individuals")
        
        return recommendations
    
    def _check_allergens(self, text: str, user_profile: Optional[UserProfile]) -> List[str]:
        """Check for allergens based on user profile"""
        warnings = []
        
        if not user_profile or not user_profile.allergies:
            return warnings
        
        text_lower = text.lower()
        
        for allergen in user_profile.allergies:
            if allergen.lower() in text_lower:
                warnings.append(f"Contains {allergen} - matches your allergy profile")
        
        return warnings
    
    def _check_health_conditions(
        self, 
        nutrition_data: Optional[NutritionData], 
        user_profile: Optional[UserProfile]
    ) -> List[str]:
        """Check for health condition warnings"""
        warnings = []
        
        if not user_profile or not user_profile.health_conditions or not nutrition_data:
            return warnings
        
        conditions = [c.lower() for c in user_profile.health_conditions]
        
        # Diabetes warnings
        if "diabetes" in conditions:
            if nutrition_data.total_sugars and nutrition_data.total_sugars > 15:
                warnings.append("High sugar content - monitor blood glucose")
            if nutrition_data.total_carbohydrates and nutrition_data.total_carbohydrates > 30:
                warnings.append("High carbohydrate content - consider portion size")
        
        # Hypertension warnings
        if "hypertension" in conditions or "high blood pressure" in conditions:
            if nutrition_data.sodium and nutrition_data.sodium > 400:
                warnings.append("High sodium content - may affect blood pressure")
        
        # Heart disease warnings
        if "heart disease" in conditions:
            if nutrition_data.saturated_fat and nutrition_data.saturated_fat > 3:
                warnings.append("High saturated fat - consider heart-healthy alternatives")
            if nutrition_data.trans_fat and nutrition_data.trans_fat > 0:
                warnings.append("Contains trans fat - avoid for heart health")
        
        return warnings
    
    def _determine_recommendation_type(
        self, 
        nutrition_score: float, 
        chemical_risk: RiskLevel, 
        user_profile: Optional[UserProfile]
    ) -> str:
        """Determine overall recommendation type"""
        
        if chemical_risk == RiskLevel.CRITICAL or nutrition_score < 3:
            return "avoid"
        elif chemical_risk == RiskLevel.HIGH or nutrition_score < 5:
            return "limit"
        else:
            return "consume"
    
    def _calculate_overall_confidence(
        self,
        nutrition_data: Optional[NutritionData],
        chemical_analysis: ChemicalAnalysis,
        extracted_text: str
    ) -> float:
        """Calculate overall confidence in the analysis"""
        confidence_factors = []
        
        # Text quality factor
        if len(extracted_text) > 100:
            confidence_factors.append(0.8)
        elif len(extracted_text) > 50:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.3)
        
        # Nutrition data factor
        if nutrition_data:
            non_null_fields = sum(1 for field in nutrition_data.dict().values() if field is not None)
            confidence_factors.append(min(non_null_fields / 10, 1.0))
        else:
            confidence_factors.append(0.2)
        
        # Chemical detection factor
        if chemical_analysis.detected_chemicals:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.7)
        
        return sum(confidence_factors) / len(confidence_factors)