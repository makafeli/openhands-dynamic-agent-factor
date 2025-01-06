 import axios from 'axios';

export async function processText(text: string): Promise<string> {
  // Remove common punctuation and normalize whitespace
  const normalized = text
    .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  // Convert to lowercase for case-insensitive matching
  return normalized.toLowerCase();
}

export function normalizeText(text: string): string {
  return text
    .replace(/[\n\r\t]/g, ' ') // Replace newlines, tabs with spaces
    .replace(/\s+/g, ' ')      // Normalize multiple spaces
    .trim();                   // Remove leading/trailing whitespace
}

export async function fetchWithTimeout(
  url: string,
  options: RequestInit & { timeout?: number } = {}
): Promise<Response> {
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
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

export function debounce<F extends (...args: any[]) => any>(
  func: F,
  waitFor: number
): (...args: Parameters<F>) => Promise<ReturnType<F>> {
  let timeout: NodeJS.Timeout;

  return (...args: Parameters<F>): Promise<ReturnType<F>> =>
    new Promise(resolve => {
      if (timeout) {
        clearTimeout(timeout);
      }

      timeout = setTimeout(() => resolve(func(...args)), waitFor);
    });
}

export function memoize<T extends (...args: any[]) => any>(
  func: T,
  options: { maxSize?: number; ttl?: number } = {}
): T {
  const { maxSize = 100, ttl = 3600000 } = options; // Default: 100 items, 1 hour TTL
  const cache = new Map<string, { value: any; timestamp: number }>();

  return ((...args: Parameters<T>): ReturnType<T> => {
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
  }) as T;
}

export function retry<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts?: number;
    delay?: number;
    backoff?: number;
    shouldRetry?: (error: any) => boolean;
  } = {}
): Promise<T> {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = 2,
    shouldRetry = () => true
  } = options;

  return new Promise<T>((resolve, reject) => {
    let attempts = 0;

    const attempt = async () => {
      try {
        const result = await fn();
        resolve(result);
      } catch (error) {
        attempts++;

        if (attempts < maxAttempts && shouldRetry(error)) {
          const nextDelay = delay * Math.pow(backoff, attempts - 1);
          setTimeout(attempt, nextDelay);
        } else {
          reject(error);
        }
      }
    };

    attempt();
  });
}

export function safeJsonParse(str: string, fallback: any = null): any {
  try {
    return JSON.parse(str);
  } catch {
    return fallback;
  }
}

export function isValidUrl(str: string): boolean {
  try {
    new URL(str);
    return true;
  } catch {
    return false;
  }
}
