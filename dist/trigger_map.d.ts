import { BaseError, OperationResult } from './utils';
export interface ValidationRule {
    name: string;
    description: string;
    validator: string;
    error_message: string;
    severity: 'error' | 'warning' | 'info';
    metadata?: Record<string, any>;
}
export interface TriggerInfo {
    class_name: string;
    description: string;
    llm_prompt_template: string;
    inputs?: string[];
    outputs?: string[];
    required_imports?: string[];
    validation_rules?: Record<string, ValidationRule>;
    metadata?: Record<string, any>;
    created_at: Date;
    last_updated: Date;
    version: string;
}
export declare class TriggerMapError extends BaseError {
    constructor(message: string, error_type: string, details?: Record<string, any>, recovery_hint?: string);
}
export declare class TriggerMapManager {
    private trigger_cache;
    private tech_cache;
    private state_manager;
    private tech_analyzer;
    private triggers;
    private readonly state_dir;
    constructor(state_dir?: string);
    private _load_state;
    private _convert_to_trigger_info;
    private _initialize_default_triggers;
    private _save_state;
    private _generate_tech_triggers;
    private _get_required_imports;
    private _get_validation_rules;
    private _get_prompt_template;
    get_trigger(key: string): Promise<OperationResult<TriggerInfo>>;
    add_trigger(key: string, trigger: TriggerInfo): Promise<OperationResult<boolean>>;
    update_trigger(key: string, trigger: TriggerInfo): Promise<OperationResult<boolean>>;
    remove_trigger(key: string): Promise<OperationResult<boolean>>;
    get all_triggers(): Map<string, TriggerInfo>;
}
export declare const trigger_manager: TriggerMapManager;
export declare const TRIGGER_MAP: Map<string, TriggerInfo>;
