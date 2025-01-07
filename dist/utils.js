"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.processText = processText;
exports.normalizeText = normalizeText;
exports.fetchWithTimeout = fetchWithTimeout;
exports.debounce = debounce;
exports.memoize = memoize;
exports.retry = retry;
exports.safeJsonParse = safeJsonParse;
exports.isValidUrl = isValidUrl;
async function processText(text) {
    // Remove common punctuation and normalize whitespace
    const normalized = text
        .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    // Convert to lowercase for case-insensitive matching
    return normalized.toLowerCase();
}
function normalizeText(text) {
    return text
        .replace(/[\n\r\t]/g, ' ') // Replace newlines, tabs with spaces
        .replace(/\s+/g, ' ') // Normalize multiple spaces
        .trim(); // Remove leading/trailing whitespace
}
async function fetchWithTimeout(url, options = {}) {
    const { timeout = 5000, ...fetchOptions } = options;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    try {
        const response = await fetch(url, {
            ...fetchOptions,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    }
    catch (error) {
        clearTimeout(id);
        throw error;
    }
}
function debounce(func, waitFor) {
    let timeout;
    return (...args) => new Promise(resolve => {
        if (timeout) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(() => resolve(func(...args)), waitFor);
    });
}
function memoize(func, options = {}) {
    const { maxSize = 100, ttl = 3600000 } = options; // Default: 100 items, 1 hour TTL
    const cache = new Map();
    return ((...args) => {
        const key = JSON.stringify(args);
        const cached = cache.get(key);
        if (cached && Date.now() - cached.timestamp < ttl) {
            return cached.value;
        }
        const result = func(...args);
        cache.set(key, { value: result, timestamp: Date.now() });
        if (cache.size > maxSize) {
            const oldestKey = Array.from(cache.entries())
                .sort(([, a], [, b]) => a.timestamp - b.timestamp)[0][0];
            cache.delete(oldestKey);
        }
        return result;
    });
}
function retry(fn, options = {}) {
    const { maxAttempts = 3, delay = 1000, backoff = 2, shouldRetry = () => true } = options;
    return new Promise((resolve, reject) => {
        let attempts = 0;
        const attempt = async () => {
            try {
                const result = await fn();
                resolve(result);
            }
            catch (error) {
                attempts++;
                if (attempts < maxAttempts && shouldRetry(error)) {
                    const nextDelay = delay * Math.pow(backoff, attempts - 1);
                    setTimeout(attempt, nextDelay);
                }
                else {
                    reject(error);
                }
            }
        };
        attempt();
    });
}
function safeJsonParse(str, fallback = null) {
    try {
        return JSON.parse(str);
    }
    catch {
        return fallback;
    }
}
function isValidUrl(str) {
    try {
        new URL(str);
        return true;
    }
    catch {
        return false;
    }
}
//# sourceMappingURL=utils.js.map