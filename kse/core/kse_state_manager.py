"""
KSE State Manager - Tracks server state and first-run status
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class StateManager:
    """Manages server state persistence"""
    
    def __init__(self, state_dir: Path = None):
        """Initialize state manager
        
        Args:
            state_dir: Directory to store state file (default: data/state)
        """
        if state_dir is None:
            state_dir = Path.cwd() / 'data' / 'state'
        
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / 'server_state.json'
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    logger.info(f"Loaded state from {self.state_file}")
                    return state
        except Exception as e:
            logger.warning(f"Could not load state file: {e}")
        
        # Return default state
        return {
            'setup_completed': False,
            'first_run_date': None,
            'last_startup': None,
            'version': '3.0.0',
            'indexed_domains_count': 0,
            'total_documents': 0
        }
    
    def _save_state(self):
        """Save state to file"""
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved state to {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def is_first_run(self) -> bool:
        """Check if this is the first run"""
        return not self.state.get('setup_completed', False)
    
    def mark_setup_complete(self):
        """Mark setup as completed"""
        now = datetime.now().isoformat()
        if not self.state.get('first_run_date'):
            self.state['first_run_date'] = now
        self.state['setup_completed'] = True
        self.state['last_startup'] = now
        self._save_state()
        logger.info("Setup marked as complete")
    
    def update_statistics(self, indexed_domains: int, total_docs: int):
        """Update statistics"""
        self.state['indexed_domains_count'] = indexed_domains
        self.state['total_documents'] = total_docs
        self.state['last_startup'] = datetime.now().isoformat()
        self._save_state()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self.state.copy()
    
    def reset_setup(self):
        """Reset setup status (for debugging)"""
        self.state['setup_completed'] = False
        self._save_state()
        logger.warning("Setup status reset - will run setup on next start")
