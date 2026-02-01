"""
Test script for new enterprise search features
Validates multi-threading, semantic similarity, and Swedish ranking
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_multi_threaded_crawler():
    """Test multi-threaded crawler feature"""
    logger.info("Testing multi-threaded crawler...")
    
    try:
        # Check that max_workers parameter exists
        with open('kse/crawler/kse_crawler_core.py', 'r') as f:
            content = f.read()
        
        assert 'max_workers: int = 5' in content or 'max_workers:int=5' in content, \
            "CrawlerCore.__init__ should have max_workers parameter"
        
        assert 'self.max_workers = max_workers' in content, \
            "max_workers should be stored as instance variable"
        
        assert 'ThreadPoolExecutor' in content, \
            "Should use ThreadPoolExecutor for multi-threading"
        
        assert '_state_lock' in content, \
            "Should have thread-safe state lock"
        
        assert 'crawl_all_domains_threaded' in content, \
            "Should have threaded crawl method"
        
        logger.info("✓ Multi-threaded crawler implementation validated")
        return True
        
    except Exception as e:
        logger.error(f"✗ Multi-threaded crawler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_semantic_similarity():
    """Test semantic similarity module"""
    logger.info("Testing semantic similarity module...")
    
    try:
        # Check that semantic similarity file exists
        semantic_file = Path('kse/ranking/kse_semantic_similarity.py')
        assert semantic_file.exists(), "Semantic similarity module should exist"
        
        # Check content
        with open(semantic_file, 'r') as f:
            content = f.read()
        
        assert 'SemanticSimilarity' in content, \
            "Should have SemanticSimilarity class"
        
        assert 'concept_clusters' in content, \
            "Should have concept clusters"
        
        assert 'question_intents' in content, \
            "Should have question intent detection"
        
        assert 'calculate_semantic_score' in content, \
            "Should have semantic scoring method"
        
        logger.info("✓ Semantic similarity module validated")
        return True
        
    except Exception as e:
        logger.error(f"✗ Semantic similarity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_swedish_ranking():
    """Test enhanced Swedish regional relevance"""
    logger.info("Testing enhanced Swedish ranking...")
    
    try:
        # Check regional relevance enhancements
        with open('kse/ranking/kse_regional_relevance.py', 'r') as f:
            content = f.read()
        
        assert 'trusted_swedish_domains' in content, \
            "Should have trusted Swedish domains"
        
        assert 'swedish_locations' in content, \
            "Should have Swedish locations"
        
        assert 'swedish_patterns' in content, \
            "Should have Swedish content patterns"
        
        # Check ranking weights
        with open('kse/ranking/kse_ranking_core.py', 'r') as f:
            ranking_content = f.read()
        
        assert 'semantic_similarity' in ranking_content, \
            "Ranking should include semantic similarity"
        
        assert 'regional_relevance: float = 0.20' in ranking_content or \
               'regional_relevance: float = 0.2' in ranking_content, \
            "Regional relevance weight should be increased to 0.20"
        
        logger.info("✓ Enhanced Swedish ranking validated")
        return True
        
    except Exception as e:
        logger.error(f"✗ Enhanced Swedish ranking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_domain_management_dialog():
    """Test domain management dialog"""
    logger.info("Testing domain management dialog...")
    
    try:
        # Check that dialog file exists
        dialog_file = Path('gui/control_center/dialogs/domain_management_dialog.py')
        assert dialog_file.exists(), "Domain management dialog should exist"
        
        # Check content
        with open(dialog_file, 'r') as f:
            content = f.read()
        
        assert 'DomainManagementDialog' in content, \
            "Should have DomainManagementDialog class"
        
        assert 'ReCrawlWorker' in content, \
            "Should have re-crawl worker thread"
        
        assert '_add_domain' in content and '_remove_selected_domains' in content, \
            "Should have add/remove domain methods"
        
        assert '_import_domains' in content and '_export_domains' in content, \
            "Should have import/export functionality"
        
        logger.info("✓ Domain management dialog validated")
        return True
        
    except Exception as e:
        logger.error(f"✗ Domain management dialog test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_nlp():
    """Test enhanced Swedish NLP"""
    logger.info("Testing enhanced Swedish NLP...")
    
    try:
        # Check query processor enhancements
        with open('kse/nlp/kse_query_processor.py', 'r') as f:
            content = f.read()
        
        # Check for specific synonym categories that we added
        required_categories = [
            'restaurang', 'resa', 'arbete', 'bostad', 
            'transport', 'shopping', 'underhållning'
        ]
        
        for category in required_categories:
            assert category in content, \
                f"Should have '{category}' in synonyms"
        
        # Check for enhanced phrase patterns
        required_patterns = [
            'hitta', 'billig', 'nära', 'öppettider', 'recension', 'jämför'
        ]
        
        for pattern in required_patterns:
            assert pattern in content, \
                f"Should have '{pattern}' in phrase patterns"
        
        logger.info("✓ Enhanced Swedish NLP validated")
        return True
        
    except Exception as e:
        logger.error(f"✗ Enhanced NLP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Enterprise Search Engine Feature Tests")
    logger.info("=" * 60)
    logger.info("")
    
    tests = [
        ("Multi-threaded Crawler", test_multi_threaded_crawler),
        ("Semantic Similarity", test_semantic_similarity),
        ("Enhanced Swedish Ranking", test_enhanced_swedish_ranking),
        ("Domain Management Dialog", test_domain_management_dialog),
        ("Enhanced Swedish NLP", test_enhanced_nlp),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info("")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info("")
    logger.info(f"Results: {passed}/{len(tests)} tests passed")
    logger.info("=" * 60)
    
    return 0 if passed == len(tests) else 1


if __name__ == '__main__':
    sys.exit(main())
