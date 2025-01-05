# Quick Start Guide

Get up and running with Dynamic Agent quickly with this guide.

## Basic Setup

First, install the package:

```bash
npm install dynamic-agent
```

## Simple Example

Here's a basic example to get you started:

```typescript
import { TechStackAnalyzer } from 'dynamic-agent';

async function analyzeStack() {
    // Initialize the analyzer
    const analyzer = new TechStackAnalyzer();

    // Analyze some text containing technology information
    const result = await analyzer.process_text(`
        We're building a web application using:
        - React with TypeScript for the frontend
        - Node.js and Express for the backend
        - MongoDB for the database
        - Jest for testing
    `);

    if (result.success) {
        // Print identified technologies
        console.log('Identified Technologies:');
        result.data.identified_technologies.forEach(tech => {
            console.log(`- ${tech.name} (${tech.type}): ${tech.confidence_score}`);
        });
    }
}

analyzeStack().catch(console.error);
```

## Common Use Cases

### 1. Analyzing Project Dependencies

```typescript
import { TechStackAnalyzer } from 'dynamic-agent';

async function analyzeDependencies() {
    const analyzer = new TechStackAnalyzer();
    
    // Read package.json content
    const packageJson = `{
        "dependencies": {
            "react": "^18.0.0",
            "express": "^4.18.0",
            "mongodb": "^5.0.0"
        }
    }`;

    const result = await analyzer.process_text(packageJson);
    console.log(result.data.identified_technologies);
}
```

### 2. Filtering by Technology Type

```typescript
import { TechStackAnalyzer } from 'dynamic-agent';

async function analyzeFrameworks() {
    const analyzer = new TechStackAnalyzer();
    
    // Only look for frameworks
    const result = await analyzer.process_text(
        'Using React, Express, and Django',
        '',  // context
        ['framework']  // tech types filter
    );

    console.log('Frameworks found:', result.data.identified_technologies);
}
```

### 3. Using Cache for Performance

```typescript
import { TechStackAnalyzer } from 'dynamic-agent';

async function analyzeWithCache() {
    const analyzer = new TechStackAnalyzer();
    
    // First call will process and cache
    const result1 = await analyzer.process_text('React and Node.js stack');
    console.log('Cache hit:', result1.metadata?.cache_hit);  // false

    // Second call will use cache
    const result2 = await analyzer.process_text('React and Node.js stack');
    console.log('Cache hit:', result2.metadata?.cache_hit);  // true
}
```

## Error Handling

```typescript
import { TechStackAnalyzer } from 'dynamic-agent';

async function handleErrors() {
    const analyzer = new TechStackAnalyzer();
    
    try {
        const result = await analyzer.process_text(null as any);
        
        if (!result.success) {
            console.error('Analysis failed:', result.error?.message);
            console.log('Error type:', result.error?.error_type);
            console.log('Recovery hint:', result.error?.recovery_hint);
        }
    } catch (error) {
        console.error('Unexpected error:', error);
    }
}
```

## Next Steps

- Learn about [Advanced Features](../usage/advanced-features.md)
- Check the [API Reference](../api/tech-analyzer.md)
- See [Basic Usage](../usage/basic-usage.md) for more examples
- Read the [Contributing Guide](../contributing.md) to get involved

## Tips and Best Practices

1. **Initialize Once**: Create a single analyzer instance and reuse it
2. **Use Caching**: Enable caching for repeated analyses
3. **Handle Errors**: Always check the `success` flag and handle errors
4. **Filter Results**: Use tech types and categories to get relevant results
5. **Check Confidence**: Use confidence scores to validate matches

## Common Pitfalls

1. **Missing Error Handling**: Always handle potential errors
2. **Ignoring Cache**: Don't create new analyzer instances unnecessarily
3. **Invalid Filters**: Verify tech types and categories exist
4. **Large Inputs**: Break down large texts into manageable chunks
5. **Async/Await**: Remember to use proper async/await patterns
