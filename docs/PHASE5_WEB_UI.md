# Klar Search Engine - Phase 5: Web UI Implementation

## Overview

Phase 5 implements the complete web user interface for the Klar Search Engine, including:

- Responsive web design
- Search results display
- Pagination and navigation
- Autocomplete functionality
- Statistics dashboard
- Error handling
- API endpoints

## Architecture

```
Web UI Layer (Phase 5)
├── Frontend (Client-side)
│   ├── HTML Templates (Jinja2)
│   ├── CSS Styling
│   └── JavaScript Interactivity
├── Backend (Server-side)
│   ├── Flask Routes
│   ├── API Endpoints
│   └── Error Handling
└── Testing
    ├── Unit Tests
    ├── Integration Tests
    └── E2E Tests
```

## Components

### Frontend Structure

```
kse/templates/
├── base.html              # Base template
├── index.html             # Home page
├── search_results.html    # Results page
├── 404.html              # 404 error
├── 500.html              # 500 error
└── error.html            # Generic error

kse/static/
├── css/
│   └── style.css         # Main stylesheet
├── js/
│   └── main.js          # Frontend JavaScript
└── img/
    └── [assets]
```

### API Endpoints

#### Search
```
GET /api/search
Parameters:
  - q (required): Search query
  - limit (optional): Results per page (1-100, default 10)
  - offset (optional): Pagination offset (default 0)

Response:
{
  "query": "search term",
  "results": [
    {
      "url": "https://example.com",
      "title": "Page title",
      "snippet": "Preview snippet",
      "score": 0.95,
      "last_updated": "2026-01-24"
    }
  ],
  "total_results": 1234,
  "search_time": 45,
  "page": 1,
  "pages": 124
}
```

#### Autocomplete
```
GET /api/autocomplete
Parameters:
  - q (optional): Query prefix

Response:
{
  "suggestions": [
    "suggestion 1",
    "suggestion 2",
    "suggestion 3"
  ]
}
```

#### Statistics
```
GET /api/stats

Response:
{
  "total_pages": 2543210,
  "total_terms": 1234567,
  "total_domains": 2543,
  "avg_search_time": 45.5,
  "index_size_mb": 4200,
  "last_updated": "2026-01-24T16:00:00Z"
}
```

#### Similar Pages
```
GET /api/similar/{url}

Response:
{
  "similar_pages": [
    {
      "url": "https://related.com",
      "title": "Related page",
      "score": 0.87
    }
  ]
}
```

#### Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2026-01-24T16:00:00Z",
  "version": "1.0.0"
}
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- Flask 2.0+
- Jinja2 2.11+
- Modern web browser

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/CKCHDX/klar.git
   cd klar
   ```

2. **Checkout phase 5 branch**
   ```bash
   git checkout ksesc
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run development server**
   ```bash
   python -m kse.server.kse_flask_app
   ```

5. **Access the UI**
   - Open browser to `http://localhost:5000`

## Configuration

### Environment Variables

```bash
# Server
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_ENV=development  # development or production

# Search Engine
SEARCH_INDEX_PATH=/path/to/index
SEARCH_CACHE_SIZE=1000

# UI
RESULTS_PER_PAGE=10
MAX_QUERY_LENGTH=500

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### config.py

```python
class Config:
    """Base configuration."""
    SECRET_KEY = 'your-secret-key'
    RESULTS_PER_PAGE = 10
    MAX_QUERY_LENGTH = 500
    CACHE_TTL = 300  # seconds

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
```

## Development

### Running Tests

```bash
# All tests
pytest

# Web UI tests only
pytest tests/test_web_ui.py -v

# Specific test class
pytest tests/test_web_ui.py::TestSearchAPI -v

# With coverage
pytest --cov=kse tests/
```

### Frontend Development

#### CSS Modifications

Edit `kse/static/css/style.css`:

```css
/* CSS Variables */
:root {
    --primary: #2172e5;
    --text-primary: #212121;
    /* ... */
}

/* Component Styles */
.btn {
    /* ... */
}
```

#### JavaScript Development

Edit `kse/static/js/main.js`:

```javascript
// API Functions
async function apiSearch(query) {
    // ...
}

// Event Handlers
document.addEventListener('DOMContentLoaded', () => {
    setupAutocomplete();
    setupResultInteractions();
});
```

### Adding New Templates

Create new template in `kse/templates/`:

```html
{% extends "base.html" %}

{% block title %}Page Title - Klar{% endblock %}

{% block content %}
<div class="container">
    <h1>Content</h1>
</div>
{% endblock %}
```

## Deployment

### Docker Deployment

1. **Build Docker image**
   ```bash
   docker build -t klar-search:latest .
   ```

2. **Run container**
   ```bash
   docker run -p 5000:5000 -e FLASK_ENV=production klar-search:latest
   ```

### Production Server (Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 'kse.server.kse_flask_app:create_app()'
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name search.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Performance Optimization

### Caching Strategy

- **Page Cache**: Shared search results (300s TTL)
- **Stats Cache**: Statistics endpoint (3600s TTL)
- **Browser Cache**: Static assets (1 year)

### Request Optimization

- **Pagination**: Limit results to 10-50 per page
- **Compression**: Enable gzip compression
- **CDN**: Serve static assets from CDN

### Database Optimization

- **Indexing**: Index query terms and scores
- **Sharding**: Distribute index across servers
- **Caching Layer**: Redis for frequent queries

## Security Considerations

### Input Validation

```python
# Validate query length
if len(query) < 2 or len(query) > MAX_QUERY_LENGTH:
    raise ValueError("Invalid query length")

# Sanitize HTML entities
query = escape(query)
```

### Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
```

### CORS Headers

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {"origins": ["*"]}
})
```

## Monitoring & Logging

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics

- Search volume
- Average response time
- Error rates
- Cache hit ratio

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9
   ```

2. **Template Not Found**
   - Verify template path in `kse/templates/`
   - Check Jinja2 configuration

3. **Static Files Not Loading**
   - Verify static files in `kse/static/`
   - Check Flask static folder configuration

## Future Enhancements

- [ ] Advanced search filters
- [ ] Search history
- [ ] User preferences
- [ ] Export results
- [ ] Mobile app
- [ ] Voice search
- [ ] Search analytics dashboard

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Template Engine](https://jinja.palletsprojects.com/)
- [Bootstrap CSS Framework](https://getbootstrap.com/)
- [Modern Web Standards](https://developer.mozilla.org/)

## Support

For issues or questions:
- GitHub Issues: https://github.com/CKCHDX/klar/issues
- Email: contact@oscyra.solutions

## License

See LICENSE file in repository.
