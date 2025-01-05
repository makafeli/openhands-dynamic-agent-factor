"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TRIGGER_MAP = exports.trigger_manager = exports.TriggerMapManager = exports.TriggerMapError = void 0;
const utils_1 = require("./utils");
const tech_analyzer_1 = require("./tech_analyzer");
class TriggerMapError extends utils_1.BaseError {
    constructor(message, error_type, details, recovery_hint) {
        super(message, error_type, details, recovery_hint || "Check trigger configuration and dependencies");
    }
}
exports.TriggerMapError = TriggerMapError;
class TriggerMapManager {
    constructor(state_dir) {
        this.state_dir = state_dir || "/tmp/dynamic_agent_factory";
        this.state_manager = new utils_1.StateManager(`${this.state_dir}/trigger_map_state.json`);
        // Initialize caches
        this.trigger_cache = new utils_1.Cache(3600);
        this.tech_cache = new utils_1.Cache(1800);
        // Initialize tech analyzer
        this.tech_analyzer = new tech_analyzer_1.TechStackAnalyzer();
        // Initialize triggers map
        this.triggers = new Map();
        // Load initial state
        this._load_state();
    }
    async _load_state() {
        const result = await this.state_manager.load_state();
        if (result.success && result.data) {
            const triggers = result.data.triggers || {};
            for (const [key, value] of Object.entries(triggers)) {
                this.triggers.set(key, this._convert_to_trigger_info(value));
            }
        }
        else {
            console.warn("Failed to load state, using defaults");
            this.triggers = new Map();
            await this._initialize_default_triggers();
        }
    }
    _convert_to_trigger_info(data) {
        return {
            ...data,
            created_at: new Date(data.created_at),
            last_updated: new Date(data.last_updated)
        };
    }
    async _initialize_default_triggers() {
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
    async _save_state() {
        const state = {
            triggers: Object.fromEntries(this.triggers.entries()),
            metadata: {
                last_updated: new Date().toISOString(),
                version: "1.0.1"
            }
        };
        await this.state_manager.save_state(state);
    }
    async _generate_tech_triggers() {
        const triggers = {};
        const result = await this.tech_analyzer.process_text("");
        if (!result.success || !result.data)
            return triggers;
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
                required_imports: this._get_required_imports(tech),
                validation_rules: this._get_validation_rules(tech),
                metadata: tech,
                llm_prompt_template: this._get_prompt_template(tech),
                created_at: new Date(),
                last_updated: new Date(),
                version: "1.0.1"
            };
        }
        return triggers;
    }
    _get_required_imports(tech) {
        const base_imports = ["typing"];
        if (tech.type === "language") {
            if (tech.name === "python") {
                return [...base_imports, "ast", "pylint"];
            }
            else if (tech.name === "javascript") {
                return [...base_imports, "esprima", "eslint"];
            }
        }
        else if (tech.type === "framework") {
            if (tech.category.includes("frontend")) {
                return [...base_imports, "esprima", "eslint"];
            }
            else if (tech.category.includes("backend")) {
                return [...base_imports, "ast", "pylint"];
            }
        }
        return base_imports;
    }
    _get_validation_rules(tech) {
        var _a;
        const rules = {
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
        }
        else if (tech.type === "framework") {
            rules.framework_version = {
                name: "Framework Version",
                description: "Validates framework version",
                validator: `data.get('version') in ${JSON.stringify(((_a = tech.version_info) === null || _a === void 0 ? void 0 : _a.supported) || ['*'])}`,
                error_message: "Unsupported framework version",
                severity: "error"
            };
        }
        return rules;
    }
    _get_prompt_template(tech) {
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
    async get_trigger(key) {
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
            const trigger = this.triggers.get(key);
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
            error: new TriggerMapError(`No trigger found for key: ${key}`, "TriggerNotFound")
        };
    }
    async add_trigger(key, trigger) {
        if (this.triggers.has(key)) {
            return {
                success: false,
                error: new TriggerMapError(`Trigger already exists: ${key}`, "DuplicateTrigger")
            };
        }
        this.triggers.set(key, trigger);
        this.trigger_cache.set(key, trigger);
        await this._save_state();
        return { success: true, data: true };
    }
    async update_trigger(key, trigger) {
        if (!this.triggers.has(key)) {
            return {
                success: false,
                error: new TriggerMapError(`Trigger not found: ${key}`, "TriggerNotFound")
            };
        }
        this.triggers.set(key, trigger);
        this.trigger_cache.set(key, trigger);
        await this._save_state();
        return { success: true, data: true };
    }
    async remove_trigger(key) {
        if (!this.triggers.has(key)) {
            return {
                success: false,
                error: new TriggerMapError(`Trigger not found: ${key}`, "TriggerNotFound")
            };
        }
        this.triggers.delete(key);
        this.trigger_cache.clear(); // Clear cache on removal
        await this._save_state();
        return { success: true, data: true };
    }
    get all_triggers() {
        return new Map(this.triggers);
    }
}
exports.TriggerMapManager = TriggerMapManager;
// Initialize the manager
exports.trigger_manager = new TriggerMapManager();
// Export the TRIGGER_MAP for backward compatibility
exports.TRIGGER_MAP = exports.trigger_manager.all_triggers;
