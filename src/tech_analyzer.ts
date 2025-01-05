import { BaseError, ValidationError, Cache, StateManager, OperationResult } from './utils';

export interface TechInfo {
    name: string;
    type: string;  // language, framework, library, tool, etc.
    category: string;  // frontend, backend, database, testing, etc.
    description: string;
    tags?: string[];
    github_url?: string;
    package_manager?: string;  // npm, pip, gem, etc.
    package_name?: string;
    stars?: number;
    last_updated?: Date;
    validation_sources?: string[];
    discovery_context?: string;
    is_validated?: boolean;
    features?: string[];
    alternatives?: string[];
    documentation_url?: string;
    popularity_metrics?: Record<string, any>;
    compatibility?: Record<string, string[]>;
    version_info?: Record<string, any>;
    ecosystem?: Record<string, string[]>;
    use_cases?: string[];
    learning_resources?: Array<{
        type: string;
        title: string;
        url: string;
    }>;
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

export class TechAnalyzerError extends BaseError {
    constructor(
        message: string,
        error_type: string,
        details?: Record<string, any>,
        recovery_hint?: string
    ) {
        super(
            message,
            error_type,
            details,
            recovery_hint || "Check technology configuration and sources"
        );
    }
}

export class TechStackAnalyzer {
    private tech_cache: Cache<string, TechInfo>;
    private results_cache: Cache<string, AnalysisResult>;
    private state_manager: StateManager<Record<string, any>>;
    private technologies: Map<string, TechInfo>;

    constructor(
        private tech_types: string[] = [
            "language",
            "framework",
            "library",
            "database",
            "tool",
            "service",
            "platform"
        ],
        private categories: string[] = [
            "frontend",
            "backend",
            "database",
            "testing",
            "devops",
            "cloud",
            "mobile",
            "desktop"
        ]
    ) {
        this.tech_cache = new Cache<string, TechInfo>(3600);
        this.results_cache = new Cache<string, AnalysisResult>(3600);
        this.state_manager = new StateManager<Record<string, any>>("/tmp/tech_analyzer/state.json");
        this.technologies = new Map();
        this._initialize_technologies();
    }

    private _initialize_technologies(): void {
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

    public async process_text(
        text: string,
        context: string = "",
        tech_types?: string[],
        categories?: string[],
        use_cache: boolean = true
    ): Promise<OperationResult<AnalysisResult>> {
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
            const results: AnalysisResult = {
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
                const seen_techs = new Set<string>();
                for (const word of words) {
                    const normalized = this._normalize_tech_name(word);
                    const tech = this.technologies.get(normalized);

                    if (tech) {
                        // Apply filters
                        if (tech_types && !tech_types.includes(tech.type)) continue;
                        if (categories && !categories.includes(tech.category)) continue;

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

        } catch (error) {
            return {
                success: false,
                error: new TechAnalyzerError(
                    `Analysis failed: ${String(error)}`,
                    "AnalysisError",
                    { text: text?.slice(0, 100), error: String(error) }
                )
            };
        }
    }

    private _normalize_tech_name(name: string): string {
        return name.toLowerCase()
            .replace(/[^a-z0-9]+/g, '')
            .trim();
    }

    private _calculate_confidence(original: string, tech_name: string): number {
        let score = 0.7;  // Base score

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
