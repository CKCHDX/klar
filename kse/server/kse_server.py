"""
KSE Server - Main Flask REST API server
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import json
from datetime import datetime
from kse.core.kse_config import get_config
from kse.core.kse_logger import KSELogger, get_logger
from kse.core.kse_network_info import get_network_info, format_server_info
from kse.core.kse_state_manager import StateManager
from kse.storage.kse_storage_manager import StorageManager
from kse.nlp.kse_nlp_core import NLPCore
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.search.kse_search_pipeline import SearchPipeline

logger = None
app = None
search_pipeline = None
network_info = None
allowed_domains = None
state_manager = None


def create_app():
    """Create Flask application"""
    global app, search_pipeline, logger, network_info, allowed_domains, state_manager
    
    # Initialize Flask
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    
    # Setup logging
    log_dir = Path(config.get("log_dir"))
    KSELogger.setup(log_dir, config.get("log_level", "INFO"), True)
    logger = get_logger(__name__, "server.log")
    
    # Initialize state manager
    data_dir = Path(config.get("data_dir"))
    state_manager = StateManager(data_dir / 'state')
    
    # Check if first run
    if state_manager.is_first_run():
        logger.info("=" * 60)
        logger.info("FIRST RUN DETECTED")
        logger.info("=" * 60)
        logger.info("Welcome to Klar Search Engine - Sveriges Sökmotor")
        logger.info("This is the initial setup. The server will index domains...")
        logger.info("=" * 60)
    else:
        logger.info("Klar Search Engine - Starting up...")
        server_state = state_manager.get_state()
        logger.info(f"Last startup: {server_state.get('last_startup', 'N/A')}")
        logger.info(f"Indexed domains: {server_state.get('indexed_domains_count', 0)}")
        logger.info(f"Total documents: {server_state.get('total_documents', 0)}")
    
    # Load allowed domains from config
    logger.info("Loading allowed domains...")
    try:
        domains_file = Path(__file__).parent.parent.parent / "config" / "swedish_domains.json"
        if domains_file.exists():
            with open(domains_file, 'r', encoding='utf-8') as f:
                domains_data = json.load(f)
                allowed_domains = {d['domain'].lower() for d in domains_data.get('domains', [])}
                logger.info(f"Loaded {len(allowed_domains)} allowed domains")
        else:
            allowed_domains = set()
            logger.warning("swedish_domains.json not found, no domains whitelisted")
    except Exception as e:
        logger.error(f"Failed to load allowed domains: {e}")
        allowed_domains = set()
    
    # Get network information (non-blocking, best effort)
    logger.info("Detecting network information...")
    try:
        network_info = get_network_info()
        logger.info(f"Network info: {network_info}")
    except Exception as e:
        logger.warning(f"Failed to detect network info: {e}")
        network_info = {
            'public_ip': None,
            'local_ip': None,
            'hostname': 'unknown'
        }
    
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
    
    # Update state statistics
    index_stats = indexer.get_statistics()
    state_manager.update_statistics(
        indexed_domains=len(allowed_domains),
        total_docs=index_stats.get('total_documents', 0)
    )
    
    # Mark setup as complete on first successful initialization
    if state_manager.is_first_run():
        state_manager.mark_setup_complete()
        logger.info("=" * 60)
        logger.info("SETUP COMPLETE! Klar Search Engine is ready.")
        logger.info("=" * 60)
    
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
    
    @app.route('/api/check-domain', methods=['GET'])
    def check_domain():
        """Check if a domain is allowed"""
        domain = request.args.get('domain', '').lower().strip()
        
        if not domain:
            return jsonify({
                'error': 'Query parameter "domain" is required',
                'allowed': False
            }), 400
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if domain is in whitelist
        is_allowed = domain in allowed_domains
        
        logger.info(f"Domain check: {domain} - {'ALLOWED' if is_allowed else 'BLOCKED'}")
        
        if is_allowed:
            return jsonify({
                'allowed': True,
                'domain': domain,
                'message': 'Domain is whitelisted'
            })
        else:
            return jsonify({
                'allowed': False,
                'domain': domain,
                'message': f'Domain "{domain}" is not in the whitelist. Only Swedish trusted domains are allowed.'
            }), 403
    
    @app.route('/api/domains', methods=['GET'])
    def get_domains():
        """Get all whitelisted domains"""
        try:
            domains_file = Path(__file__).parent.parent.parent / "config" / "swedish_domains.json"
            if domains_file.exists():
                with open(domains_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return jsonify(data)
            return jsonify({'domains': [], 'count': 0})
        except Exception as e:
            logger.error(f"Error fetching domains: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/domains/add', methods=['POST'])
    def add_domain():
        """Add a new domain to whitelist"""
        try:
            data = request.get_json()
            if not data or 'domain' not in data:
                return jsonify({'error': 'Domain is required'}), 400
            
            domain_info = {
                'domain': data['domain'].lower().strip(),
                'name': data.get('name', data['domain']),
                'category': data.get('category', 'other'),
                'trust_score': data.get('trust_score', 75),
                'priority': data.get('priority', 3)
            }
            
            # Remove www. prefix
            if domain_info['domain'].startswith('www.'):
                domain_info['domain'] = domain_info['domain'][4:]
            
            domains_file = Path(__file__).parent.parent.parent / "config" / "swedish_domains.json"
            
            # Load existing domains
            domains_data = {'domains': []}
            if domains_file.exists():
                with open(domains_file, 'r', encoding='utf-8') as f:
                    domains_data = json.load(f)
            
            # Check if domain already exists
            if any(d['domain'] == domain_info['domain'] for d in domains_data['domains']):
                return jsonify({'error': 'Domain already exists'}), 409
            
            # Add new domain
            domains_data['domains'].append(domain_info)
            
            # Save to file
            with open(domains_file, 'w', encoding='utf-8') as f:
                json.dump(domains_data, f, indent=2, ensure_ascii=False)
            
            # Update in-memory cache
            allowed_domains.add(domain_info['domain'])
            
            logger.info(f"Added domain: {domain_info['domain']}")
            
            return jsonify({
                'success': True,
                'message': f"Domain {domain_info['domain']} added successfully",
                'domain': domain_info
            })
            
        except Exception as e:
            logger.error(f"Error adding domain: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/domains/remove', methods=['POST'])
    def remove_domain():
        """Remove a domain from whitelist"""
        try:
            data = request.get_json()
            if not data or 'domain' not in data:
                return jsonify({'error': 'Domain is required'}), 400
            
            domain = data['domain'].lower().strip()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            domains_file = Path(__file__).parent.parent.parent / "config" / "swedish_domains.json"
            
            if not domains_file.exists():
                return jsonify({'error': 'Domains file not found'}), 404
            
            with open(domains_file, 'r', encoding='utf-8') as f:
                domains_data = json.load(f)
            
            # Remove domain
            original_count = len(domains_data['domains'])
            domains_data['domains'] = [d for d in domains_data['domains'] if d['domain'] != domain]
            
            if len(domains_data['domains']) == original_count:
                return jsonify({'error': 'Domain not found'}), 404
            
            # Save to file
            with open(domains_file, 'w', encoding='utf-8') as f:
                json.dump(domains_data, f, indent=2, ensure_ascii=False)
            
            # Update in-memory cache
            allowed_domains.discard(domain)
            
            logger.info(f"Removed domain: {domain}")
            
            return jsonify({
                'success': True,
                'message': f"Domain {domain} removed successfully"
            })
            
        except Exception as e:
            logger.error(f"Error removing domain: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/domains/reload', methods=['POST'])
    def reload_domains():
        """Reload domains from config file"""
        global allowed_domains
        try:
            domains_file = Path(__file__).parent.parent.parent / "config" / "swedish_domains.json"
            if domains_file.exists():
                with open(domains_file, 'r', encoding='utf-8') as f:
                    domains_data = json.load(f)
                    allowed_domains = {d['domain'].lower() for d in domains_data.get('domains', [])}
                    logger.info(f"Reloaded {len(allowed_domains)} domains")
                    return jsonify({
                        'success': True,
                        'message': f'Reloaded {len(allowed_domains)} domains',
                        'count': len(allowed_domains)
                    })
            return jsonify({'error': 'Domains file not found'}), 404
        except Exception as e:
            logger.error(f"Error reloading domains: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/system/state', methods=['GET'])
    def get_system_state():
        """Get complete system state"""
        try:
            state = state_manager.get_state()
            index_stats = search_pipeline.indexer.get_statistics()
            search_stats = search_pipeline.get_search_statistics()
            
            return jsonify({
                'state': state,
                'index': index_stats,
                'search': search_stats,
                'allowed_domains_count': len(allowed_domains),
                'network': network_info
            })
        except Exception as e:
            logger.error(f"Error getting system state: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/system/reset-setup', methods=['POST'])
    def reset_setup():
        """Reset setup status (for debugging)"""
        try:
            state_manager.reset_setup()
            return jsonify({
                'success': True,
                'message': 'Setup status reset. Server will run first-time setup on next restart.'
            })
        except Exception as e:
            logger.error(f"Error resetting setup: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/crawler/start', methods=['POST'])
    def start_crawler():
        """Start crawler for specific domains"""
        try:
            data = request.get_json()
            domains = data.get('domains', [])
            max_pages = data.get('max_pages', 100)
            
            if not domains:
                return jsonify({'error': 'No domains specified'}), 400
            
            logger.info(f"Starting crawler for domains: {domains}")
            
            # This would trigger the actual crawler
            # For now, return a placeholder response
            return jsonify({
                'success': True,
                'message': f'Crawler started for {len(domains)} domains',
                'domains': domains,
                'max_pages': max_pages,
                'status': 'queued'
            })
        except Exception as e:
            logger.error(f"Error starting crawler: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/crawler/status', methods=['GET'])
    def get_crawler_status():
        """Get crawler status"""
        try:
            # Get real crawler status from indexer
            index_stats = search_pipeline.indexer.get_statistics()
            
            return jsonify({
                'status': 'ready',
                'indexed_documents': index_stats.get('total_documents', 0),
                'indexed_terms': index_stats.get('unique_terms', 0),
                'avg_doc_length': index_stats.get('avg_document_length', 0),
                'last_indexed': index_stats.get('last_update', 'Never')
            })
        except Exception as e:
            logger.error(f"Error getting crawler status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health', methods=['GET', 'OPTIONS'])
    def health():
        """Health check endpoint"""
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = jsonify({'status': 'ok'})
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        stats = search_pipeline.indexer.get_statistics()
        config = get_config()
        public_url = config.get("server.public_url")
        
        response = jsonify({
            'status': 'healthy',
            'version': '3.0.0',
            'server_running': True,
            'timestamp': datetime.now().isoformat(),
            'public_url': public_url,
            'index_stats': stats,
            'network_info': network_info
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    @app.route('/api/server/info', methods=['GET'])
    def server_info():
        """Server information endpoint including network details"""
        config = get_config()
        host = config.get("server.host", "127.0.0.1")
        port = config.get("server.port", 5000)
        public_url = config.get("server.public_url")
        
        return jsonify({
            'status': 'running',
            'version': '3.0.0',
            'host': host,
            'port': port,
            'public_url': public_url,
            'network': network_info,
            'endpoints': [
                '/api/search?q=query',
                '/api/check-domain?domain=example.com',
                '/api/domains - GET all domains',
                '/api/domains/add - POST add domain',
                '/api/domains/remove - POST remove domain',
                '/api/domains/reload - POST reload domains',
                '/api/system/state - GET system state',
                '/api/system/reset-setup - POST reset setup',
                '/api/crawler/start - POST start crawler',
                '/api/crawler/status - GET crawler status',
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
            'description': 'Klar Search Engine - Sveriges Nationella Sökmotor',
            'tagline': 'Enterprise-grade NLP search for everyone in Sweden',
            'network': network_info,
            'endpoints': [
                '/api/search?q=query',
                '/api/check-domain?domain=example.com',
                '/api/domains - Domain management',
                '/api/system/state - System state',
                '/api/crawler/status - Crawler status',
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
    if network_info:
        info_text = format_server_info(host, port, network_info)
        print(info_text)
    else:
        print(f"\nKSE Server starting on http://{host}:{port}")
    
    logger.info(f"Starting KSE Server on {host}:{port}")
    
    # Display API endpoints
    print(f"API endpoints:")
    print(f"  - GET  http://{host}:{port}/api/search?q=<query>")
    print(f"  - GET  http://{host}:{port}/api/check-domain?domain=<domain>")
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
