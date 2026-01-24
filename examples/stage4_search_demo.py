#!/usr/bin/env python3
"""
Stage 4 Search Pipeline Demo

Demonstrates query parsing, ranking, execution, and caching.
"""

from kse.search import (
    QueryParser,
    QueryType,
    Ranker,
    RankingStrategy,
    SearchCache,
    SearchResult,
    ResultSet,
)
from datetime import datetime, timedelta


def demo_query_parser():
    """
    Demo: Query parsing and normalization
    """
    print("\n" + "="*60)
    print("DEMO 1: Query Parser")
    print("="*60)
    
    parser = QueryParser()
    
    # Test cases
    queries = [
        "python programming",
        '"machine learning" artificial intelligence',
        "cybersecurity -malware -virus",
        "site:github.com python fork",
        "tensorflow from:2024-01-01 to:2024-12-31",
        "  PYTHON  PROGRAMMING  ",  # Normalize spaces
    ]
    
    for query_str in queries:
        print(f"\nQuery: {query_str!r}")
        parsed = parser.parse(query_str)
        
        print(f"  Type: {parsed.query_type.value}")
        print(f"  Terms: {parsed.terms}")
        print(f"  Phrases: {parsed.phrases}")
        print(f"  Exclusions: {parsed.exclude_terms}")
        if parsed.domain_filter:
            print(f"  Domain: {parsed.domain_filter}")
        if parsed.date_from:
            print(f"  Date From: {parsed.date_from}")
        if parsed.date_to:
            print(f"  Date To: {parsed.date_to}")
        
        # Validate
        valid = parser.validate_query(parsed)
        print(f"  Valid: {valid}")


def demo_ranking():
    """
    Demo: Result ranking with different strategies
    """
    print("\n" + "="*60)
    print("DEMO 2: Result Ranking")
    print("="*60)
    
    # Sample results
    results = [
        {
            'page_id': 1,
            'url': 'https://example.com/article',
            'tfidf_score': 0.92,
            'domain': 'example.com',
            'inbound_links': 10,
            'created_at': datetime.now() - timedelta(days=5),
        },
        {
            'page_id': 2,
            'url': 'https://sv.wikipedia.org/wiki/Python',
            'tfidf_score': 0.78,
            'domain': 'sv.wikipedia.org',
            'inbound_links': 500,
            'created_at': datetime.now() - timedelta(days=180),
        },
        {
            'page_id': 3,
            'url': 'https://github.com/project',
            'tfidf_score': 0.65,
            'domain': 'github.com',
            'inbound_links': 150,
            'created_at': datetime.now() - timedelta(days=365),
        },
    ]
    
    ranker = Ranker()
    
    # Test different strategies
    strategies = [
        RankingStrategy.RELEVANCE,
        RankingStrategy.POPULARITY,
        RankingStrategy.RECENCY,
        RankingStrategy.HYBRID,
    ]
    
    for strategy in strategies:
        print(f"\n{strategy.value.upper()} Strategy:")
        print("-" * 40)
        
        scores = ranker.rank(results, strategy)
        
        for i, score in enumerate(scores, 1):
            print(f"{i}. {score.url}")
            print(f"   Final: {score.final_score:.3f}")
            print(f"   Relevance: {score.relevance_score:.3f}")
            print(f"   Popularity: {score.popularity_score:.3f}")
            print(f"   Recency: {score.recency_score:.3f}")


def demo_custom_weights():
    """
    Demo: Custom ranking weights
    """
    print("\n" + "="*60)
    print("DEMO 3: Custom Ranking Weights")
    print("="*60)
    
    results = [
        {
            'page_id': 1,
            'url': 'https://old-article.com',
            'tfidf_score': 0.95,
            'domain': 'old-article.com',
            'inbound_links': 5,
            'created_at': datetime.now() - timedelta(days=720),  # 2 years old
        },
        {
            'page_id': 2,
            'url': 'https://sv.wikipedia.org/wiki/Topic',
            'tfidf_score': 0.70,
            'domain': 'sv.wikipedia.org',
            'inbound_links': 1000,
            'created_at': datetime.now() - timedelta(days=30),
        },
    ]
    
    # Relevance-focused ranker
    ranker_rel = Ranker()
    ranker_rel.set_weights({
        'relevance': 0.90,
        'popularity': 0.05,
        'recency': 0.05,
    })
    
    print("\nRelevance-Focused (0.90/0.05/0.05):")
    rel_scores = ranker_rel.rank(results)
    for score in rel_scores:
        print(f"  {score.url}: {score.final_score:.3f}")
    
    # Recency-focused ranker
    ranker_rec = Ranker()
    ranker_rec.set_weights({
        'relevance': 0.33,
        'popularity': 0.33,
        'recency': 0.34,
    })
    
    print("\nRecency-Focused (0.33/0.33/0.34):")
    rec_scores = ranker_rec.rank(results)
    for score in rec_scores:
        print(f"  {score.url}: {score.final_score:.3f}")


def demo_cache():
    """
    Demo: Search result caching
    """
    print("\n" + "="*60)
    print("DEMO 4: Search Cache")
    print("="*60)
    
    cache = SearchCache(max_entries=100, default_ttl_seconds=3600)
    
    # Create sample results
    result_set_1 = ResultSet(
        query="python programming",
        total_results=1000,
        returned_results=10,
        results=[],
    )
    
    result_set_2 = ResultSet(
        query="machine learning",
        total_results=2000,
        returned_results=10,
        results=[],
    )
    
    # Cache results
    print("\nCaching queries...")
    cache.put("python programming", result_set_1)
    cache.put("machine learning", result_set_2)
    cache.put("data science", result_set_2)  # Different query, same results
    
    print(f"Cache size: {len(cache.cache)}")
    
    # Test cache hits
    print("\nTesting cache hits...")
    hit1 = cache.get("python programming")
    print(f"Cache hit for 'python programming': {hit1 is not None}")
    
    hit2 = cache.get("java programming")
    print(f"Cache hit for 'java programming': {hit2 is not None}")
    
    # Multiple accesses
    for _ in range(5):
        cache.get("python programming")
    
    # Statistics
    stats = cache.get_statistics()
    print(f"\nCache Statistics:")
    print(f"  Entries: {stats['entries']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate_percent']:.1f}%")
    print(f"  Total Requests: {stats['total_requests']}")
    
    # Top queries
    print(f"\nTop Queries:")
    top = cache.get_top_queries(limit=5)
    for query, hits in top:
        print(f"  '{query}': {hits} hits")


def demo_workflow():
    """
    Demo: Complete search workflow
    """
    print("\n" + "="*60)
    print("DEMO 5: Complete Search Workflow")
    print("="*60)
    
    # Initialize components
    parser = QueryParser()
    ranker = Ranker()
    cache = SearchCache()
    
    # User query
    user_query = "cybersecurity python site:github.com -malware"
    print(f"\nUser Query: {user_query}")
    
    # Step 1: Check cache
    print("\n1. Checking cache...")
    cached = cache.get(user_query)
    if cached:
        print(f"   Cache hit! Found {cached.total_results} results")
    else:
        print("   Cache miss, proceeding with search...")
    
    # Step 2: Parse query
    print("\n2. Parsing query...")
    parsed = parser.parse(user_query)
    print(f"   Query Type: {parsed.query_type.value}")
    print(f"   Terms: {parsed.terms}")
    print(f"   Exclusions: {parsed.exclude_terms}")
    print(f"   Domain Filter: {parsed.domain_filter}")
    print(f"   Valid: {parser.validate_query(parsed)}")
    
    # Step 3: Simulate result retrieval (in real system, from database)
    print("\n3. Executing search (simulated database results)...")
    
    # Mock search results
    search_results = [
        {
            'page_id': 1,
            'url': 'https://github.com/project1/security',
            'tfidf_score': 0.92,
            'domain': 'github.com',
            'inbound_links': 45,
            'created_at': datetime.now() - timedelta(days=10),
        },
        {
            'page_id': 2,
            'url': 'https://github.com/project2/cyber',
            'tfidf_score': 0.85,
            'domain': 'github.com',
            'inbound_links': 120,
            'created_at': datetime.now() - timedelta(days=45),
        },
        {
            'page_id': 3,
            'url': 'https://github.com/project3/tools',
            'tfidf_score': 0.78,
            'domain': 'github.com',
            'inbound_links': 200,
            'created_at': datetime.now() - timedelta(days=90),
        },
    ]
    
    print(f"   Found {len(search_results)} results")
    
    # Step 4: Rank results
    print("\n4. Ranking results...")
    ranked = ranker.rank(search_results, RankingStrategy.HYBRID)
    
    for i, score in enumerate(ranked, 1):
        print(f"   {i}. Score: {score.final_score:.3f}")
        print(f"      URL: {score.url}")
    
    # Step 5: Cache results
    print("\n5. Caching results...")
    result_set = ResultSet(
        query=user_query,
        total_results=len(search_results),
        returned_results=len(ranked),
        results=[
            SearchResult(
                page_id=score.page_id,
                url=score.url,
                title=f"Project #{score.page_id}",
                description="GitHub repository",
                domain="github.com",
                score=score.final_score,
                relevance=score.relevance_score,
            )
            for score in ranked
        ],
        execution_time_ms=45.2,
    )
    
    cache.put(user_query, result_set)
    print(f"   Cached {result_set.total_results} results")
    
    # Step 6: Statistics
    print("\n6. Final Statistics:")
    stats = cache.get_statistics()
    print(f"   Cache Hit Rate: {stats['hit_rate_percent']:.1f}%")
    print(f"   Execution Time: {result_set.execution_time_ms:.2f}ms")


def main():
    """
    Run all demos
    """
    print("\n" + "#"*60)
    print("# STAGE 4: Search Pipeline - Complete Demo")
    print("#"*60)
    
    try:
        demo_query_parser()
        demo_ranking()
        demo_custom_weights()
        demo_cache()
        demo_workflow()
        
        print("\n" + "#"*60)
        print("# All demos completed successfully!")
        print("#"*60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
