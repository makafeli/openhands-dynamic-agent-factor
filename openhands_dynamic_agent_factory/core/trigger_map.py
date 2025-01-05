"""
Enhanced trigger definitions and mappings with improved validation,
caching, and error handling.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

from .tech_analyzer import TechStackAnalyzer
from .utils import (
    BaseError, ValidationError, Cache, StateManager,
    OperationResult, monitor_performance
)

# Configure logging
logger = logging.getLogger(__name__)

class TriggerMapError(BaseError):
    """Custom error for trigger map operations."""
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
            recovery_hint or "Check trigger configuration and dependencies"
        )

@dataclass
class ValidationRule:
    """Enhanced validation rule definition."""
    name: str
    description: str
    validator: str  # Python expression for validation
    error_message: str
    severity: str = "error"  # error, warning, info
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TriggerInfo:
    """Enhanced data structure for trigger mapping information."""
    class_name: str
    description: str
    llm_prompt_template: str
    inputs: Optional[List[str]] = None
    outputs: Optional[List[str]] = None
    required_imports: Optional[List[str]] = None
    validation_rules: Optional[Dict[str, ValidationRule]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    def validate(self, data: Dict[str, Any]) -> OperationResult[bool]:
        """Validate data against trigger rules."""
        if not self.validation_rules:
            return OperationResult(success=True, data=True)
            
        violations = []
        for rule_name, rule in self.validation_rules.items():
            try:
                # Safe eval of validation expression
                is_valid = eval(
                    rule.validator,
                    {"__builtins__": {}},  # No built-ins for safety
                    {"data": data}  # Only provide the data to validate
                )
                
                if not is_valid:
                    violations.append({
                        "rule": rule_name,
                        "message": rule.error_message,
                        "severity": rule.severity
                    })
                    
            except Exception as e:
                violations.append({
                    "rule": rule_name,
                    "message": f"Validation error: {str(e)}",
                    "severity": "error"
                })
                
        if violations:
            return OperationResult(
                success=False,
                error=ValidationError(
                    "Trigger validation failed",
                    {"violations": violations}
                )
            )
            
        return OperationResult(success=True, data=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with datetime handling."""
        data = {
            "class_name": self.class_name,
            "description": self.description,
            "llm_prompt_template": self.llm_prompt_template,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "required_imports": self.required_imports,
            "validation_rules": {
                name: vars(rule)
                for name, rule in (self.validation_rules or {}).items()
            },
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "version": self.version
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TriggerInfo':
        """Create from dictionary with validation."""
        validation_rules = {}
        if "validation_rules" in data:
            for name, rule_data in data["validation_rules"].items():
                validation_rules[name] = ValidationRule(**rule_data)
                
        return cls(
            class_name=data["class_name"],
            description=data["description"],
            llm_prompt_template=data["llm_prompt_template"],
            inputs=data.get("inputs"),
            outputs=data.get("outputs"),
            required_imports=data.get("required_imports"),
            validation_rules=validation_rules,
            metadata=data.get("metadata"),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            version=data.get("version", "1.0.0")
        )

class TriggerMapManager:
    """Enhanced manager for trigger mappings."""
    
    def __init__(self, state_dir: Optional[Path] = None):
        """Initialize with state management and caching."""
        self.state_dir = state_dir or Path("/tmp/dynamic_agent_factory")
        self.state_manager = StateManager[Dict[str, Any]](
            self.state_dir / "trigger_map_state.json"
        )
        
        # Initialize caches
        self.trigger_cache = Cache[str, TriggerInfo](ttl=3600)
        self.tech_cache = Cache[str, Dict[str, Any]](ttl=1800)
        
        # Initialize tech analyzer
        self.tech_analyzer = TechStackAnalyzer()
        
        # Load initial state
        self._load_state()

    def _load_state(self) -> None:
        """Load state with validation."""
        result = self.state_manager.load_state()
        if result.success and result.data:
            self.triggers = {
                k: TriggerInfo.from_dict(v)
                for k, v in result.data.get("triggers", {}).items()
            }
        else:
            logger.warning("Failed to load state, using defaults")
            self.triggers = {}
            self._initialize_default_triggers()

    def _initialize_default_triggers(self) -> None:
        """Initialize default triggers."""
        # Add base triggers
        self.triggers = {
            "python": TriggerInfo(
                class_name="PythonAnalyzer",
                description="Advanced Python code analyzer",
                inputs=["code_snippet", "analysis_type"],
                outputs=["analysis_report", "suggestions", "complexity_score"],
                required_imports=["ast", "pylint"],
                validation_rules={
                    "code_length": ValidationRule(
                        name="Maximum Code Length",
                        description="Validates code length",
                        validator="len(data.get('code_snippet', '')) <= 10000",
                        error_message="Code exceeds maximum length of 10000 characters"
                    ),
                    "analysis_type": ValidationRule(
                        name="Analysis Type",
                        description="Validates analysis type",
                        validator="data.get('analysis_type') in ['style', 'security', 'performance']",
                        error_message="Invalid analysis type"
                    )
                },
                llm_prompt_template="""
                Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes Python code.
                The agent should:
                1. Use AST for code parsing
                2. Check for common anti-patterns
                3. Analyze code complexity
                4. Suggest improvements
                5. Handle errors gracefully

                Requirements:
                - Subclass MicroAgent
                - Accept 'code_snippet' and 'analysis_type' inputs
                - Return dict with 'analysis_report', 'suggestions', and 'complexity_score'
                - Include proper error handling
                - Follow PEP 8
                - Use type hints
                """
            )
        }
        
        # Add dynamic triggers from tech analyzer
        self.triggers.update(self._generate_tech_triggers())
        self._save_state()

    def _save_state(self) -> None:
        """Save current state."""
        state = {
            "triggers": {
                k: v.to_dict() for k, v in self.triggers.items()
            },
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
        self.state_manager.save_state(state)

    @monitor_performance("Technology trigger generation")
    def _generate_tech_triggers(self) -> Dict[str, TriggerInfo]:
        """Generate triggers for all technology types."""
        triggers = {}
        technologies = self.tech_analyzer.list_technologies(validated_only=True)
        
        for tech in technologies:
            name = tech["name"]
            name_normalized = name.lower().replace(" ", "_")
            class_name = f"{name_normalized.title()}Analyzer"
            
            # Get appropriate validation rules based on tech type
            validation_rules = self._get_validation_rules(tech)
            
            # Get appropriate imports based on tech type
            required_imports = self._get_required_imports(tech)
            
            triggers[name.lower()] = TriggerInfo(
                class_name=class_name,
                description=f"Analyzer for {name} ({tech['type']})",
                inputs=["code_snippet", "analysis_type"],
                outputs=["analysis_report", "suggestions", "compatibility_check"],
                required_imports=required_imports,
                validation_rules=validation_rules,
                metadata=tech,
                llm_prompt_template=self._get_prompt_template(tech)
            )
            
        return triggers

    def _get_validation_rules(self, tech: Dict[str, Any]) -> Dict[str, ValidationRule]:
        """Get appropriate validation rules based on technology type."""
        rules = {
            "code_length": ValidationRule(
                name="Code Length",
                description="Validates code length",
                validator="len(data.get('code_snippet', '')) <= 10000",
                error_message="Code exceeds maximum length"
            )
        }
        
        # Add type-specific rules
        if tech["type"] == "language":
            rules["syntax"] = ValidationRule(
                name="Syntax Check",
                description="Validates basic syntax",
                validator="'syntax_error' not in data.get('code_snippet', '').lower()",
                error_message="Code contains syntax errors"
            )
        elif tech["type"] == "framework":
            rules["framework_version"] = ValidationRule(
                name="Framework Version",
                description="Validates framework version",
                validator=f"data.get('version') in {tech['version_info'].get('supported', ['*'])}",
                error_message="Unsupported framework version"
            )
            
        return rules

    def _get_required_imports(self, tech: Dict[str, Any]) -> List[str]:
        """Get appropriate imports based on technology type."""
        base_imports = ["typing"]
        
        if tech["type"] == "language":
            if tech["name"] == "python":
                return base_imports + ["ast", "pylint"]
            elif tech["name"] == "javascript":
                return base_imports + ["esprima", "eslint"]
        elif tech["type"] == "framework":
            if "frontend" in tech["category"]:
                return base_imports + ["esprima", "eslint"]
            elif "backend" in tech["category"]:
                return base_imports + ["ast", "pylint"]
                
        return base_imports

    def _get_prompt_template(self, tech: Dict[str, Any]) -> str:
        """Get appropriate prompt template based on technology type."""
        return f"""
        Generate a Python OpenHands MicroAgent class named '{{class_name}}' that analyzes {tech['name']} code.
        
        Technology Type: {tech['type']}
        Category: {tech['category']}
        
        The agent should:
        1. Parse and validate {tech['name']} specific syntax
        2. Check for {tech['type']}-specific best practices
        3. Identify potential compatibility issues
        4. Suggest optimizations
        5. Validate usage patterns
        
        Features to analyze:
        {chr(10).join(f'- {feature}' for feature in tech.get('features', []))}
        
        Use cases to consider:
        {chr(10).join(f'- {case}' for case in tech.get('use_cases', []))}
        
        Requirements:
        - Subclass MicroAgent
        - Accept 'code_snippet' and 'analysis_type' inputs
        - Return dict with 'analysis_report', 'suggestions', and 'compatibility_check'
        - Include {tech['name']}-specific validations
        - Handle {tech['type']}-specific patterns
        - Follow {tech['name']} best practices
        """

    @monitor_performance("Get trigger")
    def get_trigger(self, key: str) -> OperationResult[TriggerInfo]:
        """Get trigger info with caching."""
        # Check cache
        cached = self.trigger_cache.get(key)
        if cached:
            return OperationResult(
                success=True,
                data=cached,
                metadata={"cache_hit": True}
            )
            
        # Check static triggers
        if key in self.triggers:
            trigger = self.triggers[key]
            self.trigger_cache.set(key, trigger)
            return OperationResult(
                success=True,
                data=trigger,
                metadata={"cache_hit": False}
            )
            
        # Check dynamic triggers
        tech_triggers = self._generate_tech_triggers()
        if key in tech_triggers:
            trigger = tech_triggers[key]
            self.trigger_cache.set(key, trigger)
            return OperationResult(
                success=True,
                data=trigger,
                metadata={"cache_hit": False, "source": "tech_analyzer"}
            )
            
        return OperationResult(
            success=False,
            error=TriggerMapError(
                f"No trigger found for key: {key}",
                "TriggerNotFound"
            )
        )

    def add_trigger(self, key: str, trigger: TriggerInfo) -> OperationResult[bool]:
        """Add new trigger with validation."""
        if key in self.triggers:
            return OperationResult(
                success=False,
                error=TriggerMapError(
                    f"Trigger already exists: {key}",
                    "DuplicateTrigger"
                )
            )
            
        self.triggers[key] = trigger
        self.trigger_cache.set(key, trigger)
        self._save_state()
        
        return OperationResult(success=True, data=True)

    def update_trigger(self, key: str, trigger: TriggerInfo) -> OperationResult[bool]:
        """Update existing trigger."""
        if key not in self.triggers:
            return OperationResult(
                success=False,
                error=TriggerMapError(
                    f"Trigger not found: {key}",
                    "TriggerNotFound"
                )
            )
            
        self.triggers[key] = trigger
        self.trigger_cache.set(key, trigger)
        self._save_state()
        
        return OperationResult(success=True, data=True)

    def remove_trigger(self, key: str) -> OperationResult[bool]:
        """Remove trigger."""
        if key not in self.triggers:
            return OperationResult(
                success=False,
                error=TriggerMapError(
                    f"Trigger not found: {key}",
                    "TriggerNotFound"
                )
            )
            
        del self.triggers[key]
        self.trigger_cache.clear()  # Clear cache on removal
        self._save_state()
        
        return OperationResult(success=True, data=True)

# Initialize the manager
trigger_manager = TriggerMapManager()

# Export the TRIGGER_MAP for backward compatibility
TRIGGER_MAP = trigger_manager.triggers
