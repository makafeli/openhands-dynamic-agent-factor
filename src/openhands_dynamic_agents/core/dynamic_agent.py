"""
Core implementation of the dynamic agent system that integrates with OpenHands.
"""

from typing import Dict, Any, Optional, Type
from pathlib import Path
import logging
from datetime import datetime

from openhands.microagent.microagent import BaseMicroAgent
from openhands.microagent.types import MicroAgentMetadata, MicroAgentType

from ..utils.exceptions import DynamicAgentError
from ..utils.result import OperationResult
from ..utils.monitoring import monitor_performance
from ..utils.validation import validate_input
from .llm_factory import LLMAgentFactory
from .keyword_manager import KeywordManager

logger = logging.getLogger(__name__)

class DynamicAgent(BaseMicroAgent):
    """
    A dynamic agent that can be generated at runtime based on technology keywords.
    Integrates with OpenHands' microagent system while providing dynamic capabilities.
    """

    def __init__(
        self,
        name: str,
        keyword: str,
        options: Optional[Dict[str, Any]] = None,
        workspace: Optional[Path] = None
    ):
        """Initialize the dynamic agent."""
        metadata = MicroAgentMetadata(
            name=name,
            type=MicroAgentType.TASK,
            description=f"Dynamically generated agent for {keyword}",
            triggers=[keyword.lower()],
            version="1.0.0"
        )

        super().__init__(
            name=name,
            content="",  # Content will be generated dynamically
            metadata=metadata,
            source="dynamic",
            type=MicroAgentType.TASK
        )

        self.keyword = keyword.lower()
        self.options = options or {}
        self.workspace = workspace or Path("/tmp/dynamic_agents")
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.llm_factory = LLMAgentFactory()
        self.keyword_manager = KeywordManager()

    @monitor_performance
    def generate(self) -> OperationResult[Type[BaseMicroAgent]]:
        """
        Generate the agent implementation using LLM.
        
        Returns:
            OperationResult containing the generated agent class or error details
        """
        try:
            # Validate keyword
            if not self.keyword_manager.is_valid_keyword(self.keyword):
                return OperationResult.error(
                    f"Invalid technology keyword: {self.keyword}",
                    error_type="ValidationError"
                )

            # Generate agent implementation
            result = self.llm_factory.create_agent(
                self.keyword,
                self.options,
                self.workspace
            )

            if not result.success:
                return result

            # Update metadata with generation info
            self.metadata.description = result.data.get("description", self.metadata.description)
            self.metadata.version = result.data.get("version", self.metadata.version)
            
            return OperationResult.success(
                result.data["agent_class"],
                metadata={
                    "generation_time": datetime.now().isoformat(),
                    "keyword": self.keyword,
                    "options": self.options
                }
            )

        except Exception as e:
            logger.error(f"Agent generation failed: {e}")
            return OperationResult.error(
                str(e),
                error_type="GenerationError",
                details={"keyword": self.keyword, "options": self.options}
            )

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the dynamic agent with the given input data.
        
        This method validates input, generates the agent if needed,
        and executes the generated agent's functionality.
        """
        # Validate input
        validation_result = validate_input(data)
        if not validation_result.success:
            return {
                "status": "error",
                "error": str(validation_result.error),
                "details": validation_result.error.to_dict()
            }

        # Generate agent if needed
        generation_result = self.generate()
        if not generation_result.success:
            return {
                "status": "error",
                "error": str(generation_result.error),
                "details": generation_result.error.to_dict()
            }

        # Execute generated agent
        try:
            agent_class = generation_result.data
            agent_instance = agent_class()
            result = agent_instance.run(data)
            
            return {
                "status": "success",
                "result": result,
                "metadata": generation_result.metadata
            }
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "status": "error",
                "error": f"Execution failed: {str(e)}",
                "details": {
                    "keyword": self.keyword,
                    "options": self.options,
                    "input_data": data
                }
            }