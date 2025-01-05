"""
Enhanced trigger definitions and mappings with CSS framework support.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from .css_framework_analyzer import CSSFrameworkAnalyzer

@dataclass
class TriggerInfo:
    """Enhanced data structure for trigger mapping information."""
    class_name: str
    description: str
    llm_prompt_template: str
    inputs: Optional[List[str]] = None
    outputs: Optional[List[str]] = None
    required_imports: Optional[List[str]] = None
    validation_rules: Optional[Dict] = None
    metadata: Optional[Dict[str, Any]] = None

# Initialize CSS Framework Analyzer
css_analyzer = CSSFrameworkAnalyzer()

def get_css_framework_triggers() -> Dict[str, TriggerInfo]:
    """
    Dynamically generate triggers for validated CSS frameworks.
    Only creates triggers for frameworks that have been validated.
    """
    triggers = {}
    frameworks = css_analyzer.list_frameworks(validated_only=True)
    
    for framework in frameworks:
        name = framework["name"]
        name_normalized = name.lower().replace(" ", "_")
        class_name = f"{name_normalized.title()}Analyzer"
        
        triggers[name.lower()] = TriggerInfo(
            class_name=class_name,
            description=f"Analyzer for {name} CSS framework",
            inputs=["code_snippet", "analysis_type"],
            outputs=["analysis_report", "suggestions", "compatibility_check"],
            required_imports=["cssutils", "pylint"],
            validation_rules={
                "max_code_length": 10000,
                "required_analysis_types": ["style", "compatibility", "optimization"]
            },
            metadata=framework,
            llm_prompt_template=f"""
            Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes {name} CSS code.
            The agent should:
            1. Parse and validate {name} specific syntax
            2. Check for framework-specific best practices
            3. Identify potential compatibility issues
            4. Suggest optimizations
            5. Validate class usage and structure

            Requirements:
            - Subclass MicroAgent
            - Accept 'code_snippet' and 'analysis_type' inputs
            - Return dict with 'analysis_report', 'suggestions', and 'compatibility_check'
            - Include {name}-specific validations
            - Handle framework-specific patterns
            - Follow {name} best practices
            """
        )
    
    return triggers

# Base TRIGGER_MAP with static entries
BASE_TRIGGER_MAP = {
    "python": TriggerInfo(
        class_name="PythonAnalyzer",
        description="Advanced Python code analyzer for best practices and improvements",
        inputs=["code_snippet", "analysis_type"],
        outputs=["analysis_report", "suggestions", "complexity_score"],
        required_imports=["ast", "pylint"],
        validation_rules={
            "max_code_length": 10000,
            "required_analysis_types": ["style", "security", "performance"]
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
    ),
    
    "react": TriggerInfo(
        class_name="ReactAnalyzer",
        description="React.js code analyzer focusing on performance and best practices",
        inputs=["code_snippet", "react_version"],
        outputs=["analysis_report", "performance_tips", "accessibility_report"],
        required_imports=["esprima", "eslint"],
        validation_rules={
            "max_component_size": 5000,
            "supported_versions": ["16.x", "17.x", "18.x"]
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes React code.
        The agent should:
        1. Parse JSX/TSX syntax
        2. Check component lifecycle
        3. Identify performance bottlenecks
        4. Verify hooks usage
        5. Assess accessibility

        Requirements:
        - Subclass MicroAgent
        - Accept 'code_snippet' and 'react_version' inputs
        - Return dict with 'analysis_report', 'performance_tips', and 'accessibility_report'
        - Include React-specific validations
        - Handle JSX parsing errors
        """
    )
}

def get_trigger_map() -> Dict[str, TriggerInfo]:
    """
    Get the complete trigger map combining base triggers with
    dynamically generated CSS framework triggers.
    """
    # Start with base triggers
    triggers = BASE_TRIGGER_MAP.copy()
    
    # Add CSS framework triggers
    css_triggers = get_css_framework_triggers()
    triggers.update(css_triggers)
    
    return triggers

# Export the dynamic TRIGGER_MAP
TRIGGER_MAP = get_trigger_map()
