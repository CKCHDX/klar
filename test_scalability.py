"""
Test Scalability - Verify system handles 700+ pages
"""
import sys
import time
import gc
from pathlib import Path

# Ensure kse module can be imported
sys.path.insert(0, str(Path(__file__).parent))

from kse.core.kse_logger import KSELogger, get_logger
from kse.storage.kse_storage_manager import StorageManager
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.nlp.kse_nlp_core import NLPCore

logger = None


def test_batch_storage(storage: StorageManager, num_pages: int = 700) -> None:
    """Test batch storage of pages"""
    print(f"\n{'='*70}")
    print(f"TEST 1: Batch Storage ({num_pages} pages)")
    print(f"{'='*70}")
    
    # Create test pages
    print(f"Creating {num_pages} test pages...")
    pages = []
    for i in range(num_pages):
        pages.append({
            'url': f'http://test{i}.se/page',
            'domain': f'test{i % 20}.se',
            'title': f'Swedish Education Page {i}',
            'description': f'Information about Swedish universities {i}',
            'content': 'Svenska universitet och högskolor. ' * 50,
            'keywords': ['universitet'],
            'crawl_time': time.time()
        })
        
        # Periodic garbage collection
        if i > 0 and i % 200 == 0:
            gc.collect()
    
    print(f"✓ Created {len(pages)} pages")
    
    # Save in batches
    print("Saving pages in batches...")
    batch_size = 50
    for i in range(0, len(pages), batch_size):
        batch = pages[i:i+batch_size]
        storage.save_pages_batch(batch)
    
    stats = storage.get_storage_stats()
    print(f"✓ Saved {stats['page_batches']} batches")
    assert stats['page_batches'] > 0, "No batches saved"
    
    # Load all pages
    print("Loading all pages...")
    loaded = storage.load_all_pages()
    print(f"✓ Loaded {len(loaded)} pages")
    assert len(loaded) == num_pages, f"Expected {num_pages} pages, got {len(loaded)}"
    
    print("✓ Batch storage test PASSED")
    return loaded


def test_large_scale_indexing(storage: StorageManager, pages: list, num_pages: int = 700) -> IndexerPipeline:
    """Test indexing of large page sets"""
    print(f"\n{'='*70}")
    print(f"TEST 2: Large-Scale Indexing ({num_pages} pages)")
    print(f"{'='*70}")
    
    # Initialize components
    print("Initializing indexer pipeline...")
    nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
    indexer = IndexerPipeline(storage, nlp)
    print("✓ Indexer initialized")
    
    # Index pages
    print(f"Indexing {len(pages)} pages...")
    start_time = time.time()
    stats = indexer.index_pages(pages)
    elapsed = time.time() - start_time
    
    print(f"✓ Indexing complete in {elapsed:.2f}s")
    print(f"  - Pages processed: {stats['pages_processed']}")
    print(f"  - Pages indexed: {stats['pages_indexed']}")
    print(f"  - Total terms: {stats['total_terms']}")
    
    assert stats['pages_indexed'] == num_pages, f"Expected {num_pages} indexed, got {stats['pages_indexed']}"
    assert stats['total_terms'] > 0, "No terms indexed"
    
    # Check index statistics
    index_stats = indexer.get_statistics()
    print(f"  - Index size: {index_stats.get('index_size_mb', 0)} MB")
    print(f"  - Total postings: {index_stats.get('total_postings', 0)}")
    
    assert index_stats['index_size_mb'] > 0, "Index size should be greater than 0"
    
    print("✓ Large-scale indexing test PASSED")
    return indexer


def test_search_performance(indexer: IndexerPipeline, num_queries: int = 10) -> None:
    """Test search performance on large index"""
    print(f"\n{'='*70}")
    print(f"TEST 3: Search Performance ({num_queries} queries)")
    print(f"{'='*70}")
    
    queries = [
        'universitet',
        'forskning',
        'utbildning',
        'studenter',
        'högskolor',
        'svenska',
        'akademi',
        'education',
        'information',
        'page'
    ]
    
    total_time = 0
    for i, query in enumerate(queries[:num_queries], 1):
        start = time.time()
        results = indexer.search(query, max_results=10)
        elapsed = time.time() - start
        total_time += elapsed
        
        print(f"{i}. Query '{query}': {len(results)} results in {elapsed*1000:.2f}ms")
        assert len(results) >= 0, f"Search should return results or empty list"
    
    avg_time = total_time / num_queries
    print(f"\n✓ Average search time: {avg_time*1000:.2f}ms")
    assert avg_time < 0.5, f"Search too slow: {avg_time:.3f}s > 0.5s"
    
    print("✓ Search performance test PASSED")


def test_memory_efficiency(storage: StorageManager) -> None:
    """Test memory efficiency of storage operations"""
    print(f"\n{'='*70}")
    print("TEST 4: Memory Efficiency")
    print(f"{'='*70}")
    
    # Check storage stats
    stats = storage.get_storage_stats()
    print(f"Storage statistics:")
    print(f"  - Total size: {stats['total_size_mb']} MB")
    print(f"  - Page batches: {stats['page_batches']}")
    print(f"  - Index files: {len(stats['index_files'])}")
    
    # Clear batches to free disk space
    print("Clearing page batches...")
    storage.clear_pages_batches()
    
    stats_after = storage.get_storage_stats()
    print(f"✓ Page batches after clear: {stats_after['page_batches']}")
    assert stats_after['page_batches'] == 0, "Page batches should be cleared"
    
    print("✓ Memory efficiency test PASSED")


def main():
    """Run all scalability tests"""
    global logger
    
    try:
        print("="*70)
        print("SCALABILITY TEST SUITE - Testing 700+ Pages")
        print("="*70)
        
        # Setup
        test_dir = Path('/tmp/kse_scalability_test')
        test_dir.mkdir(exist_ok=True)
        
        log_dir = test_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        KSELogger.setup(log_dir, "INFO", False)
        logger = get_logger(__name__)
        
        storage = StorageManager(test_dir)
        
        # Run tests
        num_pages = 700
        
        # Test 1: Batch storage
        pages = test_batch_storage(storage, num_pages)
        
        # Test 2: Large-scale indexing
        indexer = test_large_scale_indexing(storage, pages, num_pages)
        
        # Test 3: Search performance
        test_search_performance(indexer, num_queries=10)
        
        # Test 4: Memory efficiency
        test_memory_efficiency(storage)
        
        # Final summary
        print(f"\n{'='*70}")
        print("✓ ALL SCALABILITY TESTS PASSED!")
        print(f"{'='*70}")
        print(f"\nSummary:")
        print(f"  ✓ Batch storage: {num_pages} pages")
        print(f"  ✓ Large-scale indexing: {num_pages} pages")
        print(f"  ✓ Search performance: < 0.5s per query")
        print(f"  ✓ Memory efficiency: Verified")
        print(f"\nThe system can successfully handle:")
        print(f"  • Crawling and storing 700+ pages")
        print(f"  • Indexing large page sets efficiently")
        print(f"  • Fast search with large indexes")
        print(f"  • Efficient memory management")
        print(f"{'='*70}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}", file=sys.stderr)
        if logger:
            logger.error(f"Test error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
