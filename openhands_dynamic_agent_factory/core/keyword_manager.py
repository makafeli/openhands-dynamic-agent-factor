"""
Enhanced keyword and agent management system with improved state handling,
validation, and integration with the dynamic agent factory.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, cast
from datetime import datetime
import json
import os
import logging
from pathlib import Path
import re
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentInfo:
    """Enhanced data structure for agent information with validation."""
    keyword: str
    status: str
    created_at: datetime
    last_accessed: datetime
    metadata: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, bool]] = None
    error_history: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert AgentInfo to a JSON-serializable dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentInfo':
        """Create AgentInfo from a dictionary."""
        return cls(
            keyword=data['keyword'],
            status=data['status'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            metadata=data.get('metadata'),
            validation_results=data.get('validation_results'),
            error_history=data.get('error_history', [])
        )

class StateManager:
    """Handles persistent state management with atomic operations."""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.lock = Lock()
        self._ensure_state_file()

    def _ensure_state_file(self) -> None:
        """Ensure state file exists with valid JSON."""
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.save_state({
                "keywords": {},
                "agents": {},
                "last_updated": datetime.now().isoformat()
            })

    def load_state(self) -> Dict[str, Dict[str, Any]]:
        """Load state with error handling and validation."""
        with self.lock:
            try:
                content = self.state_file.read_text(encoding='utf-8')
                state = json.loads(content)
                
                # Validate state structure
                required_keys = {"keywords", "agents", "last_updated"}
                if not all(key in state for key in required_keys):
                    raise ValueError("Invalid state file structure")
                
                return cast(Dict[str, Dict[str, Any]], state)
            except Exception as e:
                logger.error(f"Error loading state: {e}")
                return {
                    "keywords": {},
                    "agents": {},
                    "last_updated": datetime.now().isoformat()
                }

    def save_state(self, state: Dict[str, Any]) -> None:
        """Save state atomically with backup."""
        with self.lock:
            backup_file = self.state_file.with_suffix('.backup')
            try:
                # Create backup of existing state
                if self.state_file.exists():
                    self.state_file.rename(backup_file)
                
                # Write new state
                with self.state_file.open('w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
                
                # Remove backup after successful write
                if backup_file.exists():
                    backup_file.unlink()
                    
            except Exception as e:
                logger.error(f"Error saving state: {e}")
                # Restore from backup if available
                if backup_file.exists():
                    backup_file.rename(self.state_file)
                raise

class KeywordManager:
    """
    Enhanced dynamic keyword and agent management system with improved
    validation, error handling, and state management.
    """
    
    def __init__(self):
        """Initialize with enhanced state management and validation."""
        from openhands_dynamic_agent_factory.core.triggers import TRIGGER_MAP
        
        self.state_file = Path(os.path.dirname(__file__)) / "keyword_manager_state.json"
        self.state_manager = StateManager(self.state_file)
        
        # Load initial state
        state = self.state_manager.load_state()
        self.keywords = state["keywords"]
        self.agents = {
            k: AgentInfo.from_dict(v) for k, v in state["agents"].items()
        }
        self.last_updated = datetime.fromisoformat(state["last_updated"])
        
        # Initialize with trigger map
        self._sync_with_trigger_map(TRIGGER_MAP)

    def _sync_with_trigger_map(self, trigger_map: Dict[str, Any]) -> None:
        """Synchronize keywords with trigger map."""
        for k, v in trigger_map.items():
            if k not in self.keywords:
                self.keywords[k] = v.description
        self._save_current_state()

    def _save_current_state(self) -> None:
        """Save current state with validation."""
        state = {
            "keywords": self.keywords,
            "agents": {k: v.to_dict() for k, v in self.agents.items()},
            "last_updated": self.last_updated.isoformat()
        }
        self.state_manager.save_state(state)

    def add_keyword(self, keyword: str, description: str) -> str:
        """
        Add a new keyword with validation.
        
        Args:
            keyword: The keyword to add
            description: Description of the keyword
            
        Returns:
            str: Status message
        """
        # Validate keyword format
        if not re.match(r'^[a-zA-Z0-9_-]+$', keyword):
            return f"Invalid keyword format: {keyword}"
        
        if keyword in self.keywords:
            return f"Keyword '{keyword}' already exists."
            
        self.keywords[keyword] = description
        self.last_updated = datetime.now()
        self._save_current_state()
        
        logger.info(f"Added new keyword: {keyword}")
        return f"Keyword '{keyword}' added successfully."

    def remove_keyword(self, keyword: str) -> str:
        """
        Remove a keyword and its associated agent.
        
        Args:
            keyword: The keyword to remove
            
        Returns:
            str: Status message
        """
        if keyword not in self.keywords:
            return f"Keyword '{keyword}' not found."
            
        del self.keywords[keyword]
        if keyword in self.agents:
            del self.agents[keyword]
            
        self.last_updated = datetime.now()
        self._save_current_state()
        
        logger.info(f"Removed keyword: {keyword}")
        return f"Keyword '{keyword}' removed successfully."

    def list_keywords(self, pattern: Optional[str] = None) -> Dict[str, str]:
        """
        List keywords with optional pattern matching.
        
        Args:
            pattern: Optional regex pattern to filter keywords
            
        Returns:
            Dict[str, str]: Filtered keywords and their descriptions
        """
        if pattern:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
                return cast(Dict[str, str], {
                    k: v for k, v in self.keywords.items()
                    if regex.search(k) or regex.search(v)
                })
            except re.error as e:
                logger.error(f"Invalid regex pattern: {e}")
                return cast(Dict[str, str], self.keywords)
        return cast(Dict[str, str], self.keywords)

    def detect_keyword(self, input_text: str) -> Optional[str]:
        """
        Enhanced keyword detection with fuzzy matching.
        
        Args:
            input_text: Text to analyze for keywords
            
        Returns:
            Optional[str]: Detected keyword or None
        """
        logger.debug(f"Detecting keyword in: {input_text}")
        
        # Normalize input
        input_text = input_text.lower()
        input_words = set(re.findall(r'\w+', input_text))
        
        # Score each keyword
        matches = []
        for keyword in self.keywords:
            keyword_normalized = keyword.lower()
            keyword_words = set(re.findall(r'\w+', keyword_normalized))
            
            # Calculate word overlap
            overlap = len(input_words & keyword_words)
            if overlap > 0:
                matches.append((keyword, overlap))
        
        # Return the best match if any
        if matches:
            best_match = max(matches, key=lambda x: x[1])[0]
            logger.info(f"Detected keyword: {best_match}")
            return cast(Optional[str], best_match)
            
        logger.debug("No keyword detected")
        return None

    def get_agent(self, keyword: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Get or create an agent with enhanced metadata and validation.
        
        Args:
            keyword: The keyword to get/create an agent for
            metadata: Optional metadata for the agent
            
        Returns:
            str: Status message
        """
        if keyword not in self.keywords:
            return f"Error: No keyword '{keyword}' found."
        
        now = datetime.now()
        
        if keyword in self.agents:
            agent = self.agents[keyword]
            agent.last_accessed = now
            if metadata:
                agent.metadata = {**(agent.metadata or {}), **metadata}
            status = "retrieved"
        else:
            self.agents[keyword] = AgentInfo(
                keyword=keyword,
                status="Active",
                created_at=now,
                last_accessed=now,
                metadata=metadata,
                validation_results={},
                error_history=[]
            )
            status = "created"
            
        self._save_current_state()
        
        logger.info(f"Agent {status} for keyword: {keyword}")
        return f"Agent for '{keyword}' {status} and indexed."

    def update_agent_status(
        self,
        keyword: str,
        status: str,
        error: Optional[str] = None
    ) -> None:
        """
        Update agent status with error tracking.
        
        Args:
            keyword: The keyword of the agent
            status: New status
            error: Optional error message
        """
        if keyword in self.agents:
            agent = self.agents[keyword]
            agent.status = status
            agent.last_accessed = datetime.now()
            
            if error:
                if not agent.error_history:
                    agent.error_history = []
                agent.error_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "error": error
                })
            
            self._save_current_state()
            logger.info(f"Updated status for agent {keyword}: {status}")

    def show_agents(self, include_history: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Display indexed agents with optional history.
        
        Args:
            include_history: Whether to include error history
            
        Returns:
            Dict[str, Dict[str, Any]]: Agent information
        """
        return {
            k: {
                "status": v.status,
                "created_at": v.created_at.isoformat(),
                "last_accessed": v.last_accessed.isoformat(),
                "metadata": v.metadata,
                "validation_results": v.validation_results,
                **({"error_history": v.error_history} if include_history and v.error_history else {})
            }
            for k, v in self.agents.items()
        }

    def help(self) -> str:
        """Show available commands and system functionality."""
        return """
Available Commands:
- add_keyword [term] [description]: Add new keyword
- remove_keyword [term]: Remove existing keyword
- list_keywords [pattern]: List keywords (optional regex pattern)
- show_agents [--history]: Display agents (optional error history)
- detect_keyword [text]: Detect keywords in text
- get_agent [keyword]: Get or create agent
- update_agent_status [keyword] [status]: Update agent status
"""

# Example usage
if __name__ == "__main__":
    manager = KeywordManager()
    print(manager.help())
    print(manager.list_keywords())
    print(manager.get_agent("python"))
    print(manager.show_agents())
