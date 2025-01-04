"""
Enhanced implementation of the dynamic agent factory with improved integration,
error handling, and documentation.
"""

import os
import uuid
import importlib.util
import logging
from typing import Dict, Optional, Type, Any
from pathlib import Path
from datetime import datetime

try:
    from openhands import MicroAgent
except ImportError:
    # Enhanced stub class for testing
    class MicroAgent:
        """Stub MicroAgent class for testing."""
        def __init__(self, name: str = "", description: str = "", inputs=None, outputs=None):
            self.name = name
            self.description = description
            self.inputs = inputs or []
            self.outputs = outputs or []
        def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("Stub class. Install openhands to use MicroAgent.")

from .factory import DynamicAgentFactoryLLM, AgentGenerationError
from .keyword_manager import KeywordManager
from .triggers import TRIGGER_MAP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DynamicAgentFactory(MicroAgent):
    """
    Enhanced meta-agent that creates specialized agents based on technology keywords.
    
    Features:
    - Improved integration with KeywordManager and DynamicAgentFactoryLLM
    - Enhanced error handling and validation
    - Better state management and persistence
    - Comprehensive logging
    - Performance optimizations
    """

    def __init__(self):
        """Initialize with enhanced configuration and validation."""
        super().__init__(
            name="dynamic_agent_factory",
            description=(
                "Creates specialized micro-agents based on technology keywords "
                "with enhanced validation and error handling."
            ),
            inputs=["technology_keyword", "options"],
            outputs=["agent_class", "generation_info"]
        )
        
        # Initialize components
        self.keyword_manager = KeywordManager()
        self.llm_factory = DynamicAgentFactoryLLM()
        self.temp_dir = Path("/tmp/dynamic_agent_factory")
        self.temp_dir.mkdir(exist_ok=True)

    def _validate_input(self, data: Dict[str, Any]) -> None:
        """
        Validate input data with enhanced checks.
        
        Args:
            data: Input data dictionary
            
        Raises:
            ValueError: If validation fails
        """
        if "technology_keyword" not in data:
            raise ValueError("Missing required input: technology_keyword")
            
        if not isinstance(data["technology_keyword"], str):
            raise ValueError("technology_keyword must be a string")
            
        if not data["technology_keyword"].strip():
            raise ValueError("technology_keyword cannot be empty")

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files with error handling."""
        try:
            for file in self.temp_dir.glob("*.py"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {file}: {e}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent factory with enhanced error handling and validation.
        
        Args:
            data: Dictionary containing:
                - technology_keyword: The technology to generate an agent for
                - options: Optional configuration for agent generation
                
        Returns:
            Dictionary containing:
                - agent_class: The generated agent class or None
                - generation_info: Detailed information about the generation process
        """
        start_time = datetime.now()
        generation_info = {
            "status": "pending",
            "start_time": start_time.isoformat()
        }
        
        try:
            # Validate input
            self._validate_input(data)
            tech = data["technology_keyword"].lower()
            options = data.get("options", {})
            
            # Update generation info
            generation_info.update({
                "technology": tech,
                "options": options
            })
            
            # Detect and validate keyword
            detected_keyword = self.keyword_manager.detect_keyword(tech)
            if not detected_keyword:
                logger.warning(f"Unknown technology keyword: {tech}")
                return {
                    "agent_class": None,
                    "generation_info": {
                        **generation_info,
                        "status": "error",
                        "error": f"Unknown technology: {tech}",
                        "end_time": datetime.now().isoformat()
                    }
                }
            
            # Get or create agent info
            agent_status = self.keyword_manager.get_agent(detected_keyword, {
                "options": options,
                "generation_time": start_time.isoformat()
            })
            
            logger.info(f"Agent status: {agent_status}")
            generation_info["agent_status"] = agent_status
            
            # Generate agent using LLM factory
            try:
                result = self.llm_factory.run({
                    "technology_keyword": detected_keyword,
                    "options": options
                })
                
                # Update agent status based on result
                status = "active" if result["agent_class"] else "error"
                error = result.get("generation_info", {}).get("error")
                self.keyword_manager.update_agent_status(
                    detected_keyword,
                    status,
                    error
                )
                
                # Add timing information
                end_time = datetime.now()
                generation_info.update({
                    "status": status,
                    "end_time": end_time.isoformat(),
                    "duration_seconds": (end_time - start_time).total_seconds()
                })
                
                if result["agent_class"]:
                    generation_info["validation_results"] = result["generation_info"]["validation_results"]
                
                return {
                    "agent_class": result["agent_class"],
                    "generation_info": generation_info
                }
                
            except AgentGenerationError as e:
                logger.error(f"Agent generation failed: {e}")
                self.keyword_manager.update_agent_status(
                    detected_keyword,
                    "error",
                    str(e)
                )
                
                return {
                    "agent_class": None,
                    "generation_info": {
                        **generation_info,
                        "status": "error",
                        "error": str(e),
                        "error_type": e.error_type,
                        "error_details": e.details,
                        "end_time": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "agent_class": None,
                "generation_info": {
                    **generation_info,
                    "status": "error",
                    "error": f"Unexpected error: {str(e)}",
                    "end_time": datetime.now().isoformat()
                }
            }
            
        finally:
            self._cleanup_temp_files()


def main():
    """
    Demo usage with enhanced error handling and validation.
    """
    try:
        factory = DynamicAgentFactory()
        
        # Example: Generate a Python analyzer agent
        output = factory.run({
            "technology_keyword": "python",
            "options": {
                "analysis_type": "security",
                "max_code_length": 5000
            }
        })
        
        if output["agent_class"] is None:
            print("Agent generation failed:")
            print(f"Error: {output['generation_info'].get('error')}")
            return
        
        # Create and test the generated agent
        generated_agent = output["agent_class"]()
        
        # Run with sample code
        analysis_result = generated_agent.run({
            "code_snippet": "def hello_world(): print('Hello World!')",
            "analysis_type": "security"
        })
        
        print("\nGeneration Info:")
        print(json.dumps(output["generation_info"], indent=2))
        
        print("\nAnalysis Result:")
        print(json.dumps(analysis_result, indent=2))
        
    except Exception as e:
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    import json
    main()
