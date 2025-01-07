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
export declare class TechStackAnalyzer {
    private config;
    private cache;
    constructor(options?: TechStackAnalyzerOptions);
    process_text(text: string, context?: string, tech_types?: string[], categories?: string[], use_cache?: boolean): Promise<any>;
    private identifyTechnologies;
    private calculateConfidenceScore;
    private analyzeStack;
    private checkStackCompleteness;
    private checkCompatibility;
    private generateSuggestions;
}
