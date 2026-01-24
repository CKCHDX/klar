"""
API Routes

REST API endpoint definitions.
"""

from typing import Dict, Any, Callable
from kse.api.kse_api_models import (
    SearchResponse,
    ResultItem,
    SuggestionResponse,
    CacheStatsResponse,
    ErrorResponse,
    HealthResponse,
)
from kse.core import KSELogger
from datetime import datetime

logger = KSELogger.get_logger(__name__)


class APIRoutes:
    """
    API route handlers.
    """
    
    def __init__(self, search_engine):
        """
        Initialize routes.
        
        Args:
            search_engine: KSESearchEngine instance
        """
        self.engine = search_engine
        self.start_time = datetime.now()
    
    # ═══════════════════════════════════════════════════════════════════
    # SEARCH ENDPOINT
    # ═══════════════════════════════════════════════════════════════════
    
    def search(self, query: str, limit: int = 10, offset: int = 0) -> SearchResponse:
        """
        Search endpoint.
        
        GET /api/search?q=query&limit=10&offset=0
        
        Args:
            query: Search query
            limit: Results per page
            offset: Pagination offset
        
        Returns:
            SearchResponse
        """
        logger.info(f"Search request: query='{query}', limit={limit}, offset={offset}")
        
        try:
            if not query or not query.strip():
                return SearchResponse(
                    query=query,
                    total_results=0,
                    returned_results=0,
                )
            
            # Execute search
            result = self.engine.search(query, limit=limit, offset=offset)
            
            # Convert to response
            items = [
                ResultItem(
                    id=r.page_id,
                    title=r.title,
                    url=r.url,
                    description=r.description,
                    domain=r.domain,
                    score=r.score,
                    rank_position=i + offset + 1,
                )
                for i, r in enumerate(result.get('results', []))
            ]
            
            response = SearchResponse(
                query=query,
                total_results=result.get('total', 0),
                returned_results=len(items),
                results=items,
                execution_time_ms=result.get('time_ms', 0),
                from_cache=result.get('from_cache', False),
                has_more=(offset + limit) < result.get('total', 0),
                next_offset=(offset + limit) if (offset + limit) < result.get('total', 0) else None,
            )
            
            logger.info(f"Search complete: {response.total_results} total, {len(items)} returned")
            return response
        
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            return SearchResponse(
                query=query,
                total_results=0,
                returned_results=0,
            )
    
    # ═══════════════════════════════════════════════════════════════════
    # SUGGESTIONS ENDPOINT
    # ═══════════════════════════════════════════════════════════════════
    
    def get_suggestions(self, q: str, limit: int = 5) -> SuggestionResponse:
        """
        Get search suggestions.
        
        GET /api/suggestions?q=query&limit=5
        
        Args:
            q: Partial query
            limit: Number of suggestions
        
        Returns:
            SuggestionResponse
        """
        logger.debug(f"Suggestions request: q='{q}', limit={limit}")
        
        try:
            if not q or len(q) < 2:
                return SuggestionResponse(query=q, suggestions=[])
            
            suggestions = self.engine.get_suggestions(q, limit=limit)
            
            return SuggestionResponse(
                query=q,
                suggestions=suggestions,
            )
        
        except Exception as e:
            logger.error(f"Suggestions error: {e}")
            return SuggestionResponse(query=q, suggestions=[])
    
    # ═══════════════════════════════════════════════════════════════════
    # RELATED SEARCHES ENDPOINT
    # ═══════════════════════════════════════════════════════════════════
    
    def get_related(self, page_id: int, limit: int = 5) -> SuggestionResponse:
        """
        Get related searches for page.
        
        GET /api/related?id=123&limit=5
        
        Args:
            page_id: Page ID
            limit: Number of related searches
        
        Returns:
            SuggestionResponse
        """
        logger.debug(f"Related searches request: page_id={page_id}")
        
        try:
            related = self.engine.get_related(page_id, limit=limit)
            
            return SuggestionResponse(
                query=f"Related to page {page_id}",
                suggestions=related,
            )
        
        except Exception as e:
            logger.error(f"Related searches error: {e}")
            return SuggestionResponse(query="", suggestions=[])
    
    # ═══════════════════════════════════════════════════════════════════
    # CACHE STATS ENDPOINT
    # ═══════════════════════════════════════════════════════════════════
    
    def get_cache_stats(self) -> CacheStatsResponse:
        """
        Get cache statistics.
        
        GET /api/stats/cache
        
        Returns:
            CacheStatsResponse
        """
        logger.debug("Cache stats request")
        
        try:
            stats = self.engine.get_cache_stats()
            
            return CacheStatsResponse(
                entries=stats.get('entries', 0),
                max_entries=stats.get('max_entries', 1000),
                hits=stats.get('hits', 0),
                misses=stats.get('misses', 0),
                hit_rate_percent=stats.get('hit_rate_percent', 0.0),
                puts=stats.get('puts', 0),
                evictions=stats.get('evictions', 0),
                total_requests=stats.get('total_requests', 0),
            )
        
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return CacheStatsResponse(
                entries=0, max_entries=1000, hits=0, misses=0,
                hit_rate_percent=0.0, puts=0, evictions=0, total_requests=0,
            )
    
    # ═══════════════════════════════════════════════════════════════════
    # HEALTH ENDPOINT
    # ═══════════════════════════════════════════════════════════════════
    
    def health(self) -> HealthResponse:
        """
        Server health check.
        
        GET /api/health
        
        Returns:
            HealthResponse
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return HealthResponse(
            status="healthy",
            version="5.0.0",
            stage="Stage 5: API & Web Interface",
            timestamp=datetime.now().isoformat(),
            uptime_seconds=uptime,
        )
    
    # ═══════════════════════════════════════════════════════════════════
    # INDEX INFO ENDPOINT
    # ═══════════════════════════════════════════════════════════════════
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        Get index information.
        
        GET /api/info/index
        
        Returns:
            Index info dict
        """
        logger.debug("Index info request")
        
        try:
            info = self.engine.get_index_info()
            return info or {"status": "unknown"}
        
        except Exception as e:
            logger.error(f"Index info error: {e}")
            return {"status": "error", "error": str(e)}


def register_routes(app: Any, search_engine: Any) -> None:
    """
    Register API routes with Flask/FastAPI app.
    
    Args:
        app: Flask or FastAPI application
        search_engine: KSESearchEngine instance
    """
    routes = APIRoutes(search_engine)
    
    # Detect framework by checking app attributes
    is_flask = hasattr(app, 'route')
    
    if is_flask:
        # Flask routes
        register_flask_routes(app, routes)
    else:
        # FastAPI routes
        register_fastapi_routes(app, routes)


def register_flask_routes(app: Any, routes: APIRoutes) -> None:
    """
    Register Flask routes.
    """
    @app.route('/api/search', methods=['GET'])
    def search():
        from flask import request
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        response = routes.search(query, limit, offset)
        return response.to_dict()
    
    @app.route('/api/suggestions', methods=['GET'])
    def suggestions():
        from flask import request
        q = request.args.get('q', '')
        limit = request.args.get('limit', 5, type=int)
        
        response = routes.get_suggestions(q, limit)
        return response.to_dict()
    
    @app.route('/api/related', methods=['GET'])
    def related():
        from flask import request
        page_id = request.args.get('id', 0, type=int)
        limit = request.args.get('limit', 5, type=int)
        
        response = routes.get_related(page_id, limit)
        return response.to_dict()
    
    @app.route('/api/stats/cache', methods=['GET'])
    def cache_stats():
        response = routes.get_cache_stats()
        return response.to_dict()
    
    @app.route('/api/health', methods=['GET'])
    def health():
        response = routes.health()
        return response.to_dict()
    
    @app.route('/api/info/index', methods=['GET'])
    def index_info():
        return routes.get_index_info()


def register_fastapi_routes(app: Any, routes: APIRoutes) -> None:
    """
    Register FastAPI routes.
    """
    from fastapi import Query
    
    @app.get("/api/search")
    def search(
        q: str = Query(..., description="Search query"),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        response = routes.search(q, limit, offset)
        return response.to_dict()
    
    @app.get("/api/suggestions")
    def suggestions(
        q: str = Query(..., description="Partial query"),
        limit: int = Query(5, ge=1, le=20),
    ):
        response = routes.get_suggestions(q, limit)
        return response.to_dict()
    
    @app.get("/api/related")
    def related(
        id: int = Query(..., description="Page ID"),
        limit: int = Query(5, ge=1, le=20),
    ):
        response = routes.get_related(id, limit)
        return response.to_dict()
    
    @app.get("/api/stats/cache")
    def cache_stats():
        response = routes.get_cache_stats()
        return response.to_dict()
    
    @app.get("/api/health")
    def health():
        response = routes.health()
        return response.to_dict()
    
    @app.get("/api/info/index")
    def index_info():
        return routes.get_index_info()
