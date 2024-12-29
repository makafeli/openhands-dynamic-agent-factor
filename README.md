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

1. Install the package using pip:
```bash
pip install openhands-dynamic-agent-factory
```

2. Optional: Install technology-specific dependencies:
```bash
# For Python analysis support
pip install "openhands-dynamic-agent-factory[python]"

# For React analysis support
pip install "openhands-dynamic-agent-factory[react]"

# For Node.js analysis support
pip install "openhands-dynamic-agent-factory[node]"

# For SQL analysis support
pip install "openhands-dynamic-agent-factory[sql]"

# For all technologies
pip install "openhands-dynamic-agent-factory[all]"
```

## Quick Start

```python
from openhands_dynamic_agent_factory import DynamicAgentFactoryLLM

# Create the factory
factory = DynamicAgentFactoryLLM()

# Generate a Python analyzer
result = factory.run({
    "technology_keyword": "python",
    "options": {
        "analysis_type": "security"
    }
})

if result["agent_class"]:
    # Create an instance of the generated agent
    agent = result["agent_class"]()
    
    # Analyze some code
    analysis = agent.run({
        "code_snippet": "your_code_here",
        "analysis_type": "security"
    })
    print(analysis)
```

## Configuration

1. Configure your OpenHands LLM settings in your project:
```python
# openhands_config.py
LLM_PROVIDER = "openai"  # or your preferred provider
LLM_MODEL_NAME = "gpt-4"  # or your preferred model
LLM_API_KEY = "your-api-key"
LLM_CONFIG = {
    # Additional LLM configuration
}
```

2. The factory will automatically use these settings.

## Supported Technologies

### Python Analysis
- Input: Python code snippets
- Analysis types: style, security, performance
- Outputs: analysis report, suggestions, complexity score

### React Analysis
- Input: React/JSX code
- Features: Component lifecycle, hooks usage, performance
- Outputs: analysis report, performance tips, accessibility report

### Node.js Analysis
- Input: Node.js/JavaScript code
- Focus: Security, async patterns, scalability
- Outputs: analysis report, security audit, performance metrics

### SQL Analysis
- Input: SQL queries
- Features: Query optimization, injection checks
- Outputs: analysis report, optimization suggestions, execution plan

## Advanced Usage

### Custom Technology Triggers

You can add your own technology triggers:

```python
from openhands_dynamic_agent_factory import TRIGGER_MAP, TriggerInfo

TRIGGER_MAP["java"] = TriggerInfo(
    class_name="JavaAnalyzer",
    description="Java code analyzer",
    inputs=["code_snippet"],
    outputs=["analysis_report"],
    required_imports=["javalang"],
    validation_rules={
        "max_code_length": 10000
    },
    llm_prompt_template="""
    Generate a Java code analyzer...
    """
)
```

### Error Handling

The factory provides detailed error information:

```python
result = factory.run({"technology_keyword": "python"})
if result["agent_class"] is None:
    error_info = result["generation_info"]
    print(f"Generation failed: {error_info['error']}")
```

## Examples

Check the `examples/` directory for more usage examples:
- `basic_usage.py`: Simple example of generating and using an agent
- More examples coming soon!

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on top of the amazing [OpenHands](https://github.com/All-Hands-AI/OpenHands) framework
- Uses LLM capabilities for dynamic code generation
- Inspired by the need for flexible, technology-specific code analysis
