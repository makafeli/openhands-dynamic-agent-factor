"""
Core implementation of the dynamic agent factory with improved error handling,
security, and performance optimizations.
"""

import os
import uuid
import inspect
import importlib.util
from typing import Dict, Optional, Type, Any, Tuple, List
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path

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
    # Enhanced stub classes for testing without OpenHands
    class MicroAgent:
        """Stub MicroAgent class for testing."""
        def __init__(self, name="", description="", inputs=None, outputs=None):
            self.name = name
            self.description = description
            self.inputs = inputs or []
            self.outputs = outputs or []
        def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("Stub MicroAgent. Install openhands for actual usage.")

    def get_llm(provider: str, model: str, api_key: str) -> Any:
        """Stub LLM provider for testing."""
        class StubLLM:
            def chat(self, messages: List[Dict[str, str]]) -> Any:
                return type("StubResponse", (), {
                    "content": f"# Example code from Stub LLM\nprint('Hello from {model}')"
                })()
        return StubLLM()

    LLM_PROVIDER = "openai"
    LLM_MODEL_NAME = "gpt-4"
    LLM_API_KEY = "fake-key"
    LLM_CONFIG = {}

from .triggers import TRIGGER_MAP, TriggerInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from .utils import (
    BaseError, ValidationError, StateError,
    OperationResult, Cache, StateManager,
    retry, CodeValidator, StructureValidator,
    monitor_performance
)

class AgentGenerationError(BaseError):
    """Custom exception for agent generation errors with enhanced context."""
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
            recovery_hint or "Check LLM configuration and prompt templates"
        )


@dataclass
class GenerationResult:
    """Structured result of agent generation process."""
    agent_class: Optional[Type[MicroAgent]]
    status: str
    error: Optional[str] = None
    validation_results: Optional[Dict[str, bool]] = None
    generation_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentValidator:
    """Enhanced validator for generated agents."""
    
    def __init__(self):
        self.code_validator = CodeValidator()
        self.structure_validator = StructureValidator({
            "class": "class definition",
            "MicroAgent": "MicroAgent inheritance",
            "def run": "run method",
            "def __init__": "constructor",
            "super().__init__": "parent initialization"
        })

    def validate(self, code_str: str, trigger_info: TriggerInfo) -> OperationResult[bool]:
        """Comprehensive validation of generated code."""
        # Security validation
        security_result = self.code_validator.validate(code_str)
        if not security_result.success:
            return security_result
            
        # Structure validation
        structure_result = self.structure_validator.validate(code_str)
        if not structure_result.success:
            return structure_result
            
        # Import validation
        if trigger_info.required_imports:
            import_result = self._validate_imports(code_str, trigger_info.required_imports)
            if not import_result.success:
                return import_result
                
        return OperationResult(
            success=True,
            data=True,
            duration=security_result.duration + structure_result.duration,
            metadata={
                "validations": ["security", "structure", "imports"]
            }
        )

    def _validate_imports(
        self,
        code_str: str,
        required_imports: List[str]
    ) -> OperationResult[bool]:
        """Validate required imports."""
        start_time = time.time()
        missing_imports = [
            imp for imp in required_imports
            if f"import {imp}" not in code_str and f"from {imp}" not in code_str
        ]
        
        if missing_imports:
            return OperationResult(
                success=False,
                error=ValidationError(
                    "Missing required imports",
                    {"missing_imports": missing_imports}
                ),
                duration=time.time() - start_time
            )
            
        return OperationResult(
            success=True,
            data=True,
            duration=time.time() - start_time
        )


class DynamicAgentFactoryLLM(MicroAgent):
    """
    Advanced meta-agent that generates technology-specific code analysis agents using LLM.
    
    Features:
    - Enhanced error handling and validation
    - Comprehensive security checks
    - Performance optimizations with caching
    - Detailed logging and monitoring
    - Structured generation results
    - Atomic state management
    """

    def __init__(self):
        """Initialize the factory with enhanced configuration and validation."""
        super().__init__(
            name="dynamic_agent_factory_llm",
            description="Creates specialized micro-agents via LLM with enhanced security and validation",
            inputs=["technology_keyword", "options"],
            outputs=["agent_class", "generation_info"]
        )
        
        self._initialize_llm()
        self.validator = AgentValidator()
        self.temp_dir = Path("/tmp/dynamic_agent_factory")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize caches
        self.llm_cache = Cache[str, str](ttl=3600)  # 1 hour TTL
        self.agent_cache = Cache[str, Type[MicroAgent]](ttl=3600)

    def _initialize_llm(self) -> None:
        """Initialize LLM with error handling and validation."""
        try:
            self.llm = get_llm(
                provider=LLM_PROVIDER,
                model=LLM_MODEL_NAME,
                api_key=LLM_API_KEY,
                **LLM_CONFIG
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise AgentGenerationError(
                f"LLM initialization failed: {str(e)}",
                "LLMInitializationError",
                {"provider": LLM_PROVIDER, "model": LLM_MODEL_NAME}
            )

    @monitor_performance("LLM code generation")
    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    def _generate_code(self, trigger_info: TriggerInfo) -> OperationResult[str]:
        """
        Generate code using LLM with enhanced prompt engineering.
        
        Args:
            trigger_info: The trigger information containing the prompt template
            
        Returns:
            str: The generated code
            
        Raises:
            AgentGenerationError: If code generation fails
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert code generator for OpenHands, "
                        "specializing in secure and efficient implementations."
                    )
                },
                {
                    "role": "user",
                    "content": trigger_info.llm_prompt_template.format(
                        class_name=trigger_info.class_name
                    )
                }
            ]
            
            # Check cache first
            cache_key = f"{trigger_info.class_name}:{hash(str(messages))}"
            cached_code = self.llm_cache.get(cache_key)
            if cached_code:
                return OperationResult(
                    success=True,
                    data=cached_code,
                    metadata={"cache_hit": True}
                )
            
            # Generate new code
            response = self.llm.chat(messages=messages)
            code = response.content
            
            # Cache the result
            self.llm_cache.set(cache_key, code)
            
            return OperationResult(
                success=True,
                data=code,
                metadata={"cache_hit": False}
            )

        except Exception as e:
            return OperationResult(
                success=False,
                error=AgentGenerationError(
                    f"Code generation failed: {str(e)}",
                    "CodeGenerationError",
                    {"trigger_info": trigger_info.__dict__},
                    "Check LLM service and prompt templates"
                )
            )

    def _load_agent_class(self, code_str: str, trigger_info: TriggerInfo) -> Type[MicroAgent]:
        """
        Load the generated agent class with enhanced safety checks.
        
        Args:
            code_str: The generated Python code
            trigger_info: The trigger information for validation
            
        Returns:
            Type[MicroAgent]: The generated agent class
            
        Raises:
            AgentGenerationError: If class loading fails
        """
        temp_file = self.temp_dir / f"{trigger_info.class_name.lower()}_{uuid.uuid4().hex}.py"
        try:
            # Write code to temporary file
            temp_file.write_text(code_str, encoding='utf-8')
            
            # Import the generated module
            spec = importlib.util.spec_from_file_location(
                trigger_info.class_name,
                str(temp_file)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get and validate the agent class
            agent_cls = getattr(module, trigger_info.class_name)
            
            # Validate class structure
            if not issubclass(agent_cls, MicroAgent):
                raise AgentGenerationError(
                    "Generated class does not inherit from MicroAgent",
                    "ClassValidationError"
                )
            
            return agent_cls

        except Exception as e:
            logger.error(f"Failed to load agent class: {str(e)}")
            raise AgentGenerationError(
                f"Class loading failed: {str(e)}",
                "ClassLoadingError",
                {"class_name": trigger_info.class_name}
            )
        finally:
            # Cleanup temporary file
            if temp_file.exists():
                temp_file.unlink()

    def generate_agent(
        self,
        tech: str,
        options: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        Generate a new agent class with enhanced validation and monitoring.
        
        Args:
            tech: Technology keyword
            options: Optional configuration for agent generation
            
        Returns:
            GenerationResult: Structured result of the generation process
        """
        start_time = datetime.now()
        logger.info(f"Starting agent generation for technology: {tech}")
        
        if tech not in TRIGGER_MAP:
            return GenerationResult(
                agent_class=None,
                status="error",
                error=f"Unknown technology: {tech}",
                generation_time=datetime.now()
            )

        trigger_info = TRIGGER_MAP[tech]
        validation_results = {}
        
        try:
            # Generate and validate code
            code_str = self._generate_code(trigger_info)
            
            # Security validation
            self.validator.validate_security(code_str)
            validation_results["security"] = True
            
            # Structure validation
            self.validator.validate_structure(code_str, trigger_info)
            validation_results["structure"] = True
            
            # Load and validate agent class
            agent_cls = self._load_agent_class(code_str, trigger_info)
            validation_results["class_loading"] = True
            
            return GenerationResult(
                agent_class=agent_cls,
                status="success",
                validation_results=validation_results,
                generation_time=datetime.now(),
                metadata={
                    "technology": tech,
                    "options": options,
                    "generation_duration": (datetime.now() - start_time).total_seconds()
                }
            )

        except AgentGenerationError as e:
            logger.error(f"Agent generation failed: {str(e)}")
            return GenerationResult(
                agent_class=None,
                status="error",
                error=str(e),
                validation_results=validation_results,
                generation_time=datetime.now(),
                metadata={
                    "error_type": e.error_type,
                    "error_details": e.details,
                    "technology": tech,
                    "options": options
                }
            )

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent factory with enhanced error handling and monitoring.
        
        Args:
            data: Dictionary containing:
                - technology_keyword: The technology to generate an agent for
                - options: Optional configuration for agent generation
                
        Returns:
            Dictionary containing:
                - agent_class: The generated agent class or None
                - generation_info: Detailed information about the generation process
        """
        tech = data["technology_keyword"].lower()
        options = data.get("options", {})
        
        logger.info(f"Processing request for technology: {tech}")
        
        try:
            result = self.generate_agent(tech, options)
            
            return {
                "agent_class": result.agent_class,
                "generation_info": {
                    "status": result.status,
                    "error": result.error,
                    "validation_results": result.validation_results,
                    "generation_time": result.generation_time.isoformat(),
                    "metadata": result.metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in run method: {str(e)}")
            return {
                "agent_class": None,
                "generation_info": {
                    "status": "error",
                    "error": f"Unexpected error: {str(e)}",
                    "generation_time": datetime.now().isoformat()
                }
            }
