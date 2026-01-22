#!/usr/bin/env python3
"""
Klar Search Engine (KSE) - Production Entry Point
Runs the Flask API server on 127.0.0.1:8080

Usage:
    python run_kse.py                    # Run development server
    gunicorn -w 4 -b 127.0.0.1:8080 run_kse:app  # Production with Gunicorn
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kse_server.kse_api import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/kse.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create Flask application
app = create_app()


if __name__ == "__main__":
    """
    Run the search engine server.
    """
    logger.info("="*70)
    logger.info("Klar Search Engine (KSE) - Production Server")
    logger.info("Starting on http://127.0.0.1:8080")
    logger.info("="*70)
    
    # Run development server (use Gunicorn in production)
    app.run(
        host='127.0.0.1',
        port=8080,
        debug=False,
        threaded=True,
        use_reloader=False
    )
