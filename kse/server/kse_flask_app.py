"""
KSE Flask Web Application

Main Flask application for the Klar Search Engine web interface.
Provides REST API endpoints and web UI for search functionality.
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

from kse.core import KSELogger
from kse.search import SearchEngine
from kse.database import KSEDatabase

logger = KSELogger.get_logger(__name__)


class KSEFlaskApp:
    """Main Flask application wrapper for KSE."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Flask application.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.app = Flask(__name__,
                        template_folder=self._get_template_folder(),
                        static_folder=self._get_static_folder())
        
        # Configure Flask
        self._configure_app()
        
        # Initialize components
        self.db = None
        self.search_engine = None
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        self.cache = Cache(self.app, config={'CACHE_TYPE': 'simple'})
        
        # Enable CORS
        CORS(self.app)
        
        # Register routes
        self._register_routes()
        
        logger.info("KSE Flask application initialized")
    
    def _configure_app(self):
        """Configure Flask application settings."""
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
        self.app.config['SESSION_COOKIE_SECURE'] = True
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
        self.app.config['JSON_SORT_KEYS'] = False
    
    def _get_template_folder(self) -> str:
        """Get template folder path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(os.path.dirname(current_dir), 'templates')
    
    def _get_static_folder(self) -> str:
        """Get static folder path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(os.path.dirname(current_dir), 'static')
    
    def _require_json(self, f):
        """Decorator to require JSON content type."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            return f(*args, **kwargs)
        return decorated_function
    
    def _register_routes(self):
        """Register all application routes."""
        
        # Health check
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        
        # Home page
        @self.app.route('/', methods=['GET'])
        def index():
            """Home page."""
            try:
                stats = self.search_engine.get_statistics() if self.search_engine else {}
                return render_template('index.html', stats=stats)
            except Exception as e:
                logger.error(f"Error rendering home page: {e}")
                return render_template('error.html', error="Failed to load home page"), 500
        
        # Search API
        @self.app.route('/api/search', methods=['GET', 'POST'])
        @self.limiter.limit("30 per minute")
        @self.cache.cached(timeout=300, query_string=True)
        def search():
            """Search endpoint."""
            try:
                # Get query
                query = request.args.get('q') or request.json.get('q') if request.is_json else None
                
                if not query:
                    return jsonify({'error': 'Query required'}), 400
                
                if len(query) < 2:
                    return jsonify({'error': 'Query too short (minimum 2 characters)'}), 400
                
                if len(query) > 500:
                    return jsonify({'error': 'Query too long (maximum 500 characters)'}), 400
                
                # Get parameters
                limit = int(request.args.get('limit', 10))
                offset = int(request.args.get('offset', 0))
                
                # Validate parameters
                limit = max(1, min(limit, 100))  # 1-100 results
                offset = max(0, offset)
                
                # Execute search
                start_time = datetime.now()
                results, stats = self.search_engine.search(
                    query,
                    limit=limit,
                    offset=offset,
                    explain=True
                )
                search_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Format results
                formatted_results = [
                    {
                        'rank': i + 1,
                        'url': result.get('url'),
                        'title': result.get('title'),
                        'snippet': result.get('snippet'),
                        'score': round(result.get('score', 0), 4),
                        'domain': self._extract_domain(result.get('url', '')),
                        'last_updated': result.get('last_updated'),
                    }
                    for i, result in enumerate(results)
                ]
                
                return jsonify({
                    'query': query,
                    'total_results': stats.get('total_matches', 0),
                    'results_returned': len(formatted_results),
                    'limit': limit,
                    'offset': offset,
                    'search_time_ms': search_time,
                    'results': formatted_results,
                    'facets': stats.get('facets', {}),
                })
            
            except Exception as e:
                logger.error(f"Search error: {e}")
                return jsonify({'error': str(e)}), 500
        
        # Search page
        @self.app.route('/search', methods=['GET'])
        def search_page():
            """Search results page."""
            try:
                query = request.args.get('q')
                page = int(request.args.get('page', 1))
                
                if not query:
                    return redirect(url_for('index'))
                
                limit = 10
                offset = (page - 1) * limit
                
                results, stats = self.search_engine.search(
                    query,
                    limit=limit,
                    offset=offset
                )
                
                total_results = stats.get('total_matches', 0)
                total_pages = (total_results + limit - 1) // limit
                
                return render_template('search_results.html',
                                     query=query,
                                     results=results,
                                     page=page,
                                     total_pages=total_pages,
                                     total_results=total_results,
                                     search_time=stats.get('search_time_ms', 0))
            
            except Exception as e:
                logger.error(f"Search page error: {e}")
                return render_template('error.html', error="Search failed"), 500
        
        # API: Statistics
        @self.app.route('/api/stats', methods=['GET'])
        @self.cache.cached(timeout=60)
        def get_stats():
            """Get system statistics."""
            try:
                stats = self.search_engine.get_statistics()
                return jsonify(stats)
            except Exception as e:
                logger.error(f"Stats error: {e}")
                return jsonify({'error': str(e)}), 500
        
        # API: Autocomplete
        @self.app.route('/api/autocomplete', methods=['GET'])
        @self.limiter.limit("60 per minute")
        @self.cache.cached(timeout=3600, query_string=True)
        def autocomplete():
            """Search autocomplete endpoint."""
            try:
                query = request.args.get('q', '')
                
                if len(query) < 1:
                    return jsonify({'suggestions': []})
                
                suggestions = self.search_engine.get_autocomplete_suggestions(query, limit=10)
                
                return jsonify({
                    'query': query,
                    'suggestions': suggestions
                })
            
            except Exception as e:
                logger.error(f"Autocomplete error: {e}")
                return jsonify({'suggestions': []})
        
        # API: Similar
        @self.app.route('/api/similar/<path:url>', methods=['GET'])
        @self.cache.cached(timeout=3600, query_string=True)
        def get_similar(url):
            """Get similar pages."""
            try:
                similar = self.search_engine.get_similar_pages(url, limit=5)
                return jsonify({'similar_pages': similar})
            except Exception as e:
                logger.error(f"Similar pages error: {e}")
                return jsonify({'similar_pages': []})
        
        # 404 handler
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            return render_template('404.html'), 404
        
        # 500 handler
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            logger.error(f"Internal server error: {error}")
            return render_template('500.html'), 500
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url
    
    def init_database(self, db: KSEDatabase):
        """Initialize database connection."""
        self.db = db
        logger.info("Database initialized")
    
    def init_search_engine(self, search_engine: SearchEngine):
        """Initialize search engine."""
        self.search_engine = search_engine
        logger.info("Search engine initialized")
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run Flask application."""
        logger.info(f"Starting Flask app on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)
    
    def get_app(self):
        """Get Flask application object."""
        return self.app


def create_app(db: Optional[KSEDatabase] = None, 
               search_engine: Optional[SearchEngine] = None) -> Flask:
    """
    Factory function to create Flask app.
    
    Args:
        db: Optional database connection
        search_engine: Optional search engine instance
        
    Returns:
        Configured Flask application
    """
    kse_app = KSEFlaskApp()
    
    if db:
        kse_app.init_database(db)
    
    if search_engine:
        kse_app.init_search_engine(search_engine)
    
    return kse_app.get_app()


if __name__ == '__main__':
    # Simple test run
    app = KSEFlaskApp()
    app.run(debug=True)
