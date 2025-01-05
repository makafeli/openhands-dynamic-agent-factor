# Installation Guide

This guide will help you install and set up Dynamic Agent in your project.

## Prerequisites

- Node.js >= 18.x
- npm >= 7.x (or yarn/pnpm)
- TypeScript >= 4.x (for TypeScript projects)

## Installation Methods

### NPM

```bash
npm install dynamic-agent
```

### Yarn

```bash
yarn add dynamic-agent
```

### PNPM

```bash
pnpm add dynamic-agent
```

## TypeScript Configuration

If you're using TypeScript, ensure your `tsconfig.json` includes the following settings:

```json
{
  "compilerOptions": {
    "target": "es2019",
    "module": "commonjs",
    "lib": ["es2019", "dom"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true
  }
}
```

## Verifying Installation

You can verify your installation by creating a simple test file:

```typescript
import { TechStackAnalyzer } from 'dynamic-agent';

async function testInstallation() {
    const analyzer = new TechStackAnalyzer();
    const result = await analyzer.process_text('Testing Dynamic Agent with TypeScript');
    
    if (result.success) {
        console.log('Installation successful!');
        console.log('Identified technologies:', result.data.identified_technologies);
    } else {
        console.error('Installation test failed:', result.error);
    }
}

testInstallation().catch(console.error);
```

## Environment Setup

No special environment variables are required for basic usage. However, for optimal performance, you might want to configure:

- Cache directory location
- State persistence path
- Custom technology definitions

## Next Steps

- Check out the [Quick Start Guide](quick-start.md) to begin using Dynamic Agent
- Read about [Basic Usage](../usage/basic-usage.md) for common use cases
- Explore [Advanced Features](../usage/advanced-features.md) for more capabilities
- Review the [API Reference](../api/tech-analyzer.md) for detailed documentation

## Troubleshooting

### Common Issues

1. **TypeScript Compilation Errors**
   - Ensure your TypeScript version is >= 4.x
   - Check your `tsconfig.json` settings
   - Make sure all dependencies are installed

2. **Import Errors**
   - Verify the package is listed in your `package.json`
   - Try clearing your node_modules cache
   - Check for any path alias configurations

3. **Runtime Errors**
   - Ensure Node.js version is >= 18.x
   - Check for any conflicting dependencies
   - Verify your import statements

### Getting Help

If you encounter any issues:

1. Check the [GitHub Issues](https://github.com/makafeli/openhands-dynamic-agent-factor/issues) for known problems
2. Search existing discussions for solutions
3. Create a new issue if your problem hasn't been reported

## Additional Resources

- [GitHub Repository](https://github.com/makafeli/openhands-dynamic-agent-factor)
- [NPM Package](https://www.npmjs.com/package/dynamic-agent)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
