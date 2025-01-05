# TechStackAnalyzer API Reference

The `TechStackAnalyzer` class is the main entry point for analyzing technology stacks and identifying technologies in text.

## Class: TechStackAnalyzer

### Constructor

```typescript
constructor(
    tech_types?: string[] = [
        "language",
        "framework",
        "library",
        "database",
        "tool",
        "service",
        "platform"
    ],
    categories?: string[] = [
        "frontend",
        "backend",
        "database",
        "testing",
        "devops",
        "cloud",
        "mobile",
        "desktop"
    ]
)
```

Creates a new instance of the TechStackAnalyzer.

#### Parameters

- `tech_types` (optional): Array of technology types to recognize
- `categories` (optional): Array of technology categories to recognize

### Methods

#### process_text

```typescript
async process_text(
    text: string,
    context: string = "",
    tech_types?: string[],
    categories?: string[],
    use_cache: boolean = true
): Promise<OperationResult<AnalysisResult>>
```

Analyzes text to identify technologies and their relationships.

##### Parameters

- `text`: The text to analyze
- `context` (optional): Additional context for the analysis
- `tech_types` (optional): Filter results by specific technology types
- `categories` (optional): Filter results by specific categories
- `use_cache` (optional): Whether to use cached results if available

##### Returns

Promise resolving to an `OperationResult<AnalysisResult>` containing:

```typescript
interface OperationResult<T> {
    success: boolean;
    data?: T;
    error?: BaseError;
    metadata?: Record<string, any>;
    duration?: number;
}

interface AnalysisResult {
    identified_technologies: IdentifiedTechnology[];
    tech_types: string[];
    categories: string[];
    timestamp: string;
    context: string;
    stack_analysis: {
        completeness: Record<string, boolean>;
        compatibility: Record<string, any>;
        suggestions: string[];
    };
}

interface IdentifiedTechnology {
    name: string;
    type: string;
    category: string;
    description: string;
    confidence_score: number;
    popularity?: Record<string, any>;
    version_info?: Record<string, any>;
    ecosystem?: Record<string, string[]>;
    use_cases?: string[];
}
```

##### Example

```typescript
const analyzer = new TechStackAnalyzer();

const result = await analyzer.process_text(`
    Our stack includes:
    - React for frontend
    - Node.js for backend
    - MongoDB for database
`);

if (result.success) {
    console.log('Technologies found:', result.data.identified_technologies);
    console.log('Analysis timestamp:', result.data.timestamp);
    console.log('Cache status:', result.metadata?.cache_hit);
} else {
    console.error('Analysis failed:', result.error?.message);
}
```

### Error Handling

The analyzer uses custom error types for different failure scenarios:

```typescript
class TechAnalyzerError extends BaseError {
    constructor(
        message: string,
        error_type: string,
        details?: Record<string, any>,
        recovery_hint?: string
    )
}
```

Common error types:

- `AnalysisError`: General analysis failures
- `ValidationError`: Invalid input or configuration
- `StateError`: State management issues

### Caching

The analyzer includes built-in caching:

- Results are cached by default (controlled by `use_cache` parameter)
- Cache entries expire after 1 hour
- Cache is maintained per analyzer instance
- Cache hits are indicated in the result metadata

### Best Practices

1. **Instance Reuse**
   ```typescript
   // Good: Reuse analyzer instance
   const analyzer = new TechStackAnalyzer();
   const result1 = await analyzer.process_text(text1);
   const result2 = await analyzer.process_text(text2);

   // Bad: Creating new instances unnecessarily
   const result1 = await new TechStackAnalyzer().process_text(text1);
   const result2 = await new TechStackAnalyzer().process_text(text2);
   ```

2. **Error Handling**
   ```typescript
   // Good: Proper error handling
   const result = await analyzer.process_text(text);
   if (!result.success) {
       console.error(result.error?.message);
       console.log('Recovery hint:', result.error?.recovery_hint);
   }
   ```

3. **Type Safety**
   ```typescript
   // Good: Use type assertions properly
   if (result.success && result.data) {
       const techs = result.data.identified_technologies;
       techs.forEach(tech => console.log(tech.name));
   }
   ```

### Performance Considerations

- Use caching for repeated analyses
- Reuse analyzer instances
- Keep input text concise and relevant
- Use filters (tech_types, categories) when possible
- Consider breaking large texts into smaller chunks

### Thread Safety

The analyzer is designed to be thread-safe:

- State is maintained per instance
- Cache is thread-safe
- Async operations are properly handled
- No shared mutable state between instances
