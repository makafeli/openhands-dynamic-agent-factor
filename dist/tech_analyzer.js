"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TechStackAnalyzer = exports.TechAnalyzerError = void 0;
const utils_1 = require("./utils");
class TechAnalyzerError extends utils_1.BaseError {
    constructor(message, error_type, details, recovery_hint) {
        super(message, error_type, details, recovery_hint || "Check technology configuration and sources");
    }
}
exports.TechAnalyzerError = TechAnalyzerError;
class TechStackAnalyzer {
    constructor(tech_types = [
        "language",
        "framework",
        "library",
        "database",
        "tool",
        "service",
        "platform"
    ], categories = [
        "frontend",
        "backend",
        "database",
        "testing",
        "devops",
        "cloud",
        "mobile",
        "desktop"
    ]) {
        this.tech_types = tech_types;
        this.categories = categories;
        this.tech_cache = new utils_1.Cache(3600);
        this.results_cache = new utils_1.Cache(3600);
        this.state_manager = new utils_1.StateManager("/tmp/tech_analyzer/state.json");
        this.technologies = new Map();
        this._initialize_technologies();
    }
    _initialize_technologies() {
        // Add some default technologies for testing
        this.technologies.set('python', {
            name: 'python',
            type: 'language',
            category: 'backend',
            description: 'Python programming language'
        });
        this.technologies.set('react', {
            name: 'react',
            type: 'framework',
            category: 'frontend',
            description: 'React.js framework'
        });
        this.technologies.set('mongodb', {
            name: 'mongodb',
            type: 'database',
            category: 'database',
            description: 'MongoDB database'
        });
        this.technologies.set('typescript', {
            name: 'typescript',
            type: 'language',
            category: 'frontend',
            description: 'TypeScript programming language'
        });
    }
    async process_text(text, context = "", tech_types, categories, use_cache = true) {
        try {
            if (text === null || text === undefined) {
                throw new Error("Input text cannot be null or undefined");
            }
            // Check cache
            const cache_key = `${text}:${context}:${tech_types}:${categories}`;
            if (use_cache) {
                const cached = this.results_cache.get(cache_key);
                if (cached) {
                    return {
                        success: true,
                        data: cached,
                        metadata: { cache_hit: true }
                    };
                }
            }
            // Initialize results
            const results = {
                identified_technologies: [],
                tech_types: tech_types || this.tech_types,
                categories: categories || this.categories,
                timestamp: new Date().toISOString(),
                context: context,
                stack_analysis: {
                    completeness: {},
                    compatibility: {},
                    suggestions: []
                }
            };
            // Process text
            if (text.trim()) {
                // Split text into words and clean them
                const words = text.split(/[\s,.-]+/)
                    .map(word => word.toLowerCase().trim())
                    .filter(word => word.length > 0);
                // Process each word
                const seen_techs = new Set();
                for (const word of words) {
                    const normalized = this._normalize_tech_name(word);
                    const tech = this.technologies.get(normalized);
                    if (tech) {
                        // Apply filters
                        if (tech_types && !tech_types.includes(tech.type))
                            continue;
                        if (categories && !categories.includes(tech.category))
                            continue;
                        if (!seen_techs.has(normalized)) {
                            seen_techs.add(normalized);
                            results.identified_technologies.push({
                                name: tech.name,
                                type: tech.type,
                                category: tech.category,
                                description: tech.description,
                                confidence_score: this._calculate_confidence(word, tech.name),
                                popularity: tech.popularity_metrics,
                                version_info: tech.version_info,
                                ecosystem: tech.ecosystem,
                                use_cases: tech.use_cases
                            });
                        }
                    }
                }
            }
            // Cache results
            if (use_cache) {
                this.results_cache.set(cache_key, results);
            }
            return {
                success: true,
                data: results,
                metadata: {
                    cache_hit: false,
                    tech_count: results.identified_technologies.length
                }
            };
        }
        catch (error) {
            return {
                success: false,
                error: new TechAnalyzerError(`Analysis failed: ${String(error)}`, "AnalysisError", { text: text === null || text === void 0 ? void 0 : text.slice(0, 100), error: String(error) })
            };
        }
    }
    _normalize_tech_name(name) {
        return name.toLowerCase()
            .replace(/[^a-z0-9]+/g, '')
            .trim();
    }
    _calculate_confidence(original, tech_name) {
        let score = 0.7; // Base score
        // Exact match bonus (case-insensitive)
        if (original.toLowerCase() === tech_name.toLowerCase()) {
            score += 0.3;
        }
        // Partial match bonus
        else if (tech_name.toLowerCase().includes(original.toLowerCase()) ||
            original.toLowerCase().includes(tech_name.toLowerCase())) {
            score += 0.1;
        }
        // Known technology bonus
        const normalized = this._normalize_tech_name(original);
        if (this.technologies.has(normalized)) {
            score += 0.2;
        }
        return Math.min(score, 1.0);
    }
}
exports.TechStackAnalyzer = TechStackAnalyzer;
