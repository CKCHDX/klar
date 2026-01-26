"""
kse/server/__init__.py - REST API Server

Components:
  - APIServer: Main API server
  - AuthManager: Authentication
  - RateLimiter: Rate limiting
  - RequestHandler: Request processing
  - ResponseFormatter: Response formatting
  - ServerMetrics: Performance tracking

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_api_server import APIServer
from .kse_auth_manager import AuthManager
from .kse_rate_limiter import RateLimiter
from .kse_request_handler import RequestHandler
from .kse_response_formatter import ResponseFormatter
from .kse_server_metrics import ServerMetrics

__all__ = [
    # Core
    "APIServer",
    
    # Security
    "AuthManager",
    "RateLimiter",
    
    # Processing
    "RequestHandler",
    "ResponseFormatter",
    
    # Monitoring
    "ServerMetrics",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - Server/API Layer

1. Start server:
    from kse.server import APIServer, AuthManager, RateLimiter
    from kse.search import SearchCore
    from kse.cache import CacheManager
    
    # Initialize components
    cache = CacheManager()
    search = SearchCore(...)
    auth = AuthManager()
    rate_limiter = RateLimiter(requests_per_hour=1000)
    
    # Create server
    api = APIServer(search, auth, rate_limiter)
    
    # In production, wrap with Flask or FastAPI:
    # from flask import Flask, request, jsonify
    # app = Flask(__name__)
    # 
    # @app.route('/api/search', methods=['GET'])
    # def search_api():
    #     result = api.handle_search_request(request.args.get('q'))
    #     return jsonify(result)

2. Authentication:
    from kse.server import AuthManager
    
    auth = AuthManager()
    auth.validate_api_key("kse-demo-key-123")
    new_key = auth.register_api_key("My App")

3. Rate limiting:
    from kse.server import RateLimiter
    
    limiter = RateLimiter(requests_per_hour=1000)
    if limiter.is_allowed("client-123"):
        # Process request
        pass
    else:
        # Rate limited
        remaining = limiter.get_remaining("client-123")

4. Request validation:
    from kse.server import RequestHandler
    
    handler = RequestHandler()
    valid, error, params = handler.validate_search_params({
        'q': 'svenska universitet',
        'limit': 10,
        'page': 1
    })

5. Response formatting:
    from kse.server import ResponseFormatter
    
    formatter = ResponseFormatter()
    response, code, headers = formatter.success_response({
        'query': 'svenska',
        'total_results': 1000,
        'results': []
    })

6. Server metrics:
    from kse.server import ServerMetrics
    
    metrics = ServerMetrics()
    metrics.record_request(success=True, execution_time=0.042)
    print(metrics.get_summary())

API ENDPOINTS:

GET /api/search
  Query Parameters:
    - q (required): Search query
    - limit (optional): Results per page (1-100, default 10)
    - page (optional): Page number (default 1)
  Headers:
    - X-API-Key: API key for authentication
  Response:
    {
      "success": true,
      "data": {
        "query": "svenska universitet",
        "total_results": 15432,
        "results": [
          {
            "rank": 1,
            "url": "https://www.uu.se",
            "title": "Uppsala University",
            "score": 98.5,
            "snippet": "Founded in 1477, Uppsala University..."
          }
        ],
        "execution_time_ms": 42.3,
        "cached": false
      },
      "timestamp": "2026-01-26T14:00:00Z"
    }

GET /api/health
  Response:
    {
      "status": "healthy",
      "service": "kse-search-api",
      "version": "1.0.0"
    }

POST /api/auth/register
  Body:
    {
      "name": "My App",
      "rate_limit": 1000
    }
  Response:
    {
      "success": true,
      "data": {
        "api_key": "kse-a1b2c3d4e5f6g7h8"
      }
    }

GET /api/metrics
  Response:
    {
      "success": true,
      "data": {
        "total_requests": 1000,
        "successful_requests": 980,
        "failed_requests": 20,
        "success_rate": 98.0,
        "avg_execution_time_ms": 42.5,
        "uptime_seconds": 3600
      }
    }

ARCHITECTURE:

kse/server/
├── kse_api_server.py               Main API orchestrator
├── kse_auth_manager.py             API key authentication
├── kse_rate_limiter.py             Per-client rate limiting
├── kse_request_handler.py          Request validation
├── kse_response_formatter.py       Response formatting
├── kse_server_metrics.py           Performance metrics
└── __init__.py                     Public API

INTEGRATION:

- Phase 8 (search): Execute search
- Phase 3 (cache): Cache results
- Phase 10 (gui): Frontend calls

FLOW:

HTTP Request
    ↓
Extract Headers & Params (RequestHandler)
    ├─ Validate API key (AuthManager)
    ├─ Check rate limit (RateLimiter)
    └─ Validate parameters
    ↓
Execute Search (SearchCore)
    ↓
Record Metrics (ServerMetrics)
    ↓
Format Response (ResponseFormatter)
    ↓
Return JSON Response
    ↓
Cache for next request

SECURITY FEATURES:

- API key authentication
- Rate limiting (per-client, per-hour)
- Input validation (length, format)
- Error handling (no stack traces)
- CORS support (when deployed)
- HTTPS required (in production)

PERFORMANCE TARGETS:

- Search latency: < 100ms (cold)
- Search latency: < 10ms (cached)
- API response time: < 150ms
- Success rate: > 99%
- Throughput: > 1000 req/s

DEPLOYMENT:

# Using Flask
flask run --host 0.0.0.0 --port 5000

# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 kse_server:app

# Using Docker
docker run -p 5000:5000 kse-search-api:latest

# Health check
curl http://localhost:5000/api/health

# Search example
curl "http://localhost:5000/api/search?q=svenska&limit=10"
"""
