"""
kse_url_queue.py - Smart URL Queue Management

Manages URL queues with priority support, domain-based
organization, and FIFO/priority queue strategies.

Author: Klar Development Team
Date: 2026-01-26
Version: 1.0.0
"""

import logging
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
from enum import Enum
from collections import deque
import heapq

from kse.core import get_logger, KSEException

logger = get_logger('crawler')


class QueueStrategy(Enum):
    """URL queue strategies"""
    FIFO = 'fifo'          # First-in-first-out
    PRIORITY = 'priority'   # Priority-based
    DOMAIN_ROUND_ROBIN = 'domain_rr'  # Round-robin by domain


class KSEQueueException(KSEException):
    """URL queue exception"""
    pass


class URLQueue:
    """
    Smart URL queue manager.
    
    Supports:
    - Multiple queue strategies
    - Priority-based ordering
    - Domain-based organization
    - Duplicate prevention
    - Queue statistics
    """
    
    def __init__(self, strategy: str = 'priority'):
        """
        Initialize URL queue.
        
        Args:
            strategy: Queue strategy ('fifo', 'priority', 'domain_rr')
        """
        if strategy not in [s.value for s in QueueStrategy]:
            raise KSEQueueException(f"Unknown strategy: {strategy}")
        
        self.strategy = strategy
        
        # Main queues
        self._fifo_queue: deque = deque()
        self._priority_queue: List[Tuple[int, int, str]] = []  # (priority, id, url)
        self._domain_queues: Dict[str, deque] = {}
        
        # Tracking
        self._seen_urls: Set[str] = set()
        self._next_id = 0
        self._queue_stats = {
            'added': 0,
            'processed': 0,
            'failed': 0,
            'discarded': 0,
        }
        
        logger.debug(f"URLQueue initialized with strategy: {strategy}")
    
    def add(
        self,
        url: str,
        domain: str,
        priority: int = 5,
    ) -> bool:
        """
        Add URL to queue.
        
        Args:
            url: URL to add
            domain: Domain for organization
            priority: Priority (1-10, higher = more important)
            
        Returns:
            True if added, False if duplicate
        """
        # Check for duplicates
        if url in self._seen_urls:
            self._queue_stats['discarded'] += 1
            logger.debug(f"URL already queued (duplicate): {url}")
            return False
        
        self._seen_urls.add(url)
        self._queue_stats['added'] += 1
        
        # Add based on strategy
        if self.strategy == 'fifo':
            self._fifo_queue.append((url, domain, priority))
        
        elif self.strategy == 'priority':
            # Negative priority for min-heap (higher priority first)
            heapq.heappush(
                self._priority_queue,
                (-priority, self._next_id, url, domain)
            )
            self._next_id += 1
        
        elif self.strategy == 'domain_rr':
            if domain not in self._domain_queues:
                self._domain_queues[domain] = deque()
            self._domain_queues[domain].append((url, priority))
        
        logger.debug(f"URL added to queue: {url} (priority={priority})")
        return True
    
    def get(self) -> Optional[Tuple[str, str, int]]:
        """
        Get next URL from queue.
        
        Returns:
            (url, domain, priority) or None if empty
        """
        if self.is_empty():
            return None
        
        url = None
        domain = None
        priority = 5
        
        try:
            if self.strategy == 'fifo':
                url, domain, priority = self._fifo_queue.popleft()
            
            elif self.strategy == 'priority':
                neg_priority, _, url, domain = heapq.heappop(self._priority_queue)
                priority = -neg_priority
            
            elif self.strategy == 'domain_rr':
                # Get from first non-empty domain queue
                for domain_name in self._domain_queues:
                    if self._domain_queues[domain_name]:
                        url, priority = self._domain_queues[domain_name].popleft()
                        domain = domain_name
                        break
            
            if url:
                self._queue_stats['processed'] += 1
                logger.debug(f"URL dequeued: {url}")
            
            return (url, domain, priority) if url else None
            
        except Exception as e:
            logger.error(f"Error getting URL from queue: {e}")
            raise KSEQueueException(f"Failed to get URL from queue") from e
    
    def peek(self) -> Optional[Tuple[str, str, int]]:
        """
        Peek at next URL without removing it.
        
        Returns:
            (url, domain, priority) or None if empty
        """
        if self.is_empty():
            return None
        
        if self.strategy == 'fifo' and self._fifo_queue:
            url, domain, priority = self._fifo_queue[0]
            return (url, domain, priority)
        
        elif self.strategy == 'priority' and self._priority_queue:
            neg_priority, _, url, domain = self._priority_queue[0]
            return (url, domain, -neg_priority)
        
        elif self.strategy == 'domain_rr':
            for domain_name in self._domain_queues:
                if self._domain_queues[domain_name]:
                    url, priority = self._domain_queues[domain_name][0]
                    return (url, domain_name, priority)
        
        return None
    
    def is_empty(self) -> bool:
        """
        Check if queue is empty.
        
        Returns:
            True if empty
        """
        if self.strategy == 'fifo':
            return len(self._fifo_queue) == 0
        elif self.strategy == 'priority':
            return len(self._priority_queue) == 0
        else:  # domain_rr
            return all(len(q) == 0 for q in self._domain_queues.values())
    
    def size(self) -> int:
        """
        Get queue size.
        
        Returns:
            Number of URLs in queue
        """
        if self.strategy == 'fifo':
            return len(self._fifo_queue)
        elif self.strategy == 'priority':
            return len(self._priority_queue)
        else:  # domain_rr
            return sum(len(q) for q in self._domain_queues.values())
    
    def clear(self) -> None:
        """Clear all queues"""
        self._fifo_queue.clear()
        self._priority_queue.clear()
        self._domain_queues.clear()
        self._seen_urls.clear()
        logger.info("URL queue cleared")
    
    def get_stats(self) -> Dict:
        """
        Get queue statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'strategy': self.strategy,
            'current_size': self.size(),
            'unique_urls_seen': len(self._seen_urls),
            'total_added': self._queue_stats['added'],
            'total_processed': self._queue_stats['processed'],
            'total_failed': self._queue_stats['failed'],
            'total_discarded': self._queue_stats['discarded'],
            'domains': len(self._domain_queues) if self.strategy == 'domain_rr' else 0,
        }
    
    def record_failure(self) -> None:
        """Record failed URL processing"""
        self._queue_stats['failed'] += 1
    
    def get_domain_stats(self, domain: str) -> Optional[Dict]:
        """
        Get statistics for specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Domain statistics or None
        """
        if self.strategy != 'domain_rr':
            return None
        
        if domain not in self._domain_queues:
            return None
        
        return {
            'domain': domain,
            'queue_size': len(self._domain_queues[domain]),
        }


__all__ = ["URLQueue", "QueueStrategy", "KSEQueueException"]
