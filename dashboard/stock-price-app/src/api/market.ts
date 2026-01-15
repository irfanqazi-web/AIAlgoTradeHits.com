/**
 * Market API - Market data route handlers
 *
 * Handles all market data related API calls.
 *
 * @version 5.1.0
 */

import { apiClient, ApiResponse } from './client';
import { API_CONFIG, AssetType, Timeframe, ASSET_CONFIG } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface Symbol {
  symbol: string;
  name: string;
  type: AssetType;
  exchange?: string;
  currency?: string;
}

export interface Candle {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  // Technical Indicators
  rsi_14?: number;
  macd?: number;
  macd_signal?: number;
  macd_histogram?: number;
  sma_20?: number;
  sma_50?: number;
  sma_200?: number;
  ema_12?: number;
  ema_26?: number;
  ema_50?: number;
  ema_200?: number;
  adx?: number;
  atr_14?: number;
  bb_upper?: number;
  bb_middle?: number;
  bb_lower?: number;
  // Computed
  growth_score?: number;
  trend_regime?: string;
  recommendation?: string;
  in_rise_cycle?: boolean;
}

export interface LivePrice {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
}

export interface SearchResult {
  symbol: string;
  name: string;
  type: string;
  exchange: string;
  currency: string;
}

// ============================================================================
// § 2. API FUNCTIONS
// ============================================================================

/**
 * Get list of available symbols
 */
export async function getSymbols(
  assetType?: AssetType
): Promise<ApiResponse<Symbol[]>> {
  const params: Record<string, string> = {};
  if (assetType) {
    params.asset_type = assetType;
  }
  return apiClient.get<Symbol[]>(API_CONFIG.endpoints.market.symbols, params);
}

/**
 * Get historical OHLCV data with indicators
 */
export async function getHistory(
  symbol: string,
  assetType: AssetType = 'stocks',
  timeframe: Timeframe = 'daily',
  limit = 200
): Promise<ApiResponse<Candle[]>> {
  const params: Record<string, string | number> = {
    symbol,
    asset_type: assetType,
    interval: ASSET_CONFIG.timeframes[timeframe].interval,
    limit,
  };
  return apiClient.get<Candle[]>(API_CONFIG.endpoints.market.history, params);
}

/**
 * Get live price for a symbol
 */
export async function getLivePrice(
  symbol: string,
  assetType: AssetType = 'stocks'
): Promise<ApiResponse<LivePrice>> {
  const params = { symbol, asset_type: assetType };
  return apiClient.get<LivePrice>(API_CONFIG.endpoints.market.livePrice, params);
}

/**
 * Search for symbols
 */
export async function searchSymbols(
  query: string,
  assetType?: AssetType
): Promise<ApiResponse<SearchResult[]>> {
  const params: Record<string, string> = { q: query };
  if (assetType) {
    params.asset_type = assetType;
  }
  return apiClient.get<SearchResult[]>(API_CONFIG.endpoints.market.search, params);
}

/**
 * Get multiple symbols' data at once
 */
export async function getBatchData(
  symbols: string[],
  assetType: AssetType = 'stocks',
  timeframe: Timeframe = 'daily'
): Promise<ApiResponse<Record<string, Candle[]>>> {
  const params = {
    symbols: symbols.join(','),
    asset_type: assetType,
    interval: ASSET_CONFIG.timeframes[timeframe].interval,
  };
  return apiClient.get<Record<string, Candle[]>>('/api/batch', params);
}

// ============================================================================
// § 3. EXPORT
// ============================================================================

export const marketApi = {
  getSymbols,
  getHistory,
  getLivePrice,
  searchSymbols,
  getBatchData,
};

export default marketApi;
