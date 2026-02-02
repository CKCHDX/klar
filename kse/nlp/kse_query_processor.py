"""
KSE Query Processor - Enhanced query processing for natural language searches
"""
import re
from typing import List, Dict, Set, Tuple
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class QueryProcessor:
    """Enhanced query processor for natural language understanding"""
    
    def __init__(self):
        """Initialize query processor"""
        # Swedish question words
        self.question_words = {
            'vad', 'vem', 'när', 'var', 'hur', 'varför', 'vilken', 'vilket', 'vilka',
            'finns', 'funkar', 'fungerar', 'betyder', 'handlar', 'innebär'
        }
        
        # Swedish synonyms for common terms (expanded for better natural language understanding)
        self.synonyms = {
            'nyheter': ['nyhet', 'news', 'aktuellt', 'senaste', 'notiser', 'rapporter'],
            'väder': ['vädret', 'temperatur', 'prognos', 'forecast', 'klimat', 'väderlek'],
            'sport': ['idrott', 'fotboll', 'hockey', 'matcher', 'tävling', 'spel'],
            'politik': ['politisk', 'regering', 'riksdag', 'minister', 'parti', 'val'],
            'ekonomi': ['ekonomisk', 'aktie', 'börs', 'finans', 'pengar', 'marknad'],
            'kultur': ['kulturell', 'konst', 'musik', 'film', 'teater', 'litteratur'],
            'teknologi': ['teknik', 'innovation', 'digital', 'dator', 'it', 'programvara'],
            'vetenskap': ['vetenskaplig', 'forskning', 'studie', 'forskare', 'experiment'],
            'hälsa': ['sjukvård', 'läkare', 'medicin', 'sjukdom', 'vård', 'hälsovård'],
            'utbildning': ['skola', 'universitet', 'studera', 'kurs', 'lära', 'undervisning'],
            'restaurang': ['restauranger', 'mat', 'äta', 'krog', 'matställe', 'cafè'],
            'resa': ['resor', 'turism', 'semester', 'flygning', 'hotell'],
            'arbete': ['jobb', 'anställning', 'karriär', 'lön', 'tjänst'],
            'bostad': ['lägenhet', 'hus', 'hem', 'villa', 'boende'],
            'transport': ['kollektivtrafik', 'buss', 'tåg', 'tunnelbana', 'resa'],
            'shopping': ['köpa', 'butik', 'affär', 'handel', 'inköp'],
            'underhållning': ['nöje', 'roligt', 'fritid', 'event', 'evenemang'],
        }
        
        # Common phrase patterns (expanded for natural Swedish language)
        self.phrase_patterns = [
            (r'hur (fungerar|funkar)', 'guide tutorial anvisning'),
            (r'vad (är|betyder)', 'definition förklaring betydelse'),
            (r'var (finns|ligger)', 'plats location adress karta'),
            (r'när (ska|kommer|öppnar)', 'tid datum öppettider schema'),
            (r'bästa? (.*)', r'\1 recension topp rekommendation'),
            (r'köpa (.*)', r'\1 butik affär köp handla'),
            (r'hitta (.*)', r'\1 sök leta plats'),
            (r'(billig|billigaste) (.*)', r'\1 pris låg kostnad jämför'),
            (r'nära (mig|här)', 'närhet lokalt område'),
            (r'öppettider (.*)', r'\1 tid öppet stängt'),
            (r'recension (.*)', r'\1 omdöme betyg kvalitet'),
            (r'jämföra? (.*)', r'\1 skillnad kontrast test'),
        ]
        
        logger.info("QueryProcessor initialized with synonym expansion")
    
    def process_query(self, query: str) -> Dict[str, any]:
        """
        Process query with natural language understanding
        
        Args:
            query: Raw query string
        
        Returns:
            Dict with processed query data including expanded terms, intent, etc.
        """
        if not query:
            return {'terms': [], 'expanded_terms': [], 'intent': None, 'is_question': False}
        
        query = query.strip().lower()
        
        # Detect if it's a question
        is_question = self._is_question(query)
        
        # Detect intent
        intent = self._detect_intent(query)
        
        # Extract key terms
        terms = self._extract_terms(query)
        
        # Expand terms with synonyms
        expanded_terms = self._expand_terms(terms)
        
        # Apply phrase patterns
        pattern_terms = self._apply_phrase_patterns(query)
        expanded_terms.extend(pattern_terms)
        
        # Remove duplicates
        expanded_terms = list(set(expanded_terms))
        
        result = {
            'original': query,
            'terms': terms,
            'expanded_terms': expanded_terms,
            'intent': intent,
            'is_question': is_question,
            'query_type': self._get_query_type(query, is_question)
        }
        
        logger.debug(f"Processed query: {result}")
        return result
    
    def _is_question(self, query: str) -> bool:
        """Check if query is a question"""
        # Check for question mark
        if '?' in query:
            return True
        
        # Check for question words at start
        words = query.split()
        if words and words[0] in self.question_words:
            return True
        
        return False
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['köpa', 'köp', 'pris', 'beställa']):
            return 'shopping'
        
        if any(word in query_lower for word in ['vad är', 'vad betyder', 'definition']):
            return 'definition'
        
        if any(word in query_lower for word in ['hur', 'guide', 'tutorial']):
            return 'how_to'
        
        if any(word in query_lower for word in ['var finns', 'var ligger', 'adress']):
            return 'location'
        
        if any(word in query_lower for word in ['när', 'datum', 'tid', 'öppettider']):
            return 'time'
        
        if any(word in query_lower for word in ['senaste', 'nyheter', 'aktuellt', 'idag']):
            return 'news'
        
        if any(word in query_lower for word in ['bästa', 'rekommendation', 'jämför', 'test']):
            return 'recommendation'
        
        return 'informational'
    
    def _get_query_type(self, query: str, is_question: bool) -> str:
        """Determine query type"""
        if is_question:
            return 'question'
        
        word_count = len(query.split())
        if word_count == 1:
            return 'keyword'
        elif word_count == 2:
            return 'short_phrase'
        else:
            return 'long_phrase'
    
    def _extract_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from query"""
        # Remove punctuation
        query = re.sub(r'[^\w\såäö]', '', query)
        
        # Split into words
        words = query.split()
        
        # Filter out question words and common filler words
        filter_words = self.question_words | {
            'den', 'det', 'de', 'ett', 'en', 'på', 'i', 'och', 'att', 'som', 
            'för', 'med', 'till', 'av', 'är', 'kan', 'om', 'man'
        }
        
        terms = [word for word in words if word not in filter_words and len(word) > 2]
        
        return terms
    
    def _expand_terms(self, terms: List[str]) -> List[str]:
        """Expand terms with synonyms"""
        expanded = list(terms)  # Start with original terms
        
        for term in terms:
            # Check if term has synonyms
            for base_word, synonyms in self.synonyms.items():
                if term in synonyms or term == base_word:
                    expanded.extend([base_word] + synonyms)
                    break
        
        return expanded
    
    def _apply_phrase_patterns(self, query: str) -> List[str]:
        """Apply phrase pattern matching"""
        additional_terms = []
        
        for pattern, replacement in self.phrase_patterns:
            match = re.search(pattern, query)
            if match:
                if isinstance(replacement, str):
                    # Fixed replacement
                    additional_terms.extend(replacement.split())
                else:
                    # Regex group replacement
                    expanded = re.sub(pattern, replacement, query)
                    additional_terms.extend(expanded.split())
        
        return additional_terms
    
    def expand_search_terms(self, terms: List[str]) -> List[str]:
        """
        Expand a list of search terms with variations
        
        Args:
            terms: List of terms to expand
        
        Returns:
            Expanded list of terms
        """
        expanded = list(terms)
        
        for term in terms:
            # Add common variations
            # Remove common suffixes for Swedish words
            if term.endswith('er'):
                expanded.append(term[:-2])
            elif term.endswith('ar'):
                expanded.append(term[:-2])
            elif term.endswith('en'):
                expanded.append(term[:-2])
            elif term.endswith('et'):
                expanded.append(term[:-2])
            
            # Expand with synonyms
            for base_word, synonyms in self.synonyms.items():
                if term == base_word:
                    expanded.extend(synonyms)
                elif term in synonyms:
                    expanded.append(base_word)
        
        return list(set(expanded))
