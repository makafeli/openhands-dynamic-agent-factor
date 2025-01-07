export interface TechnologyInfo {
    name: string;
    type: string;
    category: string;
    description: string;
    popularity?: Record<string, any>;
    version_info?: Record<string, any>;
    ecosystem?: Record<string, string[]>;
    use_cases?: string[];
}
export interface TriggerInfo {
    pattern: string;
    type: string;
    category: string;
}
export interface TriggerMapConfig {
    patterns: TriggerInfo[];
    caseSensitive?: boolean;
}
export interface TriggerPattern {
    pattern: RegExp;
    info: TriggerInfo;
}
export interface TriggerResult {
    matches: string[];
    info: TriggerInfo;
}
declare class TriggerMap {
    private technologies;
    private patternString;
    constructor();
    private initializeTechnologies;
    private addTechnology;
    private buildPatternString;
    get pattern(): RegExp;
    getTechnology(name: string): TechnologyInfo | undefined;
    getAllTechnologies(): TechnologyInfo[];
}
export declare const TRIGGER_MAP: TriggerMap;
export {};
//# sourceMappingURL=trigger_map.d.ts.map