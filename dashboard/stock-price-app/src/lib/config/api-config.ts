/**
 * API CONFIG - Single Source of Truth (SSOT)
 * All API-related configuration in one place
 *
 * @version 3.0.0
 * @lastModified January 13, 2026
 */

// ============================================================================
// § 1. API BASE URLS
// ============================================================================
export const API_BASE_URLS = {
  TRADING_API: import.meta.env.VITE_API_URL || "https://trading-api-1075463475276.us-central1.run.app",
  BULLETPROOF_FETCHER: "https://bulletproof-fetcher-6pmz2y7ouq-uc.a.run.app",
} as const;

// ============================================================================
// § 2. API RATE LIMITS
// ============================================================================
export const API_RATE_LIMITS = {
  TWELVEDATA: {
    calls_per_minute: 800,
    outputsize: 5000,
    daily_quota: 2_000_000,
    plan: "$229/month",
  },
  KRAKEN: {
    calls_per_minute: 60,
    public_endpoints: true,
  },
  FRED: {
    calls_per_day: 100,
    free_tier: true,
  },
  FINNHUB: {
    calls_per_minute: 60,
    free_tier: true,
  },
  COINMARKETCAP: {
    calls_per_day: 333,
    credits_per_month: 10_000,
    plan: "Basic",
  },
} as const;

// ============================================================================
// § 3. API ENDPOINTS
// ============================================================================
export const API_ENDPOINTS = {
  // Market Data
  MARKET_DATA: "/api/market-data",
  HISTORICAL_DATA: "/api/data/historical",
  LIVE_PRICES: "/api/data/prices",

  // AI & ML Endpoints
  AI: {
    TRADING_SIGNALS: "/api/ai/trading-signals",
    RISE_CYCLE_CANDIDATES: "/api/ai/rise-cycle-candidates",
    ML_PREDICTIONS: "/api/ai/ml-predictions",
    GROWTH_SCREENER: "/api/ai/growth-screener",
    PATTERN_RECOGNITION: "/api/ai/pattern-recognition",
    NESTED_SIGNALS: "/api/ai/nested-signals",
    NESTED_SUMMARY: "/api/ai/nested-summary",
    TEXT_TO_SQL: "/api/ai/text-to-sql",
  },

  // Data Export
  DATA: {
    DOWNLOAD: "/api/data/download",
    EXPORT_CSV: "/api/data/export/csv",
    EXPORT_EXCEL: "/api/data/export/excel",
    ML_TRAINING_DATA: "/api/data/ml-training",
  },

  // Admin & Monitoring
  ADMIN: {
    SCHEDULERS: "/api/admin/schedulers",
    TABLES: "/api/admin/tables",
    TABLE_COUNTS: "/api/admin/table-counts",
    USERS: "/api/admin/users",
    LOGS: "/api/admin/logs",
  },

  // Symbol Lists
  SYMBOLS: {
    STOCKS: "/api/symbols/stocks",
    CRYPTO: "/api/symbols/crypto",
    ETF: "/api/symbols/etf",
    FOREX: "/api/symbols/forex",
    ALL: "/api/symbols/all",
  },

  // Authentication
  AUTH: {
    LOGIN: "/api/auth/login",
    LOGOUT: "/api/auth/logout",
    VERIFY: "/api/auth/verify",
  },
} as const;

// ============================================================================
// § 4. BIGQUERY CONFIGURATION
// ============================================================================
export const BIGQUERY_CONFIG = {
  PROJECT_ID: "aialgotradehits",
  DATASET: "crypto_trading_data",
  ML_DATASET: "ml_models",

  TABLES: {
    // Clean Tables (Primary)
    STOCKS_DAILY_CLEAN: "stocks_daily_clean",
    STOCKS_HOURLY_CLEAN: "stocks_hourly_clean",
    STOCKS_5MIN_CLEAN: "stocks_5min_clean",
    CRYPTO_DAILY_CLEAN: "crypto_daily_clean",
    CRYPTO_HOURLY_CLEAN: "crypto_hourly_clean",
    ETF_DAILY_CLEAN: "etf_daily_clean",
    FOREX_DAILY_CLEAN: "forex_daily_clean",

    // Support Tables
    FRED_DATA: "fred_economic_data",
    CMC_DATA: "coinmarketcap_rankings",
    FINNHUB_DATA: "finnhub_recommendations",
    KRAKEN_VOLUME: "kraken_buy_sell_volume",

    // ML Tables
    NESTED_ALIGNMENT: "nested_alignment_final",
    NESTED_PREDICTIONS: "nested_predictions",
    ML_FEATURES: "daily_features_24",
  },
} as const;

// ============================================================================
// § 5. DEFAULT REQUEST OPTIONS
// ============================================================================
export const DEFAULT_REQUEST_OPTIONS = {
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds
  retries: 3,
  retryDelay: 1000, // 1 second
} as const;

// ============================================================================
// § 6. CACHE CONFIGURATION
// ============================================================================
export const CACHE_CONFIG = {
  // Client-side cache durations (milliseconds)
  MARKET_DATA: 60_000, // 1 minute
  SYMBOLS_LIST: 300_000, // 5 minutes
  ADMIN_DATA: 30_000, // 30 seconds
  ML_PREDICTIONS: 300_000, // 5 minutes

  // Storage keys
  STORAGE_KEYS: {
    SYMBOLS_CACHE: "symbols_cache",
    USER_PREFERENCES: "user_preferences",
    RECENT_SEARCHES: "recent_searches",
    THEME: "theme",
  },
} as const;

// ============================================================================
// § 7. HELPER FUNCTIONS
// ============================================================================

/**
 * Build full API URL
 */
export function buildApiUrl(endpoint: string, baseUrl?: string): string {
  const base = baseUrl || API_BASE_URLS.TRADING_API;
  return `${base}${endpoint}`;
}

/**
 * Build query string from params
 */
export function buildQueryString(params: Record<string, unknown>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      searchParams.append(key, String(value));
    }
  });
  return searchParams.toString();
}

/**
 * Get BigQuery table name
 */
export function getBigQueryTable(
  assetType: "stocks" | "crypto" | "etf" | "forex",
  timeframe: "daily" | "hourly" | "5min"
): string {
  const tableMap: Record<string, Record<string, string>> = {
    stocks: {
      daily: BIGQUERY_CONFIG.TABLES.STOCKS_DAILY_CLEAN,
      hourly: BIGQUERY_CONFIG.TABLES.STOCKS_HOURLY_CLEAN,
      "5min": BIGQUERY_CONFIG.TABLES.STOCKS_5MIN_CLEAN,
    },
    crypto: {
      daily: BIGQUERY_CONFIG.TABLES.CRYPTO_DAILY_CLEAN,
      hourly: BIGQUERY_CONFIG.TABLES.CRYPTO_HOURLY_CLEAN,
    },
    etf: {
      daily: BIGQUERY_CONFIG.TABLES.ETF_DAILY_CLEAN,
    },
    forex: {
      daily: BIGQUERY_CONFIG.TABLES.FOREX_DAILY_CLEAN,
    },
  };

  return tableMap[assetType]?.[timeframe] || "";
}
