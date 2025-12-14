"""
THOR 1.0 - Trusted Host Ranking
Authority and ranking system for Swedish sites
"""
import json
from typing import List, Dict
import numpy as np
from datetime import datetime

class THOR:
    def __init__(self):
        # Domain authority scores (0-100)
        self.domain_authority = {
            'svt.se': 95,
            'dn.se': 90,
            'aftonbladet.se': 88,
            'expressen.se': 87,
            'svd.se': 85,
            'regeringen.se': 95,
            'skatteverket.se': 93,
            'polisen.se': 92,
            'forsakringskassan.se': 90,
            'kth.se': 88,
            'uu.se': 87,
            'lu.se': 86,
            'su.se': 85,
            'stockholm.se': 82,
            'ikea.com': 90,
            'spotify.com': 92,
            'blocket.se': 80
        }
        
        print("[THOR] Initialized ranking system")
    
    def get_domain_authority(self, url: str) -> int:
        """Get authority score for domain"""
        for domain, score in self.domain_authority.items():
            if domain in url:
                return score
        return 50  # Default for unknown domains
    
    def calculate_page_rank(self, result: Dict, query_embedding: np.ndarray) -> float:
        """
        Calculate comprehensive page rank
        Combines multiple factors:
        - Domain authority
        - Content relevance
        - Freshness
        - User engagement signals
        """
        score = 0.0
        
        # Factor 1: Domain Authority (40%)
        domain_score = self.get_domain_authority(result.get('url', '')) / 100
        score += domain_score * 0.4
        
        # Factor 2: Content Relevance (35%)
        relevance = result.get('relevance_score', 0.5)
        score += relevance * 0.35
        
        # Factor 3: Freshness (15%)
        freshness = self._calculate_freshness(result.get('timestamp'))
        score += freshness * 0.15
        
        # Factor 4: Content Quality (10%)
        quality = self._assess_quality(result)
        score += quality * 0.10
        
        return score
    
    def _calculate_freshness(self, timestamp) -> float:
        """Calculate content freshness score"""
        if not timestamp:
            return 0.5
        
        try:
            # Newer content scores higher
            now = datetime.now()
            age_days = (now - timestamp).days
            
            if age_days < 1:
                return 1.0
            elif age_days < 7:
                return 0.9
            elif age_days < 30:
                return 0.7
            elif age_days < 90:
                return 0.5
            else:
                return 0.3
        except:
            return 0.5
    
    def _assess_quality(self, result: Dict) -> float:
        """Assess content quality"""
        quality = 0.5
        
        # Has title
        if result.get('title'):
            quality += 0.2
        
        # Has description
        if result.get('description'):
            quality += 0.15
        
        # Has substantial content
        content_length = len(result.get('content', ''))
        if content_length > 500:
            quality += 0.15
        
        return min(quality, 1.0)
    
    def rank(self, results: List[Dict], query_embedding: np.ndarray) -> List[Dict]:
        """Rank results using THOR algorithm"""
        for result in results:
            result['thor_score'] = self.calculate_page_rank(result, query_embedding)
        
        # Sort by score descending
        ranked = sorted(results, key=lambda x: x.get('thor_score', 0), reverse=True)
        
        return ranked