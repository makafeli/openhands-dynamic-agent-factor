"""Technology trigger map for dynamic agent generation."""

from typing import Dict, Any

TRIGGER_MAP: Dict[str, Dict[str, Any]] = {
    # Front-end Technologies
    "react": {
        "class_name": "ReactAnalyzer",
        "description": "React code analyzer for components, hooks, and performance",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["react", "react-dom"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a React code analyzer that:
        1. Analyzes {analysis_type} aspects of React code
        2. Checks for best practices and common pitfalls
        3. Provides performance optimization suggestions
        4. Returns detailed recommendations
        """
    },
    "vue": {
        "class_name": "VueAnalyzer",
        "description": "Vue.js code analyzer for components and composition API",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["vue"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Vue.js code analyzer that:
        1. Analyzes {analysis_type} aspects of Vue code
        2. Validates component structure and lifecycle
        3. Checks composition API usage
        4. Returns detailed recommendations
        """
    },
    "next": {
        "class_name": "NextJSAnalyzer",
        "description": "Next.js framework analyzer for SSR and routing",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["next"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Next.js code analyzer that:
        1. Analyzes {analysis_type} aspects of Next.js code
        2. Validates SSR implementation
        3. Checks routing and data fetching
        4. Returns detailed recommendations
        """
    },

    # Back-end Technologies
    "python": {
        "class_name": "PythonAnalyzer",
        "description": "Python code analyzer for style, security, and performance",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["ast", "pylint"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Python code analyzer that:
        1. Analyzes {analysis_type} aspects of Python code
        2. Checks PEP 8 compliance
        3. Performs security analysis
        4. Returns detailed recommendations
        """
    },
    "node": {
        "class_name": "NodeAnalyzer",
        "description": "Node.js code analyzer for async patterns and performance",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["acorn", "eslint"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Node.js code analyzer that:
        1. Analyzes {analysis_type} aspects of Node.js code
        2. Validates async/await patterns
        3. Checks for memory leaks
        4. Returns detailed recommendations
        """
    },
    "django": {
        "class_name": "DjangoAnalyzer",
        "description": "Django framework analyzer for models and views",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["django"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Django code analyzer that:
        1. Analyzes {analysis_type} aspects of Django code
        2. Validates model relationships
        3. Checks view patterns
        4. Returns detailed recommendations
        """
    },

    # Database Technologies
    "sql": {
        "class_name": "SQLAnalyzer",
        "description": "SQL query analyzer for optimization and security",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["sqlparse", "sqlalchemy"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create an SQL query analyzer that:
        1. Analyzes {analysis_type} aspects of SQL queries
        2. Optimizes query performance
        3. Checks for SQL injection risks
        4. Returns detailed recommendations
        """
    },
    "mongodb": {
        "class_name": "MongoDBAnalyzer",
        "description": "MongoDB query and schema analyzer",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["pymongo"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a MongoDB analyzer that:
        1. Analyzes {analysis_type} aspects of MongoDB code
        2. Validates schema design
        3. Optimizes query patterns
        4. Returns detailed recommendations
        """
    },

    # DevOps Technologies
    "docker": {
        "class_name": "DockerAnalyzer",
        "description": "Docker configuration and security analyzer",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["docker"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Docker configuration analyzer that:
        1. Analyzes {analysis_type} aspects of Dockerfile
        2. Checks security best practices
        3. Validates multi-stage builds
        4. Returns detailed recommendations
        """
    },
    "kubernetes": {
        "class_name": "KubernetesAnalyzer",
        "description": "Kubernetes manifest and configuration analyzer",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["kubernetes"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Kubernetes configuration analyzer that:
        1. Analyzes {analysis_type} aspects of K8s manifests
        2. Validates resource configurations
        3. Checks security contexts
        4. Returns detailed recommendations
        """
    },

    # Cloud Technologies
    "aws": {
        "class_name": "AWSAnalyzer",
        "description": "AWS infrastructure and security analyzer",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["boto3"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create an AWS configuration analyzer that:
        1. Analyzes {analysis_type} aspects of AWS resources
        2. Validates IAM policies
        3. Checks security groups
        4. Returns detailed recommendations
        """
    },

    # Testing Technologies
    "jest": {
        "class_name": "JestAnalyzer",
        "description": "Jest test suite analyzer",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["jest"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Jest test analyzer that:
        1. Analyzes {analysis_type} aspects of Jest tests
        2. Validates test coverage
        3. Checks mocking patterns
        4. Returns detailed recommendations
        """
    },
    "pytest": {
        "class_name": "PytestAnalyzer",
        "description": "Pytest test suite analyzer",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["pytest"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a Pytest analyzer that:
        1. Analyzes {analysis_type} aspects of Pytest tests
        2. Validates fixture usage
        3. Checks parametrization
        4. Returns detailed recommendations
        """
    },

    # API Technologies
    "graphql": {
        "class_name": "GraphQLAnalyzer",
        "description": "GraphQL schema and resolver analyzer",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["graphql"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a GraphQL analyzer that:
        1. Analyzes {analysis_type} aspects of GraphQL code
        2. Validates schema design
        3. Checks resolver patterns
        4. Returns detailed recommendations
        """
    },
    "rest": {
        "class_name": "RESTAnalyzer",
        "description": "REST API design and security analyzer",
        "inputs": ["code_snippet", "analysis_type"],
        "outputs": ["analysis_report", "suggestions"],
        "required_imports": ["flask", "fastapi"],
        "validation_rules": {
            "max_code_length": 10000,
            "required_fields": ["code_snippet"]
        },
        "llm_prompt_template": """
        Create a REST API analyzer that:
        1. Analyzes {analysis_type} aspects of REST endpoints
        2. Validates HTTP methods
        3. Checks authentication
        4. Returns detailed recommendations
        """
    }
}