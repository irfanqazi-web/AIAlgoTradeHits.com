/**
 * useMarketData - React Hook for Market Data
 *
 * @version 3.0.0
 */

import { useState, useEffect, useCallback } from 'react';
import { marketDataService } from '@/lib/services/market-data-service';
import type {
  CandleWithIndicators,
  Symbol,
  IntervalString,
  LoadingState,
} from '@/types';

// ============================================================================
// § 1. MARKET DATA HOOK
// ============================================================================

interface UseMarketDataOptions {
  symbol: string;
  interval?: IntervalString;
  limit?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseMarketDataResult extends LoadingState {
  data: CandleWithIndicators[];
  latestPrice: number | null;
  changePct: number | null;
  refetch: () => Promise<void>;
}

export function useMarketData(options: UseMarketDataOptions): UseMarketDataResult {
  const {
    symbol,
    interval = '1day',
    limit = 100,
    autoRefresh = false,
    refreshInterval = 60000,
  } = options;

  const [data, setData] = useState<CandleWithIndicators[]>([]);
  const [latestPrice, setLatestPrice] = useState<number | null>(null);
  const [changePct, setChangePct] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  const fetchData = useCallback(async () => {
    if (!symbol) return;

    setIsLoading(true);
    setError(undefined);

    try {
      const response = await marketDataService.getMarketData(symbol, interval, limit);
      setData(response.data || []);
      setLatestPrice(response.latest_price || null);
      setChangePct(response.change_pct || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch market data');
      setData([]);
    } finally {
      setIsLoading(false);
    }
  }, [symbol, interval, limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const intervalId = setInterval(fetchData, refreshInterval);
    return () => clearInterval(intervalId);
  }, [autoRefresh, refreshInterval, fetchData]);

  return {
    data,
    latestPrice,
    changePct,
    isLoading,
    error,
    refetch: fetchData,
  };
}

// ============================================================================
// § 2. SYMBOLS HOOK
// ============================================================================

interface UseSymbolsResult extends LoadingState {
  symbols: Symbol[];
  search: (query: string) => Promise<Symbol[]>;
}

export function useSymbols(assetType?: string): UseSymbolsResult {
  const [symbols, setSymbols] = useState<Symbol[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  useEffect(() => {
    const fetchSymbols = async () => {
      setIsLoading(true);
      try {
        const data = await marketDataService.getSymbols(assetType as any);
        setSymbols(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch symbols');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSymbols();
  }, [assetType]);

  const search = useCallback(async (query: string): Promise<Symbol[]> => {
    return marketDataService.searchSymbols(query);
  }, []);

  return { symbols, isLoading, error, search };
}

// ============================================================================
// § 3. LIVE PRICE HOOK
// ============================================================================

interface UseLivePriceResult extends LoadingState {
  price: number | null;
  change: number | null;
  changePct: number | null;
}

export function useLivePrice(
  symbol: string,
  refreshInterval: number = 30000
): UseLivePriceResult {
  const [price, setPrice] = useState<number | null>(null);
  const [change, setChange] = useState<number | null>(null);
  const [changePct, setChangePct] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  useEffect(() => {
    if (!symbol) return;

    const fetchPrice = async () => {
      try {
        const data = await marketDataService.getLivePrice(symbol);
        setPrice(data.price);
        setChange(data.change);
        setChangePct(data.changePct);
        setIsLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch price');
        setIsLoading(false);
      }
    };

    fetchPrice();
    const intervalId = setInterval(fetchPrice, refreshInterval);

    return () => clearInterval(intervalId);
  }, [symbol, refreshInterval]);

  return { price, change, changePct, isLoading, error };
}

// ============================================================================
// § 4. DEFAULT EXPORT
// ============================================================================

export default useMarketData;
