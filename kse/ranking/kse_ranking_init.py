"""
kse/ranking/__init__.py - Search Ranking Engine API

Components:
  - RankingCore: Main ranking orchestrator
  - TFIDFRanker: Factor 1 - Relevance (25%)
  - PageRank: Factor 2 - Link popularity (20%)
  - DomainAuthority: Factor 3 - Domain trust (15%)
  - RecencyScorer: Factor 4 - Content freshness (15%)
  - KeywordDensity: Factor 5 - Keyword importance (10%)
  - LinkStructure: Factor 6 - Link analysis (10%)
  - RegionalRelevance: Factor 7 - Regional focus (5%)
  - RankingStatistics: Statistics tracking

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

from .kse_ranking_core import RankingCore, KSERankingException
from .kse_tf_idf_ranker import TFIDFRanker
from .kse_pagerank import PageRank
from .kse_domain_authority import DomainAuthority
from .kse_recency_scorer import RecencyScorer
from .kse_keyword_density import KeywordDensity
from .kse_link_structure import LinkStructure
from .kse_regional_relevance import RegionalRelevance
from .kse_ranking_stats import RankingStatistics

__all__ = [
    # Core
    "RankingCore",
    
    # Ranking Factors
    "TFIDFRanker",          # 25% - Relevance
    "PageRank",             # 20% - Link popularity
    "DomainAuthority",      # 15% - Domain trust
    "RecencyScorer",        # 15% - Content freshness
    "KeywordDensity",       # 10% - Keyword importance
    "LinkStructure",        # 10% - Link analysis
    "RegionalRelevance",    # 5%  - Regional focus
    
    # Statistics
    "RankingStatistics",
    
    # Exceptions
    "KSERankingException",
]

__version__ = "1.0.0"
__author__ = "Klar Development Team"


# Quick start examples
"""
QUICK START - Ranking Layer

1. Rank search results:
    from kse.ranking import RankingCore
    from kse.cache import CacheManager
    
    cache = CacheManager()
    ranker = RankingCore(cache)
    
    ranked = ranker.rank_results(
        query="svenska universitet",
        documents=docs,
        scoring_data=scores
    )

2. TF-IDF ranking (Factor 1):
    from kse.ranking import TFIDFRanker
    
    tfidf_ranker = TFIDFRanker()
    scores = tfidf_ranker.rank_documents(documents, ["svenska"])

3. PageRank (Factor 2):
    from kse.ranking import PageRank
    
    pagerank = PageRank()
    pr_scores = pagerank.compute_pagerank(link_graph, num_pages)

4. Domain Authority (Factor 3):
    from kse.ranking import DomainAuthority
    
    authority = DomainAuthority()
    score = authority.score_document(url)

5. Recency Scoring (Factor 4):
    from kse.ranking import RecencyScorer
    
    recency = RecencyScorer()
    score = recency.score_document(url, timestamp)

6. Keyword Density (Factor 5):
    from kse.ranking import KeywordDensity
    
    density = KeywordDensity()
    score = density.score_document(document, ["svenska"])

7. Link Structure (Factor 6):
    from kse.ranking import LinkStructure
    
    links = LinkStructure()
    score = links.score_document(url, document)

8. Regional Relevance (Factor 7):
    from kse.ranking import RegionalRelevance
    
    regional = RegionalRelevance()
    score = regional.score_document(url)

9. Ranking Statistics:
    from kse.ranking import RankingStatistics
    
    stats = RankingStatistics()
    stats.calculate_statistics(ranked_results)
    print(stats.get_summary())

RANKING ALGORITHM:

Final Score = (7 weighted factors combined)

Factor 1: TF-IDF Relevance (25%)
  - How well does the page match the query?
  - Higher for pages with query terms prominently

Factor 2: PageRank (20%)
  - How popular is the page based on links?
  - Higher for pages with many quality backlinks

Factor 3: Domain Authority (15%)
  - How trustworthy is the domain?
  - Higher for established, trusted domains (.se, news sites)

Factor 4: Recency (15%)
  - How fresh is the content?
  - Higher for recently updated pages

Factor 5: Keyword Density (10%)
  - How well-optimized is the page?
  - Optimized at 1-2%, penalizes keyword stuffing

Factor 6: Link Structure (10%)
  - How good is the internal/external linking?
  - More links to quality resources = higher score

Factor 7: Regional Relevance (5%)
  - How relevant is the domain to Sweden?
  - .se domains score highest

SCORING EXAMPLE:

Query: "svenska universitet"

Document: Uppsala University (uu.se)
├─ TF-IDF:          0.9  × 0.25 = 0.225
├─ PageRank:        0.95 × 0.20 = 0.190
├─ Authority:       0.95 × 0.15 = 0.143
├─ Recency:         0.8  × 0.15 = 0.120
├─ Density:         0.9  × 0.10 = 0.090
├─ Links:           0.8  × 0.10 = 0.080
├─ Regional:        1.0  × 0.05 = 0.050
                    ─────────────────────
FINAL SCORE:                     98/100

ARCHITECTURE:

kse/ranking/
├── kse_ranking_core.py              Main orchestrator
├── kse_tf_idf_ranker.py             Factor 1 (25%)
├── kse_pagerank.py                  Factor 2 (20%)
├── kse_domain_authority.py          Factor 3 (15%)
├── kse_recency_scorer.py            Factor 4 (15%)
├── kse_keyword_density.py           Factor 5 (10%)
├── kse_link_structure.py            Factor 6 (10%)
├── kse_regional_relevance.py        Factor 7 (5%)
├── kse_ranking_stats.py             Statistics
└── __init__.py                      Public API

INTEGRATION:

- Phase 6 (indexing): Uses TF-IDF scores from index
- Phase 8 (search): Uses ranking to sort results
- Phase 3 (cache): Caches ranking results

DATA FLOW:

Search Query
    ↓
Find matching documents (from index)
    ↓
Calculate 7 ranking factors
    ↓
Combine factors with weights
    ↓
Sort by final score
    ↓
Return ranked results
    ↓
Cache for next similar query
"""
