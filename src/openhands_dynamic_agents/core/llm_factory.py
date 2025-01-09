"""
LLM-based agent factory that generates agent implementations.
"""

from typing import Dict, Any, Optional, Type
from pathlib import Path
import logging
from datetime import datetime

from openhands.microagent.microagent import BaseMicroAgent

from ..utils.result import OperationResult
from ..utils.monitoring import monitor_performance
from ..templates import AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class LLMAgentFactory:
    """
    Factory class that uses LLM to generate agent implementations.
    """

    def __init__(self, model: str = "gpt-4"):
        """Initialize the LLM factory."""
        self.model = model
        self.templates = AGENT_TEMPLATES

    @monitor_performance
    def create_agent(
        self,
        keyword: str,
        options: Dict[str, Any],
        workspace: Path
    ) -> OperationResult[Dict[str, Any]]:
        """
        Generate an agent implementation using LLM.
        
        Args:
            keyword: Technology keyword to generate agent for
            options: Additional options for generation
            workspace: Directory to store generated files
            
        Returns:
            OperationResult containing:
                - agent_class: The generated agent class
                - description: Generated agent description
                - version: Agent version
        """
        try:
            # Get appropriate template
            template = self.templates.get_template(keyword, options)
            if not template:
                return OperationResult.error(
                    f"No template found for keyword: {keyword}",
                    error_type="TemplateError"
                )

            # Generate implementation using LLM
            implementation = self._generate_implementation(
                keyword,
                template,
                options
            )

            if not implementation.success:
                return implementation

            # Create agent module
            module_path = workspace / f"{keyword}_agent.py"
            with open(module_path, "w") as f:
                f.write(implementation.data["code"])

            # Import and validate generated agent
            try:
                agent_class = self._import_agent(module_path)
            except Exception as e:
                return OperationResult.error(
                    f"Invalid generated agent: {e}",
                    error_type="ValidationError",
                    details={"code": implementation.data["code"]}
                )

            return OperationResult.success({
                "agent_class": agent_class,
                "description": implementation.data["description"],
                "version": "1.0.0"
            })

        except Exception as e:
            logger.error(f"Agent creation failed: {e}")
            return OperationResult.error(
                str(e),
                error_type="CreationError",
                details={"keyword": keyword, "options": options}
            )

    def _generate_implementation(
        self,
        keyword: str,
        template: str,
        options: Dict[str, Any]
    ) -> OperationResult[Dict[str, str]]:
        """
        Generate agent implementation using LLM.
        
        Returns:
            OperationResult containing:
                - code: Generated Python code
                - description: Generated agent description
        """
        # TODO: Implement actual LLM call
        # For now, return template-based implementation
        code = template.format(
            keyword=keyword,
            **options
        )
        
        return OperationResult.success({
            "code": code,
            "description": f"Dynamic agent for {keyword}"
        })

    def _import_agent(self, module_path: Path) -> Type[BaseMicroAgent]:
        """
        Import and validate the generated agent module.
        
        Returns:
            The agent class from the module
        """
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            f"dynamic_agent_{module_path.stem}",
            module_path
        )
        if not spec or not spec.loader:
            raise ImportError(f"Could not load module: {module_path}")
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find agent class in module
        for item in dir(module):
            if (
                item.endswith("Agent")
                and item != "BaseMicroAgent"
                and isinstance(getattr(module, item), type)
                and issubclass(getattr(module, item), BaseMicroAgent)
            ):
                return getattr(module, item)
                
        raise ValueError(f"No valid agent class found in {module_path}")