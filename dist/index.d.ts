import { TechStackAnalyzer } from './tech_analyzer';
import { TRIGGER_MAP } from './trigger_map';
import * as utils from './utils';
export { TechStackAnalyzer, TRIGGER_MAP, utils };
export interface TechInfo {
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
export interface IdentifiedTechnology extends TechInfo {
    matches?: string[];
    context?: string;
    metadata?: Record<string, any>;
}
export interface AnalysisResult {
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
export interface BaseError {
    message: string;
    error_type: string;
    details?: Record<string, any>;
    recovery_hint?: string;
}
export interface OperationResult<T> {
    success: boolean;
    data?: T;
    error?: BaseError;
    metadata?: Record<string, any>;
    duration?: number;
}
export type { TechStackAnalyzerOptions, TechStackAnalyzerConfig, ProcessTextOptions } from './tech_analyzer';
export type { TriggerInfo, TriggerMapConfig, TriggerPattern, TriggerResult } from './trigger_map';
export default TechStackAnalyzer;
