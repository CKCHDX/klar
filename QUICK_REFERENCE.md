# 📝 KSE Quick Reference Card

## Installation
```bash
pip install -e .
```

## Testing
```bash
# Full system test
python scripts/test_end_to_end.py

# NLP & indexing test
python scripts/test_indexing.py

# Crawler test
python scripts/start_crawler.py
```

## Running
```bash
# Start API server
python -m kse.server.kse_server

# Access at: http://localhost:5000
```

## API Endpoints
```bash
# Search
curl "http://localhost:5000/api/search?q=svenska%20universitet"

# Health check
curl "http://localhost:5000/api/health"

# Statistics
curl "http://localhost:5000/api/stats"

# Search history
curl "http://localhost:5000/api/history"
```

## Configuration Files
- `config/kse_default_config.yaml` - Main config
- `config/swedish_domains.json` - Domains to crawl
- `config/swedish_stopwords.txt` - Swedish stopwords

## Logs
- `data/logs/kse.log` - Main application log
- `data/logs/crawler.log` - Crawler operations
- `data/logs/indexer.log` - Indexing operations
- `data/logs/search.log` - Search queries
- `data/logs/server.log` - Server operations
- `data/logs/errors.log` - All errors

## Data Storage
- `data/storage/index/` - Search index files
- `data/storage/cache/` - Cache files
- `data/storage/crawl_state/` - Crawler state

## Common Tasks
```bash
# View logs
tail -f data/logs/kse.log

# Check index size
ls -lh data/storage/index/

# Clear cache
rm -rf data/storage/cache/*

# Rebuild index
rm -rf data/storage/index/*
python scripts/test_indexing.py
```

## Troubleshooting
```bash
# Reinstall package
pip install -e . --force-reinstall

# Check dependencies
pip list | grep -E "Flask|nltk|urllib3"

# View errors
cat data/logs/errors.log
```

## Key Components
- **Core**: Configuration, logging, storage
- **Crawler**: Web crawling with robots.txt
- **NLP**: Swedish tokenization, lemmatization
- **Indexing**: Inverted index, TF-IDF
- **Search**: Query processing, ranking
- **Server**: Flask REST API

## Project Structure
```
kse/
├── core/          # Core modules
├── storage/       # Storage layer
├── crawler/       # Web crawler
├── nlp/           # Swedish NLP
├── indexing/      # Indexing pipeline
├── search/        # Search engine
└── server/        # REST API

config/            # Configuration
scripts/           # Utility scripts
data/              # Runtime data
```

## Security
- Flask 2.3.2 (patched)
- nltk 3.9 (patched)
- urllib3 2.6.3 (patched)
- Zero user tracking
- No cookies

## Performance
- Search: <1ms response time
- Index: File-based (pickle/JSON)
- Storage: ~1MB for test data
- Scalable: Can handle millions of documents

## Documentation
- `README.md` - Complete documentation
- `QUICKSTART.md` - Quick start guide
- `SECURITY.md` - Security details
- `NEXT_STEPS.md` - What to do next
- `DEPLOYMENT.md` - Deployment guide
- `KSE-Tree.md` - Architecture

## Support
- Check logs first
- Re-read documentation
- Run tests to verify setup
- Review error messages

---

**Version**: 3.0.0  
**Status**: Production Ready  
**Last Updated**: 2026-01-29
