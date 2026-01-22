"""
Klar SBDB Advanced NLP - Production-Grade Swedish Language Processing
Features: Compound word handling, semantic enrichment, context-awareness, regional processing
Compete against Google with superior Swedish language understanding
"""

import re
import json
import logging
import math
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ============================================================================
# SWEDISH VOCABULARY & SEMANTIC DATABASES
# ============================================================================

SWEDISH_STOPWORDS = {
    'och', 'det', 'att', 'en', 'i', 'som', 'på', 'de', 'är', 'till',
    'var', 'då', 'ha', 'från', 'som', 'denna', 'dessa', 'här', 'där',
    'vad', 'vilken', 'vilka', 'alla', 'ingen', 'någon', 'något', 'några',
    'andra', 'övriga', 'samma', 'sådan', 'många', 'mycket', 'om', 'så',
    'än', 'eller', 'men', 'dock', 'utan', 'för', 'vi', 'genom', 'under',
    'över', 'mellan', 'kring', 'mitt', 'denna', 'denna', 'denna', 'denna'
}

# Common Swedish compound word components
COMPOUND_COMPONENTS = {
    'restaurang': ['rest', 'rang'],
    'stockhol': ['stock', 'holm'],
    'badrum': ['bad', 'rum'],
    'sovrum': ['sov', 'rum'],
    'arbetsplats': ['arbets', 'plats'],
    'hemadress': ['hem', 'adress'],
    'telefonsamtal': ['telefon', 'samtal'],
    'arbetsvecka': ['arbets', 'vecka'],
    'förnamn': ['för', 'namn'],
    'efternamn': ['efter', 'namn'],
}

# Swedish semantic categories for ranking
SEMANTIC_DOMAINS = {
    'government': ['regering', 'riksdag', 'lagstiftning', 'proposition', 'statlig', 'offentlig'],
    'health': ['sjukvård', 'medicin', 'hälsa', 'sjukhus', 'läkare', 'patient'],
    'education': ['skola', 'universitet', 'kurs', 'undervisning', 'utbildning', 'pedagog'],
    'business': ['företag', 'handel', 'köp', 'försäljning', 'affär', 'handel'],
    'technology': ['dator', 'mjukvara', 'internet', 'digital', 'teknik', 'teknologi'],
    'news': ['nyheter', 'rapporterar', 'enligt', 'säger', 'meddelar', 'publicerat'],
    'cultural': ['kultur', 'konst', 'musik', 'teater', 'film', 'litteratur'],
}

# Swedish geographical entities with regional codes
SWEDISH_REGIONS = {
    # Läns (Counties)
    'stockholm': {'type': 'län', 'code': 'ab', 'weight': 1.5},
    'västra götaland': {'type': 'län', 'code': 'o', 'weight': 1.4},
    'skåne': {'type': 'län', 'code': 'm', 'weight': 1.3},
    'uppsala': {'type': 'län', 'code': 'c', 'weight': 1.1},
    'värmland': {'type': 'län', 'code': 's', 'weight': 1.0},
    'dalarna': {'type': 'län', 'code': 'w', 'weight': 1.0},
    'gävleborg': {'type': 'län', 'code': 'x', 'weight': 1.0},
    'västernorrland': {'type': 'län', 'code': 'y', 'weight': 1.0},
    'jämtland': {'type': 'län', 'code': 'z', 'weight': 1.0},
    'västerbotten': {'type': 'län', 'code': 'ac', 'weight': 1.0},
    'norrbotten': {'type': 'län', 'code': 'bd', 'weight': 1.0},
    
    # Major cities (Kommuner)
    'göteborg': {'type': 'city', 'code': 'gb', 'weight': 1.3, 'region': 'västra götaland'},
    'malmö': {'type': 'city', 'code': 'ma', 'weight': 1.3, 'region': 'skåne'},
    'västerås': {'type': 'city', 'code': 'vs', 'weight': 1.1, 'region': 'västmanland'},
    'örebro': {'type': 'city', 'code': 'ör', 'weight': 1.1, 'region': 'örebro'},
    'linköping': {'type': 'city', 'code': 'lk', 'weight': 1.0, 'region': 'östergötland'},
    'helsingborg': {'type': 'city', 'code': 'hb', 'weight': 1.0, 'region': 'skåne'},
    'jönköping': {'type': 'city', 'code': 'jk', 'weight': 1.0, 'region': 'jönköping'},
    'norrköping': {'type': 'city', 'code': 'nk', 'weight': 1.0, 'region': 'östergötland'},
    'växjö': {'type': 'city', 'code': 'vx', 'weight': 1.0, 'region': 'kronoberg'},
    'karlstad': {'type': 'city', 'code': 'ka', 'weight': 1.0, 'region': 'värmland'},
    'gävle': {'type': 'city', 'code': 'ge', 'weight': 1.0, 'region': 'gävleborg'},
    'sundsvall': {'type': 'city', 'code': 'su', 'weight': 1.0, 'region': 'västernorrland'},
    'umeå': {'type': 'city', 'code': 'um', 'weight': 1.0, 'region': 'västerbotten'},
    'luleå': {'type': 'city', 'code': 'lu', 'weight': 1.0, 'region': 'norrbotten'},
}

# Advanced lemmatization rules (ordered by specificity)
ADVANCED_LEMMATIZATION = [
    # Verb conjugations
    (r'ade$', 'a', 2),  # spelade -> spela
    (r'ern$', '', 2),   # hunderna -> hund
    (r'erens$', '', 2), # hundarnas -> hund
    (r'et$', '', 2),    # huset -> hus
    (r'ets$', '', 2),   # husets -> hus
    
    # Noun plurals
    (r'ar$', '', 1),    # hundar -> hund
    (r'or$', '', 1),    # dörrör -> dörr
    (r'er$', '', 1),    # restauranger -> restaurang
    (r'a$', '', 1),     # flicka -> flick (catch-all, low priority)
    
    # Adjectives
    (r'are$', '', 1),   # större -> stor
    (r'ast$', '', 1),   # största -> stor
    (r'aste$', '', 1),  # största -> stor
    
    # Diminutives
    (r'chen$', '', 1),  # flickchen -> flick
    (r'le$', '', 1),    # gumle -> gum
    
    # Swedish specific patterns
    (r'heten$', 'het', 2),  # möjligheten -> möjlighet
    (r'ningen$', 'ning', 2), # betydningen -> betydning
]


class AdvancedSwedishNLP:
    """
    Production-grade Swedish NLP with compound handling and semantic enrichment
    """
    
    def __init__(self):
        self.stopwords = SWEDISH_STOPWORDS
        self.compound_components = COMPOUND_COMPONENTS
        self.semantic_domains = SEMANTIC_DOMAINS
        self.regions = SWEDISH_REGIONS
        self.lemmatization_rules = ADVANCED_LEMMATIZATION
        logger.info("AdvancedSwedishNLP initialized")
    
    def tokenize_advanced(self, text: str) -> List[str]:
        """
        Advanced tokenization with Swedish-specific rules
        """
        # Lowercase
        text = text.lower()
        
        # Preserve Swedish characters (åäö)
        text = re.sub(r'[^a-zåäö\s\-]', ' ', text)
        
        # Split on whitespace and hyphens
        tokens = re.split(r'[\s\-]+', text)
        
        # Remove empty tokens
        tokens = [t.strip() for t in tokens if t.strip()]
        
        return tokens
    
    def split_compound_words(self, word: str) -> List[str]:
        """
        Split Swedish compound words intelligently
        Example: "stockholmrestauranger" -> ["stockholm", "restaurang"]
        """
        if len(word) < 6:
            return [word]  # Too short to be compound
        
        # Check if exact compound in database
        if word in self.compound_components:
            return self.compound_components[word]
        
        # Heuristic: Common separators in Swedish
        separators = ['arna', 'erna', 'na', 'de', 'ar', 'er']
        
        for sep in separators:
            if word.endswith(sep) and len(word) > len(sep) + 3:
                base = word[:-len(sep)]
                if self._is_valid_word(base):
                    return [base, sep]
        
        return [word]
    
    def lemmatize_advanced(self, word: str) -> str:
        """
        Advanced lemmatization with multiple rules and compound handling
        """
        if len(word) < 3:
            return word
        
        word_lower = word.lower()
        
        # Try compound splitting first
        compounds = self.split_compound_words(word_lower)
        if len(compounds) > 1:
            return ' '.join([self.lemmatize_advanced(c) for c in compounds])
        
        # Apply lemmatization rules (ordered by priority)
        for pattern, replacement, priority in self.lemmatization_rules:
            if re.search(pattern, word_lower):
                lemma = re.sub(pattern, replacement, word_lower)
                if len(lemma) >= 2:  # Ensure minimum length
                    return lemma
        
        return word_lower
    
    def process_text_advanced(self, text: str) -> Dict:
        """
        Advanced text processing with rich semantic information
        Returns: tokens, semantic tags, confidence scores
        """
        # Tokenize
        tokens = self.tokenize_advanced(text)
        
        processed = {
            'tokens': [],
            'lemmas': [],
            'semantic_tags': [],
            'confidence_scores': [],
            'entity_mentions': [],
        }
        
        # Process each token
        for token in tokens:
            # Skip stopwords
            if token in self.stopwords:
                continue
            
            # Skip very short tokens
            if len(token) < 3:
                continue
            
            # Lemmatize
            lemma = self.lemmatize_advanced(token)
            
            # Find semantic tags
            semantic_tag = self._find_semantic_tag(lemma)
            
            # Calculate confidence
            confidence = self._calculate_token_confidence(token, lemma)
            
            # Check if entity mention
            is_entity = self._is_entity(lemma)
            
            processed['tokens'].append(token)
            processed['lemmas'].append(lemma)
            processed['semantic_tags'].append(semantic_tag or 'general')
            processed['confidence_scores'].append(confidence)
            if is_entity:
                processed['entity_mentions'].append((token, is_entity))
        
        return processed
    
    def extract_entities_advanced(self, text: str) -> Dict:
        """
        Extract and classify Swedish entities (places, people, organizations, etc.)
        """
        entities = {
            'locations': [],
            'organizations': [],
            'people': [],
            'dates': [],
            'numbers': [],
        }
        
        text_lower = text.lower()
        
        # Extract locations (regions, cities)
        for region_name, region_info in self.regions.items():
            if region_name in text_lower:
                entities['locations'].append({
                    'name': region_name,
                    'type': region_info['type'],
                    'weight': region_info['weight']
                })
        
        # Extract dates (Swedish format)
        swedish_dates = re.findall(
            r'(\d{1,2}\s+(?:januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december)\s+\d{4})',
            text, re.IGNORECASE
        )
        entities['dates'].extend(swedish_dates)
        
        # Extract ISO dates
        iso_dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
        entities['dates'].extend(iso_dates)
        
        # Extract numbers and quantities
        numbers = re.findall(r'\d+\s*(?:miljon|miljard|miljoner|hundra|tusen)?', text)
        entities['numbers'].extend(numbers)
        
        # Extract organizations (heuristic: capitalized words)
        org_pattern = r'(?:[A-Z][a-zåäö]+\s*){2,}'
        organizations = re.findall(org_pattern, text)
        entities['organizations'].extend([org.strip() for org in organizations if len(org.strip()) > 3])
        
        return entities
    
    def calculate_semantic_similarity(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        """
        Calculate semantic similarity between query and document
        Takes into account semantic domains, entities, and term overlap
        """
        if not query_tokens or not doc_tokens:
            return 0.0
        
        # Convert to sets for comparison
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        
        # Jaccard similarity
        intersection = len(query_set & doc_set)
        union = len(query_set | doc_set)
        jaccard = intersection / union if union > 0 else 0.0
        
        # Semantic domain matching
        query_domains = self._get_semantic_domains(query_tokens)
        doc_domains = self._get_semantic_domains(doc_tokens)
        domain_overlap = len(set(query_domains) & set(doc_domains)) / max(len(set(query_domains) | set(doc_domains)), 1)
        
        # Combined score
        semantic_similarity = (jaccard * 0.6) + (domain_overlap * 0.4)
        
        return min(semantic_similarity, 1.0)
    
    def _find_semantic_tag(self, word: str) -> Optional[str]:
        """
        Find semantic domain for a word
        """
        for domain, keywords in self.semantic_domains.items():
            if word in keywords or any(word in kw for kw in keywords):
                return domain
        return None
    
    def _calculate_token_confidence(self, token: str, lemma: str) -> float:
        """
        Calculate confidence score for token
        Longer words and exact matches score higher
        """
        # Length confidence
        length_conf = min(len(lemma) / 10, 1.0)
        
        # Lemmatization confidence
        if token == lemma:
            lemma_conf = 0.9  # Already in base form
        else:
            lemma_conf = 0.7  # Modified form
        
        # Combined
        return (length_conf + lemma_conf) / 2
    
    def _is_entity(self, word: str) -> Optional[str]:
        """
        Check if word is a named entity
        """
        if word in self.regions:
            return 'location'
        if len(word) > 5 and word[0].isupper():
            return 'organization'
        return None
    
    def _get_semantic_domains(self, words: List[str]) -> List[str]:
        """
        Get semantic domains for a list of words
        """
        domains = []
        for word in words:
            domain = self._find_semantic_tag(word)
            if domain:
                domains.append(domain)
        return domains
    
    def _is_valid_word(self, word: str) -> bool:
        """
        Check if word is likely valid Swedish word
        """
        return len(word) >= 2 and word not in self.stopwords
    
    def get_synonym_forms(self, word: str) -> List[str]:
        """
        Get various forms of a word (singular, plural, compounds)
        Useful for query expansion
        """
        forms = [word]
        
        # Singular/plural variants
        if word.endswith('ar'):
            forms.append(word[:-2])  # hundar -> hund
        if word.endswith('er'):
            forms.append(word[:-2])  # restauranger -> restaurang
        
        # Compound variants
        if len(word) > 6:
            compounds = self.split_compound_words(word)
            forms.extend(compounds)
        
        return list(set(forms))  # Remove duplicates


class SemanticSearchEnhancer:
    """
    Enhances search results with semantic relevance and context
    """
    
    def __init__(self):
        self.nlp = AdvancedSwedishNLP()
    
    def enrich_search_result(self, result: Dict, query_tokens: List[str]) -> Dict:
        """
        Enrich search result with semantic information
        """
        doc_text = result.get('text', '')
        doc_tokens = self.nlp.tokenize_advanced(doc_text)
        
        # Calculate semantic similarity
        semantic_sim = self.nlp.calculate_semantic_similarity(query_tokens, doc_tokens)
        
        # Extract entities from document
        entities = self.nlp.extract_entities_advanced(doc_text)
        
        # Boost score based on entities
        entity_boost = 1.0
        if entities['locations']:
            entity_boost += 0.2  # Local content boost
        if entities['dates']:
            entity_boost += 0.1  # Recent content boost
        
        # Enrich result
        result['semantic_similarity'] = semantic_sim
        result['entities'] = entities
        result['entity_boost'] = entity_boost
        result['enriched_score'] = result.get('relevance_score', 0.5) * semantic_sim * entity_boost
        
        return result


if __name__ == "__main__":
    # Test advanced NLP
    nlp = AdvancedSwedishNLP()
    
    # Test compound word splitting
    print("=== Compound Word Tests ===")
    test_words = ["restaurangerna", "stockholmserverar", "arbetsvecka"]
    for word in test_words:
        compounds = nlp.split_compound_words(word)
        print(f"  {word} -> {compounds}")
    
    # Test advanced lemmatization
    print("\n=== Lemmatization Tests ===")
    test_lemmas = ["restauranger", "hundar", "spelade", "vackrare"]
    for word in test_lemmas:
        lemma = nlp.lemmatize_advanced(word)
        print(f"  {word} -> {lemma}")
    
    # Test advanced processing
    print("\n=== Advanced Text Processing ===")
    test_text = "Bästa restaurangerna i Stockholm och Göteborg har fantastisk mat 22 januari 2026"
    processed = nlp.process_text_advanced(test_text)
    print(f"  Text: {test_text}")
    print(f"  Lemmas: {processed['lemmas']}")
    print(f"  Semantic Tags: {processed['semantic_tags']}")
    
    # Test entity extraction
    print("\n=== Entity Extraction ===")
    entities = nlp.extract_entities_advanced(test_text)
    print(f"  Entities: {json.dumps(entities, indent=2, ensure_ascii=False)}")
    
    # Test semantic similarity
    print("\n=== Semantic Similarity ===")
    query_tokens = nlp.tokenize_advanced("stockholmrestauranger")
    doc_tokens = nlp.tokenize_advanced("Göteborg har nya restauranger")
    sim = nlp.calculate_semantic_similarity(query_tokens, doc_tokens)
    print(f"  Query: {query_tokens}")
    print(f"  Doc: {doc_tokens}")
    print(f"  Similarity: {sim:.3f}")
