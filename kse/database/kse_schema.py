"""
KSE Database Schema Definition

Defines all tables, columns, and indexes for the Klar Search Engine database.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Column:
    """Represents a database column."""
    name: str
    type: str
    nullable: bool = False
    primary_key: bool = False
    unique: bool = False
    default: str = None
    index: bool = False


@dataclass
class Table:
    """Represents a database table."""
    name: str
    columns: List[Column]
    description: str = ""


# ============================================================================
# TABLE DEFINITIONS
# ============================================================================

DOMAINS = Table(
    name="domains",
    description="Swedish domains to crawl",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("url", "VARCHAR(255)", unique=True, index=True),
        Column("domain_name", "VARCHAR(255)", index=True),
        Column("category", "VARCHAR(100)", index=True),
        Column("trust_score", "DECIMAL(3,2)", default="0.50"),
        Column("crawl_priority", "INTEGER", default="5"),
        Column("last_crawled", "TIMESTAMP", nullable=True),
        Column("next_crawl", "TIMESTAMP", nullable=True),
        Column("status", "VARCHAR(20)", default="'pending'"),  # pending, active, inactive, error
        Column("error_count", "INTEGER", default="0"),
        Column("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        Column("updated_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ]
)

PAGES = Table(
    name="pages",
    description="Crawled web pages",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("domain_id", "INTEGER", index=True),
        Column("url", "TEXT", unique=True, index=True),
        Column("title", "VARCHAR(255)", nullable=True),
        Column("description", "TEXT", nullable=True),
        Column("content", "TEXT", nullable=True),
        Column("content_hash", "VARCHAR(64)", index=True),
        Column("language", "VARCHAR(5)", default="'sv'"),
        Column("status_code", "INTEGER", nullable=True),
        Column("crawl_time", "TIMESTAMP", index=True),
        Column("last_modified", "TIMESTAMP", nullable=True),
        Column("content_type", "VARCHAR(50)", nullable=True),
        Column("size_bytes", "INTEGER", nullable=True),
        Column("outgoing_links", "INTEGER", default="0"),
        Column("indexed", "BOOLEAN", default="false", index=True),
        Column("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        Column("updated_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ]
)

TERMS = Table(
    name="terms",
    description="Indexed search terms",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("term", "VARCHAR(255)", unique=True, index=True),
        Column("term_type", "VARCHAR(20)", default="'word'"),  # word, phrase, entity
        Column("language", "VARCHAR(5)", default="'sv'"),
        Column("frequency", "BIGINT", default="0"),
        Column("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ]
)

INVERTED_INDEX = Table(
    name="inverted_index",
    description="Inverted index mapping terms to pages",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("term_id", "INTEGER", index=True),
        Column("page_id", "INTEGER", index=True),
        Column("position", "INTEGER"),  # Word position in page
        Column("frequency", "INTEGER", default="1"),  # Term frequency in page
        Column("field", "VARCHAR(20)", default="'content'"),  # title, description, content
        Column("tf_idf_score", "DECIMAL(8,6)"),  # Precomputed TF-IDF
        Column("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ]
)

PAGE_RANKS = Table(
    name="page_ranks",
    description="PageRank-style scores for pages",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("page_id", "INTEGER", unique=True, index=True),
        Column("rank_score", "DECIMAL(10,8)"),  # Normalized 0-1
        Column("inbound_links", "INTEGER", default="0"),
        Column("outbound_links", "INTEGER", default="0"),
        Column("updated_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ]
)

LINKS = Table(
    name="links",
    description="Links between pages",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("source_page_id", "INTEGER", index=True),
        Column("target_page_id", "INTEGER", index=True, nullable=True),
        Column("target_url", "TEXT", nullable=True),
        Column("anchor_text", "VARCHAR(255)", nullable=True),
        Column("link_type", "VARCHAR(20)", default="'internal'"),  # internal, external, broken
        Column("discovered_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ]
)

METADATA = Table(
    name="metadata",
    description="Page metadata and computed values",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("page_id", "INTEGER", unique=True, index=True),
        Column("domain_id", "INTEGER", index=True),
        Column("freshness_score", "DECIMAL(3,2)"),  # How fresh (0-1)
        Column("authority_score", "DECIMAL(3,2)"),  # Domain authority (0-1)
        Column("spam_score", "DECIMAL(3,2)"),  # Spam likelihood (0-1)
        Column("content_quality", "DECIMAL(3,2)"),  # Content quality (0-1)
        Column("user_signals", "INTEGER", default="0"),  # CTR, dwell time aggregate
        Column("updated_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
    ]
)

CACHE = Table(
    name="cache",
    description="Search result cache",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("query_hash", "VARCHAR(64)", unique=True, index=True),
        Column("query_text", "TEXT"),
        Column("results_json", "TEXT"),  # Cached results as JSON
        Column("hit_count", "INTEGER", default="0"),
        Column("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        Column("expires_at", "TIMESTAMP", index=True),
    ]
)

CRAWL_QUEUE = Table(
    name="crawl_queue",
    description="URLs waiting to be crawled",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("url", "TEXT", unique=True, index=True),
        Column("domain_id", "INTEGER", index=True, nullable=True),
        Column("priority", "INTEGER", default="5", index=True),
        Column("retry_count", "INTEGER", default="0"),
        Column("status", "VARCHAR(20)", default="'pending'"),  # pending, processing, done, failed
        Column("error_message", "TEXT", nullable=True),
        Column("added_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        Column("processed_at", "TIMESTAMP", nullable=True),
    ]
)

CRAWL_LOGS = Table(
    name="crawl_logs",
    description="Crawl activity logs",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("domain_id", "INTEGER", index=True, nullable=True),
        Column("url", "TEXT", nullable=True),
        Column("event_type", "VARCHAR(50)"),  # fetched, parsed, indexed, error, etc.
        Column("status_code", "INTEGER", nullable=True),
        Column("duration_ms", "INTEGER", nullable=True),
        Column("message", "TEXT", nullable=True),
        Column("timestamp", "TIMESTAMP", default="CURRENT_TIMESTAMP", index=True),
    ]
)

STATISTICS = Table(
    name="statistics",
    description="System statistics and metrics",
    columns=[
        Column("id", "SERIAL", primary_key=True),
        Column("metric_name", "VARCHAR(100)", index=True),
        Column("metric_value", "BIGINT"),
        Column("timestamp", "TIMESTAMP", default="CURRENT_TIMESTAMP", index=True),
    ]
)

# ============================================================================
# SCHEMA EXPORT
# ============================================================================

SCHEMA_TABLES = [
    DOMAINS,
    PAGES,
    TERMS,
    INVERTED_INDEX,
    PAGE_RANKS,
    LINKS,
    METADATA,
    CACHE,
    CRAWL_QUEUE,
    CRAWL_LOGS,
    STATISTICS,
]

SCHEMA_INDEXES = {
    "pages": [
        ("domain_id", "pages_domain_id_idx"),
        ("url", "pages_url_idx"),
        ("indexed", "pages_indexed_idx"),
        ("crawl_time", "pages_crawl_time_idx"),
    ],
    "inverted_index": [
        ("term_id", "inv_idx_term_id_idx"),
        ("page_id", "inv_idx_page_id_idx"),
        ("(term_id, page_id)", "inv_idx_term_page_idx"),
    ],
    "domains": [
        ("domain_name", "domains_name_idx"),
        ("category", "domains_category_idx"),
        ("status", "domains_status_idx"),
    ],
    "terms": [
        ("term", "terms_term_idx"),
        ("language", "terms_language_idx"),
    ],
}


def get_create_table_sql(table: Table) -> str:
    """Generate CREATE TABLE SQL for a table definition."""
    cols = []
    for col in table.columns:
        col_def = f"{col.name} {col.type}"
        if col.primary_key:
            col_def += " PRIMARY KEY"
        if not col.nullable and not col.primary_key:
            col_def += " NOT NULL"
        if col.unique:
            col_def += " UNIQUE"
        if col.default:
            col_def += f" DEFAULT {col.default}"
        cols.append(col_def)
    
    return f"CREATE TABLE IF NOT EXISTS {table.name} ({', '.join(cols)});"


def create_schema() -> List[str]:
    """Generate all CREATE TABLE statements."""
    statements = []
    for table in SCHEMA_TABLES:
        statements.append(get_create_table_sql(table))
    return statements
