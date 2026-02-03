"""
Chemical detection and analysis system
"""
import re
import logging
from typing import List, Dict, Any, Set
from dataclasses import dataclass

from ..config import HARMFUL_CHEMICALS
from ..models.schemas import ChemicalInfo, RiskLevel

logger = logging.getLogger(__name__)


@dataclass
class ChemicalMatch:
    """Chemical detection match with context"""
    chemical: str
    category: str
    risk_level: RiskLevel
    confidence: float
    context: str
    position: int


class ChemicalDetector:
    """Advanced chemical detection system for food ingredients"""
    
    def __init__(self):
        self.chemical_database = self._build_chemical_database()
        self.patterns = self._build_detection_patterns()
        self.aliases = self._build_chemical_aliases()
    
    def detect_chemicals(self, text: str) -> List[ChemicalInfo]:
        """
        Detect chemicals in ingredient text
        
        Args:
            text: OCR extracted text or ingredient list
            
        Returns:
            List of detected chemicals with risk information
        """
        try:
            if not text:
                return []
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Detect chemicals using multiple methods
            detected_matches = []
            detected_matches.extend(self._pattern_based_detection(cleaned_text))
            detected_matches.extend(self._keyword_based_detection(cleaned_text))
            detected_matches.extend(self._fuzzy_matching(cleaned_text))
            
            # Remove duplicates and convert to ChemicalInfo objects
            unique_chemicals = self._deduplicate_matches(detected_matches)
            chemical_info_list = self._convert_to_chemical_info(unique_chemicals)
            
            logger.info(f"Detected {len(chemical_info_list)} chemicals")
            return chemical_info_list
            
        except Exception as e:
            logger.error(f"Chemical detection failed: {str(e)}")
            return []
    
    def _build_chemical_database(self) -> Dict[str, Dict[str, Any]]:
        """Build comprehensive chemical database"""
        database = {}
        
        # Add chemicals from config
        for category, chemicals in HARMFUL_CHEMICALS.items():
            for chemical, info in chemicals.items():
                database[chemical.lower()] = {
                    'category': category,
                    'risk_level': RiskLevel(info['risk_level']),
                    'description': info['description'],
                    'health_effects': self._get_health_effects(chemical),
                    'alternatives': self._get_alternatives(chemical)
                }
        
        # Add additional common chemicals
        additional_chemicals = {
            # Preservatives
            'sodium_nitrite': {
                'category': 'preservatives',
                'risk_level': RiskLevel.HIGH,
                'description': 'May form nitrosamines, potential carcinogens'
            },
            'sodium_nitrate': {
                'category': 'preservatives', 
                'risk_level': RiskLevel.HIGH,
                'description': 'May form nitrosamines, potential carcinogens'
            },
            'sulfur_dioxide': {
                'category': 'preservatives',
                'risk_level': RiskLevel.MEDIUM,
                'description': 'May cause allergic reactions in sensitive individuals'
            },
            
            # Artificial sweeteners
            'saccharin': {
                'category': 'sweeteners',
                'risk_level': RiskLevel.MEDIUM,
                'description': 'Potential bladder cancer risk in animal studies'
            },
            'cyclamate': {
                'category': 'sweeteners',
                'risk_level': RiskLevel.MEDIUM,
                'description': 'Banned in some countries due to cancer concerns'
            },
            
            # Flavor enhancers
            'monosodium_glutamate': {
                'category': 'flavor_enhancers',
                'risk_level': RiskLevel.MEDIUM,
                'description': 'May cause headaches and nausea in sensitive individuals'
            },
            'disodium_guanylate': {
                'category': 'flavor_enhancers',
                'risk_level': RiskLevel.LOW,
                'description': 'Generally recognized as safe'
            },
            
            # Emulsifiers and stabilizers
            'polysorbate_60': {
                'category': 'emulsifiers',
                'risk_level': RiskLevel.MEDIUM,
                'description': 'May affect gut microbiome'
            },
            'sodium_stearoyl_lactylate': {
                'category': 'emulsifiers',
                'risk_level': RiskLevel.LOW,
                'description': 'Generally recognized as safe'
            }
        }
        
        for chemical, info in additional_chemicals.items():
            database[chemical.lower()] = {
                **info,
                'health_effects': self._get_health_effects(chemical),
                'alternatives': self._get_alternatives(chemical)
            }
        
        return database
    
    def _build_detection_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for chemical detection"""
        return {
            'e_numbers': [
                r'\bE\s*(\d{3,4})\b',  # E100, E 100
                r'\b(\d{3,4})\s*\([^)]*E\s*\1[^)]*\)'  # 100 (E100)
            ],
            'preservatives': [
                r'\b(?:sodium|potassium|calcium)\s+(?:benzoate|sorbate|nitrite|nitrate)\b',
                r'\b(?:BHA|BHT)\b',
                r'\bsulfur\s+dioxide\b',
                r'\bsodium\s+metabisulfite\b'
            ],
            'artificial_colors': [
                r'\b(?:red|yellow|blue|green)\s+(?:dye\s+)?(?:#\s*)?(\d+)\b',
                r'\b(?:fd&c|fdc)\s+(?:red|yellow|blue|green)\s+(?:#\s*)?(\d+)\b',
                r'\bcaramel\s+colou?r\b',
                r'\btartrazine\b'
            ],
            'sweeteners': [
                r'\b(?:aspartame|sucralose|acesulfame\s+k|saccharin|cyclamate)\b',
                r'\bhigh\s+fructose\s+corn\s+syrup\b',
                r'\bcorn\s+syrup\s+solids\b'
            ],
            'msg_variants': [
                r'\b(?:monosodium\s+glutamate|msg)\b',
                r'\bhydrolyzed\s+(?:vegetable|soy|corn)\s+protein\b',
                r'\byeast\s+extract\b',
                r'\bautolyzed\s+yeast\b'
            ]
        }
    
    def _build_chemical_aliases(self) -> Dict[str, List[str]]:
        """Build aliases and alternative names for chemicals"""
        return {
            'monosodium_glutamate': ['msg', 'sodium glutamate', 'glutamic acid'],
            'high_fructose_corn_syrup': ['hfcs', 'corn syrup', 'glucose-fructose'],
            'sodium_benzoate': ['benzoate of soda'],
            'potassium_sorbate': ['sorbate of potash'],
            'carrageenan': ['irish moss extract'],
            'xanthan_gum': ['xanthan'],
            'guar_gum': ['guaran'],
            'lecithin': ['soy lecithin', 'sunflower lecithin'],
            'polysorbate_80': ['tween 80'],
            'polysorbate_60': ['tween 60'],
            'sodium_nitrite': ['sodium nitrite', 'nitrite'],
            'sodium_nitrate': ['sodium nitrate', 'nitrate'],
            'bha': ['butylated hydroxyanisole'],
            'bht': ['butylated hydroxytoluene'],
            'tbhq': ['tertiary butylhydroquinone'],
            'aspartame': ['nutrasweet', 'equal'],
            'sucralose': ['splenda'],
            'acesulfame_k': ['acesulfame potassium', 'ace-k'],
            'red_40': ['allura red', 'fd&c red 40'],
            'yellow_5': ['tartrazine', 'fd&c yellow 5'],
            'blue_1': ['brilliant blue', 'fd&c blue 1']
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for chemical detection"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize punctuation
        text = re.sub(r'[,;:]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'l')
        text = text.replace('0', 'o')  # In some contexts
        
        return text.strip()
    
    def _pattern_based_detection(self, text: str) -> List[ChemicalMatch]:
        """Detect chemicals using regex patterns"""
        matches = []
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    chemical_name = self._extract_chemical_name(match, category)
                    if chemical_name and chemical_name in self.chemical_database:
                        chemical_info = self.chemical_database[chemical_name]
                        
                        matches.append(ChemicalMatch(
                            chemical=chemical_name,
                            category=chemical_info['category'],
                            risk_level=chemical_info['risk_level'],
                            confidence=0.9,  # High confidence for pattern matches
                            context=match.group(0),
                            position=match.start()
                        ))
        
        return matches
    
    def _keyword_based_detection(self, text: str) -> List[ChemicalMatch]:
        """Detect chemicals using keyword matching"""
        matches = []
        
        for chemical, info in self.chemical_database.items():
            # Direct name match
            if chemical in text:
                matches.append(ChemicalMatch(
                    chemical=chemical,
                    category=info['category'],
                    risk_level=info['risk_level'],
                    confidence=0.95,
                    context=self._extract_context(text, chemical),
                    position=text.find(chemical)
                ))
            
            # Alias matching
            if chemical in self.aliases:
                for alias in self.aliases[chemical]:
                    if alias.lower() in text:
                        matches.append(ChemicalMatch(
                            chemical=chemical,
                            category=info['category'],
                            risk_level=info['risk_level'],
                            confidence=0.8,
                            context=self._extract_context(text, alias),
                            position=text.find(alias.lower())
                        ))
        
        return matches
    
    def _fuzzy_matching(self, text: str) -> List[ChemicalMatch]:
        """Detect chemicals using fuzzy string matching"""
        matches = []
        
        # Simple fuzzy matching for common misspellings
        fuzzy_patterns = {
            'aspartame': ['aspartam', 'asparteme'],
            'carrageenan': ['carragean', 'caragenan'],
            'xanthan_gum': ['xanthan', 'xantham'],
            'monosodium_glutamate': ['monosodium glutamat', 'msg']
        }
        
        for chemical, variants in fuzzy_patterns.items():
            if chemical in self.chemical_database:
                for variant in variants:
                    if variant in text:
                        chemical_info = self.chemical_database[chemical]
                        matches.append(ChemicalMatch(
                            chemical=chemical,
                            category=chemical_info['category'],
                            risk_level=chemical_info['risk_level'],
                            confidence=0.7,  # Lower confidence for fuzzy matches
                            context=self._extract_context(text, variant),
                            position=text.find(variant)
                        ))
        
        return matches
    
    def _extract_chemical_name(self, match: re.Match, category: str) -> str:
        """Extract chemical name from regex match"""
        match_text = match.group(0).lower()
        
        # Handle E-numbers
        if category == 'e_numbers':
            e_number = match.group(1)
            return f"e{e_number}"
        
        # Handle color numbers
        if category == 'artificial_colors':
            if match.groups():
                color_number = match.group(1)
                if 'red' in match_text:
                    return f"red_{color_number}"
                elif 'yellow' in match_text:
                    return f"yellow_{color_number}"
                elif 'blue' in match_text:
                    return f"blue_{color_number}"
        
        # Direct mapping for other categories
        chemical_mappings = {
            'sodium benzoate': 'sodium_benzoate',
            'potassium sorbate': 'potassium_sorbate',
            'monosodium glutamate': 'monosodium_glutamate',
            'high fructose corn syrup': 'high_fructose_corn_syrup',
            'caramel color': 'caramel_color',
            'caramel colour': 'caramel_color'
        }
        
        return chemical_mappings.get(match_text, match_text.replace(' ', '_'))
    
    def _extract_context(self, text: str, chemical: str) -> str:
        """Extract context around detected chemical"""
        position = text.find(chemical.lower())
        if position == -1:
            return chemical
        
        start = max(0, position - 30)
        end = min(len(text), position + len(chemical) + 30)
        
        return text[start:end].strip()
    
    def _deduplicate_matches(self, matches: List[ChemicalMatch]) -> List[ChemicalMatch]:
        """Remove duplicate chemical matches"""
        seen_chemicals = set()
        unique_matches = []
        
        # Sort by confidence (highest first)
        sorted_matches = sorted(matches, key=lambda x: x.confidence, reverse=True)
        
        for match in sorted_matches:
            if match.chemical not in seen_chemicals:
                unique_matches.append(match)
                seen_chemicals.add(match.chemical)
        
        return unique_matches
    
    def _convert_to_chemical_info(self, matches: List[ChemicalMatch]) -> List[ChemicalInfo]:
        """Convert matches to ChemicalInfo objects"""
        chemical_info_list = []
        
        for match in matches:
            if match.chemical in self.chemical_database:
                db_info = self.chemical_database[match.chemical]
                
                chemical_info = ChemicalInfo(
                    name=match.chemical.replace('_', ' ').title(),
                    category=db_info['category'],
                    risk_level=db_info['risk_level'],
                    description=db_info['description'],
                    health_effects=db_info.get('health_effects', []),
                    alternatives=db_info.get('alternatives', [])
                )
                
                chemical_info_list.append(chemical_info)
        
        return chemical_info_list
    
    def _get_health_effects(self, chemical: str) -> List[str]:
        """Get health effects for a chemical"""
        health_effects_db = {
            'bha': ['Potential carcinogen', 'May cause allergic reactions'],
            'bht': ['Potential carcinogen', 'May affect liver function'],
            'sodium_nitrite': ['May form carcinogenic nitrosamines', 'Linked to colorectal cancer'],
            'red_40': ['May cause hyperactivity in children', 'Potential allergic reactions'],
            'aspartame': ['May cause headaches', 'Not suitable for phenylketonuria'],
            'msg': ['May cause headaches', 'Can trigger nausea in sensitive individuals'],
            'high_fructose_corn_syrup': ['Linked to obesity', 'May contribute to diabetes'],
            'carrageenan': ['May cause digestive inflammation', 'Potential gut irritation']
        }
        
        return health_effects_db.get(chemical, ['Potential health concerns - consult healthcare provider'])
    
    def _get_alternatives(self, chemical: str) -> List[str]:
        """Get healthier alternatives for a chemical"""
        alternatives_db = {
            'bha': ['Vitamin E (tocopherols)', 'Rosemary extract'],
            'bht': ['Vitamin E (tocopherols)', 'Ascorbic acid'],
            'red_40': ['Beet juice', 'Paprika extract', 'Annatto'],
            'aspartame': ['Stevia', 'Monk fruit extract'],
            'msg': ['Natural herbs and spices', 'Nutritional yeast'],
            'high_fructose_corn_syrup': ['Pure cane sugar', 'Honey', 'Maple syrup'],
            'sodium_nitrite': ['Celery powder', 'Sea salt']
        }
        
        return alternatives_db.get(chemical, ['Look for organic alternatives', 'Choose products with natural ingredients'])