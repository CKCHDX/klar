"""
kse_domain_manager.py - Domain List Management

Loads and manages the list of Swedish domains to crawl.
Maintains domain status, statistics, and metadata.

Domain Files:
- swedish_domains.json: Complete list of ~2,543 Swedish domains
- domain_categories.json: Domain categorization
- trust_scores.json: Domain trust/authority scores

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from kse.core import get_logger, KSEValidationException, DEFAULT_DOMAINS_PATH
from .kse_data_serializer import DataSerializer

logger = get_logger('storage')


class DomainManager:
    """Manages Swedish domains list and metadata"""
    
    def __init__(self, domains_file: Optional[Path] = None):
        """Initialize domain manager"""
        self.domains_file = Path(domains_file) if domains_file else DEFAULT_DOMAINS_PATH
        self.domains: List[str] = []
        self.domain_categories: Dict[str, str] = {}
        self.trust_scores: Dict[str, float] = {}
        self.serializer = DataSerializer()
        logger.debug(f"DomainManager initialized")
    
    def load_domains(self) -> List[str]:
        """
        Load list of Swedish domains.
        
        Returns:
            List of domain strings
            
        Raises:
            KSEValidationException: If domains file not found or invalid
        """
        try:
            if not self.domains_file.exists():
                raise FileNotFoundError(f"Domains file not found: {self.domains_file}")
            
            with open(self.domains_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both list format and dict format
            if isinstance(data, list):
                self.domains = data
            elif isinstance(data, dict) and 'domains' in data:
                self.domains = data['domains']
            else:
                raise ValueError("Invalid domains file format")
            
            logger.info(f"Loaded {len(self.domains)} domains")
            return self.domains
            
        except Exception as e:
            logger.error(f"Failed to load domains: {e}")
            raise KSEValidationException(
                'domains',
                f"Failed to load domains: {str(e)}"
            )
    
    def load_trust_scores(self, trust_file: Optional[Path] = None) -> Dict[str, float]:
        """
        Load domain trust scores.
        
        Returns:
            Dictionary of domain -> trust_score
        """
        try:
            if trust_file is None:
                trust_file = self.domains_file.parent / "trust_scores.json"
            
            if not trust_file.exists():
                logger.warning(f"Trust scores file not found: {trust_file}")
                return {}
            
            with open(trust_file, 'r', encoding='utf-8') as f:
                self.trust_scores = json.load(f)
            
            logger.info(f"Loaded trust scores for {len(self.trust_scores)} domains")
            return self.trust_scores
            
        except Exception as e:
            logger.warning(f"Failed to load trust scores: {e}")
            return {}
    
    def get_trust_score(self, domain: str, default: float = 50.0) -> float:
        """
        Get trust score for domain.
        
        Args:
            domain: Domain name
            default: Default score if not found
            
        Returns:
            Trust score (0-100)
        """
        return self.trust_scores.get(domain, default)
    
    def is_valid_domain(self, domain: str) -> bool:
        """
        Check if domain is in the Swedish domains list.
        
        Args:
            domain: Domain to check
            
        Returns:
            True if domain is valid
        """
        if not self.domains:
            self.load_domains()
        
        return domain in self.domains
    
    def get_all_domains(self) -> List[str]:
        """Get all loaded domains"""
        if not self.domains:
            self.load_domains()
        return self.domains.copy()


__all__ = ["DomainManager"]
