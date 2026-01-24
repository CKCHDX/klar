"""
KSE Database Layer

Core database functionality for Klar Swedish Engine.
Handles PostgreSQL connection pooling, schema management, and data access.
"""

from kse.database.kse_database_connection import (
    DatabaseConnection,
    get_connection_pool,
    close_connection_pool,
    test_connection,
)
from kse.database.kse_database_schema import DatabaseSchema
from kse.database.kse_domain_loader import DomainLoader
from kse.database.kse_repository import Repository
from kse.database.kse_database_backup import BackupManager
from kse.database.kse_database_migrations import (
    MigrationManager,
    Migration,
    Migration001InitialSchema,
)
from kse.database.kse_database_consistency import ConsistencyChecker

__all__ = [
    # Connection management
    "DatabaseConnection",
    "get_connection_pool",
    "close_connection_pool",
    "test_connection",
    # Schema and initialization
    "DatabaseSchema",
    "DomainLoader",
    # Data access
    "Repository",
    # Maintenance
    "BackupManager",
    "MigrationManager",
    "Migration",
    "Migration001InitialSchema",
    "ConsistencyChecker",
]
