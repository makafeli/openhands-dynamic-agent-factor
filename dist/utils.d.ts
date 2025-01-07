export declare function processText(text: string): Promise<string>;
export declare function normalizeText(text: string): string;
export declare function fetchWithTimeout(url: string, options?: RequestInit & {
    timeout?: number;
}): Promise<Response>;
export declare function debounce<F extends (...args: any[]) => any>(func: F, waitFor: number): (...args: Parameters<F>) => Promise<ReturnType<F>>;
export declare function memoize<T extends (...args: any[]) => any>(func: T, options?: {
    maxSize?: number;
    ttl?: number;
}): T;
export declare function retry<T>(fn: () => Promise<T>, options?: {
    maxAttempts?: number;
    delay?: number;
    backoff?: number;
    shouldRetry?: (error: any) => boolean;
}): Promise<T>;
export declare function safeJsonParse(str: string, fallback?: any): any;
export declare function isValidUrl(str: string): boolean;
