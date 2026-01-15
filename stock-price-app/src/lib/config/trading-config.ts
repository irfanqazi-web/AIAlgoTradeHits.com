/**
 * TRADING CONFIG - Single Source of Truth (SSOT)
 * All trading-related configuration in one place
 * Based on masterquery.md v4.0
 *
 * @version 3.0.0
 * @lastModified January 13, 2026
 */

// ============================================================================
// § 1. VERSION & CHANGELOG
// ============================================================================
export const LOGIC_VERSION = "3.0.0";
export const CHANGELOG = [
  { version: "3.0.0", date: "2026-01-13", changes: "TypeScript migration, SSOT implementation" },
  { version: "2.0.0", date: "2026-01-11", changes: "Nested ML model integration" },
  { version: "1.0.0", date: "2025-11-15", changes: "Initial release" },
];

// ============================================================================
// § 2. INDICATOR THRESHOLDS (from masterquery.md v4.0)
// ============================================================================
export const INDICATOR_THRESHOLDS = {
  // Momentum Indicators
  RSI: {
    oversold: 30,
    overbought: 70,
    sweet_spot: [50, 70] as [number, number],
    neutral: 50,
  },
  MACD: {
    signal_cross: 0,
    histogram_threshold: 0,
  },
  ROC: {
    bullish: 0,
    strong_bullish: 2,
  },
  STOCHASTIC: {
    oversold: 20,
    overbought: 80,
    k_cross_d_bullish: true,
  },

  // Trend Indicators
  ADX: {
    weak: 20,
    strong: 25,
    very_strong: 40,
  },
  EMA: {
    short: 12,
    medium: 26,
    long: 50,
    very_long: 200,
  },
  SMA: {
    short: 20,
    medium: 50,
    long: 200,
  },

  // Volatility Indicators
  BOLLINGER: {
    std_dev: 2,
    period: 20,
  },
  ATR: {
    period: 14,
  },

  // Volume Indicators
  VOLUME: {
    surge_multiplier: 1.5,
    high_volume_multiplier: 2.0,
  },
  MFI: {
    oversold: 20,
    overbought: 80,
  },
  CMF: {
    bullish: 0,
    strong_bullish: 0.1,
  },
} as const;

// ============================================================================
// § 3. GROWTH SCORE CALCULATION (0-100)
// ============================================================================
export const GROWTH_SCORE_RULES = {
  rsi_sweet_spot: {
    points: 25,
    condition: "RSI between 50 and 70",
    range: [50, 70] as [number, number],
  },
  macd_positive: {
    points: 25,
    condition: "MACD histogram > 0",
  },
  strong_trend: {
    points: 25,
    condition: "ADX > 25",
    threshold: 25,
  },
  above_sma200: {
    points: 25,
    condition: "Close > SMA200",
  },
} as const;

export const GROWTH_SCORE_THRESHOLDS = {
  EXCELLENT: 75,
  GOOD: 50,
  MODERATE: 25,
  POOR: 0,
} as const;

// ============================================================================
// § 4. TREND REGIME CLASSIFICATION
// ============================================================================
export const TREND_REGIMES = {
  STRONG_UPTREND: {
    label: "Strong Uptrend",
    conditions: {
      close_above_sma50: true,
      sma50_above_sma200: true,
      adx_min: 25,
    },
    color: "#059669",
    action: "BUY",
  },
  WEAK_UPTREND: {
    label: "Weak Uptrend",
    conditions: {
      close_above_sma50: true,
      close_above_sma200: true,
    },
    color: "#10b981",
    action: "HOLD/BUY",
  },
  CONSOLIDATION: {
    label: "Consolidation",
    conditions: {
      default: true,
    },
    color: "#6b7280",
    action: "HOLD",
  },
  WEAK_DOWNTREND: {
    label: "Weak Downtrend",
    conditions: {
      close_below_sma50: true,
      close_below_sma200: true,
    },
    color: "#f59e0b",
    action: "HOLD/SELL",
  },
  STRONG_DOWNTREND: {
    label: "Strong Downtrend",
    conditions: {
      close_below_sma50: true,
      sma50_below_sma200: true,
      adx_min: 25,
    },
    color: "#ef4444",
    action: "SELL",
  },
} as const;

// ============================================================================
// § 5. EMA CYCLE DETECTION
// ============================================================================
export const EMA_CYCLES = {
  RISE_CYCLE: {
    condition: "ema12 > ema26",
    signal: "BULLISH",
    description: "Short-term momentum exceeds long-term",
  },
  FALL_CYCLE: {
    condition: "ema12 < ema26",
    signal: "BEARISH",
    description: "Short-term momentum below long-term",
  },
  RISE_CYCLE_START: {
    condition: "ema12 crosses above ema26",
    signal: "BUY",
    description: "New bullish momentum starting",
  },
  FALL_CYCLE_START: {
    condition: "ema12 crosses below ema26",
    signal: "SELL",
    description: "New bearish momentum starting",
  },
} as const;

// ============================================================================
// § 6. NESTED ML SIGNAL THRESHOLDS (66.2% UP Accuracy)
// ============================================================================
export const NESTED_SIGNAL_THRESHOLDS = {
  ULTRA_BUY: {
    aligned_pct: 60,
    min_scores: {
      daily: 5,
      hourly: 6,
      fivemin: 5,
    },
    action: "EXECUTE",
    confidence: "HIGH",
    color: "#059669",
  },
  STRONG_BUY: {
    aligned_pct: 50,
    min_scores: {
      daily: 4,
      hourly: 5,
      fivemin: 4,
    },
    action: "READY",
    confidence: "MEDIUM-HIGH",
    color: "#10b981",
  },
  BUY: {
    daily_hourly_aligned: true,
    min_scores: {
      daily: 4,
      hourly: 4,
    },
    action: "WATCH",
    confidence: "MEDIUM",
    color: "#34d399",
  },
  WEAK_BUY: {
    daily_bullish: true,
    min_score: 4,
    action: "WATCH",
    confidence: "LOW",
    color: "#6ee7b7",
  },
  HOLD: {
    default: true,
    action: "WAIT",
    confidence: "NONE",
    color: "#6b7280",
  },
} as const;

export const NESTED_ACTION_STATUS = {
  EXECUTE: {
    label: "Execute",
    description: "All TF aligned + ready",
    color: "#10b981",
    icon: "Zap",
  },
  READY: {
    label: "Ready",
    description: "All TF aligned",
    color: "#3b82f6",
    icon: "Target",
  },
  WATCH: {
    label: "Watch",
    description: "Partial aligned",
    color: "#f59e0b",
    icon: "Clock",
  },
  WAIT: {
    label: "Wait",
    description: "No alignment",
    color: "#6b7280",
    icon: "AlertCircle",
  },
} as const;

// ============================================================================
// § 7. RECOMMENDATION SIGNALS
// ============================================================================
export const RECOMMENDATIONS = {
  STRONG_BUY: {
    label: "Strong Buy",
    color: "#059669",
    priority: 1,
  },
  BUY: {
    label: "Buy",
    color: "#10b981",
    priority: 2,
  },
  HOLD: {
    label: "Hold",
    color: "#6b7280",
    priority: 3,
  },
  SELL: {
    label: "Sell",
    color: "#f59e0b",
    priority: 4,
  },
  STRONG_SELL: {
    label: "Strong Sell",
    color: "#ef4444",
    priority: 5,
  },
} as const;

// ============================================================================
// § 8. SENTIMENT SCORE CONFIGURATION
// ============================================================================
export const SENTIMENT_CONFIG = {
  scale: {
    min: 0,
    max: 1,
  },
  thresholds: {
    very_bullish: 0.8,
    bullish: 0.6,
    neutral: 0.4,
    bearish: 0.2,
    very_bearish: 0,
  },
  weights: {
    news_sentiment: 0.3,
    social_sentiment: 0.2,
    analyst_ratings: 0.3,
    market_momentum: 0.2,
  },
} as const;

// ============================================================================
// § 9. TIMEFRAMES
// ============================================================================
export const TIMEFRAMES = {
  DAILY: {
    interval: "1day",
    label: "Daily",
    indicators: 24,
    outputsize: 5000,
  },
  HOURLY: {
    interval: "1h",
    label: "Hourly",
    indicators: 12,
    outputsize: 5000,
  },
  FIVE_MIN: {
    interval: "5min",
    label: "5 Minute",
    indicators: 8,
    outputsize: 5000,
  },
  WEEKLY: {
    interval: "1week",
    label: "Weekly",
    indicators: 24,
    outputsize: 5000,
  },
} as const;

// ============================================================================
// § 10. ASSET TYPES
// ============================================================================
export const ASSET_TYPES = {
  STOCKS: {
    label: "Stocks",
    table_prefix: "stocks",
    symbol_format: "TICKER",
  },
  CRYPTO: {
    label: "Crypto",
    table_prefix: "crypto",
    symbol_format: "BTC/USD",
  },
  ETF: {
    label: "ETF",
    table_prefix: "etf",
    symbol_format: "TICKER",
  },
  FOREX: {
    label: "Forex",
    table_prefix: "forex",
    symbol_format: "EUR/USD",
  },
} as const;

// ============================================================================
// § 11. HELPER FUNCTIONS
// ============================================================================

/**
 * Get indicator threshold configuration
 */
export function getIndicatorThreshold(indicator: keyof typeof INDICATOR_THRESHOLDS) {
  return INDICATOR_THRESHOLDS[indicator];
}

/**
 * Get trend regime by conditions
 */
export function getTrendRegime(
  close: number,
  sma50: number,
  sma200: number,
  adx: number
): keyof typeof TREND_REGIMES {
  if (close > sma50 && sma50 > sma200 && adx > 25) return "STRONG_UPTREND";
  if (close > sma50 && close > sma200) return "WEAK_UPTREND";
  if (close < sma50 && sma50 < sma200 && adx > 25) return "STRONG_DOWNTREND";
  if (close < sma50 && close < sma200) return "WEAK_DOWNTREND";
  return "CONSOLIDATION";
}

/**
 * Get nested signal by scores
 */
export function getNestedSignal(
  dailyScore: number,
  hourlyScore: number,
  fiveMinScore: number,
  alignedPct: number
): keyof typeof NESTED_SIGNAL_THRESHOLDS {
  if (alignedPct >= 60 && dailyScore >= 5 && hourlyScore >= 6 && fiveMinScore >= 5) {
    return "ULTRA_BUY";
  }
  if (alignedPct >= 50 && dailyScore >= 4 && hourlyScore >= 5 && fiveMinScore >= 4) {
    return "STRONG_BUY";
  }
  if (dailyScore >= 4 && hourlyScore >= 4) {
    return "BUY";
  }
  if (dailyScore >= 4) {
    return "WEAK_BUY";
  }
  return "HOLD";
}
