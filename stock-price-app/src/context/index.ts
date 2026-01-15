/**
 * Context Layer - Export all contexts and providers
 *
 * Single entry point for all global state management.
 *
 * @version 5.1.0
 */

// Main App Provider (combines all)
export { AppProvider, useApp } from './AppContext';

// Individual Providers and Hooks
export { ThemeProvider, useTheme } from './ThemeContext';
export { AuthProvider, useAuth } from './AuthContext';
export { TradingProvider, useTrading } from './TradingContext';

// Types
export type { User } from './AuthContext';
export type { MarketData, TradingSignal, NestedSignal } from './TradingContext';
