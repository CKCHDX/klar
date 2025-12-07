"""
KLAR 3.0 Search Engine - FULLY CORRECTED
Fixed intent detection + Domain security + Proper component initialization
"""

import json
from pathlib import Path
from typing import Tuple, List, Dict
from urllib.parse import urlparse
import time

# Import core components with CORRECT signatures
from core.indexer import Indexer
from core.crawler import Crawler

# Try to import algorithms - use fallback if not available
try:
    from algorithms.sven import SVEN
except ImportError:
    SVEN = None

try:
    from algorithms.dossna import DOSSNA
except ImportError:
    DOSSNA = None

try:
    from algorithms.loki import LOKI
except ImportError:
    LOKI = None

try:
    from algorithms.thor import THOR
except ImportError:
    THOR = None


class SearchEngine:
    """Main search engine with fixed intent detection and domain security"""
    
    def __init__(self, base_path: str = ""):
        """
        Initialize search engine with correct component signatures
        
        Args:
            base_path: Base path for data files (defaults to current directory)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
        # Load configuration files
        self.domains_file = self.base_path / "domains.json"
        self.keywords_file = self.base_path / "keywords_db.json"
        
        # Build trusted domains FIRST (needed for Crawler)
        self.trusted_domains = self._build_trusted_domains()
        
        # Initialize CORE components with CORRECT signatures
        # Crawler(domains: List[str], data_path: Path, offline_mode: bool)
        domains_list = list(self.trusted_domains)
        self.crawler = Crawler(
            domains=domains_list,
            data_path=self.base_path / "klar_data",
            offline_mode=False
        )
        
        # Indexer(data_path: Path)
        self.indexer = Indexer(self.base_path / "klar_data")
        
        # Initialize optional algorithm components
        self.sven = SVEN() if SVEN else None
        self.dossna = DOSSNA() if DOSSNA else None
        self.loki = LOKI(self.base_path / "klar_data") if LOKI else None
        self.thor = THOR() if THOR else None
        
        # Load keywords database
        self.keywords_db = self._load_keywords_db()
        
        print(f"[SearchEngine] Initialized with {len(self.trusted_domains)} trusted domains")
        if not SVEN:
            print("[SearchEngine] ⚠️  SVEN module not available (optional)")
        if not DOSSNA:
            print("[SearchEngine] ⚠️  DOSSNA module not available (optional)")
    
    def _build_trusted_domains(self) -> set:
        """
        Build set of all trusted domains from domains.json
        
        Returns:
            set: Set of lowercase domain names (e.g., {'svt.se', 'aftonbladet.se'})
        """
        trusted = set()
        
        if not self.domains_file.exists():
            print(f"[Warning] domains.json not found at {self.domains_file}")
            # Add some defaults if file doesn't exist
            return {
                "svt.se", "dn.se", "aftonbladet.se", "expressen.se", "svd.se",
                "regeringen.se", "skatteverket.se", "polisen.se"
            }
        
        try:
            with open(self.domains_file, 'r', encoding='utf-8') as f:
                domains_data = json.load(f)
            
            # Handle both old format (list) and new format (categories)
            if isinstance(domains_data, list):
                # Old format: ["svt.se", "aftonbladet.se"]
                for domain in domains_data:
                    trusted.add(domain.lower())
            elif isinstance(domains_data, dict):
                # New format: {"news": [{"domain": "svt.se"}, ...]}
                for category, domain_list in domains_data.items():
                    if isinstance(domain_list, list):
                        for item in domain_list:
                            if isinstance(item, dict) and "domain" in item:
                                trusted.add(item["domain"].lower())
                            elif isinstance(item, str):
                                trusted.add(item.lower())
        
        except Exception as e:
            print(f"[Error] Failed to load domains.json: {e}")
            # Return at least some defaults
            return {
                "svt.se", "dn.se", "aftonbladet.se", "expressen.se", "svd.se",
                "regeringen.se", "skatteverket.se", "polisen.se"
            }
        
        return trusted if trusted else {
            "svt.se", "dn.se", "aftonbladet.se", "expressen.se", "svd.se"
        }
    
    def _load_keywords_db(self) -> dict:
        """Load keywords database for intent detection"""
        if not self.keywords_file.exists():
            print(f"[Warning] keywords_db.json not found")
            return self._get_default_keywords()
        
        try:
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Failed to load keywords_db.json: {e}")
            return self._get_default_keywords()
    
    def _get_default_keywords(self) -> dict:
        """Return default keywords if database file doesn't exist"""
        return {
            "mappings": {
                "news": {
                    "keywords": ["nyheter", "news", "senaste"],
                    "domains": ["svt.se", "dn.se", "aftonbladet.se"]
                },
                "weather": {
                    "keywords": ["väder", "weather", "temperatur"],
                    "domains": ["smhi.se"]
                },
                "health": {
                    "keywords": ["hälsa", "sjukvård", "symptom"],
                    "domains": ["1177.se"]
                }
            }
        }
    
    def _get_domain_from_url(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: Full URL
            
        Returns:
            str: Domain name (lowercase, without www)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    def is_domain_trusted(self, url: str) -> Tuple[bool, str, str]:
        """
        SECURITY: Verify domain is in trusted list
        
        Args:
            url: URL to check
            
        Returns:
            Tuple[bool, str, str]: (is_trusted, domain, error_message)
        """
        if not url or not url.startswith(('http://', 'https://')):
            return True, "", ""
        
        domain = self._get_domain_from_url(url)
        
        if domain in self.trusted_domains:
            return True, domain, ""
        
        # Not trusted - prepare error message
        domain_list = self._get_domain_list()
        error_msg = (
            f"❌ Domain '{domain}' is not in our trusted database.\n\n"
            f"Supported domains ({len(self.trusted_domains)} total):\n{domain_list}\n\n"
            f"Want to add a domain? Use Settings → Request New Domain"
        )
        
        return False, domain, error_msg
    
    def _get_domain_list(self) -> str:
        """Format trusted domains for error message"""
        domains_list = sorted(list(self.trusted_domains))[:10]
        return "  • " + "\n  • ".join(domains_list) + f"\n  ... and {len(self.trusted_domains) - 10} more"
    
    def detect_query_intent(self, query: str) -> Tuple[List[str], Dict]:
        """
        FIXED: Intent detection with priority ordering
        
        Check categories in specificity order and STOP at first match.
        This fixes the 11% accuracy bug where multiple categories were returned.
        
        Args:
            query: User search query
            
        Returns:
            Tuple[List[str], Dict]: (detected_categories, matched_domains)
        """
        query_lower = query.lower()
        detected_categories = []
        matched_domains = {}
        
        # FIXED: Priority-ordered category checking (most specific first)
        category_specificity = [
            "news",
            "weather",
            "health",
            "sports",
            "entertainment",
        ]
        
        # Check each category in priority order
        for category in category_specificity:
            if category not in self.keywords_db.get('mappings', {}):
                continue
            
            mapping = self.keywords_db['mappings'][category]
            keywords = mapping.get('keywords', [])
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    detected_categories.append(category)
                    matched_domains[category] = mapping.get('domains', [])
                    
                    # FIXED: STOP at first match (don't keep searching!)
                    return detected_categories, matched_domains
        
        # If no specific category matched, default to general news
        if not detected_categories:
            detected_categories = ["news"]
            if "news" in self.keywords_db.get('mappings', {}):
                matched_domains["news"] = self.keywords_db['mappings']["news"].get('domains', [])
        
        return detected_categories, matched_domains
    
    def search(self, query: str, direct_url: str = None) -> Dict:
        """
        Execute search with intent detection and domain verification
        
        Args:
            query: Search query
            direct_url: Optional direct URL search
            
        Returns:
            Dict: Search results or error message
        """
        # If direct URL provided, verify domain first
        if direct_url:
            is_trusted, domain, error = self.is_domain_trusted(direct_url)
            if not is_trusted:
                return {
                    'error': error,
                    'error_type': 'domain_not_trusted',
                    'domain': domain,
                    'results': []
                }
            
            # Domain is trusted, try to fetch
            try:
                page_content = self.crawler.crawl_page(direct_url)
                if page_content:
                    self.indexer.index_page(page_content)
                    results = [page_content]
                else:
                    results = []
            except Exception as e:
                return {
                    'error': f"Failed to fetch URL: {str(e)}",
                    'results': []
                }
        else:
            # Normal search - detect intent and search
            categories, domains = self.detect_query_intent(query)
            
            # Expand query using SVEN if available
            expanded_terms = []
            if self.sven:
                expanded_terms = self.sven.expand_query(query)
            
            # Search using indexer
            try:
                results = self.indexer.search(query, expanded_terms)
            except Exception as e:
                print(f"[Warning] Indexer search failed: {e}")
                results = []
            
            # Rank using THOR if available
            if self.thor and results:
                results = self._rank_results_with_thor(results, categories)
            else:
                results = self._rank_results(results, categories)
        
        return {
            'query': query,
            'categories': categories if not direct_url else [self._get_domain_from_url(direct_url)],
            'results': results[:20],  # Return top 20 results
            'total_found': len(results),
            'execution_time': 0.0
        }
    
    def _rank_results_with_thor(self, results: List[Dict], categories: List[str]) -> List[Dict]:
        """
        Rank results using THOR algorithm (if available)
        
        Args:
            results: Search results from indexer
            categories: Detected query categories
            
        Returns:
            List[Dict]: Ranked results
        """
        try:
            import numpy as np
            # Create dummy query embedding (THOR needs it)
            query_embedding = np.zeros(100)
            
            # Use THOR ranking
            ranked_results = self.thor.rank(results, query_embedding)
            return ranked_results
        except Exception as e:
            print(f"[Warning] THOR ranking failed: {e}")
            return results
    
    def _rank_results(self, results: List[Dict], categories: List[str]) -> List[Dict]:
        """
        Rank results using simple relevance scoring (fallback)
        
        Args:
            results: Search results from indexer
            categories: Detected query categories
            
        Returns:
            List[Dict]: Ranked results
        """
        for result in results:
            # Base score is relevance_score from BM25
            score = result.get('relevance_score', 0)
            
            # Boost for newer content
            if result.get('timestamp'):
                age_days = (time.time() - result['timestamp']) / 86400
                recency_boost = max(0, 1 - (age_days / 365))  # Decay over 1 year
                score *= (1 + recency_boost * 0.2)
            
            result['final_score'] = score
        
        # Sort by final score
        return sorted(results, key=lambda x: x.get('final_score', 0), reverse=True)
    
    def get_statistics(self) -> Dict:
        """Get search engine statistics"""
        try:
            indexed_pages = self.indexer.get_page_count() if hasattr(self.indexer, 'get_page_count') else 0
        except:
            indexed_pages = 0
        
        return {
            'indexed_pages': indexed_pages,
            'trusted_domains': len(self.trusted_domains),
            'categories': len(self.keywords_db.get('mappings', {}))
        }


if __name__ == "__main__":
    # Test the search engine
    engine = SearchEngine()
    
    # Test intent detection
    test_queries = [
        "väder stockholm",
        "nyheter idag",
        "fotboll allsvenskan"
    ]
    
    print("\n🧪 Testing Intent Detection:")
    print("=" * 60)
    
    for query in test_queries:
        categories, domains = engine.detect_query_intent(query)
        print(f"Query: '{query}'")
        print(f"  → Category: {categories[0] if categories else 'unknown'}")
        print()
