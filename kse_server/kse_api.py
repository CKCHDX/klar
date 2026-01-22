"""
KSE REST API Server
Flask-based production API for search engine.

Endpoints:
  GET  /api/search          - Search query
  GET  /api/suggest         - Autocomplete suggestions
  GET  /api/health          - Health check
  POST /api/admin/crawl     - Trigger crawl
  GET  /api/admin/stats     - Server statistics
"""

import logging
import json
from typing import Dict, Tuple
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from kse.kse_search import SearchEngine, SearchResponse
from kse.kse_ranking import RankingEngine
from kse.kse_index import InvertedIndex
from kse.kse_database import PostgreSQLManager, DatabaseConfig
from kse.kse_cache import CacheManager


logger = logging.getLogger(__name__)


def create_app(config: Dict = None) -> Flask:
    """
    Create Flask application with all middleware and routes.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "max_age": 3600
        }
    })
    
    # Initialize components
    app.db = PostgreSQLManager(DatabaseConfig())
    app.cache = CacheManager()
    app.index = InvertedIndex()
    app.ranking = RankingEngine()
    app.search_engine = SearchEngine(app.index, app.ranking)
    
    # Request tracking
    app.request_count = 0
    app.start_time = datetime.now()
    
    # Rate limiting
    app.rate_limit = {}  # Client IP -> (requests, last_reset_time)
    app.max_requests_per_minute = 100
    
    # Register routes
    register_routes(app)
    register_error_handlers(app)
    
    logger.info("Flask application created successfully")
    return app


def rate_limit(f):
    """
    Decorator to enforce rate limiting.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        now = datetime.now()
        
        if client_ip not in flask.current_app.rate_limit:
            flask.current_app.rate_limit[client_ip] = (0, now)
        
        count, reset_time = flask.current_app.rate_limit[client_ip]
        
        if (now - reset_time).total_seconds() > 60:
            flask.current_app.rate_limit[client_ip] = (1, now)
        else:
            if count >= flask.current_app.max_requests_per_minute:
                return jsonify({"error": "Rate limit exceeded"}), 429
            flask.current_app.rate_limit[client_ip] = (count + 1, reset_time)
        
        return f(*args, **kwargs)
    
    return decorated_function


def register_routes(app: Flask):
    """
    Register all API routes.
    """
    
    @app.route('/api/search', methods=['GET', 'POST'])
    @rate_limit
    def search():
        """
        Search endpoint.
        
        Query parameters:
            q: Search query (required)
            limit: Results to return (default 10, max 100)
            
        Returns:
            JSON with search results
            
        Example:
            GET /api/search?q=restauranger+stockholm&limit=10
        """
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        # Validation
        if not query:
            return jsonify({"error": "Missing query parameter 'q'"}), 400
        
        if len(query) > 500:
            return jsonify({"error": "Query too long (max 500 characters)"}), 400
        
        if limit < 1 or limit > 100:
            limit = 10
        
        try:
            # Execute search
            response = app.search_engine.search(query, limit=limit)
            
            # Format response
            results_data = [
                {
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                    "score": round(r.score, 3),
                    "domain_trust": round(r.domain_trust, 2),
                    "type": r.result_type,
                }
                for r in response.results
            ]
            
            return jsonify({
                "query": query,
                "results": results_data,
                "total_results": response.total_results,
                "search_time_ms": round(response.search_time_ms, 1),
                "intent": response.intent,
            }), 200
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    @app.route('/api/suggest', methods=['GET'])
    @rate_limit
    def suggest():
        """
        Autocomplete suggestions endpoint.
        
        Query parameters:
            q: Query prefix (minimum 2 characters)
            
        Returns:
            JSON with suggestions
        """
        prefix = request.args.get('q', '').strip()
        
        if len(prefix) < 2:
            return jsonify({"suggestions": []}), 200
        
        try:
            suggestions = app.search_engine.search_suggestions(prefix)
            return jsonify({"suggestions": suggestions}), 200
        except Exception as e:
            logger.error(f"Suggestion error: {e}")
            return jsonify({"suggestions": []}), 200
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """
        Health check endpoint.
        
        Returns:
            JSON with server status
        """
        uptime = (datetime.now() - app.start_time).total_seconds()
        
        cache_stats = app.cache.get_statistics()
        db_stats = app.db.get_statistics()
        
        return jsonify({
            "status": "healthy",
            "uptime_seconds": uptime,
            "requests_handled": app.request_count,
            "cache": cache_stats,
            "database": db_stats,
            "timestamp": datetime.now().isoformat(),
        }), 200
    
    @app.route('/api/admin/stats', methods=['GET'])
    def admin_stats():
        """
        Administrative statistics.
        
        Returns:
            Detailed server statistics
        """
        return jsonify({
            "cache": app.cache.get_statistics(),
            "database": app.db.get_statistics(),
            "index": app.index.get_statistics(),
            "server": {
                "uptime_seconds": (datetime.now() - app.start_time).total_seconds(),
                "requests_handled": app.request_count,
                "start_time": app.start_time.isoformat(),
            },
        }), 200


def register_error_handlers(app: Flask):
    """
    Register error handlers.
    """
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"error": str(e)}), e.code


if __name__ == "__main__":
    # Development server
    import flask
    
    app = create_app()
    
    logger.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run development server
    print("Starting Klar Search Engine API on http://127.0.0.1:8080")
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=True)
