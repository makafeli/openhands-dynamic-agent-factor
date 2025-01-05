# OpenHands Dynamic Agent Factory

A powerful system for analyzing and generating technology-specific agents with comprehensive analysis capabilities.

## Features

### 1. Technology Stack Analysis
- Comprehensive analysis of technology stacks
- Support for multiple technology types:
  * Programming Languages (Python, JavaScript, etc.)
  * Frontend Frameworks (React, Vue, etc.)
  * Backend Frameworks (Django, Express, etc.)
  * CSS Frameworks (Tailwind, Bootstrap, etc.)
  * Databases (PostgreSQL, MongoDB, etc.)
  * Testing Tools (Jest, PyTest, etc.)
  * DevOps Tools (Docker, Kubernetes, etc.)
  * Cloud Services (AWS, GCP, etc.)

### 2. Analysis Capabilities
- Stack compatibility checking
- Dependency analysis
- Version management
- Security advisories
- Learning resources
- Best practices recommendations
- Technology ecosystem mapping

### 3. Web Interface
- Interactive dashboard for analysis
- Real-time visualization
- Historical tracking
- Template management
- Analysis reports
- Stack suggestions

### 4. CLI Tool
```bash
# Install CLI
npm install -g openhands-cli

# Basic analysis
openhands analyze "Building with React and Django"

# Analysis with template
openhands analyze --template strict "Using Tailwind CSS"

# Launch dashboard
openhands dashboard

# Create custom template
openhands template create custom --description "Custom analysis"
```

### 5. NPM Package
```bash
# Install package
npm install openhands-dynamic-agent-factor

# Usage
const { TechStackAnalyzer } = require('openhands-dynamic-agent-factor');

const analyzer = new TechStackAnalyzer();
const result = await analyzer.analyze(
    "Building a web app with React and Node.js"
);
```

### 6. CI/CD Integration
- GitHub Actions integration
- GitLab CI integration
- Automated analysis in PRs
- Custom reporting
- Status checks

```yaml
# .github/workflows/tech-analysis.yml
name: Technology Stack Analysis

on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: openhands/tech-analysis-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### 7. Python API
```python
from openhands_dynamic_agent_factory import TechStackAnalyzer

# Initialize analyzer
analyzer = TechStackAnalyzer()

# Analyze tech stack
result = analyzer.process_text(
    "Building a web app with Python/Django backend, "
    "React frontend, PostgreSQL database, and testing with Jest"
)

# Get stack suggestions
suggestion = analyzer.suggest_stack({
    "project_type": "web",
    "scale": "medium",
    "team_expertise": ["python", "javascript"],
    "constraints": {
        "exclude": ["legacy"]
    }
})
```

## Installation

### NPM Package
```bash
npm install openhands-dynamic-agent-factor
```

### Python Package
```bash
pip install openhands-dynamic-agent-factor
```

### CLI Tool
```bash
npm install -g openhands-cli
```

## Web Dashboard

The web dashboard provides an interactive interface for:
- Real-time technology analysis
- Stack compatibility checking
- Learning resource suggestions
- Historical analysis tracking
- Template management
- Custom reporting

To launch the dashboard:
```bash
openhands dashboard
```

Or programmatically:
```python
from openhands_dynamic_agent_factory import launch_dashboard
launch_dashboard(port=8000)
```

## Templates

Customize analysis with templates:

```json
{
  "name": "strict",
  "description": "Strict analysis mode",
  "validation_rules": {
    "code_length": {
      "max_length": 10000,
      "severity": "error"
    },
    "compatibility": {
      "required": true,
      "severity": "warning"
    }
  }
}
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/tech-analysis.yml
name: Technology Stack Analysis

on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: openhands/tech-analysis-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          config_file: .openhands.yml
```

### GitLab CI

```yaml
# .gitlab-ci.yml
tech-analysis:
  image: openhands/tech-analyzer:latest
  script:
    - openhands analyze
  artifacts:
    reports:
      json: tech-analysis.json
```

## Configuration

### .openhands.yml
```yaml
analysis:
  types:
    - language
    - framework
    - database
    - testing
  
  templates:
    - strict
    - security
    
  reporting:
    format: markdown
    include_suggestions: true
    include_resources: true
    
  ci:
    comment_on_pr: true
    fail_on_error: false
    create_report: true
```

## API Documentation

### Python API

```python
from openhands_dynamic_agent_factory import TechStackAnalyzer

class TechStackAnalyzer:
    """
    Analyze technology stacks and provide insights.
    
    Features:
    - Technology detection
    - Stack compatibility
    - Best practices
    - Learning resources
    """
    
    def process_text(
        self,
        text: str,
        context: str = "",
        tech_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> OperationResult[Dict[str, Any]]:
        """
        Process text to identify technology stack components.
        
        Args:
            text: Input text to analyze
            context: Optional context about the text
            tech_types: Optional list of technology types to look for
            categories: Optional list of categories to look for
            use_cache: Whether to use cached results
        """
        pass
        
    def suggest_stack(
        self,
        requirements: Dict[str, Any]
    ) -> OperationResult[Dict[str, Any]]:
        """
        Suggest a technology stack based on requirements.
        
        Args:
            requirements: Dictionary containing:
                - project_type: Type of project (web, mobile, etc.)
                - scale: Expected scale (small, medium, large)
                - team_expertise: List of technologies team is familiar with
                - constraints: Any technical constraints
        """
        pass
```

### JavaScript API

```javascript
const { TechStackAnalyzer } = require('openhands-dynamic-agent-factor');

class TechStackAnalyzer {
    /**
     * Analyze technology stacks and provide insights.
     * 
     * @param {Object} options Configuration options
     */
    constructor(options = {}) {
        // Initialize analyzer
    }
    
    /**
     * Process text to identify technology stack components.
     * 
     * @param {string} text Input text to analyze
     * @param {Object} options Analysis options
     * @returns {Promise<Object>} Analysis results
     */
    async analyze(text, options = {}) {
        // Analyze text
    }
    
    /**
     * Suggest a technology stack based on requirements.
     * 
     * @param {Object} requirements Stack requirements
     * @returns {Promise<Object>} Stack suggestions
     */
    async suggestStack(requirements) {
        // Generate suggestions
    }
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
