"""
Search Query Parser

Parses and normalizes search queries.
"""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional
from enum import Enum
import re

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class QueryType(Enum):
    """Search query type classification."""
    SIMPLE = "simple"           # Single term
    PHRASE = "phrase"           # Quoted phrase
    BOOLEAN = "boolean"         # AND/OR/NOT operators
    ADVANCED = "advanced"       # Domain/date filters
    MIXED = "mixed"             # Combination


@dataclass
class SearchQuery:
    """
    Parsed search query.
    """
    original_query: str
    query_type: QueryType
    terms: List[str] = field(default_factory=list)
    phrases: List[str] = field(default_factory=list)
    exclude_terms: List[str] = field(default_factory=list)
    domain_filter: Optional[str] = None
    language_filter: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sort_by: str = "relevance"
    limit: int = 10
    offset: int = 0
    
    @property
    def all_terms(self) -> Set[str]:
        """Get all terms (single + phrases)."""
        all_t = set(self.terms)
        all_t.update(self.phrases)
        return all_t
    
    @property
    def is_empty(self) -> bool:
        """Check if query has any search terms."""
        return len(self.terms) == 0 and len(self.phrases) == 0
    
    def __str__(self) -> str:
        return f"SearchQuery(terms={self.terms}, phrases={self.phrases})"


class QueryParser:
    """
    Parse and normalize search queries.
    
    Features:
    - Term extraction
    - Phrase detection (quoted strings)
    - Boolean operators (AND, OR, NOT)
    - Advanced filters (site:, date:)
    - Query normalization
    """
    
    # Supported filters
    FILTER_PATTERNS = {
        'site': r'site:([\w.-]+)',
        'domain': r'domain:([\w.-]+)',
        'date_from': r'from:([\d-]+)',
        'date_to': r'to:([\d-]+)',
        'lang': r'lang:([a-z]{2})',
    }
    
    def __init__(
        self,
        min_term_length: int = 2,
        max_terms: int = 10,
    ):
        """
        Initialize query parser.
        
        Args:
            min_term_length: Minimum term length
            max_terms: Maximum terms to extract
        """
        self.min_term_length = min_term_length
        self.max_terms = max_terms
    
    def parse(self, query_string: str) -> SearchQuery:
        """
        Parse search query string.
        
        Args:
            query_string: Raw query string
        
        Returns:
            Parsed SearchQuery object
        """
        if not query_string or not isinstance(query_string, str):
            logger.warning(f"Invalid query: {query_string}")
            return SearchQuery(
                original_query=query_string or "",
                query_type=QueryType.SIMPLE,
            )
        
        # Clean and normalize
        original = query_string.strip()
        query = self._normalize_query(original)
        
        # Extract filters
        domain_filter = self._extract_filter(query, 'site') or self._extract_filter(query, 'domain')
        date_from = self._extract_filter(query, 'date_from')
        date_to = self._extract_filter(query, 'date_to')
        lang_filter = self._extract_filter(query, 'lang')
        
        # Remove filters from query
        query_cleaned = self._remove_filters(query)
        
        # Extract quoted phrases
        phrases = self._extract_phrases(query_cleaned)
        query_cleaned = self._remove_phrases(query_cleaned)
        
        # Extract terms and exclusions
        terms, exclude_terms = self._extract_terms(query_cleaned)
        
        # Determine query type
        query_type = self._classify_query_type(original, terms, phrases, exclude_terms)
        
        # Create query object
        parsed_query = SearchQuery(
            original_query=original,
            query_type=query_type,
            terms=terms[:self.max_terms],
            phrases=phrases,
            exclude_terms=exclude_terms,
            domain_filter=domain_filter,
            language_filter=lang_filter,
            date_from=date_from,
            date_to=date_to,
        )
        
        logger.debug(f"Parsed query: {parsed_query}")
        return parsed_query
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query string.
        
        Args:
            query: Raw query
        
        Returns:
            Normalized query
        """
        # Convert to lowercase
        query = query.lower()
        
        # Replace multiple spaces
        query = re.sub(r'\s+', ' ', query)
        
        # Remove special characters (keep basic operators)
        query = re.sub(r'[^\w\s"-]', '', query)
        
        return query.strip()
    
    def _extract_phrases(self, query: str) -> List[str]:
        """
        Extract quoted phrases.
        
        Args:
            query: Query string
        
        Returns:
            List of phrases
        """
        phrases = []
        pattern = r'"([^"]+)"'
        
        for match in re.finditer(pattern, query):
            phrase = match.group(1).strip()
            if len(phrase) >= self.min_term_length:
                phrases.append(phrase)
        
        return phrases
    
    def _remove_phrases(self, query: str) -> str:
        """
        Remove quoted phrases from query.
        
        Args:
            query: Query string
        
        Returns:
            Query without phrases
        """
        return re.sub(r'"[^"]+"', '', query).strip()
    
    def _extract_terms(self, query: str) -> tuple:
        """
        Extract terms and exclusions.
        
        Args:
            query: Query string
        
        Returns:
            Tuple of (terms, exclude_terms)
        """
        terms = []
        exclude_terms = []
        
        # Split by whitespace and hyphens
        for part in query.split():
            # Check for NOT operator
            if part.startswith('-') or part.startswith('not:'):
                term = part.lstrip('-').replace('not:', '')
                if len(term) >= self.min_term_length:
                    exclude_terms.append(term)
            else:
                # Skip AND/OR operators
                if part.upper() not in ('AND', 'OR'):
                    if len(part) >= self.min_term_length:
                        terms.append(part)
        
        return terms, exclude_terms
    
    def _extract_filter(self, query: str, filter_name: str) -> Optional[str]:
        """
        Extract filter value.
        
        Args:
            query: Query string
            filter_name: Filter name (site, date_from, etc.)
        
        Returns:
            Filter value or None
        """
        if filter_name not in self.FILTER_PATTERNS:
            return None
        
        pattern = self.FILTER_PATTERNS[filter_name]
        match = re.search(pattern, query)
        
        if match:
            return match.group(1)
        
        return None
    
    def _remove_filters(self, query: str) -> str:
        """
        Remove all filters from query.
        
        Args:
            query: Query string
        
        Returns:
            Query without filters
        """
        for pattern in self.FILTER_PATTERNS.values():
            query = re.sub(pattern, '', query)
        
        return query.strip()
    
    def _classify_query_type(self, original: str, terms: List, phrases: List, exclude_terms: List) -> QueryType:
        """
        Classify query type.
        
        Args:
            original: Original query
            terms: Extracted terms
            phrases: Extracted phrases
            exclude_terms: Exclusions
        
        Returns:
            QueryType classification
        """
        # Check for advanced features
        has_filters = any(f in original.lower() for f in ['site:', 'domain:', 'from:', 'to:', 'lang:'])
        has_boolean = any(op in original.upper() for op in [' AND ', ' OR ', ' NOT '])
        
        if has_filters:
            if has_boolean or exclude_terms:
                return QueryType.ADVANCED
            return QueryType.ADVANCED
        
        if phrases and not terms and not exclude_terms:
            return QueryType.PHRASE
        
        if has_boolean or exclude_terms:
            return QueryType.BOOLEAN
        
        if len(terms) == 1 and not phrases:
            return QueryType.SIMPLE
        
        if len(terms) > 1 or (terms and phrases):
            return QueryType.MIXED
        
        return QueryType.SIMPLE
    
    def validate_query(self, query: SearchQuery) -> bool:
        """
        Validate parsed query.
        
        Args:
            query: SearchQuery object
        
        Returns:
            True if valid, False otherwise
        """
        # Must have at least some search content
        if query.is_empty:
            logger.warning("Query has no search terms")
            return False
        
        # Check term limits
        total_terms = len(query.terms) + len(query.phrases)
        if total_terms > self.max_terms:
            logger.warning(f"Query exceeds max terms ({total_terms} > {self.max_terms})")
            return False
        
        return True
    
    def suggest_correction(self, query_string: str) -> Optional[str]:
        """
        Suggest query correction (basic).
        
        Args:
            query_string: Query string
        
        Returns:
            Suggested correction or None
        """
        # Very basic: remove duplicate spaces
        corrected = re.sub(r'\s+', ' ', query_string).strip()
        
        if corrected != query_string:
            return corrected
        
        return None
