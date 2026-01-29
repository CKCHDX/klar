"""
Domain Authority - Factor 3: Domain trust and authority scoring
Assigns trust scores to domains based on various factors
"""

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class DomainAuthority:
    """Domain authority and trust scoring system"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize domain authority scorer
        
        Args:
            config_path: Path to trust_scores.json configuration file
        """
        self.domain_scores = {}
        self.domain_categories = {}
        
        if config_path and config_path.exists():
            self._load_config(config_path)
        
        logger.info(f"DomainAuthority initialized with {len(self.domain_scores)} pre-configured domains")
    
    def _load_config(self, config_path: Path) -> None:
        """
        Load domain trust scores from configuration file
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.domain_scores = config.get('domain_scores', {})
            self.domain_categories = config.get('categories', {})
            
            logger.info(f"Loaded {len(self.domain_scores)} domain scores from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load domain authority config: {e}")
    
    def get_authority_score(self, domain: str) -> float:
        """
        Get authority score for a domain
        
        Args:
            domain: Domain name (e.g., 'uu.se')
        
        Returns:
            Authority score (0.0-1.0)
        """
        domain = domain.lower().strip()
        
        # Check if domain has pre-configured score
        if domain in self.domain_scores:
            score = self.domain_scores[domain]
            logger.debug(f"Domain {domain} has configured authority: {score}")
            return score
        
        # Calculate authority based on TLD and other factors
        score = self._calculate_default_authority(domain)
        
        logger.debug(f"Calculated default authority for {domain}: {score}")
        return score
    
    def _calculate_default_authority(self, domain: str) -> float:
        """
        Calculate default authority score based on domain characteristics
        
        Args:
            domain: Domain name
        
        Returns:
            Default authority score (0.0-1.0)
        """
        score = 0.5  # Neutral baseline
        
        # Swedish TLDs get higher trust
        if domain.endswith('.se'):
            score += 0.2
        elif domain.endswith('.nu'):
            score += 0.15
        
        # Government and education domains get high trust
        if '.gov.' in domain or domain.endswith('.gov.se'):
            score += 0.25
        elif '.edu.' in domain or 'university' in domain or 'universitet' in domain:
            score += 0.2
        elif '.ac.' in domain:
            score += 0.15
        
        # Known Swedish authorities
        swedish_authorities = [
            'riksdag', 'regeringen', 'skolverket', 'forskning',
            'scb.se', 'smhi', 'naturvardsverket', 'polisen'
        ]
        if any(auth in domain for auth in swedish_authorities):
            score += 0.15
        
        # News and media sites (moderate trust)
        news_indicators = ['news', 'nyheter', 'tidning', 'radio', 'tv']
        if any(news in domain for news in news_indicators):
            score += 0.1
        
        # Commercial sites (lower default trust)
        if '.com' in domain:
            score -= 0.1
        
        # Cap between 0 and 1
        return max(0.0, min(1.0, score))
    
    def calculate_link_based_authority(
        self,
        domain: str,
        incoming_links: List[str],
        domain_scores: Dict[str, float]
    ) -> float:
        """
        Calculate authority based on incoming links from authoritative domains
        
        Args:
            domain: Domain to calculate authority for
            incoming_links: List of domains that link to this domain
            domain_scores: Known authority scores of other domains
        
        Returns:
            Link-based authority score (0.0-1.0)
        """
        if not incoming_links:
            return 0.5
        
        # Calculate weighted average of incoming link authorities
        total_authority = 0.0
        valid_links = 0
        
        for linking_domain in incoming_links:
            linking_domain = linking_domain.lower()
            if linking_domain in domain_scores:
                total_authority += domain_scores[linking_domain]
                valid_links += 1
        
        if valid_links == 0:
            return 0.5
        
        average_authority = total_authority / valid_links
        
        # Apply diminishing returns for many links
        import math
        link_count_factor = math.log(valid_links + 1) / math.log(100)
        link_count_factor = min(1.0, link_count_factor)
        
        final_score = average_authority * link_count_factor
        
        logger.debug(f"Link-based authority for {domain}: {final_score:.3f} from {valid_links} links")
        return final_score
    
    def set_authority_score(self, domain: str, score: float) -> None:
        """
        Manually set authority score for a domain
        
        Args:
            domain: Domain name
            score: Authority score (0.0-1.0)
        """
        domain = domain.lower().strip()
        score = max(0.0, min(1.0, score))
        self.domain_scores[domain] = score
        logger.info(f"Set authority score for {domain}: {score}")
    
    def get_category(self, domain: str) -> Optional[str]:
        """
        Get category for a domain
        
        Args:
            domain: Domain name
        
        Returns:
            Category name or None
        """
        domain = domain.lower()
        return self.domain_categories.get(domain)
    
    def set_category(self, domain: str, category: str) -> None:
        """
        Set category for a domain
        
        Args:
            domain: Domain name
            category: Category name
        """
        domain = domain.lower().strip()
        self.domain_categories[domain] = category
        logger.info(f"Set category for {domain}: {category}")
    
    def get_category_boost(self, category: str, query_context: Optional[str] = None) -> float:
        """
        Get relevance boost based on domain category and query context
        
        Args:
            category: Domain category
            query_context: Query context or intent
        
        Returns:
            Category boost factor (0.8-1.2)
        """
        if not category or not query_context:
            return 1.0
        
        # Example: News sites are more relevant for news-related queries
        if 'news' in category.lower() and any(term in query_context.lower() for term in ['news', 'nyheter', 'latest']):
            return 1.2
        
        # Educational sites for research queries
        if 'education' in category.lower() and any(term in query_context.lower() for term in ['research', 'study', 'forskning']):
            return 1.15
        
        # Government for official information
        if 'government' in category.lower() and any(term in query_context.lower() for term in ['official', 'government', 'law']):
            return 1.2
        
        return 1.0
    
    def calculate_domain_age_factor(self, domain: str, registration_date: Optional[datetime] = None) -> float:
        """
        Calculate trust factor based on domain age
        
        Args:
            domain: Domain name
            registration_date: Domain registration date
        
        Returns:
            Age-based trust factor (0.5-1.0)
        """
        if not registration_date:
            # Unknown age - neutral score
            return 0.75
        
        # Calculate age in years
        age_years = (datetime.now() - registration_date).days / 365.25
        
        # Older domains generally more trustworthy
        if age_years > 10:
            return 1.0
        elif age_years > 5:
            return 0.9
        elif age_years > 2:
            return 0.8
        elif age_years > 1:
            return 0.7
        else:
            return 0.6
    
    def detect_suspicious_domains(self, domain: str) -> bool:
        """
        Detect potentially suspicious or low-quality domains
        
        Args:
            domain: Domain name to check
        
        Returns:
            True if domain appears suspicious
        """
        domain = domain.lower()
        
        # Check for excessive hyphens or numbers
        if domain.count('-') > 3 or sum(c.isdigit() for c in domain) > 5:
            logger.warning(f"Suspicious domain detected (excessive hyphens/numbers): {domain}")
            return True
        
        # Check for spam keywords
        spam_keywords = ['free', 'download', 'win', 'prize', 'click', 'buy', 'cheap']
        if any(keyword in domain for keyword in spam_keywords):
            logger.warning(f"Suspicious domain detected (spam keywords): {domain}")
            return True
        
        # Check for very long domains (often spam)
        if len(domain) > 50:
            logger.warning(f"Suspicious domain detected (too long): {domain}")
            return True
        
        return False
    
    def save_scores(self, output_path: Path) -> None:
        """
        Save domain authority scores to file
        
        Args:
            output_path: Path to save scores to
        """
        try:
            data = {
                'domain_scores': self.domain_scores,
                'categories': self.domain_categories,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.domain_scores)} domain scores to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save domain scores: {e}")
