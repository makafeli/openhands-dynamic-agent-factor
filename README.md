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

## API Documentation

### TechStackAnalyzer Class

The main class for analyzing technology stacks. It provides methods for:
- Technology detection in text
- Stack compatibility analysis
- Completeness checking
- Suggestions for improvements

```typescript
interface Technology {
    name: string;
    type: string;
    category: string;
    description: string;
    confidence_score: number;
    matches: string[];
}

interface AnalysisResult {
    success: boolean;
    data?: {
        identified_technologies: Technology[];
        tech_types: string[];
        categories: string[];
        timestamp: string;
        context: string;
        stack_analysis: {
            completeness: Record<string, boolean>;
            compatibility: {
                compatible: boolean;
                issues: string[];
            };
            suggestions: string[];
        };
    };
    error?: {
        message: string;
        error_type: string;
        recovery_hint: string;
    };
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
