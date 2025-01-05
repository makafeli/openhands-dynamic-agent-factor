"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.StateManager = exports.Cache = exports.ValidationError = exports.BaseError = void 0;
class BaseError extends Error {
    constructor(message, error_type, details, recovery_hint) {
        super(message);
        this.error_type = error_type;
        this.details = details;
        this.recovery_hint = recovery_hint;
        this.name = this.constructor.name;
    }
    to_dict() {
        return {
            message: this.message,
            error_type: this.error_type,
            details: this.details,
            recovery_hint: this.recovery_hint
        };
    }
}
exports.BaseError = BaseError;
class ValidationError extends BaseError {
    constructor(message, details, recovery_hint) {
        super(message, 'ValidationError', details, recovery_hint);
    }
}
exports.ValidationError = ValidationError;
class Cache {
    constructor(ttl = 3600) {
        this.cache = new Map();
        this.ttl = ttl * 1000; // Convert to milliseconds
    }
    set(key, value) {
        this.cache.set(key, {
            value,
            expires: Date.now() + this.ttl
        });
    }
    get(key) {
        const item = this.cache.get(key);
        if (!item)
            return undefined;
        if (Date.now() > item.expires) {
            this.cache.delete(key);
            return undefined;
        }
        return item.value;
    }
    clear() {
        this.cache.clear();
    }
}
exports.Cache = Cache;
class StateManager {
    constructor(filePath) {
        this.filePath = filePath;
    }
    async load_state() {
        try {
            const response = await fetch(this.filePath);
            if (!response.ok) {
                throw new Error(`Failed to load state: ${response.statusText}`);
            }
            const data = await response.json();
            return {
                success: true,
                data: data
            };
        }
        catch (error) {
            return {
                success: false,
                error: new BaseError('Failed to load state', 'StateLoadError', { error: String(error) })
            };
        }
    }
    async save_state(state) {
        try {
            const response = await fetch(this.filePath, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(state)
            });
            if (!response.ok) {
                throw new Error(`Failed to save state: ${response.statusText}`);
            }
            return {
                success: true,
                data: true
            };
        }
        catch (error) {
            return {
                success: false,
                error: new BaseError('Failed to save state', 'StateSaveError', { error: String(error) })
            };
        }
    }
}
exports.StateManager = StateManager;
