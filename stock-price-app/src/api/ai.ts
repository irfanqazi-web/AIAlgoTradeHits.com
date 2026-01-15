/**
 * AI API - AI/ML route handlers
 *
 * Handles all AI-related API calls including signals, predictions, and analysis.
 *
 * @version 5.1.0
 */

import { apiClient, ApiResponse } from './client';
import { API_CONFIG, AssetType, Timeframe } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface TradingSignal {
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';
  action: 'EXECUTE' | 'READY' | 'WATCH' | 'WAIT';
  growthScore: number;
  confidence: number;
  rsi: number;
  macd: number;
  trend: string;
  timestamp: string;
}

export interface NestedSignal extends TradingSignal {
  dailyScore: number;
  hourlyScore: number;
  fiveMinScore: number;
  alignedPct: number;
  isAligned: boolean;
  dailyTrend: string;
  hourlyTrend: string;
  fiveMinTrend: string;
}

export interface RiseCycleCandidate {
  symbol: string;
  datetime: string;
  close: number;
  ema_12: number;
  ema_26: number;
  rsi: number;
  volume: number;
  growthScore: number;
  cycleStartDate: string;
  daysSinceCycleStart: number;
}

export interface MLPrediction {
  symbol: string;
  predictedDirection: 'UP' | 'DOWN' | 'NEUTRAL';
  probability: number;
  confidence: number;
  features: {
    rsi: number;
    macd: number;
    adx: number;
    trend: string;
  };
  timestamp: string;
}

export interface GrowthScreenerResult {
  symbol: string;
  name: string;
  price: number;
  growthScore: number;
  trendRegime: string;
  inRiseCycle: boolean;
  recommendation: string;
  rsi: number;
  macd: number;
}

export interface TextToSQLResponse {
  query: string;
  results: Record<string, unknown>[];
  rowCount: number;
  executionTime: number;
}

export interface PatternRecognition {
  symbol: string;
  patterns: {
    name: string;
    type: 'bullish' | 'bearish' | 'neutral';
    confidence: number;
    description: string;
  }[];
  timestamp: string;
}

// ============================================================================
// § 2. API FUNCTIONS
// ============================================================================

/**
 * Get trading signals for assets
 */
export async function getTradingSignals(
  assetType: AssetType = 'stocks',
  minGrowthScore = 0
): Promise<ApiResponse<TradingSignal[]>> {
  const params = {
    asset_type: assetType,
    min_growth_score: minGrowthScore,
  };
  return apiClient.get<TradingSignal[]>(API_CONFIG.endpoints.ai.tradingSignals, params);
}

/**
 * Get nested (multi-timeframe) signals
 */
export async function getNestedSignals(
  assetType: AssetType = 'stocks',
  minAlignment = 0.6
): Promise<ApiResponse<NestedSignal[]>> {
  const params = {
    asset_type: assetType,
    min_alignment: minAlignment,
  };
  return apiClient.get<NestedSignal[]>(API_CONFIG.endpoints.ai.nestedSignals, params);
}

/**
 * Get rise cycle candidates (EMA crossover detection)
 */
export async function getRiseCycleCandidates(
  assetType: AssetType = 'stocks',
  maxDays = 5
): Promise<ApiResponse<RiseCycleCandidate[]>> {
  const params = {
    asset_type: assetType,
    max_days: maxDays,
  };
  return apiClient.get<RiseCycleCandidate[]>(API_CONFIG.endpoints.ai.riseCycleCandidates, params);
}

/**
 * Get ML predictions
 */
export async function getMLPredictions(
  assetType: AssetType = 'stocks',
  minProbability = 0.5
): Promise<ApiResponse<MLPrediction[]>> {
  const params = {
    asset_type: assetType,
    min_probability: minProbability,
  };
  return apiClient.get<MLPrediction[]>(API_CONFIG.endpoints.ai.mlPredictions, params);
}

/**
 * Get growth screener results
 */
export async function getGrowthScreener(
  assetType: AssetType = 'stocks',
  minScore = 75,
  limit = 20
): Promise<ApiResponse<GrowthScreenerResult[]>> {
  const params = {
    asset_type: assetType,
    min_score: minScore,
    limit,
  };
  return apiClient.get<GrowthScreenerResult[]>(API_CONFIG.endpoints.ai.growthScreener, params);
}

/**
 * Execute natural language query (Text-to-SQL)
 */
export async function executeTextToSQL(
  query: string
): Promise<ApiResponse<TextToSQLResponse>> {
  return apiClient.post<TextToSQLResponse>(API_CONFIG.endpoints.ai.textToSQL, { query });
}

/**
 * Get pattern recognition analysis
 */
export async function getPatternRecognition(
  symbol: string,
  assetType: AssetType = 'stocks'
): Promise<ApiResponse<PatternRecognition>> {
  const params = {
    symbol,
    asset_type: assetType,
  };
  return apiClient.get<PatternRecognition>(API_CONFIG.endpoints.ai.patternRecognition, params);
}

/**
 * Get sentiment analysis
 */
export async function getSentimentAnalysis(
  symbol: string,
  assetType: AssetType = 'stocks'
): Promise<ApiResponse<{ symbol: string; score: number; label: string; sources: string[] }>> {
  const params = {
    symbol,
    asset_type: assetType,
  };
  return apiClient.get(API_CONFIG.endpoints.ai.sentiment, params);
}

// ============================================================================
// § 3. EXPORT
// ============================================================================

export const aiApi = {
  getTradingSignals,
  getNestedSignals,
  getRiseCycleCandidates,
  getMLPredictions,
  getGrowthScreener,
  executeTextToSQL,
  getPatternRecognition,
  getSentimentAnalysis,
};

export default aiApi;
