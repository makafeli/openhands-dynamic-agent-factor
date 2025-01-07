import { TRIGGER_MAP } from './trigger_map';
import { processText, normalizeText } from './utils';

export interface TechStackAnalyzerOptions {
  tech_types?: string[];
  categories?: string[];
  use_cache?: boolean;
  cache_duration?: number;
}

export interface TechStackAnalyzerConfig {
  tech_types: string[];
  categories: string[];
  cache_enabled: boolean;
  cache_duration: number;
}

export interface ProcessTextOptions {
  context?: string;
  tech_types?: string[];
  categories?: string[];
  use_cache?: boolean;
}

export interface Technology {
  category: string;
  type: string;
  matches: string[];
  confidence_score: number;
  name: string;
  description: string;
  popularity?: Record<string, any>;
  version_info?: Record<string, any>;
  ecosystem?: Record<string, string[]>;
  use_cases?: string[];
}

export class TechStackAnalyzer {
  private config: TechStackAnalyzerConfig;
  private cache: Map<string, { result: any; timestamp: number }>;

  constructor(options: TechStackAnalyzerOptions = {}) {
    this.config = {
      tech_types: options.tech_types || [
        'language',
        'framework',
        'library',
        'database',
        'tool',
        'service',
        'platform'
      ],
      categories: options.categories || [
        'frontend',
        'backend',
        'database',
        'testing',
        'devops',
        'cloud',
        'mobile',
        'desktop'
      ],
      cache_enabled: options.use_cache !== false,
      cache_duration: options.cache_duration || 3600000 // 1 hour
    };
    this.cache = new Map();
  }

  async process_text(
    text: string,
    context: string = '',
    tech_types?: string[],
    categories?: string[],
    use_cache: boolean = true
  ) {
    try {
      // Input validation
      if (!text || typeof text !== 'string') {
        return {
          success: false,
          error: {
            message: 'Invalid input text',
            error_type: 'ValidationError',
            recovery_hint: 'Provide a non-empty string as input'
          }
        };
      }

      // Cache check
      const cacheKey = `${text}:${context}:${tech_types}:${categories}`;
      if (use_cache && this.config.cache_enabled) {
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.config.cache_duration) {
          return {
            ...cached.result,
            metadata: { ...cached.result.metadata, cache_hit: true }
          };
        }
      }

      // Process text
      const normalizedText = normalizeText(text);
      const processedText = await processText(normalizedText);

      // Analyze technologies
      const identified_technologies = this.identifyTechnologies(
        processedText,
        tech_types || this.config.tech_types,
        categories || this.config.categories
      );

      // Analyze stack
      const stack_analysis = {
        completeness: this.checkStackCompleteness(identified_technologies),
        compatibility: this.checkCompatibility(identified_technologies),
        suggestions: this.generateSuggestions(identified_technologies)
      };

      const result = {
        success: true,
        data: {
          identified_technologies,
          tech_types: tech_types || this.config.tech_types,
          categories: categories || this.config.categories,
          timestamp: new Date().toISOString(),
          context,
          stack_analysis
        },
        metadata: {
          cache_hit: false,
          processing_time: Date.now()
        }
      };

      // Cache result
      if (use_cache && this.config.cache_enabled) {
        this.cache.set(cacheKey, {
          result,
          timestamp: Date.now()
        });
      }

      return result;
    } catch (error) {
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Unknown error occurred',
          error_type: 'ProcessingError',
          details: error instanceof Error ? { stack: error.stack } : undefined,
          recovery_hint: 'Try with different input or check the error details'
        }
      };
    }
  }

  private identifyTechnologies(
    text: string,
    tech_types: string[],
    categories: string[]
  ): Technology[] {
    const matches = text.match(TRIGGER_MAP.pattern) || [];
    return matches
      .map(match => {
        const tech = TRIGGER_MAP.getTechnology(match.toLowerCase());
        if (
          tech &&
          tech_types.includes(tech.type) &&
          categories.includes(tech.category)
        ) {
          return {
            ...tech,
            matches: [match],
            confidence_score: this.calculateConfidenceScore(match, text)
          } as Technology;
        }
        return null;
      })
      .filter((tech): tech is Technology => tech !== null);
  }

  private calculateConfidenceScore(match: string, text: string): number {
    // Simple confidence score calculation
    const frequency = (text.match(new RegExp(match, 'gi')) || []).length;
    const contextScore = frequency > 1 ? 0.2 : 0;
    const baseScore = 0.7;
    return Math.min(baseScore + contextScore, 1);
  }

  private checkStackCompleteness(techs: Technology[]) {
    const completeness: Record<string, boolean> = {
      frontend: false,
      backend: false,
      database: false
    };

    for (const tech of techs) {
      if (tech.category in completeness) {
        completeness[tech.category] = true;
      }
    }

    return completeness;
  }

  private checkCompatibility(_: Technology[]) {
    // Simplified compatibility check
    return {
      compatible: true,
      issues: []
    };
  }

  private generateSuggestions(techs: Technology[]) {
    const suggestions: string[] = [];
    const categories = new Set(techs.map(t => t.category));

    if (!categories.has('testing')) {
      suggestions.push('Consider adding testing frameworks to your stack');
    }

    if (!categories.has('devops')) {
      suggestions.push('Consider adding DevOps tools for better deployment workflow');
    }

    return suggestions;
  }
}
