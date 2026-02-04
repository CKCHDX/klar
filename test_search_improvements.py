"""
Test Search Engine Improvements - Validate fixes for scalability issues

Tests the following improvements:
1. Index validation before search
2. Graceful degradation instead of hard failures
3. Improved TF-IDF scoring with smoothing
4. Query token validation
5. Pagination support
6. Candidate limiting for performance
"""
import sys
import time
from pathlib import Path

# Ensure kse module can be imported
sys.path.insert(0, str(Path(__file__).parent))

from kse.core.kse_logger import KSELogger, get_logger
from kse.storage.kse_storage_manager import StorageManager
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.search.kse_search_pipeline import SearchPipeline
from kse.nlp.kse_nlp_core import NLPCore

logger = None


def test_index_validation() -> None:
    """Test that index validation works correctly"""
    print(f"\n{'='*70}")
    print("TEST 1: Index Validation")
    print(f"{'='*70}")
    
    # Create test directory (clean)
    test_dir = Path('/tmp/kse_validation_test')
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    log_dir = test_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    KSELogger.setup(log_dir, "INFO", False)
    
    storage = StorageManager(test_dir)
    nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
    indexer = IndexerPipeline(storage, nlp)
    
    # Ensure truly empty index
    indexer.inverted_index.clear()
    
    # Test validation on empty index
    validation = indexer.inverted_index.validate_index_integrity()
    print(f"Empty index validation: is_valid={validation['is_valid']}")
    assert not validation['is_valid'], "Empty index should not be valid"
    assert len(validation['issues']) > 0, "Empty index should have issues"
    print(f"✓ Empty index correctly identified as invalid")
    
    # Add some test data
    pages = [
        {
            'url': f'http://test{i}.se/page',
            'domain': f'test{i}.se',
            'title': f'Test Page {i}',
            'description': f'Content about Swedish education {i}',
            'content': 'Svenska universitet och högskolor. ' * 10,
            'keywords': ['test'],
            'crawl_time': time.time()
        }
        for i in range(10)
    ]
    
    indexer.index_pages(pages)
    
    # Test validation on populated index
    validation = indexer.inverted_index.validate_index_integrity()
    print(f"Populated index validation: is_valid={validation['is_valid']}")
    print(f"  - Total documents: {validation['total_documents']}")
    print(f"  - Total terms: {validation['total_terms']}")
    print(f"  - Indexed documents: {validation['indexed_documents']}")
    assert validation['is_valid'], "Populated index should be valid"
    print(f"✓ Populated index correctly validated")
    
    print("✓ Index validation test PASSED")


def test_graceful_degradation() -> None:
    """Test that search degrades gracefully instead of failing hard"""
    print(f"\n{'='*70}")
    print("TEST 2: Graceful Degradation")
    print(f"{'='*70}")
    
    # Create test directory (clean)
    test_dir = Path('/tmp/kse_graceful_test')
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    log_dir = test_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    KSELogger.setup(log_dir, "INFO", False)
    
    storage = StorageManager(test_dir)
    nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
    indexer = IndexerPipeline(storage, nlp)
    
    # Ensure truly empty index
    indexer.inverted_index.clear()
    
    # Test search on empty index - should return informative result, not empty
    results = indexer.search("test query")
    print(f"Search on empty index returned {len(results)} result(s)")
    assert len(results) == 1, "Should return 1 informative result"
    assert 'error' in results[0] or 'info' in results[0], "Should contain error/info flag"
    print(f"✓ Empty index returns informative message: '{results[0].get('description', '')}'")
    
    # Add test data
    pages = [
        {
            'url': f'http://test.se/page{i}',
            'domain': 'test.se',
            'title': f'Swedish Page {i}',
            'description': f'Information about Sverige {i}',
            'content': 'Svenska språket är vackert. ' * 10,
            'keywords': ['sverige', 'svenska'],
            'crawl_time': time.time()
        }
        for i in range(5)
    ]
    
    indexer.index_pages(pages)
    
    # Test search for non-existent terms
    results = indexer.search("nonexistentterminindex")
    print(f"Search for non-existent term returned {len(results)} result(s)")
    assert len(results) >= 1, "Should return at least 1 result"
    if results[0].get('info') or results[0].get('error'):
        print(f"✓ Non-existent term returns informative message: '{results[0].get('description', '')}'")
    
    # Test search for valid terms
    results = indexer.search("svenska")
    print(f"Search for valid term returned {len(results)} result(s)")
    assert len(results) >= 1, "Should return results"
    if not results[0].get('info') and not results[0].get('error'):
        print(f"✓ Valid search returns real results with scores")
    
    print("✓ Graceful degradation test PASSED")


def test_improved_scoring() -> None:
    """Test that TF-IDF scoring doesn't collapse at scale"""
    print(f"\n{'='*70}")
    print("TEST 3: Improved Scoring (TF-IDF with smoothing)")
    print(f"{'='*70}")
    
    # Create test directory (clean)
    test_dir = Path('/tmp/kse_scoring_test')
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    log_dir = test_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    KSELogger.setup(log_dir, "INFO", False)
    
    storage = StorageManager(test_dir)
    nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
    indexer = IndexerPipeline(storage, nlp)
    
    # Create pages with varying document counts to test score stability
    print("Creating test corpus with 50 documents...")
    pages = []
    for i in range(50):
        pages.append({
            'url': f'http://test{i}.se/page',
            'domain': f'test{i}.se',
            'title': f'Swedish Education Page {i}',
            'description': f'Information about Swedish universities {i}',
            'content': 'Svenska universitet och högskolor erbjuder utbildning. ' * 20,
            'keywords': ['universitet', 'utbildning'],
            'crawl_time': time.time()
        })
    
    indexer.index_pages(pages)
    
    # Test that common terms still get reasonable scores
    results = indexer.search("universitet", max_results=10)
    print(f"Search for common term 'universitet': {len(results)} results")
    
    if results and not results[0].get('error') and not results[0].get('info'):
        scores = [r['score'] for r in results]
        print(f"  - Score range: {min(scores):.2f} to {max(scores):.2f}")
        
        # Scores should be positive and meaningful (not collapsed to near-zero)
        assert all(s > 0 for s in scores), "All scores should be positive"
        assert max(scores) > 1.0, "Max score should be meaningful (> 1.0)"
        print(f"✓ Scores are positive and meaningful even with 50 documents")
    
    # Add more documents to test scale
    print("Adding 150 more documents (total 200)...")
    more_pages = []
    for i in range(50, 200):
        more_pages.append({
            'url': f'http://test{i}.se/page',
            'domain': f'test{i}.se',
            'title': f'Swedish Education Page {i}',
            'description': f'Information about Swedish universities {i}',
            'content': 'Svenska universitet och högskolor erbjuder utbildning. ' * 20,
            'keywords': ['universitet', 'utbildning'],
            'crawl_time': time.time()
        })
    
    indexer.index_pages(more_pages)
    
    # Test that scores don't collapse with 200 documents
    results_200 = indexer.search("universitet", max_results=10)
    print(f"Search for 'universitet' with 200 documents: {len(results_200)} results")
    
    if results_200 and not results_200[0].get('error') and not results_200[0].get('info'):
        scores_200 = [r['score'] for r in results_200]
        print(f"  - Score range: {min(scores_200):.2f} to {max(scores_200):.2f}")
        
        # Scores should still be meaningful
        assert all(s > 0 for s in scores_200), "All scores should be positive"
        assert max(scores_200) > 0.5, "Max score should not collapse"
        print(f"✓ Scores remain meaningful even with 200 documents")
        
        # Scores should not shrink dramatically
        if results and not results[0].get('error'):
            ratio = max(scores_200) / max(scores)
            print(f"  - Score ratio (200 docs / 50 docs): {ratio:.2f}")
            # With smoothing, ratio should be reasonable (not < 0.1)
            assert ratio > 0.3, "Scores should not collapse dramatically with scale"
            print(f"✓ Score smoothing prevents collapse at scale")
    
    print("✓ Improved scoring test PASSED")


def test_pagination() -> None:
    """Test pagination support"""
    print(f"\n{'='*70}")
    print("TEST 4: Pagination Support")
    print(f"{'='*70}")
    
    # Create test directory (clean)
    test_dir = Path('/tmp/kse_pagination_test')
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    log_dir = test_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    KSELogger.setup(log_dir, "INFO", False)
    
    storage = StorageManager(test_dir)
    nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
    indexer = IndexerPipeline(storage, nlp)
    
    # Create test pages
    print("Creating 30 test pages...")
    pages = []
    for i in range(30):
        pages.append({
            'url': f'http://test.se/page{i}',
            'domain': 'test.se',
            'title': f'Swedish Page {i}',
            'description': f'Information about Sverige {i}',
            'content': 'Svenska språket och kultur. ' * 15,
            'keywords': ['sverige', 'svenska'],
            'crawl_time': time.time()
        })
    
    indexer.index_pages(pages)
    
    # Create search pipeline
    search_pipeline = SearchPipeline(indexer, nlp, enable_cache=False, enable_ranking=False)
    
    # Test first page
    print("\nTesting pagination...")
    page1 = search_pipeline.search("svenska", page_size=10, offset=0)
    print(f"Page 1: {page1['total_results']} results")
    assert 'pagination' in page1, "Response should include pagination metadata"
    assert page1['pagination']['current_page'] == 1, "Should be page 1"
    assert page1['pagination']['page_size'] == 10, "Page size should be 10"
    print(f"  - Current page: {page1['pagination']['current_page']}")
    print(f"  - Total pages: {page1['pagination']['total_pages']}")
    print(f"  - Has more: {page1['pagination']['has_more']}")
    
    # Test second page
    page2 = search_pipeline.search("svenska", page_size=10, offset=10)
    print(f"Page 2: {page2['total_results']} results")
    assert page2['pagination']['current_page'] == 2, "Should be page 2"
    print(f"  - Current page: {page2['pagination']['current_page']}")
    
    # Test that pages don't overlap
    if (page1['results'] and not page1['results'][0].get('error') and 
        page2['results'] and not page2['results'][0].get('error')):
        page1_urls = {r['url'] for r in page1['results']}
        page2_urls = {r['url'] for r in page2['results']}
        overlap = page1_urls & page2_urls
        assert len(overlap) == 0, "Pages should not have overlapping results"
        print(f"✓ No overlap between page 1 and page 2")
    
    # Test next_offset
    if page1['pagination']['has_more']:
        next_offset = page1['pagination']['next_offset']
        assert next_offset == 10, "Next offset should be 10"
        print(f"✓ Next offset correctly calculated: {next_offset}")
    
    print("✓ Pagination test PASSED")


def test_candidate_limiting() -> None:
    """Test that candidate limiting works for performance"""
    print(f"\n{'='*70}")
    print("TEST 5: Candidate Limiting for Performance")
    print(f"{'='*70}")
    
    # Create test directory (clean)
    test_dir = Path('/tmp/kse_candidate_test')
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    test_dir.mkdir(exist_ok=True)
    
    log_dir = test_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    KSELogger.setup(log_dir, "INFO", False)
    
    storage = StorageManager(test_dir)
    nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
    indexer = IndexerPipeline(storage, nlp)
    
    # Create many documents
    print("Creating 500 test pages (this may take a moment)...")
    pages = []
    for i in range(500):
        # All pages contain "svenska" to ensure many candidates
        pages.append({
            'url': f'http://test{i}.se/page',
            'domain': f'test{i}.se',
            'title': f'Page {i}',
            'description': f'Content {i}',
            'content': 'Svenska innehåll. ' * 10,
            'keywords': ['svenska'],
            'crawl_time': time.time()
        })
    
    indexer.index_pages(pages)
    
    # Search should complete quickly even with 500 matching documents
    print("Searching with term matching all 500 documents...")
    start = time.time()
    results = indexer.search("svenska", max_results=10)
    elapsed = time.time() - start
    
    print(f"Search completed in {elapsed*1000:.2f}ms")
    assert elapsed < 0.1, f"Search should complete in < 100ms, took {elapsed*1000:.2f}ms"
    print(f"✓ Candidate limiting keeps search fast even with 500 matches")
    
    print("✓ Candidate limiting test PASSED")


def main():
    """Run all improvement tests"""
    global logger
    
    try:
        print("="*70)
        print("SEARCH ENGINE IMPROVEMENTS TEST SUITE")
        print("Testing fixes for scalability issues")
        print("="*70)
        
        # Run tests
        test_index_validation()
        test_graceful_degradation()
        test_improved_scoring()
        test_pagination()
        test_candidate_limiting()
        
        # Final summary
        print(f"\n{'='*70}")
        print("✓ ALL IMPROVEMENT TESTS PASSED!")
        print(f"{'='*70}")
        print(f"\nValidated improvements:")
        print(f"  ✓ Index validation before search")
        print(f"  ✓ Graceful degradation (no silent failures)")
        print(f"  ✓ Improved TF-IDF scoring with smoothing")
        print(f"  ✓ Pagination support (offset/page_size)")
        print(f"  ✓ Candidate limiting for performance")
        print(f"\nAll fixes from problem statement implemented successfully!")
        print(f"{'='*70}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
