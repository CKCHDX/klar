#!/usr/bin/env python3
"""
KSE Database Initialization Script

Initializes PostgreSQL database with schema and loads 2,543 Swedish domains.

Usage:
    python init_database.py --host localhost --port 5432 --user postgres
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kse.database import (
    get_connection_pool,
    close_connection_pool,
    DatabaseSchema,
    DomainLoader,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_init.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def initialize_database(
    host: str = "localhost",
    port: int = 5432,
    database: str = "kse_db",
    user: str = "postgres",
    password: str = "postgres",
    drop_existing: bool = False
) -> bool:
    """Initialize KSE database from scratch.
    
    Args:
        host: PostgreSQL host
        port: PostgreSQL port
        database: Database name
        user: Database user
        password: Database password
        drop_existing: If True, drop existing schema first
    
    Returns:
        bool: True if successful
    """
    
    logger.info("="*60)
    logger.info("KSE DATABASE INITIALIZATION")
    logger.info("="*60)
    logger.info(f"Host: {host}:{port}")
    logger.info(f"Database: {database}")
    logger.info(f"User: {user}")
    
    try:
        # Get connection pool
        logger.info("Connecting to PostgreSQL...")
        db_connection = get_connection_pool(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        
        # Get actual connection
        with db_connection.get_connection_context() as conn:
            
            # Initialize schema
            logger.info("Initializing database schema...")
            schema = DatabaseSchema(conn)
            
            if drop_existing:
                logger.warning("Dropping existing schema...")
                schema.drop_schema(confirm=True)
            
            # Create schema
            if not schema.create_schema():
                logger.error("Failed to create schema")
                return False
            
            logger.info("✓ Schema created successfully")
            
            # Validate schema
            validation = schema.validate_schema()
            logger.info(f"Schema validation: {validation}")
            
            if not all(validation.values()):
                logger.error("Schema validation failed")
                return False
            
            logger.info("✓ Schema validation passed")
            
            # Load domains
            logger.info("Loading 2,543 Swedish domains...")
            loader = DomainLoader(conn)
            
            if not loader.load_domains(clear_existing=drop_existing):
                logger.error("Failed to load domains")
                return False
            
            logger.info(f"✓ Loaded {loader.get_domain_count()} domains")
            
            # Get statistics
            logger.info("\n" + "="*60)
            logger.info("INITIALIZATION COMPLETE")
            logger.info("="*60)
            
            domain_count = loader.get_domain_count()
            logger.info(f"Total Domains: {domain_count}")
            logger.info(f"Status: Ready for crawling")
            logger.info("="*60)
            
            return True
    
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        return False
    
    finally:
        close_connection_pool()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize KSE database"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="PostgreSQL host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5432,
        help="PostgreSQL port (default: 5432)"
    )
    parser.add_argument(
        "--database",
        default="kse_db",
        help="Database name (default: kse_db)"
    )
    parser.add_argument(
        "--user",
        default="postgres",
        help="Database user (default: postgres)"
    )
    parser.add_argument(
        "--password",
        default="postgres",
        help="Database password (default: postgres)"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing schema before creating"
    )
    
    args = parser.parse_args()
    
    # Run initialization
    success = initialize_database(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
        drop_existing=args.drop
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
