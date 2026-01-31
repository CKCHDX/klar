"""
Audit Logger - Audit trail logging for administrative actions
"""

import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit trail logger"""
    
    def __init__(self, log_path: Path = None):
        """
        Initialize audit logger
        
        Args:
            log_path: Path to audit log file
        """
        self.log_path = log_path or Path('data/logs/audit.log')
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"AuditLogger initialized (log_path={self.log_path})")
    
    def log_action(
        self,
        action: str,
        user: str = 'system',
        component: str = 'unknown',
        details: Dict[str, Any] = None
    ) -> None:
        """
        Log an auditable action
        
        Args:
            action: Action performed
            user: User who performed the action
            component: Component where action occurred
            details: Additional action details
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user': user,
            'component': component,
            'details': details or {}
        }
        
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
            
            logger.info(f"Audit: {user} - {action}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def get_recent_actions(self, limit: int = 100) -> list:
        """Get recent audit log entries"""
        if not self.log_path.exists():
            return []
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get last N lines
            recent_lines = lines[-limit:]
            
            return [json.loads(line) for line in recent_lines]
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
            return []
