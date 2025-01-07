export interface TriggerInfo {
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
export interface TriggerMapConfig {
    caseSensitive?: boolean;
    maxPatternLength?: number;
}
export interface TriggerPattern {
    pattern: string;
    flags?: string;
    score?: number;
}
export interface TriggerResult {
    match: string;
    info: TriggerInfo;
    score: number;
}
export declare class TriggerMap {
    private patterns;
    technologies: Map<string, TriggerInfo>;
    constructor();
    private initializeTechnologies;
    private addTechnology;
    get pattern(): RegExp;
    getTechnology(key: string): TriggerInfo | undefined;
    getAllTechnologies(): Map<string, TriggerInfo>;
}
export declare const TRIGGER_MAP: TriggerMap;
