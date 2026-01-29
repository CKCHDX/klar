"""
Enhanced Search Engine Integration for Klar 4.0
Integrates hierarchical keywords and metadata search with existing search engine
"""

from engine.search_engine import SearchEngine
from engine.hierarchical_keywords import HierarchicalKeywordHandler
from engine.metadata_extractor import MetadataExtractor
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class EnhancedSearchEngine(SearchEngine):
    """
    Enhanced search engine with hierarchical keywords and metadata support
    Extends existing SearchEngine with new capabilities
    """
    
    def __init__(self):
        # Initialize base search engine
        super().__init__()
        
        # Initialize new components
        self.hierarchical_keywords = HierarchicalKeywordHandler()
        self.metadata_extractor = MetadataExtractor()
        
        print("[EnhancedSearch] Hierarchical keywords initialized")
        print("[EnhancedSearch] Metadata extractor initialized")
        
        # Get statistics
        stats = self.hierarchical_keywords.get_statistics()
        print(f"[EnhancedSearch] Categories: {stats['total_categories']}")
        print(f"[EnhancedSearch] Keywords: {stats['total_keywords']}")
        print(f"[EnhancedSearch] Metadata search: {'enabled' if stats['metadata_enabled'] else 'disabled'}")
    
    def search_enhanced(self, query: str, demographic: str = "general", use_metadata: bool = True) -> Dict:
        """
        Enhanced search with hierarchical keywords and metadata
        
        Args:
            query: Search query
            demographic: User demographic
            use_metadata: Enable metadata-based search
            
        Returns:
            Enhanced search results
        """
        print(f"\n[EnhancedSearch] Query: '{query}'")
        print(f"[EnhancedSearch] Metadata search: {'enabled' if use_metadata else 'disabled'}")
        
        # Find matching categories in hierarchy
        matching_categories = self.hierarchical_keywords.find_categories(query)
        print(f"[EnhancedSearch] Found {len(matching_categories)} matching categories")
        
        # Get expanded domains from hierarchical structure
        expanded_domains = set()
        category_info = []
        
        for cat in matching_categories[:5]:  # Top 5 categories
            cat_id = cat['id']
            cat_name = cat['name']
            score = cat['score']
            
            print(f"[EnhancedSearch] Category: {cat_name} (score: {score:.2f})")
            
            # Get domains for this category
            domains = self.hierarchical_keywords.get_domains_for_category(cat_id)
            print(f"[EnhancedSearch]   Domains: {len(domains)}")
            
            # Get metadata tags
            metadata_tags = self.hierarchical_keywords.get_metadata_tags_for_category(cat_id)
            
            # Filter by whitelist
            for domain in domains:
                if self._is_domain_whitelisted(domain):
                    expanded_domains.add(domain)
            
            category_info.append({
                'id': cat_id,
                'name': cat_name,
                'score': score,
                'domains': domains,
                'metadata_tags': metadata_tags
            })
        
        # Combine with base search engine results
        base_results = self.search(query, demographic)
        
        # If metadata search is enabled, enhance results with metadata
        if use_metadata:
            enhanced_results = self._enhance_with_metadata(
                base_results['results'],
                query,
                category_info
            )
        else:
            enhanced_results = base_results['results']
        
        # Add hierarchical information to response
        return {
            **base_results,
            'results': enhanced_results,
            'hierarchical_categories': category_info,
            'expanded_domains_count': len(expanded_domains),
            'metadata_enhanced': use_metadata
        }
    
    def _enhance_with_metadata(self, results: List[Dict], query: str, category_info: List[Dict]) -> List[Dict]:
        """
        Enhance results with metadata information
        
        Args:
            results: Base search results
            query: Search query
            category_info: Hierarchical category information
            
        Returns:
            Enhanced results with metadata
        """
        enhanced = []
        
        for result in results:
            url = result.get('url', '')
            
            # Extract metadata if we have HTML content
            if 'html' in result or 'content' in result:
                html_content = result.get('html') or result.get('content', '')
                metadata = self.metadata_extractor.extract_metadata(html_content, url)
                
                # Build search index from metadata
                search_index = self.metadata_extractor.build_search_index(metadata)
                
                # Calculate metadata relevance score
                metadata_score = self._calculate_metadata_relevance(
                    query,
                    metadata,
                    category_info
                )
                
                # Add metadata to result
                result['metadata'] = {
                    'title': metadata.get('title', ''),
                    'description': metadata.get('description', ''),
                    'keywords': metadata.get('keywords', []),
                    'og_tags': metadata.get('og_tags', {}),
                    'headings': metadata.get('headings', {}),
                    'metadata_score': metadata_score
                }
                
                # Boost relevance based on metadata match
                if 'relevance' in result:
                    result['relevance'] = result['relevance'] * (1 + metadata_score * 0.3)
            
            enhanced.append(result)
        
        # Re-sort by relevance
        enhanced.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        return enhanced
    
    def _calculate_metadata_relevance(self, query: str, metadata: Dict, category_info: List[Dict]) -> float:
        """
        Calculate metadata relevance score
        
        Args:
            query: Search query
            metadata: Extracted metadata
            category_info: Category information
            
        Returns:
            Relevance score (0-1)
        """
        score = 0.0
        query_words = set(query.lower().split())
        
        # Check title match (weight: 2.0)
        title = metadata.get('title', '').lower()
        title_words = set(title.split())
        title_overlap = len(query_words & title_words)
        if title_overlap > 0:
            score += (title_overlap / max(len(query_words), 1)) * 2.0
        
        # Check description match (weight: 1.5)
        description = metadata.get('description', '').lower()
        if any(word in description for word in query_words):
            score += 1.5
        
        # Check keywords match (weight: 1.8)
        keywords = [k.lower() for k in metadata.get('keywords', [])]
        for word in query_words:
            if word in keywords:
                score += 1.8
        
        # Check metadata tags from categories
        for cat in category_info:
            metadata_tags = set(cat.get('metadata_tags', []))
            
            # Check if any metadata tags appear in page metadata
            og_tags = metadata.get('og_tags', {})
            og_values = ' '.join(og_tags.values()).lower()
            
            for tag in metadata_tags:
                if tag in title or tag in description or tag in og_values:
                    score += 0.5
        
        # Normalize score
        return min(score / 5.0, 1.0)
    
    def discover_subpages(self, domain: str, query: str, max_depth: int = 2) -> List[Dict]:
        """
        Discover subpages within a domain using metadata
        Similar to how Google discovers and indexes pages
        
        Args:
            domain: Domain to search
            query: Search query
            max_depth: Maximum depth to crawl
            
        Returns:
            List of discovered subpages with metadata
        """
        if not self._is_domain_whitelisted(domain):
            print(f"[SubpageDiscovery] Domain {domain} not whitelisted")
            return []
        
        print(f"[SubpageDiscovery] Discovering subpages on {domain} for '{query}'")
        
        discovered = []
        visited = set()
        to_visit = [f"https://{domain}"]
        
        depth = 0
        while to_visit and depth < max_depth:
            current_url = to_visit.pop(0)
            
            if current_url in visited:
                continue
            
            visited.add(current_url)
            
            try:
                # Fetch page
                response = self.session.get(current_url, timeout=5)
                if response.status_code != 200:
                    continue
                
                html = response.text
                
                # Extract metadata
                metadata = self.metadata_extractor.extract_metadata(html, current_url)
                
                # Check if metadata matches query
                search_index = self.metadata_extractor.build_search_index(metadata)
                query_lower = query.lower()
                
                # Calculate relevance
                relevance = 0.0
                if query_lower in search_index.lower():
                    relevance = search_index.lower().count(query_lower) / max(len(search_index), 1)
                
                if relevance > 0.01:  # Has some relevance
                    # Extract subpage structure
                    structure = self.metadata_extractor.extract_subpage_structure(metadata)
                    
                    discovered.append({
                        'url': current_url,
                        'title': metadata.get('title', ''),
                        'description': metadata.get('description', ''),
                        'relevance': relevance,
                        'path': structure.get('path', ''),
                        'section': structure.get('section'),
                        'metadata': metadata
                    })
                
                # Extract links for further crawling
                if depth < max_depth - 1:
                    links = metadata.get('links', [])
                    for link in links[:20]:  # Limit to 20 links per page
                        href = link.get('href', '')
                        if href.startswith('/'):
                            full_url = urljoin(current_url, href)
                            if full_url not in visited:
                                to_visit.append(full_url)
            
            except Exception as e:
                print(f"[SubpageDiscovery] Error on {current_url}: {str(e)[:50]}")
                continue
            
            depth += 1
        
        # Sort by relevance
        discovered.sort(key=lambda x: x['relevance'], reverse=True)
        
        print(f"[SubpageDiscovery] Discovered {len(discovered)} relevant subpages")
        
        return discovered[:20]  # Return top 20
    
    def search_by_metadata_tags(self, tags: List[str], limit: int = 10) -> List[Dict]:
        """
        Search for domains and pages by metadata tags
        Like Google's site: search operator
        
        Args:
            tags: List of metadata tags to search for
            limit: Maximum results to return
            
        Returns:
            List of matching results
        """
        print(f"[MetadataSearch] Searching for tags: {tags}")
        
        # Find categories matching these tags
        matching_categories = self.hierarchical_keywords.search_by_metadata_tags(tags)
        
        results = []
        for cat in matching_categories[:limit]:
            cat_id = cat['id']
            cat_name = cat['name']
            score = cat['score']
            domains = cat.get('priority_domains', [])
            
            # Filter by whitelist
            whitelisted_domains = [
                d for d in domains
                if self._is_domain_whitelisted(d)
            ]
            
            if whitelisted_domains:
                results.append({
                    'category': cat_name,
                    'category_id': cat_id,
                    'score': score,
                    'matching_tags': cat.get('matching_tags', []),
                    'domains': whitelisted_domains[:5]  # Top 5 domains
                })
        
        print(f"[MetadataSearch] Found {len(results)} matching categories")
        
        return results
    
    def get_domain_info_with_metadata(self, domain: str) -> Optional[Dict]:
        """
        Get comprehensive domain information including metadata
        
        Args:
            domain: Domain to get info for
            
        Returns:
            Domain information dictionary
        """
        if not self._is_domain_whitelisted(domain):
            return None
        
        # Get domain metadata from hierarchical database
        domain_metadata = self.hierarchical_keywords.get_domain_metadata(domain)
        
        # Try to fetch and extract metadata from homepage
        try:
            url = f"https://{domain}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                html = response.text
                extracted_metadata = self.metadata_extractor.extract_metadata(html, url)
                
                return {
                    'domain': domain,
                    'whitelisted': True,
                    'database_metadata': domain_metadata,
                    'extracted_metadata': {
                        'title': extracted_metadata.get('title', ''),
                        'description': extracted_metadata.get('description', ''),
                        'keywords': extracted_metadata.get('keywords', []),
                        'og_tags': extracted_metadata.get('og_tags', {})
                    },
                    'subpage_structure': self.metadata_extractor.extract_subpage_structure(extracted_metadata)
                }
        except Exception as e:
            print(f"[DomainInfo] Error fetching {domain}: {e}")
        
        return {
            'domain': domain,
            'whitelisted': True,
            'database_metadata': domain_metadata,
            'extracted_metadata': None
        }
