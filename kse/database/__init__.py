"""
KSE Database Layer

Core database functionality for Klar Swedish Engine.
Handles PostgreSQL connection pooling, schema management, and data access.
"""

from kse.database.kse_database_connection import (
    DatabaseConnection,
    get_connection_pool,
    close_connection_pool,
)
from kse.database.kse_database_schema import DatabaseSchema
from kse.database.kse_domain_loader import DomainLoader
from kse.database.kse_repository import Repository

__all__ = [
    "DatabaseConnection",
    "get_connection_pool",
    "close_connection_pool",
    "DatabaseSchema",
    "DomainLoader",
    "Repository",
]
