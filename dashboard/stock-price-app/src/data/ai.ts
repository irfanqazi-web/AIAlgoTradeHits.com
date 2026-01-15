/**
 * AI Data Service - AI/ML data access layer
 *
 * Handles fetching and transforming AI prediction and signal data.
 * Pure data operations, no UI concerns.
 *
 * @version 5.1.0
 */

import { api } from '@/api';
import type { TradingSignal, NestedSignal, MLPrediction, GrowthScreenerResult } from '@/api';
import { AssetType } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface SignalData {
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';
  action: 'EXECUTE' | 'READY' | 'WATCH' | 'WAIT';
  growthScore: number;
  confidence: number;
  rsi: number;
  macd: number;
  trend: string;
  timestamp: Date;
}

export interface NestedSignalData extends SignalData {
  dailyScore: number;
  hourlyScore: number;
  fiveMinScore: number;
  alignmentPercent: number;
  isAligned: boolean;
  trends: {
    daily: string;
    hourly: string;
    fiveMin: string;
  };
}

export interface PredictionData {
  symbol: string;
  direction: 'UP' | 'DOWN' | 'NEUTRAL';
  probability: number;
  confidence: number;
  features: {
    rsi: number;
    macd: number;
    adx: number;
    trend: string;
  };
  timestamp: Date;
}

export interface GrowthData {
  symbol: string;
  name: string;
  price: number;
  growthScore: number;
  trendRegime: string;
  inRiseCycle: boolean;
  recommendation: string;
  indicators: {
    rsi: number;
    macd: number;
  };
}

export interface RiseCycleData {
  symbol: string;
  datetime: Date;
  price: number;
  ema12: number;
  ema26: number;
  rsi: number;
  volume: number;
  growthScore: number;
  cycleStartDate: Date;
  daysSinceCycleStart: number;
}

// ============================================================================
// § 2. TRANSFORMERS
// ============================================================================

function transformSignal(signal: TradingSignal): SignalData {
  return {
    symbol: signal.symbol,
    signal: signal.signal as SignalData['signal'],
    action: signal.action,
    growthScore: signal.growthScore,
    confidence: signal.confidence,
    rsi: signal.rsi,
    macd: signal.macd,
    trend: signal.trend,
    timestamp: new Date(signal.timestamp),
  };
}

function transformNestedSignal(signal: NestedSignal): NestedSignalData {
  return {
    ...transformSignal(signal),
    dailyScore: signal.dailyScore,
    hourlyScore: signal.hourlyScore,
    fiveMinScore: signal.fiveMinScore,
    alignmentPercent: signal.alignedPct * 100,
    isAligned: signal.isAligned,
    trends: {
      daily: signal.dailyTrend,
      hourly: signal.hourlyTrend,
      fiveMin: signal.fiveMinTrend,
    },
  };
}

function transformPrediction(pred: MLPrediction): PredictionData {
  return {
    symbol: pred.symbol,
    direction: pred.predictedDirection,
    probability: pred.probability,
    confidence: pred.confidence,
    features: pred.features,
    timestamp: new Date(pred.timestamp),
  };
}

function transformGrowth(result: GrowthScreenerResult): GrowthData {
  return {
    symbol: result.symbol,
    name: result.name,
    price: result.price,
    growthScore: result.growthScore,
    trendRegime: result.trendRegime,
    inRiseCycle: result.inRiseCycle,
    recommendation: result.recommendation,
    indicators: {
      rsi: result.rsi,
      macd: result.macd,
    },
  };
}

// ============================================================================
// § 3. SERVICE
// ============================================================================

export const aiDataService = {
  /**
   * Get trading signals
   */
  async getTradingSignals(
    assetType: AssetType = 'stocks',
    minGrowthScore = 0
  ): Promise<SignalData[]> {
    const response = await api.ai.getTradingSignals(assetType, minGrowthScore);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to fetch signals');
    }
    return response.data.map(transformSignal);
  },

  /**
   * Get nested (multi-timeframe) signals
   */
  async getNestedSignals(
    assetType: AssetType = 'stocks',
    minAlignment = 0.6
  ): Promise<NestedSignalData[]> {
    const response = await api.ai.getNestedSignals(assetType, minAlignment);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to fetch nested signals');
    }
    return response.data.map(transformNestedSignal);
  },

  /**
   * Get ML predictions
   */
  async getMLPredictions(
    assetType: AssetType = 'stocks',
    minProbability = 0.5
  ): Promise<PredictionData[]> {
    const response = await api.ai.getMLPredictions(assetType, minProbability);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to fetch predictions');
    }
    return response.data.map(transformPrediction);
  },

  /**
   * Get growth screener results
   */
  async getGrowthScreener(
    assetType: AssetType = 'stocks',
    minScore = 75,
    limit = 20
  ): Promise<GrowthData[]> {
    const response = await api.ai.getGrowthScreener(assetType, minScore, limit);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to fetch growth data');
    }
    return response.data.map(transformGrowth);
  },

  /**
   * Get rise cycle candidates
   */
  async getRiseCycleCandidates(
    assetType: AssetType = 'stocks',
    maxDays = 5
  ): Promise<RiseCycleData[]> {
    const response = await api.ai.getRiseCycleCandidates(assetType, maxDays);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to fetch rise cycle data');
    }
    return response.data.map((rc) => ({
      symbol: rc.symbol,
      datetime: new Date(rc.datetime),
      price: rc.close,
      ema12: rc.ema_12,
      ema26: rc.ema_26,
      rsi: rc.rsi,
      volume: rc.volume,
      growthScore: rc.growthScore,
      cycleStartDate: new Date(rc.cycleStartDate),
      daysSinceCycleStart: rc.daysSinceCycleStart,
    }));
  },

  /**
   * Execute natural language query
   */
  async executeNaturalLanguageQuery(
    query: string
  ): Promise<{ results: Record<string, unknown>[]; rowCount: number }> {
    const response = await api.ai.executeTextToSQL(query);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to execute query');
    }
    return {
      results: response.data.results,
      rowCount: response.data.rowCount,
    };
  },

  /**
   * Get top signals by action
   */
  async getTopSignalsByAction(
    assetType: AssetType = 'stocks',
    action: 'EXECUTE' | 'READY' | 'WATCH' = 'EXECUTE',
    limit = 10
  ): Promise<SignalData[]> {
    const signals = await this.getTradingSignals(assetType, 50);
    return signals
      .filter((s) => s.action === action)
      .sort((a, b) => b.growthScore - a.growthScore)
      .slice(0, limit);
  },
};

export default aiDataService;
