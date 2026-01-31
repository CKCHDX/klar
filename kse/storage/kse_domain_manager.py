"""
KSE Domain Manager - Domain list management for Klar Search Engine
"""
from pathlib import Path
from typing import Dict, List, Optional
from kse.core.kse_exceptions import ConfigurationError
from kse.core.kse_logger import get_logger
from kse.storage.kse_data_serializer import DataSerializer

logger = get_logger(__name__)


class DomainManager:
    """Manages Swedish domain list for crawling"""
    
    def __init__(self, domains_file: Path):
        """
        Initialize domain manager
        
        Args:
            domains_file: Path to domains JSON file
        """
        self.domains_file = Path(domains_file)
        self._serializer = DataSerializer()
        self._domains: List[Dict] = []
        self._domains_by_name: Dict[str, Dict] = {}
        self._load_domains()
    
    def _load_domains(self) -> None:
        """Load domains from JSON file"""
        try:
            data = self._serializer.load_json(self.domains_file)
            
            if not data or "domains" not in data:
                raise ConfigurationError(f"Invalid domains file: {self.domains_file}")
            
            self._domains = data["domains"]
            self._domains_by_name = {d["domain"]: d for d in self._domains}
            
            logger.info(f"Loaded {len(self._domains)} domains from {self.domains_file}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load domains: {e}")
    
    def get_all_domains(self) -> List[Dict]:
        """
        Get all domains
        
        Returns:
            List of domain dictionaries
        """
        return self._domains.copy()
    
    def get_domain(self, domain_name: str) -> Optional[Dict]:
        """
        Get specific domain info
        
        Args:
            domain_name: Domain name (e.g., 'svt.se')
        
        Returns:
            Domain dictionary or None if not found
        """
        return self._domains_by_name.get(domain_name)
    
    def get_domains_by_category(self, category: str) -> List[Dict]:
        """
        Get domains by category
        
        Args:
            category: Category name (e.g., 'news', 'education')
        
        Returns:
            List of domains in category
        """
        return [d for d in self._domains if d.get("category") == category]
    
    def get_domains_by_priority(self, priority: int) -> List[Dict]:
        """
        Get domains by priority
        
        Args:
            priority: Priority level (1 = highest)
        
        Returns:
            List of domains with priority
        """
        return [d for d in self._domains if d.get("priority") == priority]
    
    def get_high_priority_domains(self) -> List[Dict]:
        """
        Get high priority domains (priority 1)
        
        Returns:
            List of high priority domains
        """
        return self.get_domains_by_priority(1)
    
    def get_domain_names(self) -> List[str]:
        """
        Get list of domain names only
        
        Returns:
            List of domain name strings
        """
        return [d["domain"] for d in self._domains]
    
    def get_trust_score(self, domain_name: str) -> int:
        """
        Get trust score for domain
        
        Args:
            domain_name: Domain name
        
        Returns:
            Trust score (0-100) or 50 if not found
        """
        domain = self.get_domain(domain_name)
        return domain.get("trust_score", 50) if domain else 50
    
    def get_category(self, domain_name: str) -> str:
        """
        Get category for domain
        
        Args:
            domain_name: Domain name
        
        Returns:
            Category name or "general" if not found
        """
        domain = self.get_domain(domain_name)
        return domain.get("category", "general") if domain else "general"
    
    def is_allowed_domain(self, domain_name: str) -> bool:
        """
        Check if domain is in allowed list
        
        Args:
            domain_name: Domain name to check
        
        Returns:
            True if domain is allowed
        """
        return domain_name in self._domains_by_name
    
    def get_stats(self) -> Dict:
        """
        Get domain statistics
        
        Returns:
            Dictionary with statistics
        """
        categories = {}
        priorities = {}
        
        for domain in self._domains:
            category = domain.get("category", "unknown")
            priority = domain.get("priority", 0)
            
            categories[category] = categories.get(category, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
        
        return {
            "total_domains": len(self._domains),
            "categories": categories,
            "priorities": priorities,
            "avg_trust_score": sum(d.get("trust_score", 0) for d in self._domains) / len(self._domains)
                if self._domains else 0
        }
