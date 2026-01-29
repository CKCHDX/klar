"""
Link Structure - Factor 6: Link structure and anchor text analysis
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class LinkStructure:
    """Link structure analyzer"""
    
    def __init__(self):
        logger.info("LinkStructure initialized")
    
    def calculate_link_score(self, document: Dict[str, Any]) -> float:
        """
        Calculate link structure score
        
        Args:
            document: Document with link metadata
        
        Returns:
            Link score (0.0-1.0)
        """
        inbound_count = document.get('inbound_links', 0)
        outbound_count = document.get('outbound_links', 0)
        
        # Balanced link profile scores higher
        if inbound_count == 0:
            return 0.3
        
        # Ideal ratio is 1:2 to 1:3 (inbound:outbound)
        ratio = outbound_count / max(inbound_count, 1)
        
        if 2.0 <= ratio <= 3.0:
            score = 1.0
        elif 1.0 <= ratio < 2.0:
            score = 0.8
        elif 3.0 < ratio <= 5.0:
            score = 0.7
        else:
            score = 0.5
        
        # Boost for more inbound links
        import math
        inbound_factor = math.log(inbound_count + 1) / math.log(100)
        score *= (0.7 + 0.3 * min(1.0, inbound_factor))
        
        return min(1.0, score)
