"""
KSE Page Processor - Page parsing and preparation for indexing
"""
from typing import Dict, List
from kse.nlp.kse_nlp_core import NLPCore
from kse.core.kse_logger import get_logger

logger = get_logger(__name__)


class PageProcessor:
    """Process pages for indexing"""
    
    def __init__(self, nlp_core: NLPCore):
        """
        Initialize page processor
        
        Args:
            nlp_core: NLP core instance
        """
        self.nlp = nlp_core
    
    def process_page(self, page_data: Dict) -> Dict:
        """
        Process page for indexing
        
        Args:
            page_data: Page data from crawler
        
        Returns:
            Processed page data ready for indexing
        """
        try:
            # Extract fields
            url = page_data.get('url', '')
            title = page_data.get('title', '')
            description = page_data.get('description', '')
            content = page_data.get('content', '')
            domain = page_data.get('domain', '')
            
            # Process title (higher weight)
            title_tokens = self.nlp.process_text(title)
            
            # Process description
            description_tokens = self.nlp.process_text(description)
            
            # Process main content
            content_tokens = self.nlp.process_text(content)
            
            # Combine tokens with weights
            # Title appears 3 times (higher weight)
            # Description appears 2 times
            # Content appears 1 time
            all_tokens = (
                title_tokens * 3 +
                description_tokens * 2 +
                content_tokens
            )
            
            # Extract keywords
            keywords = self.nlp.extract_keywords(content, max_keywords=10)
            
            processed = {
                'doc_id': url,
                'url': url,
                'domain': domain,
                'title': title,
                'description': description,
                'tokens': all_tokens,
                'keywords': keywords,
                'title_tokens': title_tokens,
                'content_length': len(content),
                'token_count': len(all_tokens),
                'unique_token_count': len(set(all_tokens))
            }
            
            logger.debug(f"Processed page {url}: {len(all_tokens)} tokens")
            
            return processed
        
        except Exception as e:
            logger.error(f"Failed to process page {page_data.get('url', 'unknown')}: {e}")
            return None
    
    def process_pages(self, pages: List[Dict]) -> List[Dict]:
        """
        Process multiple pages
        
        Args:
            pages: List of page data from crawler
        
        Returns:
            List of processed pages
        """
        processed_pages = []
        
        for page in pages:
            processed = self.process_page(page)
            if processed:
                processed_pages.append(processed)
        
        logger.info(f"Processed {len(processed_pages)} pages")
        
        return processed_pages
