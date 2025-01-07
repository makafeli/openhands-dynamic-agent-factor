import { TechStackAnalyzer, Technology } from './tech_analyzer';
import { TechnologyInfo, TriggerInfo, TriggerMapConfig, TriggerPattern, TriggerResult } from './trigger_map';

export {
    TechStackAnalyzer,
    Technology,
    TechnologyInfo,
    TriggerInfo,
    TriggerMapConfig,
    TriggerPattern,
    TriggerResult
};

// Create and export a default instance
export const analyzer = new TechStackAnalyzer();
