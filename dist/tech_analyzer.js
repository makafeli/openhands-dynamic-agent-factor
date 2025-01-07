"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TechStackAnalyzer = void 0;
const trigger_map_1 = require("./trigger_map");
const utils_1 = require("./utils");
class TechStackAnalyzer {
    constructor(options = {}) {
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
    async process_text(text, context = '', tech_types, categories, use_cache = true) {
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
            const normalizedText = (0, utils_1.normalizeText)(text);
            const processedText = await (0, utils_1.processText)(normalizedText);
            // Analyze technologies
            const identified_technologies = this.identifyTechnologies(processedText, tech_types || this.config.tech_types, categories || this.config.categories);
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
        }
        catch (error) {
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
    identifyTechnologies(text, tech_types, categories) {
        const matches = text.match(trigger_map_1.TRIGGER_MAP.pattern) || [];
        return matches
            .map(match => {
            const tech = trigger_map_1.TRIGGER_MAP.getTechnology(match.toLowerCase());
            if (tech &&
                tech_types.includes(tech.type) &&
                categories.includes(tech.category)) {
                return {
                    ...tech,
                    matches: [match],
                    confidence_score: this.calculateConfidenceScore(match, text)
                };
            }
            return null;
        })
            .filter((tech) => tech !== null);
    }
    calculateConfidenceScore(match, text) {
        // Simple confidence score calculation
        const frequency = (text.match(new RegExp(match, 'gi')) || []).length;
        const contextScore = frequency > 1 ? 0.2 : 0;
        const baseScore = 0.7;
        return Math.min(baseScore + contextScore, 1);
    }
    checkStackCompleteness(techs) {
        const completeness = {
            frontend: false,
            backend: false,
            database: false
        };
        // First, check for frameworks and tools
        for (const tech of techs) {
            if (tech.category in completeness) {
                if (tech.type === 'framework' || tech.type === 'database') {
                    completeness[tech.category] = true;
                }
            }
        }
        // Then, check for languages if no framework was found
        for (const tech of techs) {
            if (tech.category in completeness && !completeness[tech.category]) {
                if (tech.type === 'language') {
                    completeness[tech.category] = true;
                }
            }
        }
        return completeness;
    }
    checkCompatibility(_) {
        // Simplified compatibility check
        return {
            compatible: true,
            issues: []
        };
    }
    generateSuggestions(techs) {
        const suggestions = [];
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
exports.TechStackAnalyzer = TechStackAnalyzer;
//# sourceMappingURL=tech_analyzer.js.map