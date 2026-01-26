"""kse_indexer_pipeline.py - Main Indexing Orchestrator

Coordinates the complete indexing pipeline:
- Page processing
- TF-IDF calculation
- Inverted index building
- Metadata extraction
- Index persistence
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
import json

from kse.core import get_logger, KSEException
from kse.storage import StorageManager
from kse.cache import CacheManager
from kse.nlp import NLPCore

logger = get_logger('indexing')


class KSEIndexingException(KSEException):
    """Indexing-specific exceptions"""
    pass


class IndexerPipeline:
    """Main indexing orchestrator"""
    
    def __init__(self, storage_manager: StorageManager, cache_manager: CacheManager):
        """Initialize indexer pipeline
        
        Args:
            storage_manager: Storage operations
            cache_manager: Cache for performance
        """
        self.storage = storage_manager
        self.cache = cache_manager
        self.nlp = NLPCore()
        self.stats = {
            'total_pages': 0,
            'indexed_pages': 0,
            'failed_pages': 0,
            'start_time': None,
            'end_time': None,
        }
        logger.info("IndexerPipeline initialized")
    
    def index_pages(self, pages: List[Dict]) -> Dict:
        """Index a batch of crawled pages
        
        Args:
            pages: List of crawled page data
            
        Returns:
            Indexing statistics
        """
        import time
        self.stats['start_time'] = time.time()
        self.stats['total_pages'] = len(pages)
        
        inverted_index = {}
        metadata_index = {}
        tfidf_scores = {}
        
        try:
            for idx, page in enumerate(pages):
                try:
                    # Process each page
                    url = page.get('url')
                    content = page.get('content', '')
                    
                    # Extract metadata
                    metadata = self._extract_metadata(page)
                    metadata_index[url] = metadata
                    
                    # Process content with NLP
                    tokens = self.nlp.tokenize(content)
                    lemmas = self.nlp.lemmatize(tokens)
                    
                    # Build inverted index
                    for term in lemmas:
                        if term not in inverted_index:
                            inverted_index[term] = []
                        inverted_index[term].append(url)
                    
                    self.stats['indexed_pages'] += 1
                    
                    if (idx + 1) % 100 == 0:
                        logger.debug(f"Indexed {idx + 1}/{len(pages)} pages")
                
                except Exception as e:
                    logger.error(f"Failed to index {page.get('url')}: {e}")
                    self.stats['failed_pages'] += 1
            
            # Save indices
            self.storage.save_index(inverted_index)
            self.storage.save_metadata(metadata_index)
            
            self.stats['end_time'] = time.time()
            logger.info(f"Indexing complete: {self.stats['indexed_pages']} pages indexed")
            
            return self.stats
        
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            raise KSEIndexingException(f"Indexing error: {e}")
    
    def _extract_metadata(self, page: Dict) -> Dict:
        """Extract metadata from page"""
        return {
            'url': page.get('url'),
            'title': page.get('title', ''),
            'description': page.get('description', ''),
            'domain': page.get('domain', ''),
            'timestamp': page.get('timestamp'),
        }
    
    def get_stats(self) -> Dict:
        """Get indexing statistics"""
        return self.stats.copy()


__all__ = ["IndexerPipeline", "KSEIndexingException"]
