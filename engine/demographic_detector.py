"""
KLAR - Demographic Intent Detector
Identifies user demographic from search queries to optimize results

Supported Demographics:
- seniors_65plus: Elderly users with simplified language preferences
- women_general: Female users with gender-specific interests
- men_general: Male users with gender-specific interests  
- teens_10to20: Young users (10-20 years old)
- young_adults_20to40: Young professionals
- general: Default/unidentified demographic
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class DemographicProfile:
    """Profile for a demographic segment"""
    name: str
    keywords: List[str]
    confidence_threshold: float = 0.3
    language_style: str = "normal"


class DemographicDetector:
    """
    Detect user demographic from search queries.
    Optimizes search results based on detected demographic.
    """
    
    def __init__(self):
        self.profiles = self._load_profiles()
        self.detection_history = []
    
    def _load_profiles(self) -> Dict[str, DemographicProfile]:
        """Load demographic profiles with keywords"""
        return {
            'seniors_65plus': DemographicProfile(
                name='Seniors 65+',
                keywords=[
                    'sjukhus', 'läkare', 'medicin', 'pension', 'apotek',
                    'recept', 'sjuk', 'ont', 'värk', 'doktor', 'blodtryck',
                    'hjälp när man', 'vilka pengar får jag', 'statlig',
                    'enkel', 'inte komplicerat', 'enkelt', 'steg för steg',
                    'familj', 'barn', 'barnbarn', 'telefon', 'ring',
                    'väder idag', 'temperatur', 'nära mig', 'lokalt'
                ],
                language_style='simplified'
            ),
            
            'women_general': DemographicProfile(
                name='Women',
                keywords=[
                    'makeup', 'smink', 'hår', 'hårvård', 'klippning',
                    'mode', 'trender', 'klänning', 'byxor', 'skor',
                    'menstur', 'p-piller', 'graviditet', 'bröstcancer',
                    'mammografi', 'gynekolog', 'skönhet', 'spa', 'massage',
                    'wellness', 'yoga', 'träning dam', 'fitnessdamer',
                    'familj', 'barn', 'barnomsorg', 'mödrahälsa',
                    'dam', 'kvinnor', 'för tjejer', 'tjejkväll'
                ],
                language_style='normal'
            ),
            
            'men_general': DemographicProfile(
                name='Men',
                keywords=[
                    'gaming', 'dator', 'pc', 'bild', 'graphics card',
                    'teknik', 'elektronik', 'gadgets', 'mobile', 'telefon',
                    'spel', 'fps', 'rpg', 'esports', 'streamer',
                    'verktyg', 'workshop', 'snickeri', 'bygga',
                    'reparera', 'motor', 'bil', 'motorcykel', 'båt',
                    'friidrott', 'fotboll man', 'hockey', 'gym',
                    'prostata', 'testosteron', 'muskeluppbyggnad',
                    'hantverk', 'diy', 'själv'
                ],
                language_style='normal'
            ),
            
            'teens_10to20': DemographicProfile(
                name='Teens 10-20',
                keywords=[
                    'läxhjälp', 'matematik', 'svenska', 'engelska',
                    'np', 'nationella prov', 'högskoleprovet', 'plugga',
                    'prov', 'tentamen', 'betygräknare', 'skolschema',
                    'mobbning', 'psykisk hälsa', 'depression', 'ångest',
                    'tiktok', 'instagram', 'snapchat', 'discord', 'twitch',
                    'youtube', 'streamer', 'influencer', 'trending',
                    'dejting', 'kärlek', 'crush', 'relation',
                    'sex', 'säker sex', 'preventiv', 'könssjukdomar',
                    'musik', 'artist', 'spotify', 'konserter', 'festival',
                    'trendiga kläder', 'streetwear', 'sneakers',
                    'ungdom', 'tonåring', 'ungdomar', 'killar', 'tjejer'
                ],
                language_style='casual'
            ),
            
            'young_adults_20to40': DemographicProfile(
                name='Young Adults 20-40',
                keywords=[
                    'jobbsökning', 'cv', 'intervju', 'karriär',
                    'löneförhandling', 'chef', 'ledare', 'projekt',
                    'startup', 'företag', 'eget företag', 'boss',
                    'bostad', 'lägenhet', 'köpa', 'bolån', 'hyra',
                    'familj', 'äktenskap', 'barn', 'förälder',
                    'bröllopsp', 'äktenskapsförord', 'skilsmässa',
                    'románti', 'relation', 'träffa', 'dating',
                    'ekonomi', 'investera', 'spara', 'pension',
                    'försäkring', 'sparande', 'aktier', 'fonder'
                ],
                language_style='normal'
            )
        }
    
    def detect(self, query: str) -> Tuple[str, float, Dict]:
        """
        Detect demographic from query.
        
        Args:
            query: Search query text
        
        Returns:
            (demographic_name: str, confidence: float, metadata: dict)
        """
        query_lower = query.lower()
        scores = {}
        
        # Calculate confidence score for each demographic
        for demographic_key, profile in self.profiles.items():
            matches = 0
            for keyword in profile.keywords:
                if keyword in query_lower:
                    matches += 1
            
            # Calculate confidence (0-1)
            confidence = min(matches / max(1, len(profile.keywords) * 0.5), 1.0)
            scores[demographic_key] = confidence
        
        # Find highest confidence
        best_demographic = max(scores, key=scores.get)
        best_confidence = scores[best_demographic]
        
        # If confidence is too low, default to general
        if best_confidence < 0.1:
            best_demographic = 'general'
            best_confidence = 0.0
        
        metadata = {
            'all_scores': scores,
            'query_length': len(query.split()),
            'query_complexity': self._assess_complexity(query),
            'language_style': self.profiles[best_demographic].language_style if best_demographic != 'general' else 'normal'
        }
        
        # Store in history
        self.detection_history.append({
            'query': query,
            'detected': best_demographic,
            'confidence': best_confidence
        })
        
        return best_demographic, best_confidence, metadata
    
    def _assess_complexity(self, query: str) -> str:
        """
        Assess query complexity.
        Returns: 'simple', 'moderate', 'complex'
        """
        word_count = len(query.split())
        char_count = len(query)
        special_chars = sum(1 for c in query if c in '?!()[]')
        
        if word_count <= 2 and char_count <= 20:
            return 'simple'
        elif word_count <= 6 and char_count <= 60:
            return 'moderate'
        else:
            return 'complex'
    
    def get_optimization_hints(self, demographic: str) -> Dict:
        """
        Get search result optimization hints for demographic.
        """
        hints = {
            'seniors_65plus': {
                'result_count': 5,  # Show fewer results
                'snippet_length': 'long',
                'explanation': 'More context needed',
                'safe_domains_priority': True,
                'avoid_technical_jargon': True,
                'include_instructions': True
            },
            'women_general': {
                'result_count': 10,
                'snippet_length': 'medium',
                'include_reviews': True,
                'include_prices': True,
                'include_ratings': True
            },
            'men_general': {
                'result_count': 10,
                'snippet_length': 'short',
                'include_specs': True,
                'include_technical_details': True,
                'include_comparisons': True
            },
            'teens_10to20': {
                'result_count': 10,
                'snippet_length': 'medium',
                'safe_domains_priority': True,
                'avoid_inappropriate_content': True,
                'educational_focus': True,
                'mental_health_resources': True
            },
            'young_adults_20to40': {
                'result_count': 10,
                'snippet_length': 'medium',
                'include_latest': True,
                'include_trending': True
            },
            'general': {
                'result_count': 10,
                'snippet_length': 'medium'
            }
        }
        
        return hints.get(demographic, hints['general'])
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        if not self.detection_history:
            return {}
        
        demographics_found = {}
        for entry in self.detection_history:
            demo = entry['detected']
            demographics_found[demo] = demographics_found.get(demo, 0) + 1
        
        return {
            'total_detections': len(self.detection_history),
            'demographics_found': demographics_found,
            'most_common': max(demographics_found, key=demographics_found.get) if demographics_found else None
        }
