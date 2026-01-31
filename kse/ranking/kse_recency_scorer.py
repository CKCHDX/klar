"""
Recency Scorer - Factor 4: Content freshness and recency scoring
Prioritizes newer content for time-sensitive queries
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RecencyScorer:
    """Content recency scoring system"""
    
    def __init__(self, max_age_days: int = 365):
        """
        Initialize recency scorer
        
        Args:
            max_age_days: Maximum age in days for full decay (default: 365)
        """
        self.max_age_days = max_age_days
        logger.info(f"RecencyScorer initialized (max_age={max_age_days} days)")
    
    def calculate_recency_score(
        self,
        document: Dict[str, Any],
        query_intent: Optional[str] = None
    ) -> float:
        """
        Calculate recency score for a document
        
        Args:
            document: Document with timestamp metadata
            query_intent: Optional query intent ('news', 'current', 'recent', etc.)
        
        Returns:
            Recency score (0.0-1.0)
        """
        # Get timestamp from document
        timestamp = self._extract_timestamp(document)
        
        if not timestamp:
            # No timestamp - return neutral score
            return 0.5
        
        # Calculate age in days
        age_days = (datetime.now() - timestamp).days
        
        # Calculate base recency score
        score = self._calculate_decay_score(age_days)
        
        # Apply query intent boost
        if query_intent:
            score = self._apply_intent_boost(score, age_days, query_intent)
        
        logger.debug(f"Recency score for doc (age={age_days}d): {score:.3f}")
        return score
    
    def _extract_timestamp(self, document: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract timestamp from document metadata
        
        Args:
            document: Document with metadata
        
        Returns:
            Datetime object or None
        """
        # Try various timestamp fields
        for field in ['last_modified', 'published_date', 'crawl_date', 'timestamp']:
            if field in document:
                timestamp = document[field]
                
                # Handle different timestamp formats
                if isinstance(timestamp, datetime):
                    return timestamp
                elif isinstance(timestamp, str):
                    try:
                        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except Exception as e:
                        logger.warning(f"Failed to parse timestamp: {timestamp}")
                elif isinstance(timestamp, (int, float)):
                    try:
                        return datetime.fromtimestamp(timestamp)
                    except Exception as e:
                        logger.warning(f"Failed to parse timestamp: {timestamp}")
        
        return None
    
    def _calculate_decay_score(self, age_days: int) -> float:
        """
        Calculate recency score with exponential decay
        
        Args:
            age_days: Age of content in days
        
        Returns:
            Decay score (0.0-1.0)
        """
        import math
        
        if age_days < 0:
            age_days = 0
        
        # Exponential decay function
        # Score = e^(-age / max_age)
        decay_rate = age_days / self.max_age_days
        score = math.exp(-decay_rate)
        
        return max(0.0, min(1.0, score))
    
    def _apply_intent_boost(self, base_score: float, age_days: int, query_intent: str) -> float:
        """
        Apply query intent-based boost to recency score
        
        Args:
            base_score: Base recency score
            age_days: Age in days
            query_intent: Query intent
        
        Returns:
            Adjusted recency score
        """
        intent = query_intent.lower()
        
        # Very recent content boost for news/current queries
        if intent in ['news', 'nyheter', 'current', 'latest', 'senaste']:
            if age_days <= 1:
                return min(1.0, base_score * 1.5)
            elif age_days <= 7:
                return min(1.0, base_score * 1.3)
            elif age_days <= 30:
                return min(1.0, base_score * 1.1)
        
        # Recent content boost for trends/events
        elif intent in ['trend', 'event', 'händelse']:
            if age_days <= 7:
                return min(1.0, base_score * 1.4)
            elif age_days <= 30:
                return min(1.0, base_score * 1.2)
        
        # Moderate recency for general queries
        elif intent in ['recent', 'ny', 'new']:
            if age_days <= 30:
                return min(1.0, base_score * 1.2)
            elif age_days <= 90:
                return min(1.0, base_score * 1.1)
        
        # Historical queries - older content may be more valuable
        elif intent in ['history', 'historia', 'historical']:
            if age_days > 365:
                return min(1.0, base_score * 1.2)
        
        return base_score
    
    def detect_query_intent(self, query: str) -> Optional[str]:
        """
        Detect if query has recency intent
        
        Args:
            query: Search query
        
        Returns:
            Intent string or None
        """
        query_lower = query.lower()
        
        # News/current events intent
        news_keywords = [
            'nyheter', 'news', 'latest', 'senaste', 'idag', 'today',
            'nu', 'now', 'aktuellt', 'current'
        ]
        if any(kw in query_lower for kw in news_keywords):
            return 'news'
        
        # Recent/new intent
        recent_keywords = ['ny', 'new', 'recent', 'nyligen', 'recently']
        if any(kw in query_lower for kw in recent_keywords):
            return 'recent'
        
        # Trend/event intent
        trend_keywords = ['trend', 'event', 'händelse', 'what happened']
        if any(kw in query_lower for kw in trend_keywords):
            return 'trend'
        
        # Historical intent
        history_keywords = ['history', 'historia', 'historical', 'tidigare']
        if any(kw in query_lower for kw in history_keywords):
            return 'history'
        
        return None
    
    def calculate_update_frequency_score(self, document: Dict[str, Any]) -> float:
        """
        Score based on how frequently content is updated
        
        Args:
            document: Document with update history
        
        Returns:
            Update frequency score (0.0-1.0)
        """
        update_history = document.get('update_history', [])
        
        if not update_history or len(update_history) < 2:
            return 0.5
        
        # Calculate average time between updates
        timestamps = sorted(update_history)
        intervals = []
        
        for i in range(1, len(timestamps)):
            if isinstance(timestamps[i], datetime) and isinstance(timestamps[i-1], datetime):
                interval = (timestamps[i] - timestamps[i-1]).days
                intervals.append(interval)
        
        if not intervals:
            return 0.5
        
        avg_interval = sum(intervals) / len(intervals)
        
        # More frequent updates = higher score
        if avg_interval <= 1:  # Daily updates
            return 1.0
        elif avg_interval <= 7:  # Weekly updates
            return 0.9
        elif avg_interval <= 30:  # Monthly updates
            return 0.7
        elif avg_interval <= 90:  # Quarterly updates
            return 0.5
        else:
            return 0.3
    
    def calculate_staleness_penalty(self, age_days: int, content_type: str) -> float:
        """
        Apply penalty for stale content based on content type
        
        Args:
            age_days: Age in days
            content_type: Type of content ('news', 'reference', 'guide', etc.)
        
        Returns:
            Staleness penalty factor (0.5-1.0)
        """
        content_type = content_type.lower()
        
        # News becomes stale quickly
        if content_type == 'news':
            if age_days > 7:
                return 0.5
            elif age_days > 3:
                return 0.7
            elif age_days > 1:
                return 0.9
        
        # Technical documentation has moderate staleness
        elif content_type in ['documentation', 'guide', 'tutorial']:
            if age_days > 730:  # 2 years
                return 0.6
            elif age_days > 365:  # 1 year
                return 0.8
        
        # Reference content ages slowly
        elif content_type == 'reference':
            if age_days > 1825:  # 5 years
                return 0.7
            elif age_days > 1095:  # 3 years
                return 0.9
        
        return 1.0  # No penalty
    
    def get_time_range_relevance(
        self,
        document_date: datetime,
        query_time_range: Optional[tuple] = None
    ) -> float:
        """
        Calculate relevance for time-range queries
        
        Args:
            document_date: Document timestamp
            query_time_range: (start_date, end_date) tuple or None
        
        Returns:
            Time range relevance score (0.0-1.0)
        """
        if not query_time_range:
            return 1.0
        
        start_date, end_date = query_time_range
        
        # Check if document is within time range
        if start_date <= document_date <= end_date:
            return 1.0
        
        # Calculate distance from time range
        if document_date < start_date:
            days_before = (start_date - document_date).days
            # Gradual decay for content before range
            if days_before <= 30:
                return 0.8
            elif days_before <= 90:
                return 0.6
            elif days_before <= 365:
                return 0.4
            else:
                return 0.2
        else:  # document_date > end_date
            days_after = (document_date - end_date).days
            # Gradual decay for content after range
            if days_after <= 30:
                return 0.8
            elif days_after <= 90:
                return 0.6
            else:
                return 0.3
