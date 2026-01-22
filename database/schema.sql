-- 
-- Klar Search Engine (KSE) - PostgreSQL Production Schema
-- Swedish search engine database structure
-- Version: 1.0.0
--

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- Text search
CREATE EXTENSION IF NOT EXISTS ltree;   -- Hierarchical data

-- Configuration table
CREATE TABLE IF NOT EXISTS kse_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)
);

CREATE INDEX idx_kse_config_key ON kse_config(key);

-- Swedish domains (2,543 sites)
CREATE TABLE IF NOT EXISTS kse_domains (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100),
    trust_score FLOAT DEFAULT 0.5 CHECK (trust_score >= 0 AND trust_score <= 1),
    indexed BOOLEAN DEFAULT FALSE,
    last_crawl TIMESTAMP,
    pages_count INTEGER DEFAULT 0,
    last_change_detected TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT valid_domain CHECK (domain LIKE '%.se')
);

CREATE INDEX idx_kse_domains_indexed ON kse_domains(indexed);
CREATE INDEX idx_kse_domains_trust ON kse_domains(trust_score DESC);
CREATE INDEX idx_kse_domains_active ON kse_domains(is_active);

-- Indexed pages (2.8M+ pages)
CREATE TABLE IF NOT EXISTS kse_pages (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    domain_id INTEGER REFERENCES kse_domains(id) ON DELETE CASCADE,
    title TEXT,
    content TEXT,
    content_hash VARCHAR(32),
    status_code INTEGER,
    page_rank FLOAT DEFAULT 0.5,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP,
    CONSTRAINT valid_url CHECK (url ~ '^https?://')
);

CREATE INDEX idx_kse_pages_domain ON kse_pages(domain_id);
CREATE INDEX idx_kse_pages_url_hash ON kse_pages USING hash(url);
CREATE INDEX idx_kse_pages_page_rank ON kse_pages(page_rank DESC);
CREATE INDEX idx_kse_pages_active ON kse_pages(is_active);
CREATE INDEX idx_kse_pages_updated ON kse_pages(last_updated DESC);

-- Inverted index (word -> pages)
CREATE TABLE IF NOT EXISTS kse_index (
    id BIGSERIAL PRIMARY KEY,
    word VARCHAR(255) NOT NULL,
    page_id INTEGER REFERENCES kse_pages(id) ON DELETE CASCADE,
    frequency INTEGER DEFAULT 1 CHECK (frequency > 0),
    positions INTEGER[],
    tf_idf FLOAT,
    CONSTRAINT unique_word_page UNIQUE(word, page_id)
);

CREATE INDEX idx_kse_index_word ON kse_index(word);
CREATE INDEX idx_kse_index_page ON kse_index(page_id);
CREATE INDEX idx_kse_index_word_page ON kse_index(word, page_id);

-- Full-text search vector (PostgreSQL native)
CREATE TABLE IF NOT EXISTS kse_fts_index (
    id SERIAL PRIMARY KEY,
    page_id INTEGER UNIQUE REFERENCES kse_pages(id) ON DELETE CASCADE,
    fts_vector tsvector
);

CREATE INDEX idx_kse_fts ON kse_fts_index USING gin(fts_vector);

-- Search logs (analytics, no PII)
CREATE TABLE IF NOT EXISTS kse_search_log (
    id BIGSERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    query_hash VARCHAR(32),
    results_count INTEGER,
    search_time_ms FLOAT,
    intent VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kse_search_log_hash ON kse_search_log(query_hash);
CREATE INDEX idx_kse_search_log_timestamp ON kse_search_log(timestamp DESC);
CREATE INDEX idx_kse_search_log_intent ON kse_search_log(intent);

-- Crawl logs (diagnostics)
CREATE TABLE IF NOT EXISTS kse_crawl_log (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES kse_domains(id),
    pages_crawled INTEGER DEFAULT 0,
    pages_changed INTEGER DEFAULT 0,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(50),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kse_crawl_log_domain ON kse_crawl_log(domain_id);
CREATE INDEX idx_kse_crawl_log_status ON kse_crawl_log(status);
CREATE INDEX idx_kse_crawl_log_created ON kse_crawl_log(created_at DESC);

-- Suggestions cache (popular searches)
CREATE TABLE IF NOT EXISTS kse_suggestions (
    id SERIAL PRIMARY KEY,
    query TEXT UNIQUE NOT NULL,
    frequency INTEGER DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_promoted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_kse_suggestions_frequency ON kse_suggestions(frequency DESC);
CREATE INDEX idx_kse_suggestions_query ON kse_suggestions(query);

-- Backups metadata
CREATE TABLE IF NOT EXISTS kse_backups (
    id SERIAL PRIMARY KEY,
    backup_file VARCHAR(255),
    size_mb FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status VARCHAR(50)
);

CREATE INDEX idx_kse_backups_created ON kse_backups(created_at DESC);

-- System maintenance log
CREATE TABLE IF NOT EXISTS kse_maintenance_log (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(100),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kse_maintenance_log_status ON kse_maintenance_log(status);
CREATE INDEX idx_kse_maintenance_log_created ON kse_maintenance_log(created_at DESC);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO kse_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO kse_user;

-- Comment on tables
COMMENT ON TABLE kse_pages IS 'Indexed Swedish pages (2.8M+)';
COMMENT ON TABLE kse_index IS 'Inverted index for fast searching';
COMMENT ON TABLE kse_search_log IS 'Search analytics (NO PII)';
COMMENT ON TABLE kse_domains IS 'Swedish .se domains (2,543 total)';
