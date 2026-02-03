"""
KSE Indexer Pipeline - Main indexing orchestrator
"""
from typing import List, Dict, Union
from kse.indexing.kse_inverted_index import InvertedIndex
from kse.indexing.kse_tf_idf_calculator import TFIDFCalculator
from kse.indexing.kse_page_processor import PageProcessor
from kse.nlp.kse_nlp_core import NLPCore
from kse.storage.kse_storage_manager import StorageManager
from kse.core.kse_logger import get_logger

logger = get_logger(__name__, "indexer.log")


class IndexerPipeline:
    """Main indexing pipeline orchestrator"""
    
    # Configuration constants
    DEFAULT_INDEX_BATCH_SIZE = 100  # Process pages in batches to avoid memory overflow
    GC_INTERVAL = 500  # Run garbage collection every N pages
    
    def __init__(self, storage_manager: StorageManager, nlp_core: NLPCore = None, batch_size: int = None):
        """
        Initialize indexer pipeline
        
        Args:
            storage_manager: Storage manager instance
            nlp_core: NLP core instance (creates default if None)
            batch_size: Number of pages to process per batch (defaults to DEFAULT_INDEX_BATCH_SIZE)
        """
        self.storage = storage_manager
        self.nlp = nlp_core or NLPCore(enable_lemmatization=True, enable_stopword_removal=True)
        self.batch_size = batch_size or self.DEFAULT_INDEX_BATCH_SIZE
        
        # Initialize components
        self.inverted_index = InvertedIndex()
        self.page_processor = PageProcessor(self.nlp)
        self.tfidf_calculator = None  # Initialized after indexing
        
        # Try to load existing index
        self._load_index()
        
        logger.info(f"Indexer pipeline initialized (batch_size={self.batch_size})")
    
    def _load_index(self) -> None:
        """Load existing index from storage"""
        try:
            # Load inverted index
            index_data = self.storage.load_index("inverted")
            if index_data:
                # Convert loaded dict back to defaultdict
                from collections import defaultdict
                loaded_index = index_data.get('index', {})
                
                # Rebuild defaultdict structure
                for term, docs in loaded_index.items():
                    self.inverted_index.index[term] = defaultdict(list, docs)
                
                self.inverted_index.documents = index_data.get('documents', {})
                self.inverted_index.total_documents = index_data.get('total_documents', 0)
                logger.info(f"Loaded existing index with {self.inverted_index.total_documents} documents")
        except Exception as e:
            logger.warning(f"Failed to load existing index: {e}")
    
    def _save_index(self) -> None:
        """Save index to storage"""
        try:
            # Convert defaultdict to regular dict for serialization
            # Also convert nested defaultdicts
            regular_index = {}
            for term, docs in self.inverted_index.index.items():
                regular_index[term] = dict(docs)
            
            index_data = {
                'index': regular_index,
                'documents': self.inverted_index.documents,
                'total_documents': self.inverted_index.total_documents
            }
            self.storage.save_index(index_data, "inverted")
            
            # Save statistics
            stats = self.inverted_index.get_statistics()
            self.storage.save_metadata(stats, "index")
            
            logger.info(f"Saved index with {self.inverted_index.total_documents} documents, size: {stats.get('index_size_mb', 0)} MB")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def index_pages(self, pages: List[Dict]) -> Dict:
        """
        Index pages from crawler
        
        Args:
            pages: List of page data from crawler
        
        Returns:
            Dictionary with indexing statistics
        """
        logger.info(f"Starting indexing of {len(pages)} pages")
        
        # Process pages in batches to avoid memory overflow
        total_indexed = 0
        
        for batch_start in range(0, len(pages), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(pages))
            batch = pages[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//self.batch_size + 1}/{(len(pages)-1)//self.batch_size + 1}")
            
            # Process pages
            processed_pages = self.page_processor.process_pages(batch)
            
            # Index pages
            for page in processed_pages:
                try:
                    doc_id = page['doc_id']
                    tokens = page['tokens']
                    
                    # Metadata for document
                    metadata = {
                        'url': page['url'],
                        'domain': page['domain'],
                        'title': page['title'],
                        'description': page['description'],
                        'keywords': page['keywords'],
                        'content_length': page['content_length'],
                        'token_count': page['token_count']
                    }
                    
                    # Add to inverted index
                    self.inverted_index.add_document(doc_id, tokens, metadata)
                    total_indexed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to index page {page.get('url', 'unknown')}: {e}")
            
            # Periodic garbage collection to free memory
            if batch_start > 0 and batch_start % self.GC_INTERVAL == 0:
                import gc
                gc.collect()
                logger.debug(f"Garbage collection performed after {batch_start} pages")
        
        # Initialize TF-IDF calculator
        self.tfidf_calculator = TFIDFCalculator(self.inverted_index)
        
        # Save index
        self._save_index()
        
        logger.info(f"Indexed {total_indexed} pages successfully")
        
        return {
            'pages_processed': len(pages),
            'pages_indexed': total_indexed,
            'total_documents': self.inverted_index.total_documents,
            'total_terms': len(self.inverted_index.index)
        }
    
    def search(self, query: Union[str, List[str]], max_results: int = 10) -> List[Dict]:
        """
        Search the index
        
        Args:
            query: Search query. Can be either:
                   - str: Raw query string that will be processed through NLP pipeline
                   - List[str]: Pre-processed terms (already tokenized, lemmatized, and lowercased)
            max_results: Maximum number of results
        
        Returns:
            List of search results
        """
        # Handle pre-processed terms (list) or raw query (string)
        if isinstance(query, list):
            query_terms = query
            query_str = ' '.join(query_terms) if query_terms else ''
        else:
            query_str = query
            query_terms = self.nlp.process_query(query)
        
        if not query_terms:
            logger.warning(f"No valid terms in query: {query_str if query_str else '(empty)'}")
            return []
        
        logger.info(f"Searching for: {query_str} -> {query_terms}")
        
        # Initialize TF-IDF if not already done
        if not self.tfidf_calculator:
            self.tfidf_calculator = TFIDFCalculator(self.inverted_index)
        
        # Rank documents
        ranked_docs = self.tfidf_calculator.rank_documents(query_terms)
        
        # Get top results
        results = []
        for doc_id, score in ranked_docs[:max_results]:
            metadata = self.inverted_index.documents.get(doc_id, {})
            results.append({
                'url': doc_id,
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'domain': metadata.get('domain', ''),
                'score': round(score * 100, 2)  # Convert to 0-100 scale
            })
        
        logger.info(f"Found {len(results)} results for query: {query_str}")
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        Get indexer statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = self.inverted_index.get_statistics()
        
        if self.tfidf_calculator:
            stats['tfidf_cache_size'] = len(self.tfidf_calculator.idf_cache)
        
        return stats
    
    def rebuild_index(self, pages: List[Dict]) -> Dict:
        """
        Rebuild index from scratch
        
        Args:
            pages: List of page data
        
        Returns:
            Dictionary with statistics
        """
        logger.info("Rebuilding index from scratch")
        
        # Clear existing index
        self.inverted_index.clear()
        
        # Index pages
        return self.index_pages(pages)
