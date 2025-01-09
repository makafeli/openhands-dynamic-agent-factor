"""
Manager for technology keywords and their associated agents.
"""

from typing import Dict, Any, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class KeywordManager:
    """
    Manages technology keywords and their associated agents.
    """
    
    def __init__(self, state_file: Optional[Path] = None):
        """Initialize the keyword manager."""
        self.state_file = state_file or Path("/tmp/dynamic_agents/keywords.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize state
        self.keywords = self._load_state()
        
    def is_valid_keyword(self, keyword: str) -> bool:
        """Check if a keyword is valid."""
        keyword = keyword.lower()
        return keyword in self.keywords
        
    def register_keyword(
        self,
        keyword: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a new keyword."""
        keyword = keyword.lower()
        if keyword not in self.keywords:
            self.keywords[keyword] = {
                "metadata": metadata or {},
                "agents": {}
            }
            self._save_state()
            
    def update_agent_status(
        self,
        keyword: str,
        agent_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update agent status for a keyword."""
        keyword = keyword.lower()
        if keyword not in self.keywords:
            self.register_keyword(keyword)
            
        self.keywords[keyword]["agents"][agent_id] = {
            "status": status,
            "metadata": metadata or {},
            "updated_at": datetime.now().isoformat()
        }
        self._save_state()
        
    def get_agent_status(
        self,
        keyword: str,
        agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get agent status for a keyword."""
        keyword = keyword.lower()
        return (
            self.keywords.get(keyword, {})
            .get("agents", {})
            .get(agent_id)
        )
        
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            
        return {
            # Default keywords
            "python": {"metadata": {}, "agents": {}},
            "javascript": {"metadata": {}, "agents": {}},
            "typescript": {"metadata": {}, "agents": {}},
            "rust": {"metadata": {}, "agents": {}},
            "go": {"metadata": {}, "agents": {}}
        }
        
    def _save_state(self) -> None:
        """Save state to file."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.keywords, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")