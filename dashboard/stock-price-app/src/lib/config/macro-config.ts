/**
 * MACRO CONFIG - Single Source of Truth (SSOT)
 *
 * This is the master configuration file for AIAlgoTradeHits Trading Platform.
 * All configuration values should be defined here and imported elsewhere.
 * Following EI Platform Layer Cake Architecture principles.
 *
 * @version 5.1.0
 * @lastUpdated 2026-01-14
 */

// ============================================================================
// § 1. APPLICATION METADATA
// ============================================================================

export const APP_CONFIG = {
  name: 'AIAlgoTradeHits',
  version: '5.1.0',
  description: 'AI-Powered Trading Analytics Platform',
  environment: import.meta.env.MODE || 'development',
  logicVersion: '3.0.0',
} as const;

// ============================================================================
// § 2. API CONFIGURATION
// ============================================================================

export const API_CONFIG = {
  // Base URLs
  baseUrl: import.meta.env.VITE_API_URL || 'https://trading-api-1075463475276.us-central1.run.app',

  // Endpoints - Route-based structure
  endpoints: {
    // Market Data
    market: {
      symbols: '/api/symbols',
      history: '/api/history',
      livePrice: '/api/live-price',
      search: '/api/search',
    },
    // AI/ML Endpoints
    ai: {
      tradingSignals: '/api/ai/trading-signals',
      riseCycleCandidates: '/api/ai/rise-cycle-candidates',
      mlPredictions: '/api/ai/ml-predictions',
      growthScreener: '/api/ai/growth-screener',
      textToSql: '/api/ai/text-to-sql',
      analyzeSymbol: '/api/ai/analyze-symbol',
      marketSummary: '/api/ai/market-summary',
      nestedSignals: '/api/ai/nested-signals',
      nestedSummary: '/api/ai/nested-summary',
    },
    // Admin Endpoints
    admin: {
      users: '/api/admin/users',
      tableCounts: '/api/admin/table-counts',
      schedulerStatus: '/api/scheduler/status',
    },
    // Auth Endpoints
    auth: {
      login: '/api/login',
      logout: '/api/logout',
      changePassword: '/api/change-password',
    },
    // Data Endpoints
    data: {
      download: '/api/data/download',
      reconciliation: '/api/data/reconciliation',
      export: '/api/data/export',
    },
  },

  // Rate Limits
  rateLimits: {
    requestsPerMinute: 60,
    requestsPerSecond: 5,
    retryAttempts: 3,
    retryDelayMs: 1000,
  },

  // Timeouts (in milliseconds)
  timeouts: {
    default: 30000,
    long: 60000,
    realtime: 5000,
  },

  // Cache Configuration
  cache: {
    enabled: true,
    ttlMs: 300000, // 5 minutes
    maxSize: 100,
  },
} as const;

// ============================================================================
// § 3. TRADING INDICATORS CONFIGURATION
// ============================================================================

export const INDICATOR_CONFIG = {
  // RSI Configuration
  rsi: {
    period: 14,
    oversold: 30,
    overbought: 70,
    sweetSpot: { min: 50, max: 70 },
  },

  // MACD Configuration
  macd: {
    fastPeriod: 12,
    slowPeriod: 26,
    signalPeriod: 9,
    histogramThreshold: 0,
  },

  // ADX Configuration
  adx: {
    period: 14,
    weak: 20,
    strong: 25,
    veryStrong: 40,
  },

  // Moving Averages
  movingAverages: {
    sma: [20, 50, 200],
    ema: [12, 20, 26, 50, 200],
  },

  // Bollinger Bands
  bollingerBands: {
    period: 20,
    stdDev: 2,
  },

  // ATR
  atr: {
    period: 14,
  },

  // Stochastic
  stochastic: {
    kPeriod: 14,
    dPeriod: 3,
    oversold: 20,
    overbought: 80,
  },

  // MFI
  mfi: {
    period: 14,
    oversold: 20,
    overbought: 80,
  },

  // Volume
  volume: {
    highRatio: 1.5,
    veryHighRatio: 2.0,
  },
} as const;

// ============================================================================
// § 4. SIGNAL CLASSIFICATION THRESHOLDS
// ============================================================================

export const SIGNAL_CONFIG = {
  // Growth Score Calculation Weights
  growthScore: {
    rsiWeight: 25,
    macdWeight: 25,
    adxWeight: 25,
    trendWeight: 25,
    maxScore: 100,
  },

  // Nested Multi-Timeframe Signal Thresholds
  nestedSignals: {
    ULTRA_BUY: {
      alignedPct: 60,
      minScores: { daily: 5, hourly: 6, fivemin: 5 },
      action: 'EXECUTE',
    },
    STRONG_BUY: {
      alignedPct: 55,
      minScores: { daily: 4, hourly: 5, fivemin: 4 },
      action: 'EXECUTE',
    },
    BUY: {
      alignedPct: 50,
      minScores: { daily: 3, hourly: 4, fivemin: 3 },
      action: 'READY',
    },
    WEAK_BUY: {
      alignedPct: 45,
      minScores: { daily: 2, hourly: 3, fivemin: 2 },
      action: 'WATCH',
    },
    NEUTRAL: {
      alignedPct: 40,
      minScores: { daily: 0, hourly: 0, fivemin: 0 },
      action: 'WAIT',
    },
  },

  // Trend Regime Classification
  trendRegimes: {
    STRONG_UPTREND: { aboveSma50: true, sma50AboveSma200: true, adxStrong: true },
    WEAK_UPTREND: { aboveSma50: true, aboveSma200: true },
    STRONG_DOWNTREND: { belowSma50: true, sma50BelowSma200: true, adxStrong: true },
    WEAK_DOWNTREND: { belowSma50: true, belowSma200: true },
    CONSOLIDATION: {},
  },

  // Recommendation Thresholds
  recommendations: {
    STRONG_BUY: { growthScoreMin: 75, rsiRange: [30, 70] },
    BUY: { growthScoreMin: 50, rsiRange: [30, 70] },
    HOLD: { growthScoreMin: 25 },
    SELL: { growthScoreMax: 25, rsiAbove: 70 },
    STRONG_SELL: { growthScoreMax: 0, rsiAbove: 80 },
  },
} as const;

// ============================================================================
// § 5. ML MODEL CONFIGURATION
// ============================================================================

export const ML_CONFIG = {
  // Model Performance Metrics
  performance: {
    upAccuracy: 66.2,
    downAccuracy: 70.6,
    rocAuc: 0.777,
    f1Score: 68.4,
  },

  // Confidence Thresholds
  confidence: {
    high: 0.70,
    medium: 0.55,
    low: 0.40,
    minimum: 0.55,
  },

  // Feature Configuration
  features: {
    daily: 24,
    hourly: 12,
    fiveMin: 8,
    total: 44,
  },

  // Lookback Periods
  lookbackPeriods: {
    daily: 200,
    hourly: 100,
    fiveMin: 50,
  },

  // Model Types
  models: {
    primary: 'xgboost',
    ensemble: ['xgboost', 'lightgbm', 'catboost'],
    nestedMultiframe: true,
  },
} as const;

// ============================================================================
// § 6. ASSET TYPE CONFIGURATION
// ============================================================================

export const ASSET_CONFIG = {
  types: {
    stocks: {
      label: 'Stocks',
      color: '#3b82f6',
      icon: 'TrendingUp',
      description: 'US Stocks (S&P 500, NASDAQ)',
      table: 'stocks_daily_clean',
    },
    crypto: {
      label: 'Crypto',
      color: '#f59e0b',
      icon: 'Coins',
      description: 'Cryptocurrencies (BTC, ETH, etc.)',
      table: 'crypto_daily_clean',
    },
    forex: {
      label: 'Forex',
      color: '#10b981',
      icon: 'DollarSign',
      description: 'Currency Pairs (EUR/USD, etc.)',
      table: 'forex_daily_clean',
    },
    etfs: {
      label: 'ETFs',
      color: '#8b5cf6',
      icon: 'PieChart',
      description: 'Exchange Traded Funds',
      table: 'etfs_daily_clean',
    },
    indices: {
      label: 'Indices',
      color: '#ec4899',
      icon: 'BarChart3',
      description: 'Market Indices (S&P 500, DOW)',
      table: 'indices_daily_clean',
    },
    commodities: {
      label: 'Commodities',
      color: '#14b8a6',
      icon: 'Package',
      description: 'Gold, Oil, etc.',
      table: 'commodities_daily_clean',
    },
    interestRates: {
      label: 'Interest Rates',
      color: '#6366f1',
      icon: 'Globe',
      description: 'Treasury Yields, FRED Data',
      table: 'interest_rates_daily',
    },
  },

  // Timeframes
  timeframes: {
    daily: { interval: '1day', outputsize: 5000, label: 'Daily' },
    hourly: { interval: '1h', outputsize: 5000, label: 'Hourly' },
    fiveMin: { interval: '5min', outputsize: 5000, label: '5 Min' },
    weekly: { interval: '1week', outputsize: 5000, label: 'Weekly' },
  },
} as const;

// ============================================================================
// § 7. UI/THEME CONFIGURATION
// ============================================================================

export const UI_CONFIG = {
  // Theme Colors (matching Tailwind config)
  themes: {
    dark: {
      name: 'dark',
      bg: '#0a0a0f',
      bgSecondary: '#12121a',
      card: '#12121a',
      cardHover: '#1a1a24',
      border: '#1e1e2d',
      text: '#e0e0e0',
      textSecondary: '#8b8b9e',
      accent: '#6366f1',
      accentHover: '#818cf8',
    },
    light: {
      name: 'light',
      bg: '#ffffff',
      bgSecondary: '#f8fafc',
      card: '#ffffff',
      cardHover: '#f1f5f9',
      border: '#e2e8f0',
      text: '#1e293b',
      textSecondary: '#64748b',
      accent: '#6366f1',
      accentHover: '#4f46e5',
    },
  },

  // Signal Colors
  signalColors: {
    ULTRA_BUY: { bg: '#059669', text: '#ffffff' },
    STRONG_BUY: { bg: '#10b981', text: '#ffffff' },
    BUY: { bg: '#34d399', text: '#000000' },
    WEAK_BUY: { bg: '#6ee7b7', text: '#000000' },
    HOLD: { bg: '#6b7280', text: '#ffffff' },
    WEAK_SELL: { bg: '#fca5a5', text: '#000000' },
    SELL: { bg: '#f87171', text: '#ffffff' },
    STRONG_SELL: { bg: '#ef4444', text: '#ffffff' },
    ULTRA_SELL: { bg: '#dc2626', text: '#ffffff' },
  },

  // Action Colors
  actionColors: {
    EXECUTE: { bg: '#10b981', text: '#ffffff' },
    READY: { bg: '#3b82f6', text: '#ffffff' },
    WATCH: { bg: '#f59e0b', text: '#000000' },
    WAIT: { bg: '#6b7280', text: '#ffffff' },
  },

  // Chart Configuration
  chart: {
    defaultHeight: 400,
    candleColors: {
      up: '#10b981',
      down: '#ef4444',
    },
    volumeColors: {
      up: 'rgba(16, 185, 129, 0.5)',
      down: 'rgba(239, 68, 68, 0.5)',
    },
    gridColor: 'rgba(255, 255, 255, 0.05)',
    crosshairColor: 'rgba(255, 255, 255, 0.3)',
  },

  // Animation Configuration
  animations: {
    duration: {
      fast: 150,
      normal: 300,
      slow: 500,
    },
    easing: 'ease-in-out',
  },

  // Pagination Defaults
  pagination: {
    defaultPageSize: 20,
    pageSizeOptions: [10, 20, 50, 100],
  },

  // Auto-refresh Intervals
  autoRefresh: {
    realtime: 5000,      // 5 seconds
    fast: 30000,         // 30 seconds
    normal: 60000,       // 1 minute
    slow: 300000,        // 5 minutes
  },
} as const;

// ============================================================================
// § 8. DATA SOURCES CONFIGURATION
// ============================================================================

export const DATA_SOURCES = {
  twelveData: {
    name: 'TwelveData',
    priority: 1,
    rateLimit: 800, // calls per minute
    dailyQuota: 2000000, // records per day
    outputsize: 5000,
  },
  kraken: {
    name: 'Kraken',
    priority: 2,
    rateLimit: 60,
    features: ['buy_volume', 'sell_volume', 'trade_count'],
  },
  fred: {
    name: 'FRED',
    priority: 3,
    rateLimit: 100, // per day
    features: ['interest_rates', 'economic_indicators'],
  },
  finnhub: {
    name: 'Finnhub',
    priority: 4,
    rateLimit: 60,
    features: ['news', 'sentiment', 'fundamentals'],
  },
  coinMarketCap: {
    name: 'CoinMarketCap',
    priority: 5,
    rateLimit: 333, // per day
    features: ['crypto_rankings', 'market_cap'],
  },
} as const;

// ============================================================================
// § 9. BIGQUERY CONFIGURATION
// ============================================================================

export const BIGQUERY_CONFIG = {
  project: 'aialgotradehits',
  dataset: 'crypto_trading_data',
  mlDataset: 'ml_models',

  // Clean Tables (Primary)
  tables: {
    stocksDaily: 'stocks_daily_clean',
    stocksHourly: 'stocks_hourly_clean',
    stocks5Min: 'stocks_5min_clean',
    cryptoDaily: 'crypto_daily_clean',
    cryptoHourly: 'crypto_hourly_clean',
    forexDaily: 'forex_daily_clean',
    etfsDaily: 'etfs_daily_clean',
    indicesDaily: 'indices_daily_clean',
    commoditiesDaily: 'commodities_daily_clean',
    interestRates: 'interest_rates_daily',
  },

  // ML Tables
  mlTables: {
    dailyFeatures: 'daily_features_24',
    predictions: 'v_daily_predictions',
    modelMetrics: 'model_metrics',
  },
} as const;

// ============================================================================
// § 10. FEATURE FLAGS
// ============================================================================

export const FEATURE_FLAGS = {
  nestedSignals: true,
  walkForwardValidation: true,
  voiceSearch: true,
  aiPatternRecognition: true,
  portfolioTracking: true,
  priceAlerts: true,
  dataExport: true,
  mlPredictions: true,
  textToSql: true,
  realTimeUpdates: false, // Coming soon
  paperTrading: false, // Coming soon
} as const;

// ============================================================================
// § 11. TYPE EXPORTS
// ============================================================================

export type AppConfig = typeof APP_CONFIG;
export type ApiConfig = typeof API_CONFIG;
export type IndicatorConfig = typeof INDICATOR_CONFIG;
export type SignalConfig = typeof SIGNAL_CONFIG;
export type MlConfig = typeof ML_CONFIG;
export type AssetConfig = typeof ASSET_CONFIG;
export type UiConfig = typeof UI_CONFIG;
export type DataSources = typeof DATA_SOURCES;
export type BigQueryConfig = typeof BIGQUERY_CONFIG;
export type FeatureFlags = typeof FEATURE_FLAGS;

export type AssetType = keyof typeof ASSET_CONFIG.types;
export type Timeframe = keyof typeof ASSET_CONFIG.timeframes;
export type SignalType = keyof typeof SIGNAL_CONFIG.nestedSignals;
export type ActionType = keyof typeof UI_CONFIG.actionColors;
export type TrendRegime = keyof typeof SIGNAL_CONFIG.trendRegimes;
export type ThemeName = keyof typeof UI_CONFIG.themes;

// ============================================================================
// § 12. DEFAULT EXPORT
// ============================================================================

const MACRO_CONFIG = {
  app: APP_CONFIG,
  api: API_CONFIG,
  indicators: INDICATOR_CONFIG,
  signals: SIGNAL_CONFIG,
  ml: ML_CONFIG,
  assets: ASSET_CONFIG,
  ui: UI_CONFIG,
  dataSources: DATA_SOURCES,
  bigQuery: BIGQUERY_CONFIG,
  features: FEATURE_FLAGS,
} as const;

export default MACRO_CONFIG;
