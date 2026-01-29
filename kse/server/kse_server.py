"""
KSE Server - Main Flask REST API server
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
from kse.core.kse_config import get_config
from kse.core.kse_logger import KSELogger, get_logger
from kse.storage.kse_storage_manager import StorageManager
from kse.nlp.kse_nlp_core import NLPCore
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.search.kse_search_pipeline import SearchPipeline

logger = None
app = None
search_pipeline = None


def create_app():
    """Create Flask application"""
    global app, search_pipeline, logger
    
    # Initialize Flask
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    
    # Setup logging
    log_dir = Path(config.get("log_dir"))
    KSELogger.setup(log_dir, config.get("log_level", "INFO"), True)
    logger = get_logger(__name__, "server.log")
    
    # Enable CORS
    if config.get("server.enable_cors", True):
        CORS(app)
    
    # Initialize components
    data_dir = Path(config.get("data_dir"))
    storage_manager = StorageManager(data_dir)
    nlp_core = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
    indexer = IndexerPipeline(storage_manager, nlp_core)
    search_pipeline = SearchPipeline(indexer, nlp_core)
    
    logger.info("KSE Server initialized")
    
    # Register routes
    register_routes()
    
    return app


def register_routes():
    """Register API routes"""
    
    @app.route('/api/search', methods=['GET'])
    def search():
        """Search endpoint"""
        query = request.args.get('q', '')
        max_results = request.args.get('max', 10, type=int)
        
        if not query:
            return jsonify({
                'error': 'Query parameter "q" is required'
            }), 400
        
        # Execute search
        results = search_pipeline.search(query, max_results)
        
        return jsonify(results)
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        stats = search_pipeline.indexer.get_statistics()
        
        return jsonify({
            'status': 'healthy',
            'version': '3.0.0',
            'index_stats': stats
        })
    
    @app.route('/api/stats', methods=['GET'])
    def stats():
        """Statistics endpoint"""
        index_stats = search_pipeline.indexer.get_statistics()
        search_stats = search_pipeline.get_search_statistics()
        
        return jsonify({
            'index': index_stats,
            'search': search_stats
        })
    
    @app.route('/api/history', methods=['GET'])
    def history():
        """Search history endpoint"""
        limit = request.args.get('limit', 100, type=int)
        history = search_pipeline.get_search_history(limit)
        
        return jsonify({
            'history': history,
            'count': len(history)
        })
    
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint"""
        return jsonify({
            'name': 'KSE API',
            'version': '3.0.0',
            'endpoints': [
                '/api/search?q=query',
                '/api/health',
                '/api/stats',
                '/api/history'
            ]
        })


def main():
    """Main entry point"""
    app = create_app()
    config = get_config()
    
    host = config.get("server.host", "127.0.0.1")
    port = config.get("server.port", 5000)
    debug = config.get("server.debug", False)
    
    logger.info(f"Starting KSE Server on {host}:{port}")
    print(f"\nKSE Server starting on http://{host}:{port}")
    print(f"API endpoints:")
    print(f"  - GET http://{host}:{port}/api/search?q=<query>")
    print(f"  - GET http://{host}:{port}/api/health")
    print(f"  - GET http://{host}:{port}/api/stats")
    print(f"  - GET http://{host}:{port}/api/history")
    print()
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
