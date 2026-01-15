/**
 * Trading Context - Global trading state management
 *
 * Manages trading data, signals, and market state across the application.
 * Provides centralized access to trading functionality.
 *
 * @version 5.1.0
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useReducer,
  ReactNode,
} from 'react';
import { ASSET_CONFIG, UI_CONFIG, AssetType, Timeframe } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  timestamp: string;
}

export interface TradingSignal {
  symbol: string;
  signal: string;
  action: 'EXECUTE' | 'READY' | 'WATCH' | 'WAIT';
  growthScore: number;
  confidence: number;
  timestamp: string;
}

export interface NestedSignal extends TradingSignal {
  dailyScore: number;
  hourlyScore: number;
  fiveMinScore: number;
  alignedPct: number;
  isAligned: boolean;
}

interface TradingState {
  // Selection State
  selectedSymbol: string | null;
  selectedAssetType: AssetType;
  selectedTimeframe: Timeframe;

  // Market Data
  marketData: MarketData[];
  isLoadingMarketData: boolean;

  // Signals
  signals: TradingSignal[];
  nestedSignals: NestedSignal[];
  isLoadingSignals: boolean;

  // Watchlist
  watchlist: string[];

  // Errors
  error: string | null;
}

type TradingAction =
  | { type: 'SET_SYMBOL'; payload: string | null }
  | { type: 'SET_ASSET_TYPE'; payload: AssetType }
  | { type: 'SET_TIMEFRAME'; payload: Timeframe }
  | { type: 'SET_MARKET_DATA'; payload: MarketData[] }
  | { type: 'SET_SIGNALS'; payload: TradingSignal[] }
  | { type: 'SET_NESTED_SIGNALS'; payload: NestedSignal[] }
  | { type: 'SET_LOADING_MARKET_DATA'; payload: boolean }
  | { type: 'SET_LOADING_SIGNALS'; payload: boolean }
  | { type: 'ADD_TO_WATCHLIST'; payload: string }
  | { type: 'REMOVE_FROM_WATCHLIST'; payload: string }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' };

interface TradingContextValue extends TradingState {
  // Actions
  setSelectedSymbol: (symbol: string | null) => void;
  setAssetType: (type: AssetType) => void;
  setTimeframe: (timeframe: Timeframe) => void;
  addToWatchlist: (symbol: string) => void;
  removeFromWatchlist: (symbol: string) => void;
  isInWatchlist: (symbol: string) => boolean;
  clearError: () => void;

  // Computed
  currentAssetConfig: typeof ASSET_CONFIG.types.stocks;
  currentTimeframeConfig: typeof ASSET_CONFIG.timeframes.daily;
}

interface TradingProviderProps {
  children: ReactNode;
}

// ============================================================================
// § 2. REDUCER
// ============================================================================

const initialState: TradingState = {
  selectedSymbol: null,
  selectedAssetType: 'stocks',
  selectedTimeframe: 'daily',
  marketData: [],
  isLoadingMarketData: false,
  signals: [],
  nestedSignals: [],
  isLoadingSignals: false,
  watchlist: [],
  error: null,
};

function tradingReducer(state: TradingState, action: TradingAction): TradingState {
  switch (action.type) {
    case 'SET_SYMBOL':
      return { ...state, selectedSymbol: action.payload };

    case 'SET_ASSET_TYPE':
      return { ...state, selectedAssetType: action.payload };

    case 'SET_TIMEFRAME':
      return { ...state, selectedTimeframe: action.payload };

    case 'SET_MARKET_DATA':
      return { ...state, marketData: action.payload, isLoadingMarketData: false };

    case 'SET_SIGNALS':
      return { ...state, signals: action.payload, isLoadingSignals: false };

    case 'SET_NESTED_SIGNALS':
      return { ...state, nestedSignals: action.payload, isLoadingSignals: false };

    case 'SET_LOADING_MARKET_DATA':
      return { ...state, isLoadingMarketData: action.payload };

    case 'SET_LOADING_SIGNALS':
      return { ...state, isLoadingSignals: action.payload };

    case 'ADD_TO_WATCHLIST':
      if (state.watchlist.includes(action.payload)) return state;
      return { ...state, watchlist: [...state.watchlist, action.payload] };

    case 'REMOVE_FROM_WATCHLIST':
      return {
        ...state,
        watchlist: state.watchlist.filter(s => s !== action.payload),
      };

    case 'SET_ERROR':
      return { ...state, error: action.payload };

    case 'CLEAR_ERROR':
      return { ...state, error: null };

    default:
      return state;
  }
}

// ============================================================================
// § 3. CONTEXT
// ============================================================================

const TradingContext = createContext<TradingContextValue | undefined>(undefined);

// Storage key for watchlist persistence
const WATCHLIST_STORAGE_KEY = 'aialgotradehits-watchlist';

// ============================================================================
// § 4. PROVIDER
// ============================================================================

export function TradingProvider({ children }: TradingProviderProps) {
  const [state, dispatch] = useReducer(tradingReducer, initialState);

  // Load watchlist from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(WATCHLIST_STORAGE_KEY);
      if (stored) {
        const watchlist = JSON.parse(stored) as string[];
        watchlist.forEach(symbol => {
          dispatch({ type: 'ADD_TO_WATCHLIST', payload: symbol });
        });
      }
    } catch {
      // Ignore errors
    }
  }, []);

  // Persist watchlist changes
  useEffect(() => {
    localStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(state.watchlist));
  }, [state.watchlist]);

  // Action creators
  const setSelectedSymbol = useCallback((symbol: string | null) => {
    dispatch({ type: 'SET_SYMBOL', payload: symbol });
  }, []);

  const setAssetType = useCallback((type: AssetType) => {
    dispatch({ type: 'SET_ASSET_TYPE', payload: type });
  }, []);

  const setTimeframe = useCallback((timeframe: Timeframe) => {
    dispatch({ type: 'SET_TIMEFRAME', payload: timeframe });
  }, []);

  const addToWatchlist = useCallback((symbol: string) => {
    dispatch({ type: 'ADD_TO_WATCHLIST', payload: symbol });
  }, []);

  const removeFromWatchlist = useCallback((symbol: string) => {
    dispatch({ type: 'REMOVE_FROM_WATCHLIST', payload: symbol });
  }, []);

  const isInWatchlist = useCallback((symbol: string) => {
    return state.watchlist.includes(symbol);
  }, [state.watchlist]);

  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, []);

  // Computed values
  const currentAssetConfig = ASSET_CONFIG.types[state.selectedAssetType];
  const currentTimeframeConfig = ASSET_CONFIG.timeframes[state.selectedTimeframe];

  const value: TradingContextValue = {
    ...state,
    setSelectedSymbol,
    setAssetType,
    setTimeframe,
    addToWatchlist,
    removeFromWatchlist,
    isInWatchlist,
    clearError,
    currentAssetConfig,
    currentTimeframeConfig,
  };

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
}

// ============================================================================
// § 5. HOOK
// ============================================================================

export function useTrading(): TradingContextValue {
  const context = useContext(TradingContext);
  if (!context) {
    throw new Error('useTrading must be used within a TradingProvider');
  }
  return context;
}

export default TradingContext;
