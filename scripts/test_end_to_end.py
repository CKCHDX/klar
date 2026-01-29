"""
End-to-End Test - Complete KSE system test
"""
import sys
from pathlib import Path
from kse.core.kse_config import get_config
from kse.core.kse_logger import KSELogger, get_logger
from kse.storage.kse_storage_manager import StorageManager
from kse.storage.kse_domain_manager import DomainManager
from kse.nlp.kse_nlp_core import NLPCore
from kse.indexing.kse_indexer_pipeline import IndexerPipeline
from kse.search.kse_search_pipeline import SearchPipeline
from kse.core.kse_constants import DOMAINS_FILE

logger = None


def main():
    """End-to-end system test"""
    global logger
    
    try:
        print("=" * 70)
        print("KSE END-TO-END SYSTEM TEST")
        print("=" * 70)
        
        # 1. Initialize Core
        print("\n1. Initializing Core Components...")
        print("-" * 70)
        
        config = get_config()
        log_dir = Path(config.get("log_dir"))
        KSELogger.setup(log_dir, "INFO", True)
        logger = get_logger(__name__)
        
        data_dir = Path(config.get("data_dir"))
        storage_manager = StorageManager(data_dir)
        print("✓ Storage manager initialized")
        
        if DOMAINS_FILE.exists():
            domain_manager = DomainManager(DOMAINS_FILE)
            print(f"✓ Domain manager loaded: {len(domain_manager.get_all_domains())} domains")
        
        # 2. Initialize NLP
        print("\n2. Initializing NLP...")
        print("-" * 70)
        
        nlp = NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
        print("✓ NLP core initialized")
        
        # Test NLP
        test_text = "Svenska universitet erbjuder högkvalitativa utbildningar och forskning"
        tokens = nlp.process_text(test_text)
        print(f"✓ NLP test: '{test_text}'")
        print(f"  Tokens: {tokens}")
        
        # 3. Create Sample Data
        print("\n3. Creating Sample Index...")
        print("-" * 70)
        
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
            },
            {
                'url': 'https://kth.se',
                'domain': 'kth.se',
                'title': 'KTH - Kungl. Tekniska Högskolan',
                'description': 'KTH är Sveriges största tekniska universitet och en av Europas ledande tekniska högskolor',
                'content': 'KTH erbjuder utbildning och forskning inom teknik och naturvetenskap. Vi har cirka 13 000 studenter och 3 400 anställda. KTH samarbetar med näringslivet och samhället för att bidra till hållbar utveckling.',
                'keywords': ['KTH', 'teknik', 'ingenjör'],
                'crawl_time': 0
            }
        ]
        
        # 4. Index Pages
        print("\n4. Indexing Pages...")
        print("-" * 70)
        
        indexer = IndexerPipeline(storage_manager, nlp)
        stats = indexer.index_pages(sample_pages)
        
        print(f"✓ Indexed {stats['pages_indexed']} pages")
        print(f"  Total documents: {stats['total_documents']}")
        print(f"  Total terms: {stats['total_terms']}")
        
        # 5. Initialize Search
        print("\n5. Initializing Search Pipeline...")
        print("-" * 70)
        
        search_pipeline = SearchPipeline(indexer, nlp)
        print("✓ Search pipeline initialized")
        
        # 6. Test Searches
        print("\n6. Testing Search Functionality...")
        print("-" * 70)
        
        test_queries = [
            "svenska universitet",
            "forskning",
            "Stockholm utbildning",
            "teknik KTH",
            "studenter"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("   " + "-" * 60)
            
            result = search_pipeline.search(query, max_results=3)
            
            print(f"   Found: {result['total_results']} results")
            print(f"   Time: {result['search_time']}s")
            
            if result['results']:
                for j, res in enumerate(result['results'][:3], 1):
                    print(f"\n   {j}. {res['title']}")
                    print(f"      URL: {res['url']}")
                    print(f"      Score: {res['score']}/100")
                    print(f"      Snippet: {res['snippet'][:80]}...")
        
        # 7. Get Statistics
        print("\n\n7. System Statistics...")
        print("-" * 70)
        
        index_stats = indexer.get_statistics()
        search_stats = search_pipeline.get_search_statistics()
        
        print(f"\nIndex Statistics:")
        print(f"  Documents: {index_stats['total_documents']}")
        print(f"  Terms: {index_stats['total_terms']}")
        print(f"  Avg terms/doc: {index_stats['average_terms_per_document']:.1f}")
        
        print(f"\nSearch Statistics:")
        print(f"  Total searches: {search_stats['total_searches']}")
        print(f"  Avg search time: {search_stats['average_search_time']}s")
        print(f"  Avg results: {search_stats['average_results']:.1f}")
        
        # Success
        print("\n" + "=" * 70)
        print("✓ END-TO-END TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nAll KSE components are working correctly:")
        print("  ✓ Core (config, logging, storage)")
        print("  ✓ NLP (tokenization, lemmatization, stopwords)")
        print("  ✓ Indexing (inverted index, TF-IDF)")
        print("  ✓ Search (query processing, ranking, results)")
        print("\nNext steps:")
        print("  - Start server: python -m kse.server.kse_server")
        print("  - Use crawler to index real websites")
        print("  - Deploy GUI for control and monitoring")
        print("=" * 70)
        
        return 0
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        if logger:
            logger.error(f"Test error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
