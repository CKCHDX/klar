"""
KSE Server - Main Flask REST API server
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
from kse.core.kse_config import get_config
from kse.core.kse_logger import KSELogger, get_logger
from kse.core.kse_network_info import get_network_info, format_server_info
from kse.storage.kse_storage_manager import StorageManager
from kse.nlp.kse_nlp_core import NLPCore
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.search.kse_search_pipeline import SearchPipeline

logger = None
app = None
search_pipeline = None
network_info = None


def create_app():
    """Create Flask application"""
    global app, search_pipeline, logger, network_info
    
    # Initialize Flask
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    
    # Setup logging
    log_dir = Path(config.get("log_dir"))
    KSELogger.setup(log_dir, config.get("log_level", "INFO"), True)
    logger = get_logger(__name__, "server.log")
    
    # Get network information
    logger.info("Detecting network information...")
    network_info = get_network_info()
    logger.info(f"Network info: {network_info}")
    
    # Enable CORS
    if config.get("server.enable_cors", True):
        CORS(app)
    
    # Initialize components
    data_dir = Path(config.get("data_dir"))
    storage_manager = StorageManager(data_dir)
    nlp_core = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
    indexer = IndexerPipeline(storage_manager, nlp_core)
    search_pipeline = SearchPipeline(
        indexer,
        nlp_core,
        enable_cache=config.get("cache.enabled", True),
        enable_ranking=config.get("ranking.enabled", True)
    )
    
    # Initialize monitoring if enabled
    monitoring = None
    if config.get("monitoring.enabled", True):
        from kse.monitoring.kse_monitoring_core import MonitoringCore
        monitoring = MonitoringCore(check_interval=60)
        monitoring.start_monitoring()
        logger.info("Monitoring enabled")
    
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
            'index_stats': stats,
            'network_info': network_info
        })
    
    @app.route('/api/server/info', methods=['GET'])
    def server_info():
        """Server information endpoint including network details"""
        config = get_config()
        host = config.get("server.host", "127.0.0.1")
        port = config.get("server.port", 5000)
        
        return jsonify({
            'status': 'running',
            'version': '3.0.0',
            'host': host,
            'port': port,
            'network': network_info,
            'endpoints': [
                '/api/search?q=query',
                '/api/health',
                '/api/stats',
                '/api/history',
                '/api/server/info',
                '/api/cache/clear',
                '/api/cache/stats',
                '/api/ranking/weights',
                '/api/monitoring/status'
            ]
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
    
    @app.route('/api/cache/clear', methods=['POST'])
    def clear_cache():
        """Clear search cache"""
        search_pipeline.clear_cache()
        return jsonify({
            'status': 'success',
            'message': 'Cache cleared'
        })
    
    @app.route('/api/cache/stats', methods=['GET'])
    def cache_stats():
        """Get cache statistics"""
        if search_pipeline.enable_cache:
            stats = search_pipeline.cache_manager.get_statistics()
            return jsonify(stats)
        return jsonify({
            'error': 'Cache not enabled'
        }), 400
    
    @app.route('/api/ranking/weights', methods=['GET'])
    def ranking_weights():
        """Get current ranking weights"""
        weights = search_pipeline.get_ranking_weights()
        return jsonify(weights)
    
    @app.route('/api/monitoring/status', methods=['GET'])
    def monitoring_status():
        """Get system monitoring status"""
        if monitoring:
            status = monitoring.get_system_status()
            return jsonify(status)
        return jsonify({
            'error': 'Monitoring not enabled'
        }), 400
    
    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint"""
        return jsonify({
            'name': 'KSE API',
            'version': '3.0.0',
            'network': network_info,
            'endpoints': [
                '/api/search?q=query',
                '/api/health',
                '/api/stats',
                '/api/history',
                '/api/server/info',
                '/api/cache/clear',
                '/api/cache/stats',
                '/api/ranking/weights',
                '/api/monitoring/status'
            ]
        })


def main():
    """Main entry point"""
    app = create_app()
    config = get_config()
    
    host = config.get("server.host", "127.0.0.1")
    port = config.get("server.port", 5000)
    debug = config.get("server.debug", False)
    
    # Display network information
    info_text = format_server_info(host, port, network_info)
    print(info_text)
    logger.info(f"Starting KSE Server on {host}:{port}")
    
    # Display API endpoints
    print(f"API endpoints:")
    print(f"  - GET  http://{host}:{port}/api/search?q=<query>")
    print(f"  - GET  http://{host}:{port}/api/server/info")
    print(f"  - GET  http://{host}:{port}/api/health")
    print(f"  - GET  http://{host}:{port}/api/stats")
    print(f"  - GET  http://{host}:{port}/api/history")
    print(f"  - POST http://{host}:{port}/api/cache/clear")
    print(f"  - GET  http://{host}:{port}/api/cache/stats")
    print(f"  - GET  http://{host}:{port}/api/ranking/weights")
    print(f"  - GET  http://{host}:{port}/api/monitoring/status")
    
    if network_info and network_info.get('public_ip'):
        public_ip = network_info['public_ip']
        print(f"\n👉 For remote clients, use: http://{public_ip}:{port}")
    
    print()
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
