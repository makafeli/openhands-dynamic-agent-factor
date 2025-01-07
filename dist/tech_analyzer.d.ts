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
export declare class TechStackAnalyzer {
    private config;
    private cache;
    constructor(options?: TechStackAnalyzerOptions);
    process_text(text: string, context?: string, tech_types?: string[], categories?: string[], use_cache?: boolean): Promise<any>;
    private identifyTechnologies;
    private calculateConfidenceScore;
    private checkStackCompleteness;
    private checkCompatibility;
    private generateSuggestions;
}
//# sourceMappingURL=tech_analyzer.d.ts.map