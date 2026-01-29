"""
Test Indexing Pipeline - Script to test NLP and indexing
"""
import sys
from pathlib import Path
from kse.core.kse_config import get_config
from kse.core.kse_logger import KSELogger, get_logger
from kse.storage.kse_storage_manager import StorageManager
from kse.nlp.kse_nlp_core import NLPCore
from kse.indexing.kse_indexer_pipeline import IndexerPipeline

logger = None


def main():
    """Test NLP and indexing"""
    global logger
    
    try:
        # Load configuration
        config = get_config()
        
        # Setup logging
        log_dir = Path(config.get("log_dir"))
        KSELogger.setup(log_dir, config.get("log_level", "INFO"), True)
        logger = get_logger(__name__)
        
        print("=" * 60)
        print("KSE NLP and Indexing Test")
        print("=" * 60)
        
        # Initialize storage
        data_dir = Path(config.get("data_dir"))
        storage_manager = StorageManager(data_dir)
        
        # Initialize NLP
        nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
        
        # Test NLP processing
        print("\n1. Testing NLP Processing:")
        print("-" * 60)
        
        test_texts = [
            "Svenska universitet erbjuder högkvalitativa utbildningar",
            "Stockholms universitet är ett av Sveriges största universitet",
            "Forskning och innovation är viktiga för samhället"
        ]
        
        for text in test_texts:
            tokens = nlp.process_text(text)
            print(f"\nText: {text}")
            print(f"Tokens: {tokens}")
        
        # Test query processing
        print("\n\n2. Testing Query Processing:")
        print("-" * 60)
        
        test_queries = [
            "svenska universitet",
            "var kan jag studera?",
            "forskning och utveckling"
        ]
        
        for query in test_queries:
            tokens = nlp.process_query(query)
            print(f"\nQuery: {query}")
            print(f"Tokens: {tokens}")
        
        # Test indexing with sample data
        print("\n\n3. Testing Indexing Pipeline:")
        print("-" * 60)
        
        sample_pages = [
            {
                'url': 'https://uu.se',
                'domain': 'uu.se',
                'title': 'Uppsala Universitet - Sveriges äldsta universitet',
                'description': 'Uppsala universitet är Sveriges äldsta och ett av Nordens främsta lärosäten',
                'content': 'Uppsala universitet grundades 1477 och är ett av världens 100 bästa universitet. Vi bedriver forskning och utbildning inom alla områden. Universitetet har cirka 45 000 studenter och 7 000 anställda.',
                'keywords': ['universitet', 'utbildning', 'forskning'],
                'crawl_time': 0
            },
            {
                'url': 'https://lu.se',
                'domain': 'lu.se',
                'title': 'Lunds Universitet - Ett av världens främsta lärosäten',
                'description': 'Lunds universitet grundades 1666 och rankas konsekvent som ett av världens 100 bästa universitet',
                'content': 'Lunds universitet är ett av Nordens största forskningsuniversitet. Vi har åtta fakulteter och ett flertal forskningscentrum och specialiserade forskningsinstitutioner. Universitetet har cirka 42 000 studenter.',
                'keywords': ['universitet', 'forskning', 'utbildning'],
                'crawl_time': 0
            },
            {
                'url': 'https://su.se',
                'domain': 'su.se',
                'title': 'Stockholms Universitet - Forskning och utbildning',
                'description': 'Stockholms universitet är ett av Europas ledande lärosäten inom humaniora och samhällsvetenskap',
                'content': 'Stockholms universitet grundades 1878 och är Sveriges tredje äldsta universitet. Vi har cirka 34 000 studenter och 5 000 anställda. Universitetet bedriver forskning och utbildning inom naturvetenskap, humaniora, samhällsvetenskap och juridik.',
                'keywords': ['universitet', 'Stockholm', 'forskning'],
                'crawl_time': 0
            }
        ]
        
        # Initialize indexer
        indexer = IndexerPipeline(storage_manager, nlp)
        
        # Index pages
        print("\nIndexing sample pages...")
        stats = indexer.index_pages(sample_pages)
        
        print(f"\nIndexing Statistics:")
        print(f"  Pages indexed: {stats['pages_indexed']}")
        print(f"  Total documents: {stats['total_documents']}")
        print(f"  Total terms: {stats['total_terms']}")
        
        # Test search
        print("\n\n4. Testing Search:")
        print("-" * 60)
        
        test_search_queries = [
            "svenska universitet",
            "forskning",
            "Stockholm",
            "studenter utbildning"
        ]
        
        for query in test_search_queries:
            print(f"\nQuery: '{query}'")
            results = indexer.search(query, max_results=3)
            
            if results:
                print(f"Found {len(results)} results:")
                for i, result in enumerate(results):
                    print(f"\n  {i+1}. {result['title']}")
                    print(f"     URL: {result['url']}")
                    print(f"     Score: {result['score']}/100")
                    print(f"     Description: {result['description'][:80]}...")
            else:
                print("  No results found")
        
        # Get final statistics
        final_stats = indexer.get_statistics()
        print("\n\nFinal Index Statistics:")
        print("=" * 60)
        for key, value in final_stats.items():
            print(f"{key}: {value}")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if logger:
            logger.error(f"Test error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
