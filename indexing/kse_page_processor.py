"""kse_page_processor.py - Page Content Processing

Processes crawled pages for indexing:
- Text extraction
- NLP tokenization
- Lemmatization
- Content cleaning
"""

import logging
from typing import Dict, List
import re

from kse.core import get_logger
from kse.nlp import NLPCore, StopwordManager

logger = get_logger('indexing')


class PageProcessor:
    """Process crawled pages for indexing"""
    
    def __init__(self):
        """Initialize page processor"""
        self.nlp = NLPCore()
        self.stopwords = StopwordManager()
        logger.debug("PageProcessor initialized")
    
    def process_page(self, page: Dict) -> Dict:
        """Process a single page for indexing
        
        Args:
            page: Page data with url, content, etc.
            
        Returns:
            Processed page data
        """
        try:
            # Extract text
            content = page.get('content', '')
            title = page.get('title', '')
            description = page.get('description', '')
            
            # Combine content
            full_text = f"{title} {description} {content}"
            
            # Clean text
            cleaned = self._clean_text(full_text)
            
            # Tokenize
            tokens = self.nlp.tokenize(cleaned)
            
            # Lemmatize
            lemmas = self.nlp.lemmatize(tokens)
            
            # Remove stopwords
            filtered = self.stopwords.remove_stopwords(lemmas)
            
            # Return processed page
            return {
                'url': page.get('url'),
                'title': title,
                'description': description,
                'domain': page.get('domain'),
                'original_tokens': tokens,
                'processed_tokens': filtered,
                'token_count': len(filtered),
            }
        
        except Exception as e:
            logger.error(f"Error processing page: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean text for processing
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^a-z0-9äöå\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def batch_process(self, pages: List[Dict]) -> List[Dict]:
        """Process multiple pages
        
        Args:
            pages: List of page data
            
        Returns:
            List of processed pages
        """
        processed = []
        for idx, page in enumerate(pages):
            try:
                processed_page = self.process_page(page)
                processed.append(processed_page)
                
                if (idx + 1) % 100 == 0:
                    logger.debug(f"Processed {idx + 1}/{len(pages)} pages")
            
            except Exception as e:
                logger.error(f"Failed to process page {page.get('url')}: {e}")
        
        return processed


__all__ = ["PageProcessor"]
