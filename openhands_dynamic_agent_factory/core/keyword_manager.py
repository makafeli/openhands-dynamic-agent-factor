from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

@dataclass
class AgentInfo:
    """Data structure for agent information."""
    keyword: str
    status: str
    created_at: datetime
    last_accessed: datetime

class KeywordManager:
    """Dynamic keyword and agent management system."""
    
    def __init__(self):
        from openhands_dynamic_agent_factory.core.triggers import TRIGGER_MAP
        self.keywords = {k: v.description for k, v in TRIGGER_MAP.items()}
        self.agents: Dict[str, AgentInfo] = {}
        self.last_updated = datetime.now()
        self.load_state()

    def save_state(self):
        """Save the current state to a file."""
        state = {
            "keywords": self.keywords,
            "agents": {
                k: {
                    "keyword": v.keyword,
                    "status": v.status,
                    "created_at": v.created_at.isoformat(),
                    "last_accessed": v.last_accessed.isoformat()
                }
                for k, v in self.agents.items()
            },
            "last_updated": self.last_updated.isoformat()
        }
        try:
            state_file_path = os.path.join(os.path.dirname(__file__), "keyword_manager_state.json")
            with open(state_file_path, "w") as f:
                json.dump(state, f)
            print(f"State saved successfully to {state_file_path}.")
        except Exception as e:
            print(f"Error saving state: {e}")

    def load_state(self):
        """Load the state from a file."""
        try:
            state_file_path = os.path.join(os.path.dirname(__file__), "keyword_manager_state.json")
            with open(state_file_path, "r") as f:
                state = json.load(f)
                self.keywords = state["keywords"]
                self.agents = {
                    k: AgentInfo(
                        keyword=v["keyword"],
                        status=v["status"],
                        created_at=datetime.fromisoformat(v["created_at"]),
                        last_accessed=datetime.fromisoformat(v["last_accessed"])
                    )
                    for k, v in state["agents"].items()
                }
                self.last_updated = datetime.fromisoformat(state["last_updated"])
            print(f"State loaded successfully from {state_file_path}.")
        except FileNotFoundError:
            print("No state file found. Initializing with base keywords.")
            # Initialize with base set of predefined keywords if no state file exists
            from openhands_dynamic_agent_factory.core.triggers import TRIGGER_MAP
            self.keywords = {k: v.description for k, v in TRIGGER_MAP.items()}
        except Exception as e:
            print(f"Error loading state: {e}")

    def add_keyword(self, keyword: str, description: str) -> str:
        """Add a new keyword to the database."""
        if keyword in self.keywords:
            return f"Keyword '{keyword}' already exists."
        self.keywords[keyword] = description
        self.last_updated = datetime.now()
        self.save_state()
        return f"Keyword '{keyword}' added successfully."

    def list_keywords(self) -> str:
        """Display all stored keywords."""
        return json.dumps(self.keywords, indent=2)

    def update_keywords(self) -> str:
        """Force refresh of GitHub keyword list."""
        # Placeholder for GitHub API integration
        self.last_updated = datetime.now()
        return "Keywords updated successfully."

    def detect_keyword(self, input_text: str) -> Optional[str]:
        """Detect a keyword in the input text."""
        print(f"Detecting keyword in input: {input_text}")  # Debug logging
        input_text_lower = input_text.lower().replace(" ", "").replace("-", "").replace("/", "")
        print(f"Normalized input text: {input_text_lower}")  # Debug logging
        keywords = self.keywords.keys()
        print(f"Available keywords: {keywords}")  # Debug logging
        for keyword in keywords:
            # Normalize keyword for matching
            keyword_normalized = keyword.lower().replace(" ", "").replace("-", "").replace("/", "")
            print(f"Checking keyword: {keyword} (normalized: {keyword_normalized})")  # Debug logging
            if keyword_normalized in input_text_lower:
                print(f"Keyword detected: {keyword}")  # Debug logging
                return keyword
        print("No keyword detected.")  # Debug logging
        return None

    def get_agent(self, keyword: str) -> str:
        """Get or create an agent for the given keyword."""
        if keyword not in self.keywords:
            return f"Error: No keyword '{keyword}' found."
        
        if keyword in self.agents:
            agent = self.agents[keyword]
            agent.last_accessed = datetime.now()
            return f"Agent for '{keyword}' exists. Status: {agent.status}."
        
        # Create and index new agent
        self.agents[keyword] = AgentInfo(
            keyword=keyword,
            status="Active",
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        self.save_state()  # Save the state after creating a new agent
        return f"Agent for '{keyword}' created and indexed."

    def show_agents(self) -> str:
        """Display all indexed and active agents."""
        if not self.agents:
            return "No agents are currently indexed."
        return json.dumps(
            {k: {"status": v.status, "created_at": str(v.created_at), "last_accessed": str(v.last_accessed)} 
             for k, v in self.agents.items()},
            indent=2
        )

    def help(self) -> str:
        """Show available commands and system functionality."""
        return """
Available Commands:
- Show Agents: Display all indexed and active agents
- Help: Show available commands and system functionality
- Add Keyword [term]: Add new keyword to database
- List Keywords: Display all stored keywords
- Update Keywords: Force refresh of GitHub keyword list
"""

# Example usage
if __name__ == "__main__":
    manager = KeywordManager()
    print(manager.help())
    print(manager.list_keywords())
    print(manager.get_agent("python"))
    print(manager.show_agents())