"""
Klar SBDB API - Flask REST API Endpoints (with Advanced NLP Integration)
Provides search, status, and administrative endpoints
"""

from flask import Flask, request, jsonify
import logging
import time
from typing import Dict
from pathlib import Path

from sbdb_core import SwedishNLPEngine, TextProcessor
from sbdb_core_advanced import AdvancedSwedishNLP
from sbdb_index import SearchEngine
from sbdb_crawler import DomainCrawler, ChangeDetector

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SBDBAPIServer:
    """Klar SBDB API Server using Flask"""
    
    def __init__(self, data_dir: str = "klar_sbdb_data", host: str = "127.0.0.1", port: int = 8080):
        self.app = Flask(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.host = host
        self.port = port
        
        # NLP engines
        self.nlp_engine = SwedishNLPEngine()
        self.advanced_nlp = AdvancedSwedishNLP()
        self.text_processor = TextProcessor()
        
        # Core components
        self.search_engine = SearchEngine(str(self.data_dir))
        self.crawler = DomainCrawler(str(self.data_dir))
        self.change_detector = ChangeDetector(self.crawler, check_interval=86400)
        
        # Statistics
        self.start_time = time.time()
        self.queries_served = 0
        self.total_response_time = 0
        
        self._register_routes()
        logger.info(f"SBDBAPIServer initialized: {host}:{port}")
    
    def _register_routes(self) -> None:
        @self.app.route('/api/search', methods=['POST'])
        def search():
            return self._handle_search()
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            return self._handle_status()
        
        @self.app.route('/api/stats', methods=['GET'])
        def stats():
            return self._handle_stats()
        
        @self.app.route('/api/admin/domains/add', methods=['POST'])
        def add_domain():
            return self._handle_add_domain()
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            return jsonify({'status': 'healthy', 'timestamp': time.time()})
        
        logger.info("Routes registered")
    
    def _handle_search(self) -> Dict:
        try:
            data = request.get_json() or {}
            query = data.get('query', '').strip()
            top_k = int(data.get('top_k', 10))
            
            if not query:
                return jsonify({'error': 'Query is required', 'results': []}), 400
            
            start_time = time.time()
            
            # Use simple Swedish NLP for index terms
            simple_tokens = self.nlp_engine.process_text(query)
            
            # Run search (SearchEngine will apply advanced re-ranking internally)
            search_results = self.search_engine.search(
                query=query,
                processed_tokens=simple_tokens,
                top_k=top_k,
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            self.queries_served += 1
            self.total_response_time += response_time_ms
            
            return jsonify({
                'query': search_results['query'],
                'results': search_results['results'],
                'total_results': search_results['total_results'],
                'response_time_ms': search_results['response_time_ms'],
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return jsonify({'error': str(e), 'results': []}), 500
    
    def _handle_status(self) -> Dict:
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
        try:
            data = request.get_json() or {}
            domain = data.get('domain', '').strip()
            max_pages = int(data.get('max_pages', 100))
            
            if not domain:
                return jsonify({'error': 'Domain is required'}), 400
            
            pages = self.crawler.crawl_domain(domain, max_pages)
            page_id_base = len(self.search_engine.index.pages)
            for i, page_data in enumerate(pages):
                processed = self.text_processor.process_page(
                    title=page_data.get('title', ''),
                    text=page_data.get('text', ''),
                    url=page_data.get('url', '')
                )
                self.search_engine.index.add_page(page_id_base + i, processed)
            self.search_engine.index.save()
            
            return jsonify({
                'status': 'success',
                'domain': domain,
                'pages_crawled': len(pages),
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"Error adding domain: {e}")
            return jsonify({'error': str(e)}), 500
    
    def run(self, debug: bool = False) -> None:
        logger.info(f"Starting SBDB API Server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)
    
    def start_change_detector(self) -> None:
        self.change_detector.start()
        logger.info("Change detector started")
    
    def stop_change_detector(self) -> None:
        self.change_detector.stop()
        logger.info("Change detector stopped")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    api_server = SBDBAPIServer(
        data_dir="klar_sbdb_data",
        host="127.0.0.1",
        port=8080,
    )
    api_server.start_change_detector()
    try:
        api_server.run(debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
        api_server.stop_change_detector()
