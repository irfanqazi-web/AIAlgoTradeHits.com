/**
 * Market Data Service - Market data access layer
 *
 * Handles fetching and transforming market data.
 * Pure data operations, no UI concerns.
 *
 * @version 5.1.0
 */

import { api } from '@/api';
import type { Candle, Symbol as ApiSymbol } from '@/api';
import { AssetType, Timeframe, ASSET_CONFIG } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface MarketDataPoint {
  datetime: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface CandleData extends MarketDataPoint {
  // Technical Indicators
  rsi?: number;
  macd?: number;
  macdSignal?: number;
  macdHistogram?: number;
  sma20?: number;
  sma50?: number;
  sma200?: number;
  ema12?: number;
  ema26?: number;
  ema50?: number;
  ema200?: number;
  adx?: number;
  atr?: number;
  bbUpper?: number;
  bbMiddle?: number;
  bbLower?: number;
  // Computed
  growthScore?: number;
  trendRegime?: string;
  recommendation?: string;
  inRiseCycle?: boolean;
}

export interface SymbolInfo {
  symbol: string;
  name: string;
  type: AssetType;
  exchange?: string;
  currency?: string;
}

export interface TimeframeData {
  timeframe: Timeframe;
  interval: string;
  label: string;
  candles: CandleData[];
}

// ============================================================================
// § 2. TRANSFORMERS
// ============================================================================

/**
 * Transform API candle to CandleData
 */
function transformCandle(candle: Candle): CandleData {
  return {
    datetime: new Date(candle.datetime),
    open: candle.open,
    high: candle.high,
    low: candle.low,
    close: candle.close,
    volume: candle.volume,
    rsi: candle.rsi_14,
    macd: candle.macd,
    macdSignal: candle.macd_signal,
    macdHistogram: candle.macd_histogram,
    sma20: candle.sma_20,
    sma50: candle.sma_50,
    sma200: candle.sma_200,
    ema12: candle.ema_12,
    ema26: candle.ema_26,
    ema50: candle.ema_50,
    ema200: candle.ema_200,
    adx: candle.adx,
    atr: candle.atr_14,
    bbUpper: candle.bb_upper,
    bbMiddle: candle.bb_middle,
    bbLower: candle.bb_lower,
    growthScore: candle.growth_score,
    trendRegime: candle.trend_regime,
    recommendation: candle.recommendation,
    inRiseCycle: candle.in_rise_cycle,
  };
}

/**
 * Transform API symbol to SymbolInfo
 */
function transformSymbol(symbol: ApiSymbol): SymbolInfo {
  return {
    symbol: symbol.symbol,
    name: symbol.name,
    type: symbol.type,
    exchange: symbol.exchange,
    currency: symbol.currency,
  };
}

// ============================================================================
// § 3. SERVICE
// ============================================================================

export const marketDataService = {
  /**
   * Get available symbols
   */
  async getSymbols(assetType?: AssetType): Promise<SymbolInfo[]> {
    const response = await api.market.getSymbols(assetType);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to fetch symbols');
    }
    return response.data.map(transformSymbol);
  },

  /**
   * Get historical candle data
   */
  async getHistory(
    symbol: string,
    assetType: AssetType = 'stocks',
    timeframe: Timeframe = 'daily',
    limit = 200
  ): Promise<CandleData[]> {
    const response = await api.market.getHistory(symbol, assetType, timeframe, limit);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to fetch history');
    }
    return response.data.map(transformCandle);
  },

  /**
   * Get multi-timeframe data
   */
  async getMultiTimeframeData(
    symbol: string,
    assetType: AssetType = 'stocks'
  ): Promise<TimeframeData[]> {
    const timeframes: Timeframe[] = ['daily', 'hourly', '5min'];
    const results = await Promise.all(
      timeframes.map(async (tf) => {
        const candles = await this.getHistory(symbol, assetType, tf);
        return {
          timeframe: tf,
          interval: ASSET_CONFIG.timeframes[tf].interval,
          label: ASSET_CONFIG.timeframes[tf].label,
          candles,
        };
      })
    );
    return results;
  },

  /**
   * Get current price
   */
  async getCurrentPrice(
    symbol: string,
    assetType: AssetType = 'stocks'
  ): Promise<{
    price: number;
    change: number;
    changePercent: number;
    volume: number;
  }> {
    const response = await api.market.getLivePrice(symbol, assetType);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to fetch price');
    }
    return {
      price: response.data.price,
      change: response.data.change,
      changePercent: response.data.change_percent,
      volume: response.data.volume,
    };
  },

  /**
   * Search symbols
   */
  async searchSymbols(query: string, assetType?: AssetType): Promise<SymbolInfo[]> {
    const response = await api.market.searchSymbols(query, assetType);
    if (!response.success || !response.data) {
      return [];
    }
    return response.data.map((r) => ({
      symbol: r.symbol,
      name: r.name,
      type: r.type as AssetType,
      exchange: r.exchange,
      currency: r.currency,
    }));
  },

  /**
   * Get latest candle for symbol
   */
  async getLatestCandle(
    symbol: string,
    assetType: AssetType = 'stocks',
    timeframe: Timeframe = 'daily'
  ): Promise<CandleData | null> {
    const candles = await this.getHistory(symbol, assetType, timeframe, 1);
    return candles.length > 0 ? candles[0] : null;
  },
};

export default marketDataService;
