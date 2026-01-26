"""
kse/indexing/__init__.py - Search Indexing Pipeline API

Components:
  - IndexerPipeline: Main indexing orchestrator
  - InvertedIndex: Inverted index data structure
  - TFIDFCalculator: TF-IDF score computation
  - PageProcessor: Page content processing
  - MetadataExtractor: Metadata extraction
  - IndexBuilder: Index building & optimization
  - IndexStatistics: Statistics tracking
  - IncrementalIndexing: Incremental updates

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_indexer_pipeline import IndexerPipeline, KSEIndexingException
from .kse_inverted_index import InvertedIndex
from .kse_tf_idf_calculator import TFIDFCalculator
from .kse_page_processor import PageProcessor
from .kse_metadata_extractor import MetadataExtractor
from .kse_index_builder import IndexBuilder
from .kse_index_statistics import IndexStatistics
from .kse_incremental_indexing import IncrementalIndexing

__all__ = [
    # Core
    "IndexerPipeline",
    
    # Index Structure
    "InvertedIndex",
    
    # Scoring
    "TFIDFCalculator",
    
    # Processing
    "PageProcessor",
    "MetadataExtractor",
    
    # Building
    "IndexBuilder",
    "IndexStatistics",
    
    # Updates
    "IncrementalIndexing",
    
    # Exceptions
    "KSEIndexingException",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - Indexing Layer

1. Index crawled pages:
    from kse.indexing import IndexerPipeline
    from kse.storage import StorageManager
    from kse.cache import CacheManager
    
    storage = StorageManager()
    cache = CacheManager()
    indexer = IndexerPipeline(storage, cache)
    stats = indexer.index_pages(crawled_pages)

2. Inverted index:
    from kse.indexing import InvertedIndex
    
    index = InvertedIndex()
    index.add_document("url1", ["token1", "token2"])
    docs = index.search(["token1"])

3. TF-IDF scoring:
    from kse.indexing import TFIDFCalculator
    
    tfidf = TFIDFCalculator()
    score = tfidf.calculate_tfidf(tf=0.5, idf=2.0)

4. Page processing:
    from kse.indexing import PageProcessor
    
    processor = PageProcessor()
    processed = processor.process_page(page)
    tokens = processed['processed_tokens']

5. Metadata extraction:
    from kse.indexing import MetadataExtractor
    
    extractor = MetadataExtractor()
    metadata = extractor.extract(page)

6. Index building:
    from kse.indexing import IndexBuilder
    
    builder = IndexBuilder()
    stats = builder.build_index(pages)
    opt_stats = builder.optimize_index()

7. Index statistics:
    from kse.indexing import IndexStatistics
    
    stats = IndexStatistics()
    stats.calculate_statistics(index, pages, build_time)
    print(stats.get_summary())

8. Incremental updates:
    from kse.indexing import IncrementalIndexing
    
    updater = IncrementalIndexing(index)
    result = updater.add_page(new_page)
    updater.remove_page(old_url)

ARCHITECTURE:

kse/indexing/
├── kse_indexer_pipeline.py         Main orchestrator
├── kse_inverted_index.py           Index structure
├── kse_tf_idf_calculator.py        TF-IDF scoring
├── kse_page_processor.py           Page processing
├── kse_metadata_extractor.py       Metadata extraction
├── kse_index_builder.py            Index building
├── kse_index_statistics.py         Statistics
├── kse_incremental_indexing.py     Incremental updates
└── __init__.py                     Public API

INTEGRATION:

- Phase 4 (crawler): Provides crawled pages as input
- Phase 5 (nlp): Processes text with NLP
- Phase 7 (ranking): Uses index for ranking
- Phase 8 (search): Searches the index

DATA FLOW:

Crawled Pages (Phase 4)
    ↓
Page Processing (NLP)
    ↓
TF-IDF Calculation
    ↓
Inverted Index Building
    ↓
Metadata Extraction
    ↓
Index Optimization
    ↓
Save to Storage (Phase 2)
    ↓
Cache Results (Phase 3)
    ↓
Ready for Search & Ranking!

FEATURES:

Building:
  - Full index construction (2.8M pages)
  - TF-IDF scoring
  - Inverted index creation
  - Metadata extraction

Optimization:
  - Noise removal (low-frequency terms)
  - Compression for storage
  - Performance tuning
  - Index statistics

Updates:
  - Add new pages incrementally
  - Remove outdated pages
  - Update changed pages
  - Maintain consistency
"""
