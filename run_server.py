#!/usr/bin/env python3
"""
Klar Search Engine - Main Server

Runnable entry point for the API server.

Usage:
    python run_server.py                    # Default: http://localhost:5000
    python run_server.py --port 8000       # Custom port
    python run_server.py --host 0.0.0.0    # Custom host
    python run_server.py --debug            # Debug mode
"""

import argparse
import sys
from pathlib import Path

from kse.api.kse_api_server import KSEAPIServer, KSESearchEngine
from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description='Klar Search Engine API Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_server.py                        # Default (localhost:5000)
  python run_server.py --port 8000           # Custom port
  python run_server.py --host 0.0.0.0        # Public access
  python run_server.py --debug               # Debug mode
  python run_server.py --db data/index.db    # Custom database
        """
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Server host (default: 0.0.0.0)',
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Server port (default: 5000)',
    )
    
    parser.add_argument(
        '--db',
        default='data/index.db',
        help='Path to database (default: data/index.db)',
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode',
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of worker processes (default: 4)',
    )
    
    args = parser.parse_args()
    
    try:
        # Check database exists
        db_path = Path(args.db)
        if not db_path.exists():
            logger.error(f"Database not found: {db_path}")
            logger.info("Please run: python -m kse.indexer")
            return 1
        
        # Initialize search engine
        logger.info(f"Initializing search engine with database: {args.db}")
        engine = KSESearchEngine(args.db)
        
        # Create and run server
        logger.info(f"Starting API server on {args.host}:{args.port}")
        server = KSEAPIServer(
            engine,
            host=args.host,
            port=args.port,
            debug=args.debug,
        )
        
        logger.info("""\n
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🔍 Klar Search Engine - API Server                   ║
║                                                              ║
║  Web Interface:  http://localhost:{:<37} ║
║  API Base:       http://localhost:{}/api                    ║
║                                                              ║
║  Endpoints:                                                  ║
║    GET /api/search?q=query             Search               ║
║    GET /api/suggestions?q=query        Suggestions          ║
║    GET /api/related?id=page_id         Related              ║
║    GET /api/stats/cache                Cache stats          ║
║    GET /api/health                     Health check         ║
║    GET /api/info/index                 Index info           ║
║                                                              ║
║  Press Ctrl+C to stop                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """.format(args.port, args.port))
        
        server.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
