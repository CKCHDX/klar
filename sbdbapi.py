#!/usr/bin/env python3
"""
SBDB API - Flask REST API for Search Engine
Production-ready API endpoints with logging and error handling
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Global state (will be set by main app)
GLOBAL_STATE = {
    'search_engine': None,
    'config_manager': None,
    'index': None,
    'stats': {'uptime_start': None, 'queries_served': 0, 'total_response_time': 0},
}


def init_api(search_engine, config_manager, inverted_index):
    """
    Initialize API with dependencies.
    Called by main app on startup.
    """
    GLOBAL_STATE['search_engine'] = search_engine
    GLOBAL_STATE['config_manager'] = config_manager
    GLOBAL_STATE['index'] = inverted_index
    GLOBAL_STATE['stats']['uptime_start'] = time.time()
    logger.info("✓ API initialized")


@api_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@api_bp.route('/search', methods=['POST'])
def search():
    """
    Main search endpoint.
    
    Request JSON:
    {
        "query": "Stockholm restauranger",
        "top_k": 10
    }
    
    Response JSON:
    {
        "results": [
            {
                "title": "Best Restaurants in Stockholm",
                "url": "https://example.com/...",
                "snippet": "The best restaurants in Stockholm include...",
                "trust_score": 0.95,
                "region": "Stockholm",
                "domain": "example.se",
                "response_time_ms": 347
            }
        ],
        "total_results": 1,
        "response_time_ms": 347,
        "query_tokens": ["stockholm", "restauranger"]
    }
    """
    try:
        if not GLOBAL_STATE['search_engine']:
            return jsonify({'error': 'Search engine not initialized'}), 500
        
        start_time = time.time()
        
        # Parse request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data.get('query', '').strip()
        top_k = int(data.get('top_k', 10))
        
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        if top_k < 1 or top_k > 100:
            top_k = 10
        
        # Execute search
        results = GLOBAL_STATE['search_engine'].search(query, top_k)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'title': result.get('title'),
                'url': result.get('url'),
                'snippet': result.get('snippet'),
                'trust_score': round(result.get('trust_score', 0), 3),
                'region': result.get('region'),
                'domain': result.get('domain'),
                'final_score': round(result.get('final_score', 0), 4),
            })
        
        response_time = (time.time() - start_time) * 1000  # milliseconds
        
        # Update stats
        GLOBAL_STATE['stats']['queries_served'] += 1
        GLOBAL_STATE['stats']['total_response_time'] += response_time
        
        # Log search
        _log_search(query, len(formatted_results), response_time)
        
        return jsonify({
            'results': formatted_results,
            'total_results': len(formatted_results),
            'response_time_ms': round(response_time, 1),
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Search error: {e}")
        _log_error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500


@api_bp.route('/status', methods=['GET'])
def status():
    """
    Get server status.
    """
    try:
        uptime_seconds = int(time.time() - GLOBAL_STATE['stats']['uptime_start'])
        queries_served = GLOBAL_STATE['stats']['queries_served']
        
        avg_response_time = 0
        if queries_served > 0:
            avg_response_time = GLOBAL_STATE['stats']['total_response_time'] / queries_served
        
        return jsonify({
            'status': 'active',
            'uptime_seconds': uptime_seconds,
            'queries_served': queries_served,
            'avg_response_time_ms': round(avg_response_time, 1),
            'timestamp': datetime.now().isoformat(),
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Status error: {e}")
        return jsonify({'error': 'Status check failed'}), 500


@api_bp.route('/stats', methods=['GET'])
def stats():
    """
    Get index statistics.
    """
    try:
        if not GLOBAL_STATE['index']:
            return jsonify({'error': 'Index not initialized'}), 500
        
        index_stats = GLOBAL_STATE['index'].get_stats()
        config = GLOBAL_STATE['config_manager'].config
        
        selected_domains = len(GLOBAL_STATE['config_manager'].get_selected_domains())
        
        return jsonify({
            'domains_total': len(GLOBAL_STATE['config_manager'].domains),
            'domains_selected': selected_domains,
            'pages_indexed': index_stats.get('total_pages', 0),
            'unique_keywords': index_stats.get('unique_terms', 0),
            'index_size_mb': index_stats.get('index_size_mb', 0),
            'avg_terms_per_page': index_stats.get('avg_terms_per_page', 0),
            'last_full_reindex': GLOBAL_STATE['config_manager'].stats.get('last_full_reindex'),
            'last_incremental_update': GLOBAL_STATE['config_manager'].stats.get('last_incremental_update'),
            'timestamp': datetime.now().isoformat(),
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Stats error: {e}")
        return jsonify({'error': 'Stats retrieval failed'}), 500


@api_bp.route('/admin/domains/add', methods=['POST'])
def admin_domains_add():
    """
    Admin: Add a new domain to the crawl list.
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing url parameter'}), 400
        
        domain = {
            'url': data['url'],
            'trust_score': float(data.get('trust_score', 0.5)),
            'category': data.get('category', 'Other'),
            'region': data.get('region', 'Unknown'),
            'selected': True,
        }
        
        GLOBAL_STATE['config_manager'].domains.append(domain)
        GLOBAL_STATE['config_manager'].save_domains()
        
        logger.info(f"✓ Added domain: {domain['url']}")
        
        return jsonify({
            'status': 'success',
            'message': f"Domain {domain['url']} added"
        }), 201
    
    except Exception as e:
        logger.error(f"✗ Admin add domain error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/admin/corruption/scan', methods=['POST'])
def admin_corruption_scan():
    """
    Admin: Scan database for corruption.
    """
    try:
        diagnostics = _run_corruption_scan()
        _log_diagnostic(diagnostics)
        
        return jsonify(diagnostics), 200
    
    except Exception as e:
        logger.error(f"✗ Corruption scan error: {e}")
        return jsonify({'error': str(e)}), 500


def _run_corruption_scan() -> Dict[str, Any]:
    """
    Run comprehensive database corruption scan.
    """
    diagnostics = {
        'timestamp': datetime.now().isoformat(),
        'checks': {},
        'status': 'HEALTHY',
    }
    
    try:
        # File integrity check
        all_files_ok = True
        for file_path in [GLOBAL_STATE['config_manager'].config_file,
                         GLOBAL_STATE['config_manager'].domains_file,
                         GLOBAL_STATE['config_manager'].pages_file,
                         GLOBAL_STATE['config_manager'].index_file]:
            try:
                if file_path.exists():
                    json.loads(file_path.read_text(encoding='utf-8'))
            except:
                all_files_ok = False
                diagnostics['status'] = 'CORRUPTED'
        
        diagnostics['checks']['file_integrity'] = 'OK' if all_files_ok else 'FAILED'
        
        # Index-pages cross-reference
        orphaned = 0
        index = GLOBAL_STATE['index']
        for page_ids in index.index.values():
            for pid in page_ids:
                if pid not in index.pages:
                    orphaned += 1
        
        diagnostics['checks']['orphaned_entries'] = orphaned
        if orphaned > 10:
            diagnostics['status'] = 'WARNINGS'
        
        # Index size
        diagnostics['checks']['index_size_mb'] = GLOBAL_STATE['index'].get_stats().get('index_size_mb')
        
    except Exception as e:
        diagnostics['status'] = 'CORRUPTED'
        diagnostics['error'] = str(e)
    
    return diagnostics


def _log_search(query: str, results_count: int, response_time_ms: float):
    """
    Log a search query.
    """
    try:
        logs_dir = GLOBAL_STATE['config_manager'].logs_dir
        search_log_file = logs_dir / 'searchlog.json'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results_count': results_count,
            'response_time_ms': response_time_ms,
        }
        
        logs = []
        if search_log_file.exists():
            logs = json.loads(search_log_file.read_text(encoding='utf-8'))
        
        logs.append(log_entry)
        # Keep last 10k searches
        if len(logs) > 10000:
            logs = logs[-10000:]
        
        search_log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
    
    except Exception as e:
        logger.warning(f"Failed to log search: {e}")


def _log_error(error_msg: str):
    """
    Log an error.
    """
    try:
        logs_dir = GLOBAL_STATE['config_manager'].logs_dir
        error_log_file = logs_dir / 'errorlog.json'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': error_msg,
        }
        
        logs = []
        if error_log_file.exists():
            logs = json.loads(error_log_file.read_text(encoding='utf-8'))
        
        logs.append(log_entry)
        
        error_log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
    
    except Exception as e:
        logger.warning(f"Failed to log error: {e}")


def _log_diagnostic(diagnostics: Dict):
    """
    Log diagnostic results.
    """
    try:
        logs_dir = GLOBAL_STATE['config_manager'].logs_dir
        diag_log_file = logs_dir / 'diagnosticlog.json'
        
        logs = []
        if diag_log_file.exists():
            logs = json.loads(diag_log_file.read_text(encoding='utf-8'))
        
        logs.append(diagnostics)
        
        diag_log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
    
    except Exception as e:
        logger.warning(f"Failed to log diagnostic: {e}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("SBDB API module loaded")
