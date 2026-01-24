"""
KSE Database Module

Provides database initialization, migrations, and schema management
for the Klar Search Engine.
"""

from .kse_database_init import (
    KSEDatabase,
    initialize_database,
    get_db_connection,
)

from .kse_schema import (
    SCHEMA_TABLES,
    SCHEMA_INDEXES,
    create_schema,
)

__version__ = "1.0.0"
__all__ = [
    "KSEDatabase",
    "initialize_database",
    "get_db_connection",
    "SCHEMA_TABLES",
    "SCHEMA_INDEXES",
    "create_schema",
]
