"""
KSE Result Processor - Process and format search results
"""
from typing import List, Dict
from kse.core.kse_logger import get_logger

logger = get_logger(__name__, "search.log")


class ResultProcessor:
    """Process and format search results"""
    
    def __init__(self):
        """Initialize result processor"""
        pass
    
    def format_results(
        self,
        results: List[Dict],
        query: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Format search results
        
        Args:
            results: Raw search results
            query: Original query
            max_results: Maximum number of results
        
        Returns:
            Formatted results
        """
        # Limit results
        results = results[:max_results]
        
        # Format each result
        formatted = []
        for i, result in enumerate(results):
            formatted_result = {
                'rank': i + 1,
                'url': result.get('url', ''),
                'title': result.get('title', 'Untitled'),
                'description': result.get('description', ''),
                'domain': result.get('domain', ''),
                'score': result.get('score', 0),
                'snippet': self._generate_snippet(
                    result.get('description', ''),
                    query
                )
            }
            formatted.append(formatted_result)
        
        logger.debug(f"Formatted {len(formatted)} results")
        
        return formatted
    
    def _generate_snippet(self, text: str, query: str, max_length: int = 150) -> str:
        """
        Generate search result snippet with query highlight context
        
        Args:
            text: Full text
            query: Search query
            max_length: Maximum snippet length
        
        Returns:
            Snippet text
        """
        if not text:
            return ""
        
        # If text is short enough, return as is
        if len(text) <= max_length:
            return text
        
        # Try to find query terms in text
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find position of query in text
        pos = text_lower.find(query_lower)
        
        if pos >= 0:
            # Center snippet around query
            start = max(0, pos - max_length // 3)
            end = min(len(text), start + max_length)
            
            snippet = text[start:end]
            
            # Add ellipsis
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
        else:
            # Just take first part
            snippet = text[:max_length] + "..."
        
        return snippet
    
    def deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """
        Remove duplicate results (same URL or very similar title)
        
        Args:
            results: Search results
        
        Returns:
            Deduplicated results
        """
        seen_urls = set()
        deduplicated = []
        
        for result in results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(result)
        
        return deduplicated
    
    def diversify_results(
        self,
        results: List[Dict],
        max_per_domain: int = 3
    ) -> List[Dict]:
        """
        Diversify results to avoid too many from same domain
        
        Args:
            results: Search results
            max_per_domain: Maximum results per domain
        
        Returns:
            Diversified results
        """
        domain_count = {}
        diversified = []
        
        for result in results:
            domain = result.get('domain', '')
            count = domain_count.get(domain, 0)
            
            if count < max_per_domain:
                diversified.append(result)
                domain_count[domain] = count + 1
        
        return diversified
    
    def add_metadata(self, results: List[Dict], metadata: Dict) -> List[Dict]:
        """
        Add metadata to results
        
        Args:
            results: Search results
            metadata: Metadata to add
        
        Returns:
            Results with metadata
        """
        for result in results:
            result['_metadata'] = metadata
        
        return results
