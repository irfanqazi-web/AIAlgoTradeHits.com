/**
 * Trading Types - Core domain types for the trading platform
 *
 * @version 3.0.0
 */

// ============================================================================
// § 1. MARKET DATA TYPES
// ============================================================================

/**
 * OHLCV candle data
 */
export interface Candle {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/**
 * Extended candle with indicators
 */
export interface CandleWithIndicators extends Candle {
  // Momentum Indicators
  rsi_14?: number;
  macd?: number;
  macd_signal?: number;
  macd_histogram?: number;
  roc?: number;
  stoch_k?: number;
  stoch_d?: number;

  // Trend Indicators
  sma_20?: number;
  sma_50?: number;
  sma_200?: number;
  ema_12?: number;
  ema_20?: number;
  ema_26?: number;
  ema_50?: number;
  ema_200?: number;
  adx?: number;
  plus_di?: number;
  minus_di?: number;

  // Volatility Indicators
  atr_14?: number;
  bb_upper?: number;
  bb_middle?: number;
  bb_lower?: number;

  // Volume Indicators
  mfi?: number;
  cmf?: number;

  // Calculated Fields
  growth_score?: number;
  sentiment_score?: number;
  trend_regime?: TrendRegime;
  recommendation?: Recommendation;
  in_rise_cycle?: boolean;
  rise_cycle_start?: boolean;
  fall_cycle_start?: boolean;
}

/**
 * Symbol information
 */
export interface Symbol {
  symbol: string;
  name: string;
  exchange?: string;
  type: AssetType;
  currency?: string;
}

// ============================================================================
// § 2. SIGNAL TYPES
// ============================================================================

/**
 * Trend regime classification
 */
export type TrendRegime =
  | "STRONG_UPTREND"
  | "WEAK_UPTREND"
  | "CONSOLIDATION"
  | "WEAK_DOWNTREND"
  | "STRONG_DOWNTREND";

/**
 * Trade recommendation
 */
export type Recommendation =
  | "STRONG_BUY"
  | "BUY"
  | "HOLD"
  | "SELL"
  | "STRONG_SELL";

/**
 * Nested signal classification
 */
export type NestedSignal =
  | "ULTRA_BUY"
  | "STRONG_BUY"
  | "BUY"
  | "WEAK_BUY"
  | "HOLD";

/**
 * Action status for nested signals
 */
export type ActionStatus = "EXECUTE" | "READY" | "WATCH" | "WAIT";

/**
 * Trading signal
 */
export interface TradingSignal {
  symbol: string;
  datetime: string;
  signal: Recommendation;
  confidence: number;
  reason: string;
  price: number;
  target_price?: number;
  stop_loss?: number;
  risk_reward_ratio?: number;
}

/**
 * Nested multi-timeframe signal
 */
export interface NestedTradingSignal {
  symbol: string;
  trade_date: string;
  trade_hour: number;
  nested_signal: NestedSignal;
  action_status: ActionStatus;
  scores: {
    daily: number;
    hourly: number;
    fivemin: number;
  };
  alignment: {
    all_tf_aligned: boolean;
    daily_hourly_aligned: boolean;
    hourly_5min_aligned: boolean;
  };
  actual_outcome?: "UP" | "DOWN";
  hour_pct_change?: number;
}

// ============================================================================
// § 3. ASSET TYPES
// ============================================================================

/**
 * Asset type classification
 */
export type AssetType = "stocks" | "crypto" | "etf" | "forex";

/**
 * Timeframe classification
 */
export type Timeframe = "daily" | "hourly" | "5min" | "weekly";

/**
 * Interval string for API calls
 */
export type IntervalString = "1day" | "1h" | "5min" | "1week";

// ============================================================================
// § 4. ML PREDICTION TYPES
// ============================================================================

/**
 * ML prediction result
 */
export interface MLPrediction {
  symbol: string;
  datetime: string;
  predicted_direction: "UP" | "DOWN";
  probability: number;
  features_used: string[];
  model_version: string;
}

/**
 * Growth score breakdown
 */
export interface GrowthScoreBreakdown {
  total: number;
  rsi_component: number;
  macd_component: number;
  adx_component: number;
  sma_component: number;
}

// ============================================================================
// § 5. API RESPONSE TYPES
// ============================================================================

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp?: string;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Market data response
 */
export interface MarketDataResponse {
  symbol: string;
  interval: IntervalString;
  data: CandleWithIndicators[];
  latest_price?: number;
  change_pct?: number;
}

/**
 * Trading signals response
 */
export interface TradingSignalsResponse {
  signals: TradingSignal[];
  generated_at: string;
  model_version: string;
}

/**
 * Nested signals response
 */
export interface NestedSignalsResponse {
  signals: NestedTradingSignal[];
  total: number;
  filtered_count: number;
}

/**
 * Nested summary response
 */
export interface NestedSummaryResponse {
  model_summary: {
    accuracy: string;
    roc_auc: string;
    up_accuracy: string;
    down_accuracy: string;
  };
  data_summary: {
    total_records: number;
    aligned_signals: number;
    date_range: string;
    unique_symbols: number;
    up_down_split: {
      up_pct: number;
      down_pct: number;
    };
  };
  hypothesis: {
    validated: boolean;
    evidence: string;
  };
}

// ============================================================================
// § 6. ADMIN TYPES
// ============================================================================

/**
 * Scheduler job status
 */
export interface SchedulerJob {
  name: string;
  schedule: string;
  last_run: string;
  next_run: string;
  status: "ENABLED" | "DISABLED" | "RUNNING" | "FAILED";
  target_url?: string;
}

/**
 * BigQuery table info
 */
export interface TableInfo {
  table_name: string;
  row_count: number;
  size_bytes: number;
  last_modified: string;
  schema_fields: number;
}

/**
 * User information
 */
export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user" | "viewer";
  created_at: string;
  last_login?: string;
}

// ============================================================================
// § 7. CHART TYPES
// ============================================================================

/**
 * Chart data point for lightweight-charts
 */
export interface ChartDataPoint {
  time: string | number;
  value: number;
}

/**
 * Candlestick data for lightweight-charts
 */
export interface CandlestickData {
  time: string | number;
  open: number;
  high: number;
  low: number;
  close: number;
}

/**
 * Volume data for charts
 */
export interface VolumeData {
  time: string | number;
  value: number;
  color?: string;
}

// ============================================================================
// § 8. FILTER & QUERY TYPES
// ============================================================================

/**
 * Market data query parameters
 */
export interface MarketDataQuery {
  symbol: string;
  interval?: IntervalString;
  start_date?: string;
  end_date?: string;
  limit?: number;
}

/**
 * Signal filter parameters
 */
export interface SignalFilter {
  asset_type?: AssetType;
  signal_type?: Recommendation;
  min_confidence?: number;
  timeframe?: Timeframe;
  limit?: number;
}

/**
 * Nested signal filter parameters
 */
export interface NestedSignalFilter {
  action?: ActionStatus;
  aligned_only?: boolean;
  symbol?: string;
  limit?: number;
}

// ============================================================================
// § 9. NLP TYPES
// ============================================================================

/**
 * Text-to-SQL query
 */
export interface TextToSQLQuery {
  query: string;
  context?: string;
}

/**
 * Text-to-SQL response
 */
export interface TextToSQLResponse {
  sql: string;
  explanation: string;
  results?: Record<string, unknown>[];
  error?: string;
}

// ============================================================================
// § 10. UTILITY TYPES
// ============================================================================

/**
 * Date range
 */
export interface DateRange {
  start: string;
  end: string;
}

/**
 * Sorting options
 */
export interface SortOptions {
  field: string;
  direction: "asc" | "desc";
}

/**
 * Loading state
 */
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}
