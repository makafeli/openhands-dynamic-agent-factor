"""
Enhanced implementation of the dynamic agent factory with improved integration,
error handling, caching, and monitoring.
"""

import os
import uuid
import importlib.util
import logging
import time
from typing import Dict, Optional, Type, Any, List
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
from .utils import (
    BaseError, ValidationError, StateError,
    OperationResult, Cache, StateManager,
    retry, monitor_performance
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentFactoryError(BaseError):
    """Custom error for agent factory operations."""
    def __init__(
        self,
        message: str,
        error_type: str,
        details: Optional[Dict[str, Any]] = None,
        recovery_hint: Optional[str] = None
    ):
        super().__init__(
            message,
            error_type,
            details,
            recovery_hint or "Check factory configuration and dependencies"
        )

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

    def __init__(self, state_dir: Optional[Path] = None):
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
        
        # Initialize components with state management
        state_dir = state_dir or Path("/tmp/dynamic_agent_factory")
        self.state_manager = StateManager[Dict[str, Any]](state_dir / "factory_state.json")
        self.keyword_manager = KeywordManager()
        self.llm_factory = DynamicAgentFactoryLLM()
        
        # Initialize caches
        self.agent_cache = Cache[str, Type[MicroAgent]](ttl=3600)  # 1 hour TTL
        self.result_cache = Cache[str, Dict[str, Any]](ttl=1800)  # 30 minutes TTL
        
        # Ensure directories
        self.temp_dir = state_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    @monitor_performance("Input validation")
    def _validate_input(self, data: Dict[str, Any]) -> OperationResult[bool]:
        """
        Validate input data with enhanced checks.
        
        Args:
            data: Input data dictionary
            
        Raises:
            ValueError: If validation fails
        """
        start_time = time.time()
        try:
            if "technology_keyword" not in data:
                return OperationResult(
                    success=False,
                    error=ValidationError(
                        "Missing required input: technology_keyword",
                        {"input_data": data}
                    )
                )
                
            if not isinstance(data["technology_keyword"], str):
                return OperationResult(
                    success=False,
                    error=ValidationError(
                        "technology_keyword must be a string",
                        {"type": type(data["technology_keyword"]).__name__}
                    )
                )
                
            if not data["technology_keyword"].strip():
                return OperationResult(
                    success=False,
                    error=ValidationError(
                        "technology_keyword cannot be empty"
                    )
                )
                
            return OperationResult(
                success=True,
                data=True,
                duration=time.time() - start_time
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                error=ValidationError(
                    f"Validation failed: {str(e)}",
                    {"exception": str(e)}
                )
            )

    @monitor_performance("Temp file cleanup")
    def _cleanup_temp_files(self) -> OperationResult[bool]:
        """Clean up temporary files with error handling."""
        start_time = time.time()
        failed_files = []
        
        try:
            for file in self.temp_dir.glob("*.py"):
                try:
                    file.unlink()
                except Exception as e:
                    failed_files.append((str(file), str(e)))
                    logger.warning(f"Failed to delete temporary file {file}: {e}")
            
            success = len(failed_files) == 0
            return OperationResult(
                success=success,
                data=success,
                duration=time.time() - start_time,
                metadata={
                    "failed_files": failed_files
                } if failed_files else None
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                error=AgentFactoryError(
                    f"Cleanup failed: {str(e)}",
                    "CleanupError",
                    {"failed_files": failed_files}
                )
            )

    @monitor_performance("Agent factory run")
    @retry(max_attempts=3, delay=1.0, backoff=2.0)
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
        try:
            # Validate input
            validation_result = self._validate_input(data)
            if not validation_result.success:
                return {
                    "agent_class": None,
                    "generation_info": {
                        "status": "error",
                        "error": str(validation_result.error),
                        "validation_error": validation_result.error.to_dict(),
                        "start_time": datetime.now().isoformat()
                    }
                }
                
            tech = data["technology_keyword"].lower()
            options = data.get("options", {})
            
            # Check result cache
            cache_key = f"{tech}:{hash(str(options))}"
            cached_result = self.result_cache.get(cache_key)
            if cached_result:
                logger.info(f"Using cached result for {tech}")
                return cached_result
            
            # Initialize generation info
            generation_info = {
                "status": "pending",
                "start_time": datetime.now().isoformat(),
                "technology": tech,
                "options": options
            }
            
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
