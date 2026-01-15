/**
 * API Client - Base HTTP client with interceptors
 *
 * Provides a centralized HTTP client for all API calls.
 * Includes request/response interceptors, error handling, and retry logic.
 *
 * @version 5.1.0
 */

import { API_CONFIG } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
    timestamp?: string;
  };
}

export interface RequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: unknown;
  params?: Record<string, string | number | boolean>;
  timeout?: number;
  retries?: number;
  cache?: boolean;
}

type RequestInterceptor = (config: RequestConfig) => RequestConfig | Promise<RequestConfig>;
type ResponseInterceptor = <T>(response: ApiResponse<T>) => ApiResponse<T> | Promise<ApiResponse<T>>;
type ErrorInterceptor = (error: Error) => Error | Promise<Error>;

// ============================================================================
// § 2. CACHE IMPLEMENTATION
// ============================================================================

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class ApiCache {
  private cache = new Map<string, CacheEntry<unknown>>();
  private maxSize: number;

  constructor(maxSize = 100) {
    this.maxSize = maxSize;
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined;
    if (!entry) return null;

    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  set<T>(key: string, data: T, ttl = API_CONFIG.cache.ttlMs): void {
    // Evict oldest entries if cache is full
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) this.cache.delete(oldestKey);
    }

    this.cache.set(key, { data, timestamp: Date.now(), ttl });
  }

  clear(): void {
    this.cache.clear();
  }

  delete(key: string): void {
    this.cache.delete(key);
  }
}

// ============================================================================
// § 3. API CLIENT CLASS
// ============================================================================

class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;
  private cache: ApiCache;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private errorInterceptors: ErrorInterceptor[] = [];

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || API_CONFIG.baseUrl;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
    this.cache = new ApiCache(API_CONFIG.cache.maxSize);
  }

  // -------------------------------------------------------------------------
  // Interceptors
  // -------------------------------------------------------------------------

  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor);
  }

  addErrorInterceptor(interceptor: ErrorInterceptor): void {
    this.errorInterceptors.push(interceptor);
  }

  // -------------------------------------------------------------------------
  // Request Methods
  // -------------------------------------------------------------------------

  async request<T>(endpoint: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    // Apply request interceptors
    let finalConfig = { ...config };
    for (const interceptor of this.requestInterceptors) {
      finalConfig = await interceptor(finalConfig);
    }

    const {
      method = 'GET',
      headers = {},
      body,
      params,
      timeout = API_CONFIG.timeouts.default,
      retries = API_CONFIG.rateLimits.retryAttempts,
      cache = method === 'GET' && API_CONFIG.cache.enabled,
    } = finalConfig;

    // Build URL with params
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        searchParams.append(key, String(value));
      });
      url += `?${searchParams.toString()}`;
    }

    // Check cache for GET requests
    const cacheKey = `${method}:${url}`;
    if (cache && method === 'GET') {
      const cached = this.cache.get<ApiResponse<T>>(cacheKey);
      if (cached) return cached;
    }

    // Make request with retry logic
    let lastError: Error | null = null;
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          method,
          headers: { ...this.defaultHeaders, ...headers },
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        let result: ApiResponse<T>;

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          result = {
            success: false,
            error: errorData.error || `HTTP ${response.status}: ${response.statusText}`,
          };
        } else {
          const data = await response.json();
          result = {
            success: true,
            data: data.data !== undefined ? data.data : data,
            meta: data.meta,
          };
        }

        // Apply response interceptors
        for (const interceptor of this.responseInterceptors) {
          result = await interceptor(result);
        }

        // Cache successful GET responses
        if (cache && method === 'GET' && result.success) {
          this.cache.set(cacheKey, result);
        }

        return result;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));

        // Apply error interceptors
        for (const interceptor of this.errorInterceptors) {
          lastError = await interceptor(lastError);
        }

        // Don't retry on abort
        if (lastError.name === 'AbortError') break;

        // Exponential backoff
        if (attempt < retries) {
          await new Promise(resolve =>
            setTimeout(resolve, API_CONFIG.rateLimits.retryDelayMs * Math.pow(2, attempt))
          );
        }
      }
    }

    return {
      success: false,
      error: lastError?.message || 'Request failed',
    };
  }

  // Convenience methods
  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  async post<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'POST', body });
  }

  async put<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'PUT', body });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // Cache management
  clearCache(): void {
    this.cache.clear();
  }

  invalidateCache(endpoint: string): void {
    this.cache.delete(`GET:${this.baseUrl}${endpoint}`);
  }
}

// ============================================================================
// § 4. SINGLETON INSTANCE
// ============================================================================

export const apiClient = new ApiClient();

// Add default interceptors
apiClient.addRequestInterceptor((config) => {
  // Add timestamp to all requests
  return {
    ...config,
    headers: {
      ...config.headers,
      'X-Request-Time': new Date().toISOString(),
    },
  };
});

export default apiClient;
