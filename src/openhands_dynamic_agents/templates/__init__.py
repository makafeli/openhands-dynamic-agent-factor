"""
Templates for generating dynamic agents.
"""

from typing import Dict, Any, Optional

class AgentTemplates:
    """Manager for agent templates."""
    
    def __init__(self):
        """Initialize with default templates."""
        self.templates = {
            "python": self._python_agent_template,
            "javascript": self._javascript_agent_template,
            # Add more templates as needed
        }
    
    def get_template(
        self,
        keyword: str,
        options: Dict[str, Any]
    ) -> Optional[str]:
        """Get template for the given keyword."""
        return self.templates.get(keyword.lower())
    
    @property
    def _python_agent_template(self) -> str:
        """Template for Python analysis agent."""
        return '''
from typing import Dict, Any
from openhands.microagent.microagent import BaseMicroAgent
from openhands.microagent.types import MicroAgentMetadata, MicroAgentType

class {keyword}AnalysisAgent(BaseMicroAgent):
    """Dynamic agent for analyzing {keyword} code."""
    
    def __init__(self):
        metadata = MicroAgentMetadata(
            name="{keyword}_analysis",
            type=MicroAgentType.TASK,
            description="Analyzes {keyword} code for {analysis_type}",
            version="1.0.0"
        )
        
        super().__init__(
            name="{keyword}_analysis",
            content="",
            metadata=metadata,
            source="dynamic",
            type=MicroAgentType.TASK
        )
    
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the analysis."""
        code = data.get("code_snippet", "")
        analysis_type = data.get("analysis_type", "general")
        
        # Add analysis logic here
        result = {
            "code_length": len(code),
            "analysis_type": analysis_type,
            "findings": []
        }
        
        return result
'''
    
    @property
    def _javascript_agent_template(self) -> str:
        """Template for JavaScript analysis agent."""
        return '''
from typing import Dict, Any
from openhands.microagent.microagent import BaseMicroAgent
from openhands.microagent.types import MicroAgentMetadata, MicroAgentType

class {keyword}AnalysisAgent(BaseMicroAgent):
    """Dynamic agent for analyzing {keyword} code."""
    
    def __init__(self):
        metadata = MicroAgentMetadata(
            name="{keyword}_analysis",
            type=MicroAgentType.TASK,
            description="Analyzes {keyword} code",
            version="1.0.0"
        )
        
        super().__init__(
            name="{keyword}_analysis",
            content="",
            metadata=metadata,
            source="dynamic",
            type=MicroAgentType.TASK
        )
    
    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the analysis."""
        code = data.get("code_snippet", "")
        
        # Add JavaScript-specific analysis
        result = {
            "code_length": len(code),
            "findings": []
        }
        
        return result
'''

AGENT_TEMPLATES = AgentTemplates()