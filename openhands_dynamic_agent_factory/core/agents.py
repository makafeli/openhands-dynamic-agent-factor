"""Agent management module for OpenHands Dynamic Agent Factory."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class Agent:
    """Base class for OpenHands agents."""
    def __init__(self, name: str, agent_type: str, technologies: List[str]):
        self.name = name
        self.type = agent_type
        self.technologies = technologies
        self.status = "inactive"
        self.current_task = None
        self.load = 0.0
        self.last_active = None
    
    def activate(self):
        """Activate the agent."""
        self.status = "active"
        self.last_active = datetime.now(timezone.utc)
    
    def deactivate(self):
        """Deactivate the agent."""
        self.status = "inactive"
        self.current_task = None
        self.load = 0.0
    
    def assign_task(self, task: str, estimated_load: float = 0.5):
        """Assign a task to the agent."""
        self.current_task = task
        self.load = min(1.0, max(0.0, estimated_load))
        self.last_active = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "technologies": self.technologies,
            "status": self.status,
            "current_task": self.current_task,
            "load": self.load,
            "last_active": self.last_active.isoformat() if self.last_active else None
        }

class AgentTemplate:
    """Template for creating new agents."""
    def __init__(self, 
                 name: str,
                 agent_type: str,
                 technologies: List[str],
                 capabilities: List[str],
                 description: str):
        self.name = name
        self.type = agent_type
        self.technologies = technologies
        self.capabilities = capabilities
        self.description = description
    
    def create_agent(self) -> Agent:
        """Create a new agent from this template."""
        return Agent(self.name, self.type, self.technologies)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "technologies": self.technologies,
            "capabilities": self.capabilities,
            "description": self.description
        }

class AgentManager:
    """Manages OpenHands agents."""
    def __init__(self):
        self.active_agents: Dict[str, Agent] = {}
        self.agent_templates: Dict[str, AgentTemplate] = {}
    
    def register_template(self, template: AgentTemplate):
        """Register an agent template."""
        self.agent_templates[template.name] = template
        logger.info(f"Registered agent template: {template.name}")
    
    def create_agent(self, template_name: str) -> Optional[Agent]:
        """Create an agent from a template."""
        template = self.agent_templates.get(template_name)
        if template:
            agent = template.create_agent()
            self.active_agents[agent.name] = agent
            logger.info(f"Created agent: {agent.name}")
            return agent
        return None
    
    def get_active_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all active agents."""
        return {name: agent.to_dict() for name, agent in self.active_agents.items()}
    
    def get_agent_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent templates."""
        return {name: template.to_dict() for name, template in self.agent_templates.items()}
