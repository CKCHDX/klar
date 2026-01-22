"""
Klar SBDB API - Flask REST API Endpoints
Provides search, status, and administrative endpoints
"""

from flask import Flask, request, jsonify
import logging
import time
import json
from typing import Dict
from pathlib import Path

from sbdb_core import SwedishNLPEngine, TextProcessor
from sbdb_index import SearchEngine
from sbdb_crawler import DomainCrawler, ChangeDetector

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SBDBAPIServer:
    """
    Klar SBDB API Server using Flask
    """
    
    def __init__(self, data_dir: str = "klar_sbdb_data", host: str = "127.0.0.1", port: int = 8080):
        self.app = Flask(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.host = host
        self.port = port
        
        # Initialize components
        self.nlp_engine = SwedishNLPEngine()
        self.text_processor = TextProcessor()
        self.search_engine = SearchEngine(str(self.data_dir))
        self.crawler = DomainCrawler(str(self.data_dir))
        self.change_detector = ChangeDetector(self.crawler, check_interval=86400)  # 24h
        
        # Statistics
        self.start_time = time.time()
        self.queries_served = 0
        self.total_response_time = 0
        
        # Register routes
        self._register_routes()
        
        logger.info(f"SBDBAPIServer initialized: {host}:{port}")
    
    def _register_routes(self) -> None:
        """
        Register Flask API routes
        """
        # Search endpoint
        @self.app.route('/api/search', methods=['POST'])
        def search():
            return self._handle_search()
        
        # Status endpoint
        @self.app.route('/api/status', methods=['GET'])
        def status():
            return self._handle_status()
        
        # Stats endpoint
        @self.app.route('/api/stats', methods=['GET'])
        def stats():
            return self._handle_stats()
        
        # Admin: Add domain
        @self.app.route('/api/admin/domains/add', methods=['POST'])
        def add_domain():
            return self._handle_add_domain()
        
        # Health check
        @self.app.route('/api/health', methods=['GET'])
        def health():
            return jsonify({'status': 'healthy', 'timestamp': time.time()})
        
        logger.info("Routes registered")
    
    def _handle_search(self) -> Dict:
        """
        Handle /api/search POST request
        
        Expected JSON:
        {"query": "Stockholm restauranger"}
        
        Returns:
        {
            "results": [...],
            "response_time_ms": 123,
            "timestamp": 1234567890
        }
        """
        try:
            data = request.get_json()
            query = data.get('query', '').strip()
            top_k = data.get('top_k', 10)
            
            if not query:
                return jsonify({
                    'error': 'Query is required',
                    'results': []
                }), 400
            
            # Process query
            start_time = time.time()
            query_tokens = self.nlp_engine.process_text(query)
            
            # Search
            search_results = self.search_engine.search(
                query=query,
                processed_tokens=query_tokens,
                top_k=top_k
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            self.queries_served += 1
            self.total_response_time += response_time_ms
            
            return jsonify({
                'query': query,
                'results': search_results.get('results', []),
                'total_results': search_results.get('total_results', 0),
                'response_time_ms': round(response_time_ms, 2),
                'timestamp': time.time()
            })
        
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return jsonify({
                'error': str(e),
                'results': []
            }), 500
    
    def _handle_status(self) -> Dict:
        """
        Handle /api/status GET request
        
        Returns current server status
        """
        uptime = time.time() - self.start_time
        avg_response_time = self.total_response_time / self.queries_served if self.queries_served > 0 else 0
        
        return jsonify({
            'status': 'active',
            'uptime_seconds': int(uptime),
            'queries_served': self.queries_served,
            'avg_response_time_ms': round(avg_response_time, 2),
            'server_host': self.host,
            'server_port': self.port,
            'timestamp': time.time()
        })
    
    def _handle_stats(self) -> Dict:
        """
        Handle /api/stats GET request
        
        Returns index statistics
        """
        try:
            index_stats = self.search_engine.index.get_stats()
            
            return jsonify({
                'index': {
                    'unique_words': index_stats.get('unique_words', 0),
                    'total_pages': index_stats.get('total_pages', 0),
                    'size_bytes': index_stats.get('index_size_bytes', 0),
                    'size_mb': round(index_stats.get('index_size_bytes', 0) / (1024*1024), 2)
                },
                'server': {
                    'queries_served': self.queries_served,
                    'avg_response_time_ms': round(self.total_response_time / self.queries_served, 2) if self.queries_served > 0 else 0,
                    'uptime_seconds': int(time.time() - self.start_time)
                },
                'timestamp': time.time()
            })
        
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return jsonify({'error': str(e)}), 500
    
    def _handle_add_domain(self) -> Dict:
        """
        Handle /api/admin/domains/add POST request
        
        Expected JSON:
        {"domain": "example.se", "max_pages": 100}
        
        Crawls a new domain and adds it to index
        """
        try:
            data = request.get_json()
            domain = data.get('domain', '').strip()
            max_pages = data.get('max_pages', 100)
            
            if not domain:
                return jsonify({
                    'error': 'Domain is required'
                }), 400
            
            # Start crawl in background
            pages = self.crawler.crawl_domain(domain, max_pages)
            
            # Add to index
            page_id_base = len(self.search_engine.index.pages)
            for i, page_data in enumerate(pages):
                processed = self.text_processor.process_page(
                    title=page_data.get('title', ''),
                    text=page_data.get('text', ''),
                    url=page_data.get('url', '')
                )
                self.search_engine.index.add_page(page_id_base + i, processed)
            
            # Save index
            self.search_engine.index.save()
            
            return jsonify({
                'status': 'success',
                'domain': domain,
                'pages_crawled': len(pages),
                'timestamp': time.time()
            })
        
        except Exception as e:
            logger.error(f"Error adding domain: {e}")
            return jsonify({
                'error': str(e)
            }), 500
    
    def run(self, debug: bool = False) -> None:
        """
        Start Flask server
        
        Args:
            debug: Enable Flask debug mode
        """
        logger.info(f"Starting SBDB API Server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)
    
    def start_change_detector(self) -> None:
        """
        Start background change detection
        """
        self.change_detector.start()
        logger.info("Change detector started")
    
    def stop_change_detector(self) -> None:
        """
        Stop background change detection
        """
        self.change_detector.stop()
        logger.info("Change detector stopped")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start server
    api_server = SBDBAPIServer(
        data_dir="klar_sbdb_data",
        host="127.0.0.1",
        port=8080
    )
    
    # Start change detector
    api_server.start_change_detector()
    
    # Run server
    try:
        api_server.run(debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
        api_server.stop_change_detector()
