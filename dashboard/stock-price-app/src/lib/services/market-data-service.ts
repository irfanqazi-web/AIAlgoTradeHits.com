/**
 * MARKET DATA SERVICE - Orchestration Layer
 * Coordinates between API calls and engines
 *
 * @version 3.0.0
 */

import {
  API_BASE_URLS,
  API_ENDPOINTS,
  DEFAULT_REQUEST_OPTIONS,
  CACHE_CONFIG,
  buildApiUrl,
  buildQueryString,
} from '@/lib/config/api-config';
import {
  calculateGrowthScore,
  calculateCompositeScore,
} from '@/lib/engines/growth-score-engine';
import {
  classifyTrendRegime,
  generateTradingSignal,
} from '@/lib/engines/signal-engine';
import type {
  CandleWithIndicators,
  MarketDataResponse,
  Symbol,
  AssetType,
  IntervalString,
  TradingSignal,
} from '@/types';

// ============================================================================
// § 1. SERVICE CLASS
// ============================================================================

class MarketDataService {
  private cache: Map<string, { data: unknown; timestamp: number }> = new Map();

  /**
   * Fetch market data with indicators
   */
  async getMarketData(
    symbol: string,
    interval: IntervalString = '1day',
    limit: number = 100
  ): Promise<MarketDataResponse> {
    const cacheKey = `market_${symbol}_${interval}_${limit}`;
    const cached = this.getFromCache<MarketDataResponse>(cacheKey, CACHE_CONFIG.MARKET_DATA);
    if (cached) return cached;

    const params = buildQueryString({ symbol, interval, limit });
    const url = buildApiUrl(`${API_ENDPOINTS.MARKET_DATA}?${params}`);

    const response = await this.fetchWithRetry(url);
    const data: MarketDataResponse = await response.json();

    // Enhance with calculated fields
    if (data.data && data.data.length > 0) {
      data.data = this.enhanceWithCalculations(data.data);
    }

    this.setCache(cacheKey, data);
    return data;
  }

  /**
   * Fetch historical data
   */
  async getHistoricalData(
    symbol: string,
    startDate: string,
    endDate: string,
    interval: IntervalString = '1day'
  ): Promise<CandleWithIndicators[]> {
    const params = buildQueryString({
      symbol,
      interval,
      start_date: startDate,
      end_date: endDate,
    });
    const url = buildApiUrl(`${API_ENDPOINTS.HISTORICAL_DATA}?${params}`);

    const response = await this.fetchWithRetry(url);
    const data = await response.json();

    return this.enhanceWithCalculations(data.data || []);
  }

  /**
   * Fetch symbols list
   */
  async getSymbols(assetType?: AssetType): Promise<Symbol[]> {
    const cacheKey = `symbols_${assetType || 'all'}`;
    const cached = this.getFromCache<Symbol[]>(cacheKey, CACHE_CONFIG.SYMBOLS_LIST);
    if (cached) return cached;

    const endpoint = assetType
      ? API_ENDPOINTS.SYMBOLS[assetType.toUpperCase() as keyof typeof API_ENDPOINTS.SYMBOLS]
      : API_ENDPOINTS.SYMBOLS.ALL;

    const url = buildApiUrl(endpoint);
    const response = await this.fetchWithRetry(url);
    const data = await response.json();

    const symbols = data.symbols || data.data || [];
    this.setCache(cacheKey, symbols);
    return symbols;
  }

  /**
   * Search symbols
   */
  async searchSymbols(query: string): Promise<Symbol[]> {
    const allSymbols = await this.getSymbols();
    const lowerQuery = query.toLowerCase();

    return allSymbols.filter(
      (s) =>
        s.symbol.toLowerCase().includes(lowerQuery) ||
        s.name.toLowerCase().includes(lowerQuery)
    );
  }

  /**
   * Get live price
   */
  async getLivePrice(symbol: string): Promise<{
    price: number;
    change: number;
    changePct: number;
  }> {
    const url = buildApiUrl(`${API_ENDPOINTS.LIVE_PRICES}?symbol=${symbol}`);
    const response = await this.fetchWithRetry(url);
    const data = await response.json();

    return {
      price: data.price || 0,
      change: data.change || 0,
      changePct: data.change_pct || 0,
    };
  }

  // ============================================================================
  // § 2. DATA ENHANCEMENT
  // ============================================================================

  /**
   * Enhance candle data with calculated fields
   */
  private enhanceWithCalculations(
    candles: CandleWithIndicators[]
  ): CandleWithIndicators[] {
    return candles.map((candle, index) => {
      // Calculate growth score
      const growthScore = calculateGrowthScore({
        rsi_14: candle.rsi_14,
        macd_histogram: candle.macd_histogram,
        adx: candle.adx,
        close: candle.close,
        sma_200: candle.sma_200,
      });

      // Classify trend regime
      const trendRegime = classifyTrendRegime(
        candle.close,
        candle.sma_50 || candle.close,
        candle.sma_200 || candle.close,
        candle.adx || 0
      );

      // Detect EMA cycle
      const inRiseCycle =
        candle.ema_12 !== undefined &&
        candle.ema_26 !== undefined &&
        candle.ema_12 > candle.ema_26;

      // Detect cycle starts
      let riseCycleStart = false;
      let fallCycleStart = false;

      if (index > 0) {
        const prev = candles[index - 1];
        if (
          candle.ema_12 !== undefined &&
          candle.ema_26 !== undefined &&
          prev.ema_12 !== undefined &&
          prev.ema_26 !== undefined
        ) {
          riseCycleStart =
            candle.ema_12 > candle.ema_26 && prev.ema_12 <= prev.ema_26;
          fallCycleStart =
            candle.ema_12 < candle.ema_26 && prev.ema_12 >= prev.ema_26;
        }
      }

      return {
        ...candle,
        growth_score: growthScore,
        trend_regime: trendRegime,
        in_rise_cycle: inRiseCycle,
        rise_cycle_start: riseCycleStart,
        fall_cycle_start: fallCycleStart,
      };
    });
  }

  // ============================================================================
  // § 3. HELPER METHODS
  // ============================================================================

  /**
   * Fetch with retry logic
   */
  private async fetchWithRetry(
    url: string,
    options: RequestInit = {},
    retries: number = DEFAULT_REQUEST_OPTIONS.retries
  ): Promise<Response> {
    const fetchOptions: RequestInit = {
      ...options,
      headers: {
        ...DEFAULT_REQUEST_OPTIONS.headers,
        ...options.headers,
      },
    };

    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, fetchOptions);
        if (response.ok) return response;

        if (response.status >= 500 && i < retries - 1) {
          await this.delay(DEFAULT_REQUEST_OPTIONS.retryDelay * (i + 1));
          continue;
        }

        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      } catch (error) {
        if (i === retries - 1) throw error;
        await this.delay(DEFAULT_REQUEST_OPTIONS.retryDelay * (i + 1));
      }
    }

    throw new Error('Max retries exceeded');
  }

  /**
   * Get from cache if valid
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

  /**
   * Delay helper
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// ============================================================================
// § 4. SINGLETON EXPORT
// ============================================================================

export const marketDataService = new MarketDataService();
export default marketDataService;
