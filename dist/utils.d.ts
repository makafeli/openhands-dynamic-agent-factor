export interface OperationResult<T> {
    success: boolean;
    data?: T;
    error?: BaseError;
    metadata?: Record<string, any>;
    duration?: number;
}
export declare class BaseError extends Error {
    error_type: string;
    details?: Record<string, any> | undefined;
    recovery_hint?: string | undefined;
    constructor(message: string, error_type: string, details?: Record<string, any> | undefined, recovery_hint?: string | undefined);
    to_dict(): Record<string, any>;
}
export declare class ValidationError extends BaseError {
    constructor(message: string, details?: Record<string, any>, recovery_hint?: string);
}
export declare class Cache<K, V> {
    private cache;
    private ttl;
    constructor(ttl?: number);
    set(key: K, value: V): void;
    get(key: K): V | undefined;
    clear(): void;
}
export declare class StateManager<T> {
    private filePath;
    constructor(filePath: string);
    load_state(): Promise<OperationResult<T>>;
    save_state(state: T): Promise<OperationResult<boolean>>;
}
