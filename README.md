# OpenHands Dynamic Agent Factory

A powerful extension for OpenHands that provides dynamic agent generation capabilities based on technology keywords. This module automatically creates specialized micro-agents for analyzing different technologies like Python, React, Node.js, and SQL using LLM-powered code generation.

## Features

- 🤖 **Dynamic Agent Generation**: Automatically create specialized micro-agents based on technology keywords
- 🔄 **OpenHands Integration**: Seamless integration with OpenHands' LLM configuration system
- 🛡️ **Security First**: Built-in code validation and security checks
- 🎯 **Technology-Specific**: Pre-configured for Python, React, Node.js, and SQL analysis
- 🔌 **Extensible**: Easy to add new technology triggers and customizations
- ⚡ **Production Ready**: Comprehensive error handling and validation

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenHands framework
- Access to an LLM provider (e.g., OpenAI)

### Basic Installation

```bash
pip install openhands-dynamic-agent-factory
```

### Technology-Specific Dependencies

Choose the dependencies based on your needs:

```bash
# Python analysis support
pip install "openhands-dynamic-agent-factory[python]"

# React analysis support
pip install "openhands-dynamic-agent-factory[react]"

# Node.js analysis support
pip install "openhands-dynamic-agent-factory[node]"

# SQL analysis support
pip install "openhands-dynamic-agent-factory[sql]"

# All technologies
pip install "openhands-dynamic-agent-factory[all]"
```

## Quick Start

### Basic Usage

```python
from openhands_dynamic_agent_factory import DynamicAgentFactoryLLM

# Initialize the factory
factory = DynamicAgentFactoryLLM()

# Generate a Python code analyzer
result = factory.run({
    "technology_keyword": "python",
    "options": {
        "analysis_type": "security"
    }
})

# Use the generated agent
if result["agent_class"]:
    agent = result["agent_class"]()
    analysis = agent.run({
        "code_snippet": """
        def process_data(user_input):
            return eval(user_input)  # Security risk!
        """,
        "analysis_type": "security"
    })
    print(analysis)
```

### Configuration

Configure your OpenHands LLM settings in your project:

```python
# config.py
from openhands.config import Config

config = Config({
    "llm": {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "your-api-key",
        "temperature": 0.7
    }
})
```

The factory will automatically use these settings from your OpenHands configuration.

## Supported Technologies

### Python Analysis
- **Input**: Python code snippets
- **Analysis Types**: 
  - Style (PEP 8 compliance)
  - Security (vulnerability detection)
  - Performance (optimization suggestions)
- **Outputs**: Detailed analysis report with:
  - Code quality metrics
  - Security vulnerabilities
  - Performance recommendations

### React Analysis
- **Input**: React/JSX components
- **Features**: 
  - Component structure analysis
  - Hooks usage patterns
  - Performance optimization
- **Outputs**: 
  - Best practices compliance
  - Performance bottlenecks
  - Accessibility issues

### Node.js Analysis
- **Input**: Node.js/JavaScript code
- **Focus Areas**: 
  - Security vulnerabilities
  - Async/await patterns
  - Scalability issues
- **Outputs**: 
  - Security audit report
  - Performance metrics
  - Best practices suggestions

### SQL Analysis
- **Input**: SQL queries
- **Features**: 
  - Query optimization
  - Injection prevention
  - Performance analysis
- **Outputs**: 
  - Optimization suggestions
  - Security recommendations
  - Execution plan analysis

## Advanced Usage

### Custom Technology Triggers

Add your own technology-specific analyzers:

```python
from openhands_dynamic_agent_factory import TRIGGER_MAP, TriggerInfo

# Define a new Java analyzer
TRIGGER_MAP["java"] = TriggerInfo(
    class_name="JavaAnalyzer",
    description="Advanced Java code analyzer",
    inputs=["code_snippet", "analysis_type"],
    outputs=["analysis_report", "suggestions"],
    required_imports=["javalang"],
    validation_rules={
        "max_code_length": 10000,
        "required_fields": ["code_snippet"]
    },
    llm_prompt_template="""
    Create a Java code analyzer that:
    1. Parses the input using javalang
    2. Analyzes for {analysis_type}
    3. Returns detailed suggestions
    """
)
```

### Error Handling

The factory provides comprehensive error handling:

```python
try:
    result = factory.run({
        "technology_keyword": "python",
        "options": {"analysis_type": "security"}
    })
    if result["agent_class"] is None:
        error_info = result["generation_info"]
        print(f"Agent generation failed: {error_info['error']}")
        print(f"Details: {error_info.get('details', 'No additional details')}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Project Structure

```
openhands-dynamic-agent-factory/
├── openhands_dynamic_agent_factory/
│   ├── core/
│   │   ├── factory.py         # Main factory implementation
│   │   ├── triggers.py        # Technology trigger definitions
│   │   └── dynamic_agent_factory_llm.py
│   └── __init__.py
├── examples/
│   └── basic_usage.py         # Usage examples
├── README.md
├── LICENSE
└── pyproject.toml
```

## Contributing

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes and commit:
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. Push to your branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

### Development Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest tests/
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of the [OpenHands](https://github.com/All-Hands-AI/OpenHands) framework
- Powered by state-of-the-art LLM capabilities
- Inspired by the need for intelligent, technology-specific code analysis
