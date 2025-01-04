"""
Trigger definitions and mappings for the dynamic agent factory.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class TriggerInfo:
    """Data structure for trigger mapping information."""
    class_name: str
    description: str
    llm_prompt_template: str
    inputs: Optional[List[str]] = None
    outputs: Optional[List[str]] = None
    required_imports: Optional[List[str]] = None
    validation_rules: Optional[Dict] = None


# Expanded TRIGGER_MAP with comprehensive metadata
TRIGGER_MAP = {
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
    ),
    
    "node": TriggerInfo(
        class_name="NodeAnalyzer",
        description="Node.js backend code analyzer with security focus",
        inputs=["code_snippet", "node_version", "environment"],
        outputs=["analysis_report", "security_audit", "performance_metrics"],
        required_imports=["acorn", "eslint"],
        validation_rules={
            "environments": ["development", "production", "testing"],
            "security_checks": ["sql-injection", "xss", "csrf"]
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes Node.js code.
        The agent should:
        1. Parse JavaScript/TypeScript
        2. Perform security analysis
        3. Check async patterns
        4. Validate error handling
        5. Assess scalability

        Requirements:
        - Subclass MicroAgent
        - Accept 'code_snippet', 'node_version', and 'environment' inputs
        - Return dict with 'analysis_report', 'security_audit', and 'performance_metrics'
        - Include security-focused validations
        - Handle Node.js specific patterns
        """
    ),
    
    "sql": TriggerInfo(
        class_name="SQLAnalyzer",
        description="SQL query analyzer and optimizer",
        inputs=["query", "dialect", "schema"],
        outputs=["analysis_report", "optimization_suggestions", "execution_plan"],
        required_imports=["sqlparse", "sqlalchemy"],
        validation_rules={
            "supported_dialects": ["mysql", "postgresql", "sqlite"],
            "max_query_length": 5000
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes SQL queries.
        The agent should:
        1. Parse SQL syntax
        2. Analyze query performance
        3. Suggest optimizations
        4. Check for SQL injection risks
        5. Generate execution plans

        Requirements:
        - Subclass MicroAgent
        - Accept 'query', 'dialect', and 'schema' inputs
        - Return dict with 'analysis_report', 'optimization_suggestions', and 'execution_plan'
        - Include SQL-specific validations
        - Handle different SQL dialects
        """
    ),

    "ci/cd": TriggerInfo(
        class_name="CICDAnalyzer",
        description="CI/CD pipeline analyzer and optimizer",
        inputs=["pipeline_config", "platform"],
        outputs=["analysis_report", "optimization_suggestions", "security_audit"],
        required_imports=["yaml", "requests"],
        validation_rules={
            "supported_platforms": ["github", "gitlab", "jenkins"]
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes CI/CD pipelines.
        The agent should:
        1. Parse pipeline configuration files
        2. Identify performance bottlenecks
        3. Suggest optimizations
        4. Check for security vulnerabilities
        5. Generate detailed reports

        Requirements:
        - Subclass MicroAgent
        - Accept 'pipeline_config' and 'platform' inputs
        - Return dict with 'analysis_report', 'optimization_suggestions', and 'security_audit'
        - Include platform-specific validations
        - Handle different CI/CD platforms
        """
    ),

    "github": TriggerInfo(
        class_name="GitHubAnalyzer",
        description="GitHub integration for code analysis and automation",
        inputs=["repository", "pull_request", "workflow"],
        outputs=["analysis_report", "automation_suggestions", "security_audit"],
        required_imports=["requests", "github"],
        validation_rules={
            "supported_events": ["pull_request", "push", "workflow_dispatch"]
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that integrates with GitHub.
        The agent should:
        1. Analyze repository code
        2. Automate pull request reviews
        3. Optimize workflows
        4. Check for security vulnerabilities
        5. Generate detailed reports

        Requirements:
        - Subclass MicroAgent
        - Accept 'repository', 'pull_request', and 'workflow' inputs
        - Return dict with 'analysis_report', 'automation_suggestions', and 'security_audit'
        - Include GitHub-specific validations
        - Handle different GitHub events
        """
    ),

    "gitlab": TriggerInfo(
        class_name="GitLabAnalyzer",
        description="GitLab integration for code analysis and automation",
        inputs=["repository", "merge_request", "pipeline"],
        outputs=["analysis_report", "automation_suggestions", "security_audit"],
        required_imports=["requests", "gitlab"],
        validation_rules={
            "supported_events": ["merge_request", "push", "pipeline"]
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that integrates with GitLab.
        The agent should:
        1. Analyze repository code
        2. Automate merge request reviews
        3. Optimize pipelines
        4. Check for security vulnerabilities
        5. Generate detailed reports

        Requirements:
        - Subclass MicroAgent
        - Accept 'repository', 'merge_request', and 'pipeline' inputs
        - Return dict with 'analysis_report', 'automation_suggestions', and 'security_audit'
        - Include GitLab-specific validations
        - Handle different GitLab events
        """
    ),

    "pull_requests": TriggerInfo(
        class_name="PullRequestAnalyzer",
        description="Pull request analyzer for code review and merging",
        inputs=["pull_request", "repository", "platform"],
        outputs=["analysis_report", "review_suggestions", "security_audit"],
        required_imports=["requests", "github", "gitlab"],
        validation_rules={
            "supported_platforms": ["github", "gitlab"]
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes pull requests.
        The agent should:
        1. Review code changes
        2. Suggest improvements
        3. Check for security vulnerabilities
        4. Automate merging
        5. Generate detailed reports

        Requirements:
        - Subclass MicroAgent
        - Accept 'pull_request', 'repository', and 'platform' inputs
        - Return dict with 'analysis_report', 'review_suggestions', and 'security_audit'
        - Include platform-specific validations
        - Handle different platforms
        """
    ),

    "deployments": TriggerInfo(
        class_name="DeploymentAnalyzer",
        description="Deployment analyzer for release management",
        inputs=["deployment_config", "environment", "platform"],
        outputs=["analysis_report", "optimization_suggestions", "security_audit"],
        required_imports=["yaml", "requests"],
        validation_rules={
            "supported_platforms": ["kubernetes", "docker", "aws"]
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes deployments.
        The agent should:
        1. Parse deployment configurations
        2. Identify performance bottlenecks
        3. Suggest optimizations
        4. Check for security vulnerabilities
        5. Generate detailed reports

        Requirements:
        - Subclass MicroAgent
        - Accept 'deployment_config', 'environment', and 'platform' inputs
        - Return dict with 'analysis_report', 'optimization_suggestions', and 'security_audit'
        - Include platform-specific validations
        - Handle different deployment platforms
        """
    ),
    "tailwind": TriggerInfo(
        class_name="TailwindAnalyzer",
        description="Tailwind CSS analyzer for best practices and optimizations",
        inputs=["css_snippet", "config"],
        outputs=["analysis_report", "optimization_suggestions", "performance_metrics"],
        required_imports=["cssutils", "tailwindcss"],
        validation_rules={
            "max_css_length": 10000,
            "supported_versions": ["3.x", "2.x"]
        },
        llm_prompt_template="""
        Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes Tailwind CSS code.
        The agent should:
        1. Parse Tailwind CSS classes
        2. Check for unused classes
        3. Suggest optimizations
        4. Analyze performance
        5. Handle errors gracefully

        Requirements:
        - Subclass MicroAgent
        - Accept 'css_snippet' and 'config' inputs
        - Return dict with 'analysis_report', 'optimization_suggestions', and 'performance_metrics'
        - Include proper error handling
        - Follow best practices for Tailwind CSS
        """
    )
}
