import { BaseError, ValidationError, Cache, StateManager, OperationResult } from './utils';
import { TechInfo, TechStackAnalyzer } from './tech_analyzer';

export interface ValidationRule {
    name: string;
    description: string;
    validator: string;  // Python expression for validation
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

export class TriggerMapError extends BaseError {
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
            recovery_hint || "Check trigger configuration and dependencies"
        );
    }
}

export class TriggerMapManager {
    private trigger_cache: Cache<string, TriggerInfo>;
    private tech_cache: Cache<string, Record<string, any>>;
    private state_manager: StateManager<Record<string, any>>;
    private tech_analyzer: TechStackAnalyzer;
    private triggers: Map<string, TriggerInfo>;
    private readonly state_dir: string;

    constructor(state_dir?: string) {
        this.state_dir = state_dir || "/tmp/dynamic_agent_factory";
        this.state_manager = new StateManager<Record<string, any>>(
            `${this.state_dir}/trigger_map_state.json`
        );
        
        // Initialize caches
        this.trigger_cache = new Cache<string, TriggerInfo>(3600);
        this.tech_cache = new Cache<string, Record<string, any>>(1800);
        
        // Initialize tech analyzer
        this.tech_analyzer = new TechStackAnalyzer();
        
        // Initialize triggers map
        this.triggers = new Map();
        
        // Load initial state
        this._load_state();
    }

    private async _load_state(): Promise<void> {
        const result = await this.state_manager.load_state();
        if (result.success && result.data) {
            const triggers = result.data.triggers || {};
            for (const [key, value] of Object.entries(triggers)) {
                this.triggers.set(key, this._convert_to_trigger_info(value));
            }
        } else {
            console.warn("Failed to load state, using defaults");
            this.triggers = new Map();
            await this._initialize_default_triggers();
        }
    }

    private _convert_to_trigger_info(data: any): TriggerInfo {
        return {
            ...data,
            created_at: new Date(data.created_at),
            last_updated: new Date(data.last_updated)
        };
    }

    private async _initialize_default_triggers(): Promise<void> {
        // Add base triggers
        this.triggers.set("python", {
            class_name: "PythonAnalyzer",
            description: "Advanced Python code analyzer",
            inputs: ["code_snippet", "analysis_type"],
            outputs: ["analysis_report", "suggestions", "complexity_score"],
            required_imports: ["ast", "pylint"],
            validation_rules: {
                code_length: {
                    name: "Maximum Code Length",
                    description: "Validates code length",
                    validator: "len(data.get('code_snippet', '')) <= 10000",
                    error_message: "Code exceeds maximum length of 10000 characters",
                    severity: "error"
                },
                analysis_type: {
                    name: "Analysis Type",
                    description: "Validates analysis type",
                    validator: "data.get('analysis_type') in ['style', 'security', 'performance']",
                    error_message: "Invalid analysis type",
                    severity: "error"
                }
            },
            llm_prompt_template: `
                Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes Python code.
                The agent should:
                1. Use AST for code parsing
                2. Check for common anti-patterns
                3. Analyze code complexity
                4. Suggest improvements
                5. Handle errors gracefully

                Requirements:
                - Subclass MicroAgent
                - Accept 'code_snippet' and 'analysis_type' inputs
                - Return dict with 'analysis_report', 'suggestions', and 'complexity_score'
                - Include proper error handling
                - Follow PEP 8
                - Use type hints
            `,
            created_at: new Date(),
            last_updated: new Date(),
            version: "1.0.1"
        });

        // Add dynamic triggers from tech analyzer
        const tech_triggers = await this._generate_tech_triggers();
        for (const [key, trigger] of Object.entries(tech_triggers)) {
            this.triggers.set(key, trigger);
        }

        await this._save_state();
    }

    private async _save_state(): Promise<void> {
        const state = {
            triggers: Object.fromEntries(this.triggers.entries()),
            metadata: {
                last_updated: new Date().toISOString(),
                version: "1.0.1"
            }
        };
        await this.state_manager.save_state(state);
    }

    private async _generate_tech_triggers(): Promise<Record<string, TriggerInfo>> {
        const triggers: Record<string, TriggerInfo> = {};
        const result = await this.tech_analyzer.process_text("");
        if (!result.success || !result.data) return triggers;

        const technologies = result.data.identified_technologies;
        for (const tech of technologies) {
            const name = tech.name;
            const name_normalized = name.toLowerCase().replace(/\s+/g, '_');
            const class_name = `${name_normalized.charAt(0).toUpperCase()}${name_normalized.slice(1)}Analyzer`;

            triggers[name.toLowerCase()] = {
                class_name,
                description: `Analyzer for ${name} (${tech.type})`,
                inputs: ["code_snippet", "analysis_type"],
                outputs: ["analysis_report", "suggestions", "compatibility_check"],
                required_imports: this._get_required_imports(tech as TechInfo),
                validation_rules: this._get_validation_rules(tech as TechInfo),
                metadata: tech,
                llm_prompt_template: this._get_prompt_template(tech as TechInfo),
                created_at: new Date(),
                last_updated: new Date(),
                version: "1.0.1"
            };
        }

        return triggers;
    }

    private _get_required_imports(tech: TechInfo): string[] {
        const base_imports = ["typing"];
        
        if (tech.type === "language") {
            if (tech.name === "python") {
                return [...base_imports, "ast", "pylint"];
            } else if (tech.name === "javascript") {
                return [...base_imports, "esprima", "eslint"];
            }
        } else if (tech.type === "framework") {
            if (tech.category.includes("frontend")) {
                return [...base_imports, "esprima", "eslint"];
            } else if (tech.category.includes("backend")) {
                return [...base_imports, "ast", "pylint"];
            }
        }
        
        return base_imports;
    }

    private _get_validation_rules(tech: TechInfo): Record<string, ValidationRule> {
        const rules: Record<string, ValidationRule> = {
            code_length: {
                name: "Code Length",
                description: "Validates code length",
                validator: "len(data.get('code_snippet', '')) <= 10000",
                error_message: "Code exceeds maximum length",
                severity: "error"
            }
        };

        if (tech.type === "language") {
            rules.syntax = {
                name: "Syntax Check",
                description: "Validates basic syntax",
                validator: "'syntax_error' not in data.get('code_snippet', '').lower()",
                error_message: "Code contains syntax errors",
                severity: "error"
            };
        } else if (tech.type === "framework") {
            rules.framework_version = {
                name: "Framework Version",
                description: "Validates framework version",
                validator: `data.get('version') in ${JSON.stringify(tech.version_info?.supported || ['*'])}`,
                error_message: "Unsupported framework version",
                severity: "error"
            };
        }

        return rules;
    }

    private _get_prompt_template(tech: TechInfo): string {
        return `
            Generate a Python OpenHands MicroAgent class named '{class_name}' that analyzes ${tech.name} code.
            
            Technology Type: ${tech.type}
            Category: ${tech.category}
            
            The agent should:
            1. Parse and validate ${tech.name} specific syntax
            2. Check for ${tech.type}-specific best practices
            3. Identify potential compatibility issues
            4. Suggest optimizations
            5. Validate usage patterns
            
            Features to analyze:
            ${(tech.features || []).map(f => `- ${f}`).join('\n')}
            
            Use cases to consider:
            ${(tech.use_cases || []).map(c => `- ${c}`).join('\n')}
            
            Requirements:
            - Subclass MicroAgent
            - Accept 'code_snippet' and 'analysis_type' inputs
            - Return dict with 'analysis_report', 'suggestions', and 'compatibility_check'
            - Include ${tech.name}-specific validations
            - Handle ${tech.type}-specific patterns
            - Follow ${tech.name} best practices
        `;
    }

    public async get_trigger(key: string): Promise<OperationResult<TriggerInfo>> {
        // Check cache
        const cached = this.trigger_cache.get(key);
        if (cached) {
            return {
                success: true,
                data: cached,
                metadata: { cache_hit: true }
            };
        }

        // Check static triggers
        if (this.triggers.has(key)) {
            const trigger = this.triggers.get(key)!;
            this.trigger_cache.set(key, trigger);
            return {
                success: true,
                data: trigger,
                metadata: { cache_hit: false }
            };
        }

        // Check dynamic triggers
        const tech_triggers = await this._generate_tech_triggers();
        if (key in tech_triggers) {
            const trigger = tech_triggers[key];
            this.trigger_cache.set(key, trigger);
            return {
                success: true,
                data: trigger,
                metadata: { cache_hit: false, source: "tech_analyzer" }
            };
        }

        return {
            success: false,
            error: new TriggerMapError(
                `No trigger found for key: ${key}`,
                "TriggerNotFound"
            )
        };
    }

    public async add_trigger(key: string, trigger: TriggerInfo): Promise<OperationResult<boolean>> {
        if (this.triggers.has(key)) {
            return {
                success: false,
                error: new TriggerMapError(
                    `Trigger already exists: ${key}`,
                    "DuplicateTrigger"
                )
            };
        }

        this.triggers.set(key, trigger);
        this.trigger_cache.set(key, trigger);
        await this._save_state();

        return { success: true, data: true };
    }

    public async update_trigger(key: string, trigger: TriggerInfo): Promise<OperationResult<boolean>> {
        if (!this.triggers.has(key)) {
            return {
                success: false,
                error: new TriggerMapError(
                    `Trigger not found: ${key}`,
                    "TriggerNotFound"
                )
            };
        }

        this.triggers.set(key, trigger);
        this.trigger_cache.set(key, trigger);
        await this._save_state();

        return { success: true, data: true };
    }

    public async remove_trigger(key: string): Promise<OperationResult<boolean>> {
        if (!this.triggers.has(key)) {
            return {
                success: false,
                error: new TriggerMapError(
                    `Trigger not found: ${key}`,
                    "TriggerNotFound"
                )
            };
        }

        this.triggers.delete(key);
        this.trigger_cache.clear();  // Clear cache on removal
        await this._save_state();

        return { success: true, data: true };
    }

    public get all_triggers(): Map<string, TriggerInfo> {
        return new Map(this.triggers);
    }
}

// Initialize the manager
export const trigger_manager = new TriggerMapManager();

// Export the TRIGGER_MAP for backward compatibility
export const TRIGGER_MAP = trigger_manager.all_triggers;
