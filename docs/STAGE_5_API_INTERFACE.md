# Stage 5: API & Web Interface

## Overview

Stage 5 provides a complete REST API and web interface for Klar search engine, making it accessible to users and applications.

**Components:**
- REST API endpoints
- Data models
- Flask web server
- HTML web interface
- CORS support
- Health monitoring

## Quick Start

### Starting the Server

```python
from kse.api import KSEAPIServer, KSESearchEngine

# Initialize search engine
engine = KSESearchEngine("data/index.db")

# Create and run server
server = KSEAPIServer(engine, host="0.0.0.0", port=5000)
server.run()
```

### Web Interface

Access at: `http://localhost:5000/`

- Clean, modern UI
- Real-time suggestions
- Result rankings
- Cache statistics
- Responsive design

## REST API

### Base URL

```
http://localhost:5000/api
```

### Endpoints

#### 1. Search

**Request:**
```
GET /api/search?q=query&limit=10&offset=0
```

**Parameters:**
- `q` (required): Search query
- `limit` (optional): Results per page (default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "query": "python programming",
  "total_results": 1000,
  "returned_results": 10,
  "results": [
    {
      "id": 1,
      "title": "Python Programming Guide",
      "url": "https://example.com/python-guide",
      "description": "Learn Python programming basics...",
      "domain": "example.com",
      "score": 0.92,
      "rank": 1
    }
  ],
  "execution_time_ms": 45.2,
  "from_cache": false,
  "has_more": true,
  "next_offset": 10
}
```

**Example:**
```bash
curl 'http://localhost:5000/api/search?q=machine%20learning&limit=5'
```

#### 2. Suggestions

**Request:**
```
GET /api/suggestions?q=query&limit=5
```

**Parameters:**
- `q` (required): Partial query (minimum 2 characters)
- `limit` (optional): Number of suggestions (default: 5)

**Response:**
```json
{
  "query": "pyt",
  "suggestions": [
    "python programming",
    "python tutorial",
    "python documentation",
    "python packages",
    "python libraries"
  ],
  "execution_time_ms": 2.1
}
```

**Example:**
```bash
curl 'http://localhost:5000/api/suggestions?q=mach'
```

#### 3. Related Searches

**Request:**
```
GET /api/related?id=page_id&limit=5
```

**Parameters:**
- `id` (required): Page ID
- `limit` (optional): Number of related searches (default: 5)

**Response:**
```json
{
  "query": "Related to page 123",
  "suggestions": [
    "python libraries",
    "python modules",
    "python packages",
    "python frameworks",
    "python tools"
  ],
  "execution_time_ms": 1.5
}
```

#### 4. Cache Statistics

**Request:**
```
GET /api/stats/cache
```

**Response:**
```json
{
  "entries": 45,
  "max_entries": 5000,
  "hits": 234,
  "misses": 89,
  "hit_rate_percent": 72.4,
  "puts": 89,
  "evictions": 5,
  "total_requests": 323
}
```

#### 5. Health Check

**Request:**
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "5.0.0",
  "stage": "Stage 5: API & Web Interface",
  "timestamp": "2026-01-24T15:16:00Z",
  "uptime_seconds": 3600.5
}
```

#### 6. Index Information

**Request:**
```
GET /api/info/index
```

**Response:**
```json
{
  "total_pages": 1000000,
  "total_terms": 5000000,
  "index_size_mb": 2500,
  "last_update": "2026-01-24T00:00:00Z"
}
```

#### 7. API Root

**Request:**
```
GET /api
```

**Response:**
```json
{
  "service": "Klar Search Engine",
  "version": "5.0.0",
  "stage": "Stage 5: API & Web Interface",
  "endpoints": {
    "search": "GET /api/search?q=query&limit=10&offset=0",
    "suggestions": "GET /api/suggestions?q=query&limit=5",
    "related": "GET /api/related?id=page_id&limit=5",
    "cache_stats": "GET /api/stats/cache",
    "health": "GET /api/health",
    "index_info": "GET /api/info/index"
  }
}
```

## Data Models

### QueryRequest
```python
@dataclass
class QueryRequest:
    query: str
    limit: int = 10
    offset: int = 0
    sort: str = "relevance"
    lang: Optional[str] = None
```

### SearchResponse
```python
@dataclass
class SearchResponse:
    query: str
    total_results: int
    returned_results: int
    results: List[ResultItem]
    execution_time_ms: float
    from_cache: bool
    has_more: bool
    next_offset: Optional[int]
```

### ResultItem
```python
@dataclass
class ResultItem:
    id: int
    title: str
    url: str
    description: str
    domain: str
    score: float
    snippet: Optional[str]
    keywords: List[str]
    rank_position: int
```

## Web Interface

### Features

- **Search Box:** Clean, minimal search interface
- **Auto-suggestions:** Real-time query suggestions
- **Results Display:** Ranked results with:
  - Title (clickable link)
  - URL
  - Description
  - Domain
  - Relevance score
- **Pagination:** Navigate through results
- **Cache Statistics:** Show hit rate and performance
- **Responsive Design:** Mobile-friendly layout
- **Dark Mode Ready:** CSS variables for theming

### Keyboard Shortcuts

- `Enter` - Search
- `Esc` - Close suggestions
- `Arrow Up/Down` - Navigate suggestions

## Error Handling

### Error Responses

**400 Bad Request:**
```json
{
  "error": "Bad Request",
  "code": 400,
  "message": "Query parameter required"
}
```

**404 Not Found:**
```json
{
  "error": "Not Found",
  "code": 404,
  "message": "Endpoint not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal Server Error",
  "code": 500,
  "message": "An error occurred"
}
```

## CORS Support

API supports CORS with:
- Origin: `*`
- Methods: `GET, OPTIONS`
- Headers: `Content-Type`

Enable in-browser requests from any origin.

## Performance

### Typical Response Times

- **Search (cache hit):** < 1ms
- **Search (cache miss):** 15-50ms
- **Suggestions:** 1-5ms
- **Cache stats:** < 1ms
- **Health check:** < 1ms

### Response Sizes

- **Search (10 results):** ~5-10 KB
- **Suggestions:** ~1-2 KB
- **Cache stats:** ~0.5 KB

## Deployment

### Production Server

**Using Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 'kse.api:create_app()'
```

**Using uWSGI:**
```bash
uwsgi --http :8000 --wsgi-file app.py --master --processes 4
```

### Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "-m", "kse.api"]
```

```bash
docker build -t klar-search .
docker run -p 5000:5000 klar-search
```

## Configuration

### Environment Variables

```bash
# API Configuration
KSE_HOST=0.0.0.0
KSE_PORT=5000
KSE_DEBUG=false

# Database
KSE_DB_PATH=data/index.db

# Cache
KSE_CACHE_SIZE=5000
KSE_CACHE_TTL=3600

# Logging
KSE_LOG_LEVEL=INFO
```

## Examples

### JavaScript Fetch

```javascript
// Search
const response = await fetch('/api/search?q=python&limit=10');
const data = await response.json();

// Suggestions
const suggResponse = await fetch('/api/suggestions?q=py&limit=5');
const suggestions = await suggResponse.json();
```

### Python Requests

```python
import requests

# Search
response = requests.get('http://localhost:5000/api/search', 
    params={'q': 'python', 'limit': 10})
results = response.json()

# Suggestions
sugg_response = requests.get('http://localhost:5000/api/suggestions',
    params={'q': 'py', 'limit': 5})
suggestions = sugg_response.json()
```

### cURL

```bash
# Search
curl 'http://localhost:5000/api/search?q=python&limit=10'

# Suggestions
curl 'http://localhost:5000/api/suggestions?q=py'

# Cache stats
curl 'http://localhost:5000/api/stats/cache'

# Health
curl 'http://localhost:5000/api/health'
```

## Next Steps

Future enhancements:
- GraphQL endpoint
- WebSocket for real-time updates
- Advanced analytics dashboard
- Query history tracking
- User preferences
- Multi-language support
- Search filters UI
