"""
API Data Models

Request/response models for REST API.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class SortOrder(Enum):
    """Sort order for results."""
    RELEVANCE = "relevance"
    POPULARITY = "popularity"
    RECENCY = "recency"
    NEWEST = "newest"
    OLDEST = "oldest"


@dataclass
class QueryRequest:
    """
    Search query request.
    """
    query: str
    limit: int = 10
    offset: int = 0
    sort: str = "relevance"
    lang: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


@dataclass
class ResultItem:
    """
    Single search result item.
    """
    id: int
    title: str
    url: str
    description: str
    domain: str
    score: float
    snippet: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    rank_position: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'domain': self.domain,
            'score': round(self.score, 3),
            'snippet': self.snippet,
            'keywords': self.keywords,
            'rank': self.rank_position,
        }


@dataclass
class SearchResponse:
    """
    Search query response.
    """
    query: str
    total_results: int
    returned_results: int
    results: List[ResultItem] = field(default_factory=list)
    execution_time_ms: float = 0.0
    from_cache: bool = False
    has_more: bool = False
    next_offset: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query': self.query,
            'total_results': self.total_results,
            'returned_results': self.returned_results,
            'results': [r.to_dict() for r in self.results],
            'execution_time_ms': round(self.execution_time_ms, 2),
            'from_cache': self.from_cache,
            'has_more': self.has_more,
            'next_offset': self.next_offset,
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


@dataclass
class SuggestionResponse:
    """
    Search suggestions response.
    """
    query: str
    suggestions: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query': self.query,
            'suggestions': self.suggestions,
            'execution_time_ms': round(self.execution_time_ms, 2),
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


@dataclass
class CacheStatsResponse:
    """
    Cache statistics response.
    """
    entries: int
    max_entries: int
    hits: int
    misses: int
    hit_rate_percent: float
    puts: int
    evictions: int
    total_requests: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'entries': self.entries,
            'max_entries': self.max_entries,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate_percent': round(self.hit_rate_percent, 2),
            'puts': self.puts,
            'evictions': self.evictions,
            'total_requests': self.total_requests,
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


@dataclass
class ErrorResponse:
    """
    Error response.
    """
    error: str
    code: int = 400
    details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'error': self.error,
            'code': self.code,
        }
        if self.details:
            data['details'] = self.details
        return data
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())


@dataclass
class HealthResponse:
    """
    Server health response.
    """
    status: str = "healthy"
    version: str = "5.0.0"
    stage: str = "Stage 5: API & Web Interface"
    timestamp: str = ""
    uptime_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'status': self.status,
            'version': self.version,
            'stage': self.stage,
            'timestamp': self.timestamp,
            'uptime_seconds': self.uptime_seconds,
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())
