export interface OperationResult<T> {
    success: boolean;
    data?: T;
    error?: BaseError;
    metadata?: Record<string, any>;
    duration?: number;
}

export class BaseError extends Error {
    constructor(
        message: string,
        public error_type: string,
        public details?: Record<string, any>,
        public recovery_hint?: string
    ) {
        super(message);
        this.name = this.constructor.name;
    }

    public to_dict(): Record<string, any> {
        return {
            message: this.message,
            error_type: this.error_type,
            details: this.details,
            recovery_hint: this.recovery_hint
        };
    }
}

export class ValidationError extends BaseError {
    constructor(
        message: string,
        details?: Record<string, any>,
        recovery_hint?: string
    ) {
        super(message, 'ValidationError', details, recovery_hint);
    }
}

export class Cache<K, V> {
    private cache: Map<K, { value: V; expires: number }>;
    private ttl: number;

    constructor(ttl: number = 3600) {
        this.cache = new Map();
        this.ttl = ttl * 1000; // Convert to milliseconds
    }

    set(key: K, value: V): void {
        this.cache.set(key, {
            value,
            expires: Date.now() + this.ttl
        });
    }

    get(key: K): V | undefined {
        const item = this.cache.get(key);
        if (!item) return undefined;

        if (Date.now() > item.expires) {
            this.cache.delete(key);
            return undefined;
        }

        return item.value;
    }

    clear(): void {
        this.cache.clear();
    }
}

export class StateManager<T> {
    constructor(private filePath: string) {}

    async load_state(): Promise<OperationResult<T>> {
        try {
            const response = await fetch(this.filePath);
            if (!response.ok) {
                throw new Error(`Failed to load state: ${response.statusText}`);
            }
            const data = await response.json();
            return {
                success: true,
                data: data as T
            };
        } catch (error) {
            return {
                success: false,
                error: new BaseError(
                    'Failed to load state',
                    'StateLoadError',
                    { error: String(error) }
                )
            };
        }
    }

    async save_state(state: T): Promise<OperationResult<boolean>> {
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
        } catch (error) {
            return {
                success: false,
                error: new BaseError(
                    'Failed to save state',
                    'StateSaveError',
                    { error: String(error) }
                )
            };
        }
    }
}
