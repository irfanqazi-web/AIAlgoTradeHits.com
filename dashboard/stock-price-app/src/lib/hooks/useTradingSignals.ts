/**
 * useTradingSignals - React Hook for Trading Signals
 *
 * @version 3.0.0
 */

import { useState, useEffect, useCallback } from 'react';
import { tradingSignalService } from '@/lib/services/trading-signal-service';
import type {
  TradingSignal,
  NestedTradingSignal,
  NestedSummaryResponse,
  SignalFilter,
  NestedSignalFilter,
  ActionStatus,
  LoadingState,
} from '@/types';

// ============================================================================
// § 1. TRADING SIGNALS HOOK
// ============================================================================

interface UseTradingSignalsOptions {
  filter?: SignalFilter;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseTradingSignalsResult extends LoadingState {
  signals: TradingSignal[];
  refetch: () => Promise<void>;
}

export function useTradingSignals(
  options: UseTradingSignalsOptions = {}
): UseTradingSignalsResult {
  const { filter, autoRefresh = false, refreshInterval = 300000 } = options;

  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  const fetchSignals = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);

    try {
      const data = await tradingSignalService.getTradingSignals(filter);
      setSignals(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch signals');
      setSignals([]);
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchSignals();
  }, [fetchSignals]);

  useEffect(() => {
    if (!autoRefresh) return;

    const intervalId = setInterval(fetchSignals, refreshInterval);
    return () => clearInterval(intervalId);
  }, [autoRefresh, refreshInterval, fetchSignals]);

  return { signals, isLoading, error, refetch: fetchSignals };
}

// ============================================================================
// § 2. NESTED SIGNALS HOOK
// ============================================================================

interface UseNestedSignalsOptions {
  filter?: NestedSignalFilter;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseNestedSignalsResult extends LoadingState {
  signals: NestedTradingSignal[];
  total: number;
  summary: NestedSummaryResponse | null;
  refetch: () => Promise<void>;
}

export function useNestedSignals(
  options: UseNestedSignalsOptions = {}
): UseNestedSignalsResult {
  const { filter, autoRefresh = false, refreshInterval = 300000 } = options;

  const [signals, setSignals] = useState<NestedTradingSignal[]>([]);
  const [total, setTotal] = useState(0);
  const [summary, setSummary] = useState<NestedSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);

    try {
      const [signalsResponse, summaryResponse] = await Promise.all([
        tradingSignalService.getNestedSignals(filter),
        tradingSignalService.getNestedSummary(),
      ]);

      setSignals(signalsResponse.signals || []);
      setTotal(signalsResponse.total || 0);
      setSummary(summaryResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch nested signals');
      setSignals([]);
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const intervalId = setInterval(fetchData, refreshInterval);
    return () => clearInterval(intervalId);
  }, [autoRefresh, refreshInterval, fetchData]);

  return { signals, total, summary, isLoading, error, refetch: fetchData };
}

// ============================================================================
// § 3. RISE CYCLE CANDIDATES HOOK
// ============================================================================

interface UseRiseCycleCandidatesResult extends LoadingState {
  candidates: TradingSignal[];
  refetch: () => Promise<void>;
}

export function useRiseCycleCandidates(
  limit: number = 20
): UseRiseCycleCandidatesResult {
  const [candidates, setCandidates] = useState<TradingSignal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  const fetchCandidates = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);

    try {
      const data = await tradingSignalService.getRiseCycleCandidates(limit);
      setCandidates(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch candidates');
      setCandidates([]);
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  return { candidates, isLoading, error, refetch: fetchCandidates };
}

// ============================================================================
// § 4. TOP SIGNALS HOOK
// ============================================================================

interface UseTopSignalsResult extends LoadingState {
  executeSignals: NestedTradingSignal[];
  readySignals: NestedTradingSignal[];
  watchSignals: NestedTradingSignal[];
  refetch: () => Promise<void>;
}

export function useTopSignals(): UseTopSignalsResult {
  const [executeSignals, setExecuteSignals] = useState<NestedTradingSignal[]>([]);
  const [readySignals, setReadySignals] = useState<NestedTradingSignal[]>([]);
  const [watchSignals, setWatchSignals] = useState<NestedTradingSignal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | undefined>();

  const fetchSignals = useCallback(async () => {
    setIsLoading(true);
    setError(undefined);

    try {
      const [execute, ready, watch] = await Promise.all([
        tradingSignalService.getSignalsByAction('EXECUTE'),
        tradingSignalService.getSignalsByAction('READY'),
        tradingSignalService.getSignalsByAction('WATCH'),
      ]);

      setExecuteSignals(execute.slice(0, 10));
      setReadySignals(ready.slice(0, 10));
      setWatchSignals(watch.slice(0, 10));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch top signals');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSignals();
  }, [fetchSignals]);

  return {
    executeSignals,
    readySignals,
    watchSignals,
    isLoading,
    error,
    refetch: fetchSignals,
  };
}

// ============================================================================
// § 5. DEFAULT EXPORT
// ============================================================================

export default useTradingSignals;
