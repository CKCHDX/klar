"""
Regional Relevance - Factor 7: Regional and Swedish-specific relevance
Enhanced for enterprise Swedish search engine (Naver-style for Sweden)
"""

import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)


class RegionalRelevance:
    """Enhanced regional relevance scoring for Swedish content"""
    
    def __init__(self):
        # Swedish TLDs (top-level domains)
        self.swedish_tlds = ['.se', '.nu']
        
        # Swedish cities and regions (for geographic relevance)
        self.swedish_locations = [
            'stockholm', 'göteborg', 'malmö', 'uppsala', 'västerås', 
            'örebro', 'linköping', 'helsingborg', 'jönköping', 'norrköping',
            'lund', 'umeå', 'gävle', 'borås', 'eskilstuna', 'södertälje',
            'karlstad', 'täby', 'växjö', 'halmstad', 'sundsvall', 'luleå',
            'trollhättan', 'östersund', 'borlänge', 'falun', 'kalmar',
            'kristianstad', 'karlskrona', 'skellefteå', 'uddevalla', 'skövde'
        ]
        
        # Swedish language indicators (expanded)
        self.swedish_keywords = [
            'sverige', 'swedish', 'svensk', 'svenska', 'svenskt',
            'riksdag', 'regering', 'kommun', 'landsting', 'region',
            'kunglig', 'nobel', 'ikea', 'volvo', 'ericsson',
            'karolinska', 'chalmers', 'lund universitet',
            'stockholm universitet', 'göteborgs universitet'
        ]
        
        # Swedish government and trusted domains
        self.trusted_swedish_domains = [
            'regeringen.se', 'riksdagen.se', 'skatteverket.se',
            'försäkringskassan.se', 'arbetsförmedlingen.se',
            'folkhälsomyndigheten.se', 'socialstyrelsen.se',
            'svt.se', 'sr.se', 'dn.se', 'aftonbladet.se',
            'expressen.se', 'svenskaakademien.se', 'kb.se',
            'wikipedia.org', 'ne.se', 'scb.se'  # Statistics Sweden
        ]
        
        # Swedish-specific content patterns
        self.swedish_patterns = [
            r'\bkr\b',  # Swedish krona
            r'\b\d{6}-\d{4}\b',  # Swedish personal number format
            r'\b\d{3}\s\d{2}\s\d{2}\b',  # Swedish postal code
            r'å|ä|ö',  # Swedish letters
        ]
        
        logger.info("Enhanced RegionalRelevance initialized for Swedish search")
    
    def calculate_regional_score(self, document: Dict[str, Any]) -> float:
        """
        Calculate enhanced regional relevance score for Swedish content
        
        Args:
            document: Document with metadata
        
        Returns:
            Regional score (0.0-1.0) optimized for Swedish content
        """
        url = document.get('url', '').lower()
        domain = document.get('domain', '').lower()
        title = document.get('title', '').lower()
        content = document.get('content', '').lower()
        
        score = 0.0  # Start at 0 for non-Swedish content
        
        # 1. Swedish TLD bonus (strong indicator)
        if any(tld in url for tld in self.swedish_tlds):
            score += 0.30
            logger.debug(f"Swedish TLD bonus: {url}")
        
        # 2. Trusted Swedish domain bonus (very strong indicator)
        if any(trusted in domain for trusted in self.trusted_swedish_domains):
            score += 0.25
            logger.debug(f"Trusted Swedish domain bonus: {domain}")
        
        # 3. Swedish location mentions (geographic relevance)
        location_matches = sum(1 for loc in self.swedish_locations if loc in content)
        if location_matches > 0:
            location_score = min(0.15, location_matches * 0.03)
            score += location_score
            logger.debug(f"Location matches: {location_matches}, score: {location_score}")
        
        # 4. Swedish language indicators (content quality)
        keyword_matches = sum(1 for kw in self.swedish_keywords if kw in content)
        if keyword_matches > 0:
            keyword_score = min(0.15, keyword_matches * 0.03)
            score += keyword_score
            logger.debug(f"Keyword matches: {keyword_matches}, score: {keyword_score}")
        
        # 5. Swedish-specific patterns (strong language indicator)
        pattern_matches = 0
        for pattern in self.swedish_patterns:
            if re.search(pattern, content):
                pattern_matches += 1
        
        if pattern_matches > 0:
            pattern_score = min(0.10, pattern_matches * 0.025)
            score += pattern_score
            logger.debug(f"Pattern matches: {pattern_matches}, score: {pattern_score}")
        
        # 6. Title in Swedish (indicates Swedish-focused content)
        if any(kw in title for kw in self.swedish_keywords):
            score += 0.05
        
        # Normalize to 0-1 range
        final_score = min(1.0, score)
        
        logger.debug(f"Regional score for {url}: {final_score:.3f}")
        return final_score
    
    def is_swedish_content(self, document: Dict[str, Any]) -> bool:
        """
        Determine if content is Swedish
        
        Args:
            document: Document with metadata
        
        Returns:
            True if content is Swedish-focused
        """
        score = self.calculate_regional_score(document)
        return score >= 0.30  # Threshold for Swedish content
