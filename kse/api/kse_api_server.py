"""
API Server

REST API server implementation using Flask.
"""

from flask import Flask, jsonify, request as flask_request
from typing import Optional
import json

from kse.api.kse_api_routes import APIRoutes
from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class KSEAPIServer:
    """
    Klar Search Engine REST API Server.
    
    Features:
    - RESTful API endpoints
    - JSON responses
    - Error handling
    - CORS support
    - Health checks
    - Analytics endpoints
    """
    
    def __init__(
        self,
        search_engine,
        host: str = "0.0.0.0",
        port: int = 5000,
        debug: bool = False,
    ):
        """
        Initialize API server.
        
        Args:
            search_engine: KSESearchEngine instance
            host: Server host
            port: Server port
            debug: Debug mode
        """
        self.engine = search_engine
        self.host = host
        self.port = port
        self.debug = debug
        
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['JSON_SORT_KEYS'] = False
        
        # Initialize routes
        self.routes = APIRoutes(search_engine)
        
        # Register error handlers
        self._register_error_handlers()
        
        # Register API endpoints
        self._register_endpoints()
        
        # Enable CORS
        self._setup_cors()
        
        logger.info(f"API Server initialized on {host}:{port}")
    
    def _register_error_handlers(self):
        """
        Register error handlers.
        """
        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'error': 'Bad Request',
                'code': 400,
                'message': str(error),
            }), 400
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Not Found',
                'code': 404,
                'message': 'Endpoint not found',
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal error: {error}", exc_info=True)
            return jsonify({
                'error': 'Internal Server Error',
                'code': 500,
                'message': 'An error occurred',
            }), 500
    
    def _register_endpoints(self):
        """
        Register API endpoints.
        """
        # Search endpoint
        @self.app.route('/api/search', methods=['GET'])
        def search():
            query = flask_request.args.get('q', '')
            limit = flask_request.args.get('limit', 10, type=int)
            offset = flask_request.args.get('offset', 0, type=int)
            
            if not query:
                return jsonify({'error': 'Query parameter required'}), 400
            
            response = self.routes.search(query, limit, offset)
            return jsonify(response.to_dict())
        
        # Suggestions endpoint
        @self.app.route('/api/suggestions', methods=['GET'])
        def suggestions():
            q = flask_request.args.get('q', '')
            limit = flask_request.args.get('limit', 5, type=int)
            
            if not q:
                return jsonify({'error': 'Query parameter required'}), 400
            
            response = self.routes.get_suggestions(q, limit)
            return jsonify(response.to_dict())
        
        # Related searches endpoint
        @self.app.route('/api/related', methods=['GET'])
        def related():
            page_id = flask_request.args.get('id', type=int)
            limit = flask_request.args.get('limit', 5, type=int)
            
            if page_id is None:
                return jsonify({'error': 'ID parameter required'}), 400
            
            response = self.routes.get_related(page_id, limit)
            return jsonify(response.to_dict())
        
        # Cache stats endpoint
        @self.app.route('/api/stats/cache', methods=['GET'])
        def cache_stats():
            response = self.routes.get_cache_stats()
            return jsonify(response.to_dict())
        
        # Health check endpoint
        @self.app.route('/api/health', methods=['GET'])
        def health():
            response = self.routes.health()
            return jsonify(response.to_dict())
        
        # Index info endpoint
        @self.app.route('/api/info/index', methods=['GET'])
        def index_info():
            return jsonify(self.routes.get_index_info())
        
        # Root endpoint
        @self.app.route('/api', methods=['GET'])
        def root():
            return jsonify({
                'service': 'Klar Search Engine',
                'version': '5.0.0',
                'stage': 'Stage 5: API & Web Interface',
                'endpoints': {
                    'search': 'GET /api/search?q=query&limit=10&offset=0',
                    'suggestions': 'GET /api/suggestions?q=query&limit=5',
                    'related': 'GET /api/related?id=page_id&limit=5',
                    'cache_stats': 'GET /api/stats/cache',
                    'health': 'GET /api/health',
                    'index_info': 'GET /api/info/index',
                },
            })
        
        logger.info("API endpoints registered")
    
    def _setup_cors(self):
        """
        Setup CORS support.
        """
        try:
            from flask_cors import CORS
            CORS(self.app, resources={r"/api/*": {"origins": "*"}})
            logger.info("CORS enabled")
        except ImportError:
            logger.warning("flask-cors not installed, CORS disabled")
            # Manual CORS headers
            @self.app.after_request
            def after_request(response):
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
                return response
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Run API server.
        
        Args:
            host: Server host (default: self.host)
            port: Server port (default: self.port)
        """
        host = host or self.host
        port = port or self.port
        
        logger.info(f"Starting API server on {host}:{port}")
        
        try:
            self.app.run(
                host=host,
                port=port,
                debug=self.debug,
                use_reloader=False,  # Disable reloader for threading
            )
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
    
    def get_app(self):
        """
        Get Flask app for testing or deployment.
        
        Returns:
            Flask app instance
        """
        return self.app


class KSESearchEngine:
    """
    Complete search engine combining all stages.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize search engine.
        
        Args:
            db_path: Path to database
        """
        from kse.database import Repository
        from kse.search import (
            QueryParser,
            Ranker,
            SearchExecutor,
            SearchCache,
        )
        
        self.db = Repository(db_path)
        self.cache = SearchCache(max_entries=5000)
        self.executor = SearchExecutor(
            db_repository=self.db,
            query_parser=QueryParser(),
            ranker=Ranker(),
        )
        
        logger.info(f"Search engine initialized with database: {db_path}")
    
    def search(self, query: str, limit: int = 10, offset: int = 0) -> dict:
        """
        Execute search with caching.
        
        Args:
            query: Search query
            limit: Results per page
            offset: Pagination offset
        
        Returns:
            Search results dict
        """
        # Check cache
        cached = self.cache.get(query)
        if cached:
            return {
                'results': cached.results,
                'total': cached.total_results,
                'time_ms': 0,
                'from_cache': True,
            }
        
        # Execute search
        results = self.executor.search(query, limit=limit, offset=offset)
        
        # Cache results
        if results.total_results > 0:
            self.cache.put(query, results)
        
        return {
            'results': results.results,
            'total': results.total_results,
            'time_ms': results.execution_time_ms,
            'from_cache': False,
        }
    
    def get_suggestions(self, q: str, limit: int = 5) -> list:
        """
        Get search suggestions.
        
        Args:
            q: Partial query
            limit: Number of suggestions
        
        Returns:
            List of suggestions
        """
        return self.executor.get_suggestions(q, limit=limit)
    
    def get_related(self, page_id: int, limit: int = 5) -> list:
        """
        Get related searches.
        
        Args:
            page_id: Page ID
            limit: Number of related
        
        Returns:
            List of related searches
        """
        return self.executor.get_related_searches(page_id, limit=limit)
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Cache stats dict
        """
        return self.cache.get_statistics()
    
    def get_index_info(self) -> dict:
        """
        Get index information.
        
        Returns:
            Index info dict
        """
        try:
            info = self.db.get_index_stats()
            return info or {'status': 'unknown'}
        except:
            return {'status': 'unavailable'}
