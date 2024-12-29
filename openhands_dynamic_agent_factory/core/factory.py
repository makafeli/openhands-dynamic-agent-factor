"""
Core implementation of the dynamic agent factory.
"""

import os
import uuid
import inspect
import importlib.util
from typing import Dict, Optional, Type, Any, Tuple

try:
    from openhands import MicroAgent
    from openhands.llms import get_llm
    from openhands.config import (
        LLM_PROVIDER,
        LLM_MODEL_NAME,
        LLM_API_KEY,
        LLM_CONFIG
    )
except ImportError:
    # Stub classes for testing without OpenHands
    class MicroAgent:
        def __init__(self, name="", description="", inputs=None, outputs=None):
            self.name = name
            self.description = description
            self.inputs = inputs or []
            self.outputs = outputs or []
        def run(self, data):
            raise NotImplementedError("Stub MicroAgent. Install openhands for actual usage.")

    def get_llm(provider, model, api_key):
        class StubLLM:
            def chat(self, messages):
                return type("StubResponse", (), {
                    "content": f"# Example code from Stub LLM\nprint('Hello from {model}')"
                })()
        return StubLLM()

    LLM_PROVIDER = "openai"
    LLM_MODEL_NAME = "gpt-4"
    LLM_API_KEY = "fake-key"
    LLM_CONFIG = {}

from .triggers import TRIGGER_MAP, TriggerInfo


class AgentGenerationError(Exception):
    """Custom exception for agent generation errors."""
    pass


class DynamicAgentFactoryLLM(MicroAgent):
    """
    Advanced meta-agent that generates technology-specific code analysis agents using LLM.
    
    Features:
    - OpenHands LLM configuration integration
    - Comprehensive error handling
    - Code validation
    - Dynamic imports with security checks
    """

    def __init__(self):
        super().__init__(
            name="dynamic_agent_factory_llm",
            description="Creates specialized micro-agents via LLM for various technologies",
            inputs=["technology_keyword", "options"],
            outputs=["agent_class", "generation_info"]
        )
        
        # Initialize LLM with OpenHands configuration
        try:
            self.llm = get_llm(
                provider=LLM_PROVIDER,
                model=LLM_MODEL_NAME,
                api_key=LLM_API_KEY,
                **LLM_CONFIG
            )
        except Exception as e:
            raise AgentGenerationError(f"Failed to initialize LLM: {str(e)}")

    def validate_generated_code(self, code_str: str, trigger_info: TriggerInfo) -> None:
        """
        Validate the LLM-generated code for security and correctness.
        
        Args:
            code_str: The generated Python code
            trigger_info: The trigger information containing validation rules
        
        Raises:
            AgentGenerationError: If validation fails
        """
        # Basic security checks
        forbidden_terms = [
            "os.system", "subprocess", "eval(", "exec(", 
            "__import__", "open(", "socket."
        ]
        for term in forbidden_terms:
            if term in code_str:
                raise AgentGenerationError(f"Generated code contains forbidden term: {term}")

        # Check for required class structure
        if not all(term in code_str for term in ["class", "MicroAgent", "def run"]):
            raise AgentGenerationError("Generated code missing required class structure")

        # Verify imports
        if trigger_info.required_imports:
            for imp in trigger_info.required_imports:
                if imp not in code_str:
                    raise AgentGenerationError(f"Generated code missing required import: {imp}")

    def validate_agent_class(self, agent_cls: Type[MicroAgent], trigger_info: TriggerInfo) -> None:
        """
        Validate the generated agent class meets requirements.
        
        Args:
            agent_cls: The generated agent class
            trigger_info: The trigger information containing validation rules
        
        Raises:
            AgentGenerationError: If validation fails
        """
        # Check inheritance
        if not issubclass(agent_cls, MicroAgent):
            raise AgentGenerationError("Generated class does not inherit from MicroAgent")

        # Verify method signatures
        run_method = getattr(agent_cls, "run", None)
        if not run_method or not inspect.isfunction(run_method):
            raise AgentGenerationError("Generated class missing run method")

        # Check inputs/outputs match
        instance = agent_cls()
        if trigger_info.inputs and not all(inp in instance.inputs for inp in trigger_info.inputs):
            raise AgentGenerationError("Generated agent missing required inputs")
        if trigger_info.outputs and not all(out in instance.outputs for out in trigger_info.outputs):
            raise AgentGenerationError("Generated agent missing required outputs")

    def generate_agent(self, tech: str, options: Dict[str, Any] = None) -> Tuple[Optional[Type[MicroAgent]], Dict[str, Any]]:
        """
        Generate a new agent class for the given technology.
        
        Args:
            tech: Technology keyword
            options: Optional configuration for agent generation
        
        Returns:
            Tuple of (agent_class, generation_info)
        """
        if tech not in TRIGGER_MAP:
            return None, {"error": f"Unknown technology: {tech}"}

        trigger_info = TRIGGER_MAP[tech]
        generation_info = {
            "status": "pending",
            "class_name": trigger_info.class_name,
            "description": trigger_info.description
        }

        try:
            # Generate code using LLM
            messages = [
                {"role": "system", "content": "You are an expert code generator for OpenHands."},
                {"role": "user", "content": trigger_info.llm_prompt_template.format(
                    class_name=trigger_info.class_name
                )}
            ]
            
            response = self.llm.chat(messages=messages)
            code_str = response.content

            # Validate generated code
            self.validate_generated_code(code_str, trigger_info)

            # Create temporary file with unique name
            temp_filename = f"{trigger_info.class_name.lower()}_{uuid.uuid4().hex}.py"
            with open(temp_filename, "w", encoding="utf-8") as f:
                f.write(code_str)

            try:
                # Import the generated module
                spec = importlib.util.spec_from_file_location(trigger_info.class_name, temp_filename)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Get and validate the agent class
                agent_cls = getattr(module, trigger_info.class_name)
                self.validate_agent_class(agent_cls, trigger_info)

                generation_info.update({
                    "status": "success",
                    "validation": "passed"
                })
                
                return agent_cls, generation_info

            finally:
                # Cleanup: Always remove the temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        except Exception as e:
            generation_info.update({
                "status": "error",
                "error": str(e)
            })
            raise AgentGenerationError(f"Agent generation failed: {str(e)}")

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent factory to generate a new agent class.
        
        Args:
            data: Dictionary containing:
                - technology_keyword: The technology to generate an agent for
                - options: Optional configuration for agent generation
        
        Returns:
            Dictionary containing:
                - agent_class: The generated agent class or None
                - generation_info: Information about the generation process
        """
        tech = data["technology_keyword"].lower()
        options = data.get("options", {})

        try:
            agent_cls, generation_info = self.generate_agent(tech, options)
            return {
                "agent_class": agent_cls,
                "generation_info": generation_info
            }
        except AgentGenerationError as e:
            return {
                "agent_class": None,
                "generation_info": {
                    "status": "error",
                    "error": str(e)
                }
            }