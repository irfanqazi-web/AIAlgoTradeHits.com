/**
 * TRADING SIGNAL SERVICE - Orchestration Layer
 * Coordinates signal generation and AI predictions
 *
 * @version 3.0.0
 */

import {
  API_BASE_URLS,
  API_ENDPOINTS,
  buildApiUrl,
  buildQueryString,
  CACHE_CONFIG,
} from '@/lib/config/api-config';
import {
  generateTradingSignal,
  batchGenerateSignals,
  getBuySignals,
  getSellSignals,
} from '@/lib/engines/signal-engine';
import {
  classifyNestedSignal,
  determineActionStatus,
  filterByActionStatus,
  filterAlignedOnly,
  sortByScore,
  getTopSignals,
} from '@/lib/engines/nested-ml-engine';
import type {
  TradingSignal,
  NestedTradingSignal,
  NestedSignalsResponse,
  NestedSummaryResponse,
  ActionStatus,
  SignalFilter,
  NestedSignalFilter,
  CandleWithIndicators,
} from '@/types';

// ============================================================================
// § 1. SERVICE CLASS
// ============================================================================

class TradingSignalService {
  private cache: Map<string, { data: unknown; timestamp: number }> = new Map();

  // ============================================================================
  // § 2. AI TRADING SIGNALS
  // ============================================================================

  /**
   * Fetch AI-generated trading signals
   */
  async getTradingSignals(filter?: SignalFilter): Promise<TradingSignal[]> {
    const params = buildQueryString({
      asset_type: filter?.asset_type,
      signal_type: filter?.signal_type,
      min_confidence: filter?.min_confidence,
      timeframe: filter?.timeframe,
      limit: filter?.limit || 50,
    });

    const url = buildApiUrl(`${API_ENDPOINTS.AI.TRADING_SIGNALS}?${params}`);
    const response = await fetch(url);
    const data = await response.json();

    return data.signals || [];
  }

  /**
   * Fetch rise cycle candidates
   */
  async getRiseCycleCandidates(limit: number = 20): Promise<TradingSignal[]> {
    const url = buildApiUrl(
      `${API_ENDPOINTS.AI.RISE_CYCLE_CANDIDATES}?limit=${limit}`
    );
    const response = await fetch(url);
    const data = await response.json();

    return data.candidates || [];
  }

  /**
   * Fetch ML predictions
   */
  async getMLPredictions(
    symbol?: string,
    limit: number = 50
  ): Promise<TradingSignal[]> {
    const params = buildQueryString({ symbol, limit });
    const url = buildApiUrl(`${API_ENDPOINTS.AI.ML_PREDICTIONS}?${params}`);
    const response = await fetch(url);
    const data = await response.json();

    return data.predictions || [];
  }

  /**
   * Fetch growth screener results
   */
  async getGrowthScreener(minScore: number = 75): Promise<TradingSignal[]> {
    const url = buildApiUrl(
      `${API_ENDPOINTS.AI.GROWTH_SCREENER}?min_score=${minScore}`
    );
    const response = await fetch(url);
    const data = await response.json();

    return data.results || [];
  }

  // ============================================================================
  // § 3. NESTED MULTI-TIMEFRAME SIGNALS
  // ============================================================================

  /**
   * Fetch nested multi-timeframe signals
   */
  async getNestedSignals(
    filter?: NestedSignalFilter
  ): Promise<NestedSignalsResponse> {
    const cacheKey = `nested_${JSON.stringify(filter)}`;
    const cached = this.getFromCache<NestedSignalsResponse>(
      cacheKey,
      CACHE_CONFIG.ML_PREDICTIONS
    );
    if (cached) return cached;

    const params = buildQueryString({
      action: filter?.action,
      aligned_only: filter?.aligned_only,
      symbol: filter?.symbol,
      limit: filter?.limit || 100,
    });

    const url = buildApiUrl(`${API_ENDPOINTS.AI.NESTED_SIGNALS}?${params}`);
    const response = await fetch(url);
    const data: NestedSignalsResponse = await response.json();

    this.setCache(cacheKey, data);
    return data;
  }

  /**
   * Fetch nested model summary
   */
  async getNestedSummary(): Promise<NestedSummaryResponse> {
    const cacheKey = 'nested_summary';
    const cached = this.getFromCache<NestedSummaryResponse>(
      cacheKey,
      CACHE_CONFIG.ML_PREDICTIONS
    );
    if (cached) return cached;

    const url = buildApiUrl(API_ENDPOINTS.AI.NESTED_SUMMARY);
    const response = await fetch(url);
    const data: NestedSummaryResponse = await response.json();

    this.setCache(cacheKey, data);
    return data;
  }

  /**
   * Get top nested signals (EXECUTE and READY)
   */
  async getTopNestedSignals(limit: number = 10): Promise<NestedTradingSignal[]> {
    const response = await this.getNestedSignals({ limit: 100 });
    return getTopSignals(response.signals, limit);
  }

  /**
   * Get signals by action status
   */
  async getSignalsByAction(
    action: ActionStatus
  ): Promise<NestedTradingSignal[]> {
    const response = await this.getNestedSignals({ action, limit: 100 });
    return response.signals;
  }

  /**
   * Get aligned signals only
   */
  async getAlignedSignals(): Promise<NestedTradingSignal[]> {
    const response = await this.getNestedSignals({
      aligned_only: true,
      limit: 100,
    });
    return response.signals;
  }

  // ============================================================================
  // § 4. LOCAL SIGNAL GENERATION
  // ============================================================================

  /**
   * Generate signals from candle data locally
   */
  generateLocalSignals(
    candles: CandleWithIndicators[],
    symbol: string
  ): TradingSignal[] {
    return batchGenerateSignals(candles, symbol);
  }

  /**
   * Get buy signals from local data
   */
  getLocalBuySignals(
    candles: CandleWithIndicators[],
    symbol: string
  ): TradingSignal[] {
    const signals = this.generateLocalSignals(candles, symbol);
    return getBuySignals(signals);
  }

  /**
   * Get sell signals from local data
   */
  getLocalSellSignals(
    candles: CandleWithIndicators[],
    symbol: string
  ): TradingSignal[] {
    const signals = this.generateLocalSignals(candles, symbol);
    return getSellSignals(signals);
  }

  // ============================================================================
  // § 5. PATTERN RECOGNITION
  // ============================================================================

  /**
   * Fetch AI pattern recognition results
   */
  async getPatternRecognition(symbol: string): Promise<{
    patterns: Array<{
      name: string;
      type: 'bullish' | 'bearish' | 'neutral';
      confidence: number;
    }>;
  }> {
    const url = buildApiUrl(
      `${API_ENDPOINTS.AI.PATTERN_RECOGNITION}?symbol=${symbol}`
    );
    const response = await fetch(url);
    return response.json();
  }

  // ============================================================================
  // § 6. HELPER METHODS
  // ============================================================================

  /**
   * Get from cache
   */
  private getFromCache<T>(key: string, maxAge: number): T | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < maxAge) {
      return cached.data as T;
    }
    return null;
  }

  /**
   * Set cache
   */
  private setCache(key: string, data: unknown): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }
}

// ============================================================================
// § 7. SINGLETON EXPORT
// ============================================================================

export const tradingSignalService = new TradingSignalService();
export default tradingSignalService;
