"""
Semantic Similarity Module - Enhanced Natural Language Search for Swedish
Uses advanced NLP techniques to understand query intent and semantic meaning
"""

import logging
from typing import List, Dict, Any, Tuple
import re

logger = logging.getLogger(__name__)


class SemanticSimilarity:
    """
    Semantic similarity scorer for natural language queries
    Optimized for Swedish language and conversational search
    """
    
    def __init__(self):
        """Initialize semantic similarity module"""
        
        # Configuration constants
        self.MAX_CLUSTER_TERMS = 3  # Maximum terms to add from concept clusters
        
        # Swedish question word to intent mapping
        self.question_intents = {
            'vad': 'definition',  # What is
            'vem': 'person',  # Who
            'när': 'time',  # When
            'var': 'location',  # Where
            'hur': 'how_to',  # How
            'varför': 'reason',  # Why
            'vilken': 'selection',  # Which
            'vilket': 'selection',
            'vilka': 'selection_plural'
        }
        
        # Semantic concept clusters for Swedish
        self.concept_clusters = {
            'food': ['mat', 'äta', 'restaurang', 'krog', 'middag', 'lunch', 'frukost', 
                    'måltid', 'rätt', 'recept', 'kök', 'matlagning'],
            'travel': ['resa', 'semester', 'flyg', 'hotell', 'turism', 'destination',
                      'utflykt', 'biljett', 'airport', 'flygplats'],
            'health': ['hälsa', 'sjuk', 'läkare', 'vård', 'sjukvård', 'medicin',
                      'patient', 'behandling', 'symtom', 'doktor'],
            'education': ['utbildning', 'skola', 'universitet', 'studera', 'kurs',
                         'lära', 'elev', 'student', 'lärare', 'undervisning'],
            'work': ['arbete', 'jobb', 'karriär', 'anställning', 'tjänst', 'lön',
                    'arbetsgivare', 'företag', 'kontor', 'yrkesroll'],
            'housing': ['bostad', 'lägenhet', 'hus', 'hem', 'villa', 'hyra', 'köpa',
                       'bostadsrätt', 'hemnet', 'fastighet'],
            'technology': ['teknik', 'dator', 'mobil', 'internet', 'app', 'programvara',
                          'it', 'digital', 'elektronik', 'teknologi'],
            'entertainment': ['underhållning', 'film', 'musik', 'konsert', 'teater',
                            'bio', 'show', 'event', 'nöje', 'kultur'],
            'shopping': ['köpa', 'butik', 'affär', 'handel', 'pris', 'rea', 'erbjudande',
                        'webshop', 'shopping', 'köp'],
            'news': ['nyheter', 'nyhet', 'aktuellt', 'senaste', 'rapport', 'händelse',
                    'notis', 'information', 'uppdatering'],
        }
        
        # Common Swedish phrase transformations
        self.phrase_transformations = [
            # Question phrases to search terms
            (r'var kan jag (hitta|köpa|få)', r'\1'),
            (r'hur (fungerar|gör|använder)', r'\1 guide tutorial'),
            (r'vad (är|betyder)', r'\1 definition'),
            (r'när (öppnar|stänger)', r'\1 öppettider'),
            (r'vilken (är (bäst|bästa))', 'recension topp rekommendation'),
            (r'(finns det|finns)', 'hitta lista'),
        ]
        
        logger.info("SemanticSimilarity initialized for Swedish natural language search")
    
    def calculate_semantic_score(
        self, 
        query: str, 
        document: Dict[str, Any],
        query_intent: str = None
    ) -> float:
        """
        Calculate semantic similarity between query and document
        
        Args:
            query: User's search query (natural language)
            document: Document to score
            query_intent: Detected query intent (from QueryProcessor)
        
        Returns:
            Semantic similarity score (0.0-1.0)
        """
        query_lower = query.lower()
        content = document.get('content', '').lower()
        title = document.get('title', '').lower()
        description = document.get('description', '').lower()
        
        score = 0.0
        
        # 1. Intent matching
        if query_intent:
            intent_score = self._match_intent(query_intent, document)
            score += intent_score * 0.30
        
        # 2. Concept cluster matching
        concept_score = self._match_concepts(query_lower, content, title)
        score += concept_score * 0.25
        
        # 3. Phrase similarity (for conversational queries)
        phrase_score = self._phrase_similarity(query_lower, content, title)
        score += phrase_score * 0.25
        
        # 4. Question answer matching
        question_score = self._question_answer_match(query_lower, content, title)
        score += question_score * 0.20
        
        return min(1.0, score)
    
    def _match_intent(self, intent: str, document: Dict[str, Any]) -> float:
        """Match query intent with document type"""
        content = document.get('content', '').lower()
        title = document.get('title', '').lower()
        
        intent_patterns = {
            'definition': ['definition', 'är', 'betyder', 'innebär', 'förklaring'],
            'how_to': ['guide', 'hur', 'steg', 'instruktion', 'tutorial', 'gör'],
            'location': ['adress', 'plats', 'karta', 'var', 'ligger', 'finns'],
            'time': ['öppettider', 'tid', 'datum', 'när', 'schema'],
            'shopping': ['köpa', 'pris', 'butik', 'köp', 'beställa', 'webshop'],
            'news': ['senaste', 'nyhet', 'aktuellt', 'idag', 'rapport'],
            'recommendation': ['bäst', 'topp', 'recension', 'rekommendation', 'test']
        }
        
        if intent in intent_patterns:
            patterns = intent_patterns[intent]
            matches = sum(1 for p in patterns if p in content or p in title)
            return min(1.0, matches * 0.25)
        
        return 0.0
    
    def _match_concepts(self, query: str, content: str, title: str) -> float:
        """Match semantic concept clusters"""
        score = 0.0
        
        # Find which concept clusters the query belongs to
        query_concepts = set()
        for concept_name, terms in self.concept_clusters.items():
            if any(term in query for term in terms):
                query_concepts.add(concept_name)
        
        # Check if document matches these concepts
        for concept_name in query_concepts:
            terms = self.concept_clusters[concept_name]
            # Count matches in content and title (title weighted higher)
            content_matches = sum(1 for term in terms if term in content)
            title_matches = sum(1 for term in terms if term in title)
            
            concept_score = min(1.0, (content_matches * 0.1 + title_matches * 0.3))
            score += concept_score
        
        # Normalize by number of concepts
        if query_concepts:
            score = score / len(query_concepts)
        
        return min(1.0, score)
    
    def _phrase_similarity(self, query: str, content: str, title: str) -> float:
        """Calculate phrase-level similarity"""
        # Extract meaningful phrases from query (2-3 word phrases)
        query_words = query.split()
        
        if len(query_words) < 2:
            return 0.0
        
        # Generate bi-grams and tri-grams
        phrases = []
        for i in range(len(query_words) - 1):
            phrases.append(' '.join(query_words[i:i+2]))
            if i < len(query_words) - 2:
                phrases.append(' '.join(query_words[i:i+3]))
        
        # Count phrase matches (exact or partial)
        title_matches = sum(1 for phrase in phrases if phrase in title)
        content_matches = sum(1 for phrase in phrases if phrase in content)
        
        # Title matches are more valuable
        total_matches = title_matches * 2 + content_matches
        max_possible = len(phrases) * 3  # Maximum if all in title
        
        return min(1.0, total_matches / max_possible if max_possible > 0 else 0.0)
    
    def _question_answer_match(self, query: str, content: str, title: str) -> float:
        """Match questions to potential answers"""
        score = 0.0
        
        # Check if query is a question
        is_question = any(q in query.split() for q in self.question_intents.keys())
        
        if not is_question:
            return 0.0
        
        # Look for answer indicators in content
        answer_indicators = [
            'svaret', 'är', 'betyder', 'innebär', 'kan', 'ska', 'kommer',
            'definition', 'förklaring', 'genom att', 'på grund av'
        ]
        
        indicator_matches = sum(1 for ind in answer_indicators if ind in content)
        
        # Documents with many answer indicators are likely to answer questions
        score = min(1.0, indicator_matches * 0.15)
        
        return score
    
    def enhance_query(self, query: str) -> List[str]:
        """
        Enhance query with semantically related terms
        
        Args:
            query: Original query
        
        Returns:
            List of enhanced query terms
        """
        enhanced_terms = set(query.lower().split())
        
        # Apply phrase transformations
        for pattern, replacement in self.phrase_transformations:
            if re.search(pattern, query.lower()):
                transformed = re.sub(pattern, replacement, query.lower())
                enhanced_terms.update(transformed.split())
        
        # Add concept cluster terms
        for concept_name, terms in self.concept_clusters.items():
            if any(term in query.lower() for term in terms):
                # Add most relevant terms from cluster
                enhanced_terms.update(terms[:self.MAX_CLUSTER_TERMS])
        
        return list(enhanced_terms)
    
    def detect_conversational_query(self, query: str) -> bool:
        """
        Detect if query is conversational (natural language)
        
        Args:
            query: Search query
        
        Returns:
            True if conversational, False if keyword-based
        """
        query_lower = query.lower()
        
        # Check for question words
        has_question_words = any(q in query_lower.split() for q in self.question_intents.keys())
        
        # Check for conversational phrases
        conversational_phrases = [
            'kan jag', 'vill jag', 'skulle jag', 'behöver jag',
            'var finns', 'hur gör', 'vad är', 'när öppnar',
            'vilken är', 'finns det', 'hur mycket'
        ]
        has_conversational = any(phrase in query_lower for phrase in conversational_phrases)
        
        # Check length (conversational queries are typically longer)
        is_long_enough = len(query.split()) >= 4
        
        return (has_question_words or has_conversational) and is_long_enough
