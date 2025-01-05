import { BaseError, OperationResult } from './utils';
export interface TechInfo {
    name: string;
    type: string;
    category: string;
    description: string;
    tags?: string[];
    github_url?: string;
    package_manager?: string;
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
export declare class TechAnalyzerError extends BaseError {
    constructor(message: string, error_type: string, details?: Record<string, any>, recovery_hint?: string);
}
export declare class TechStackAnalyzer {
    private tech_types;
    private categories;
    private tech_cache;
    private results_cache;
    private state_manager;
    private technologies;
    constructor(tech_types?: string[], categories?: string[]);
    private _initialize_technologies;
    process_text(text: string, context?: string, tech_types?: string[], categories?: string[], use_cache?: boolean): Promise<OperationResult<AnalysisResult>>;
    private _normalize_tech_name;
    private _calculate_confidence;
}
export {};
