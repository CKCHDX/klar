"""
Crawl Scheduling & Job Management

Manages domain crawl scheduling and job queue.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum
import heapq

from kse.core import KSELogger

logger = KSELogger.get_logger(__name__)


class CrawlJobStatus(Enum):
    """Status of a crawl job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class CrawlJob:
    """A crawl job for a domain."""
    domain_id: int
    domain_name: str
    domain_url: str
    priority: int = 0  # Higher = more urgent (for heap sorting)
    status: CrawlJobStatus = CrawlJobStatus.PENDING
    scheduled_time: datetime = field(default_factory=datetime.utcnow)
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    pages_crawled: int = 0
    errors: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """Comparison for heap queue (min-heap by scheduled_time)."""
        return self.scheduled_time < other.scheduled_time
    
    @property
    def is_ready(self) -> bool:
        """Check if job is ready to run."""
        return self.status == CrawlJobStatus.PENDING and \
               datetime.utcnow() >= self.scheduled_time
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get crawl duration in seconds."""
        if self.started_time and self.completed_time:
            return (self.completed_time - self.started_time).total_seconds()
        return None
    
    def start(self) -> None:
        """Mark job as started."""
        self.status = CrawlJobStatus.RUNNING
        self.started_time = datetime.utcnow()
    
    def complete(self, pages_crawled: int = 0) -> None:
        """Mark job as completed."""
        self.status = CrawlJobStatus.COMPLETED
        self.completed_time = datetime.utcnow()
        self.pages_crawled = pages_crawled
    
    def fail(self, error_message: str) -> None:
        """Mark job as failed."""
        self.status = CrawlJobStatus.FAILED
        self.completed_time = datetime.utcnow()
        self.error_message = error_message
        self.errors += 1
    
    def schedule_retry(self, delay_seconds: float = 300.0) -> None:
        """Schedule retry after delay."""
        if self.retry_count < self.max_retries:
            self.status = CrawlJobStatus.RETRY
            self.scheduled_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
            self.retry_count += 1
            logger.debug(f"Scheduled retry for {self.domain_name} in {delay_seconds}s (attempt {self.retry_count})")
        else:
            self.fail(f"Max retries exceeded ({self.max_retries})")


class CrawlScheduler:
    """
    Manages crawl job scheduling and queue.
    
    Features:
    - Priority-based scheduling
    - Retry management
    - Frequency management
    """
    
    def __init__(
        self,
        default_crawl_frequency_days: int = 7,
        max_queue_size: int = 10000
    ):
        """
        Initialize scheduler.
        
        Args:
            default_crawl_frequency_days: Days between crawls
            max_queue_size: Maximum pending jobs
        """
        self.default_frequency_days = default_crawl_frequency_days
        self.max_queue_size = max_queue_size
        self._queue: List[CrawlJob] = []  # Min-heap by scheduled_time
        self._jobs_by_domain: Dict[int, CrawlJob] = {}  # domain_id -> job
        self._job_history: List[CrawlJob] = []  # Completed/failed jobs
    
    def add_job(
        self,
        domain_id: int,
        domain_name: str,
        domain_url: str,
        delay_seconds: float = 0.0,
        priority: int = 0
    ) -> CrawlJob:
        """Add a crawl job to queue.
        
        Args:
            domain_id: Domain ID from database
            domain_name: Domain name
            domain_url: Domain URL
            delay_seconds: Delay before scheduling
            priority: Priority level (higher = more urgent)
        
        Returns:
            CrawlJob instance
        """
        # Check queue size
        if len(self._queue) >= self.max_queue_size:
            logger.warning(f"Crawl queue full ({self.max_queue_size} jobs)")
            return None
        
        # Create job
        scheduled = datetime.utcnow() + timedelta(seconds=delay_seconds)
        job = CrawlJob(
            domain_id=domain_id,
            domain_name=domain_name,
            domain_url=domain_url,
            scheduled_time=scheduled,
            priority=priority
        )
        
        # Add to queue and tracking
        heapq.heappush(self._queue, job)
        self._jobs_by_domain[domain_id] = job
        
        logger.debug(f"Scheduled {domain_name} (queue size: {len(self._queue)})")
        return job
    
    def get_next_job(self) -> Optional[CrawlJob]:
        """Get next job ready to run.
        
        Returns:
            CrawlJob if available, None otherwise
        """
        while self._queue:
            job = heapq.heappop(self._queue)
            
            if job.is_ready:
                return job
            else:
                # Put back in queue (not ready yet)
                heapq.heappush(self._queue, job)
                return None  # No jobs ready
        
        return None
    
    def get_pending_count(self) -> int:
        """Get number of pending jobs.
        
        Returns:
            Number of jobs
        """
        return sum(1 for job in self._queue if job.status == CrawlJobStatus.PENDING)
    
    def get_job_status(self, domain_id: int) -> Optional[CrawlJobStatus]:
        """Get status of job for domain.
        
        Args:
            domain_id: Domain ID
        
        Returns:
            CrawlJobStatus or None
        """
        job = self._jobs_by_domain.get(domain_id)
        return job.status if job else None
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        stats = {
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0,
            'retry': 0,
        }
        
        for job in self._queue:
            status_key = job.status.value
            if status_key in stats:
                stats[status_key] += 1
        
        # Add history
        for job in self._job_history:
            status_key = job.status.value
            if status_key in stats:
                stats[status_key] += 1
        
        return stats
    
    def clear_queue(self) -> int:
        """Clear pending jobs from queue.
        
        Returns:
            Number of jobs cleared
        """
        cleared = len(self._queue)
        self._queue = []
        self._jobs_by_domain = {}
        logger.info(f"Cleared {cleared} jobs from queue")
        return cleared
    
    def get_job_history(
        self,
        limit: int = 100,
        status_filter: Optional[CrawlJobStatus] = None
    ) -> List[CrawlJob]:
        """Get job history.
        
        Args:
            limit: Maximum jobs to return
            status_filter: Filter by status
        
        Returns:
            List of CrawlJob instances
        """
        history = self._job_history
        
        if status_filter:
            history = [j for j in history if j.status == status_filter]
        
        return history[-limit:]
    
    def archive_job(self, job: CrawlJob) -> None:
        """Move completed job to history.
        
        Args:
            job: CrawlJob instance
        """
        self._job_history.append(job)
        if job.domain_id in self._jobs_by_domain:
            del self._jobs_by_domain[job.domain_id]
