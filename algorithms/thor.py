"""
THOR - Authority-Based Ranking Algorithm
Rank search results by domain authority, relevance, and freshness
"""

from typing import List, Dict, Tuple
from datetime import datetime


class THOR:
    """Result ranking based on domain authority and relevance"""
    
    def __init__(self):
        # Pre-defined authority scores for trusted domains
        self.domain_authority = {
            'svt.se': 0.95,
            'dn.se': 0.93,
            'aftonbladet.se': 0.92,
            'expressen.se': 0.91,
            'bbc.com': 0.94,
            'wikipedia.org': 0.96,
            'smhi.se': 0.97,  # Weather authority
        }
    
    def calculate_authority_score(self, domain: str) -> float:
        """Calculate domain authority score (0-1)"""
        domain_clean = domain.replace('www.', '')
        return self.domain_authority.get(domain_clean, 0.6)
    
    def calculate_relevance_score(self, result: Dict, query: str) -> float:
        """Calculate query relevance score (0-1)"""
        score = 0.0
        content = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
        query_lower = query.lower()
        
        # Exact match boost
        if query_lower in content:
            score += 0.5
        
        # Partial matches
        words = query_lower.split()
        matches = sum(1 for word in words if word in content)
        score += (matches / len(words)) * 0.5 if words else 0
        
        return min(score, 1.0)
    
    def calculate_freshness_score(self, result: Dict) -> float:
        """Calculate content freshness score (0-1)"""
        try:
            date_str = result.get('date')
            if not date_str:
                return 0.7  # Default if no date
            
            # Assume ISO format date
            result_date = datetime.fromisoformat(date_str)
            days_old = (datetime.now() - result_date).days
            
            if days_old == 0:
                return 1.0
            elif days_old <= 7:
                return 0.9
            elif days_old <= 30:
                return 0.7
            elif days_old <= 365:
                return 0.5
            else:
                return 0.3
        except:
            return 0.7
    
    def rank_results(self, results: List[Dict], query: str, category: str = None) -> List[Dict]:
        """
        Rank results by:
        1. Domain authority (40%)
        2. Query relevance (40%)
        3. Position bonus (10%)
        4. Freshness (10%)
        """
        scored = []
        
        for idx, result in enumerate(results):
            # Calculate individual scores
            authority = self.calculate_authority_score(result.get('domain', ''))
            relevance = self.calculate_relevance_score(result, query)
            position_bonus = (1.0 / (idx + 1)) * 0.15
            freshness = self.calculate_freshness_score(result)
            
            # Category boost
            category_boost = 0
            if category and category in result.get('snippet', '').lower():
                category_boost = 0.1
            
            # Weighted final score
            final_score = (
                authority * 0.40 +
                relevance * 0.40 +
                position_bonus +
                freshness * 0.10 +
                category_boost
            )
            
            scored.append((result, final_score))
        
        # Sort by score descending
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)
        return [r for r, _ in ranked]
    
    def boost_subpage_results(self, results: List[Dict], category: str) -> List[Dict]:
        """Boost results from category-specific subpages"""
        subpage_patterns = {
            'news': ['/nyheter', '/senaste', '/breaking'],
            'weather': ['/vader', '/väder', '/prognos'],
            'jobs': ['/jobs', '/jobb', '/lediga'],
            'food': ['/mat', '/recept', '/matlagning'],
        }
        
        patterns = subpage_patterns.get(category, [])
        
        for result in results:
            url = result.get('url', '').lower()
            if any(pattern in url for pattern in patterns):
                result['_boost'] = 0.2  # Add boost factor
        
        return results
