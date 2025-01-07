# OpenHands Dynamic Agent Factory

A powerful system for analyzing and generating technology-specific agents with comprehensive analysis capabilities.

## Features

### 1. Technology Stack Analysis
- Comprehensive analysis of technology stacks
- Support for multiple technology types:
  * Programming Languages (Python, JavaScript, etc.)
  * Frontend Frameworks (React, Vue, etc.)
  * Backend Frameworks (Django, Express, etc.)
  * Databases (PostgreSQL, MongoDB, etc.)
  * Testing Tools (Jest, PyTest, etc.)
  * DevOps Tools (Docker, Kubernetes, etc.)

### 2. Analysis Capabilities
- Stack compatibility checking
- Technology detection
- Confidence scoring
- Stack completeness analysis
- Best practices recommendations
- Technology suggestions

### 3. Web Dashboard
- Interactive analysis interface
- Real-time visualization
- Analysis history tracking
- Template management
- Statistical insights
- Framework detection visualization

### 4. CI/CD Integration
- GitHub Actions integration
- GitLab CI integration
- Automated analysis in PRs
- Custom reporting
- Status checks
- PR comments with analysis results

## Installation

### NPM Package
```bash
npm install dynamic-agent
```

### Python Package
```bash
pip install openhands-dynamic-agent-factor
```

## Usage

### JavaScript/TypeScript API

```typescript
import { TechStackAnalyzer } from 'dynamic-agent';

// Initialize analyzer
const analyzer = new TechStackAnalyzer();

// Analyze tech stack
const result = await analyzer.process_text(
    "Building a web app with React frontend, Node.js backend, and MongoDB database"
);

// Access results
if (result.success) {
    const { identified_technologies, stack_analysis } = result.data;
    console.log('Technologies:', identified_technologies);
    console.log('Stack Analysis:', stack_analysis);
}
```

### Python API

```python
from openhands_dynamic_agent_factory import TechStackAnalyzer

# Initialize analyzer
analyzer = TechStackAnalyzer()

# Analyze tech stack
result = analyzer.process_text(
    "Building a web app with Python/Django backend, "
    "React frontend, and PostgreSQL database"
)

# Access results
if result.success:
    identified_technologies = result.data.get('identified_technologies')
    stack_analysis = result.data.get('stack_analysis')
    print('Technologies:', identified_technologies)
    print('Stack Analysis:', stack_analysis)
```

### Command Line Interface

The package includes a CLI for interactive analysis:

```bash
# Basic analysis
python -m openhands_dynamic_agent_factory.core.cli analyze "Building with React and Django"

# Analysis with template
python -m openhands_dynamic_agent_factory.core.cli analyze --template strict "Using Tailwind CSS"

# Launch dashboard
python -m openhands_dynamic_agent_factory.core.cli dashboard

# Create custom template
python -m openhands_dynamic_agent_factory.core.cli template create custom --description "Custom analysis"
```

### Web Dashboard

Launch the interactive web dashboard:

```python
from openhands_dynamic_agent_factory.core.dashboard import launch_dashboard

# Launch dashboard on default port (8000)
launch_dashboard()

# Launch on custom port
launch_dashboard(port=8080)
```

The dashboard provides:
- Interactive analysis interface
- Real-time visualization
- Analysis history
- Template management
- Statistical insights

### CI/CD Integration

#### GitHub Actions

```yaml
# .github/workflows/framework-analysis.yml
name: Framework Analysis

on:
  pull_request:
    paths:
      - '**/*.html'
      - '**/*.css'
      - '**/*.js'
      - '**/*.jsx'
      - '**/*.ts'
      - '**/*.tsx'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: pip install openhands-dynamic-agent-factor
      - name: Analyze frameworks
        run: python -m openhands_dynamic_agent_factory.core.ci_integration analyze
```

#### GitLab CI

```yaml
# .gitlab-ci.yml
framework-analysis:
  image: python:3
  script:
    - pip install openhands-dynamic-agent-factor
    - python -m openhands_dynamic_agent_factory.core.ci_integration analyze
  artifacts:
    reports:
      json: framework-analysis.json
```

## Configuration

### Analysis Templates

Create custom analysis templates:

```json
{
  "name": "strict",
  "description": "Strict analysis mode",
  "use_cache": true,
  "fallback_enabled": true,
  "confidence_threshold": 0.7,
  "custom_patterns": []
}
```

### CI Configuration

```json
{
  "include_patterns": ["**/*.{html,css,js,jsx,ts,tsx}"],
  "exclude_patterns": ["**/node_modules/**", "**/vendor/**"],
  "min_confidence": 0.7,
  "fail_on_detection": false,
  "comment_on_pr": true,
  "create_report": true,
  "report_path": "framework-analysis.json"
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
