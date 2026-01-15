/**
 * App Context - Combined Provider
 *
 * Wraps all context providers for the application.
 * Provides a single entry point for global state.
 *
 * @version 5.1.0
 */

import { ReactNode } from 'react';
import { ThemeProvider, useTheme } from './ThemeContext';
import { AuthProvider, useAuth } from './AuthContext';
import { TradingProvider, useTrading } from './TradingContext';

// ============================================================================
// § 1. COMBINED PROVIDER
// ============================================================================

interface AppProviderProps {
  children: ReactNode;
}

/**
 * AppProvider - Combines all context providers
 *
 * Provider hierarchy (outer to inner):
 * 1. ThemeProvider - Theme must be outermost for CSS variables
 * 2. AuthProvider - Authentication state
 * 3. TradingProvider - Trading data and signals
 */
export function AppProvider({ children }: AppProviderProps) {
  return (
    <ThemeProvider defaultTheme="dark">
      <AuthProvider>
        <TradingProvider>
          {children}
        </TradingProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

// ============================================================================
// § 2. RE-EXPORTS
// ============================================================================

// Re-export all hooks for convenience
export { useTheme } from './ThemeContext';
export { useAuth } from './AuthContext';
export { useTrading } from './TradingContext';

// Re-export types
export type { User } from './AuthContext';
export type { MarketData, TradingSignal, NestedSignal } from './TradingContext';

// ============================================================================
// § 3. COMPOSITE HOOK
// ============================================================================

/**
 * useApp - Access all app contexts at once
 *
 * Provides unified access to theme, auth, and trading contexts.
 * Use individual hooks when you only need specific context.
 */
export function useApp() {
  const theme = useTheme();
  const auth = useAuth();
  const trading = useTrading();

  return {
    theme,
    auth,
    trading,
  };
}

export default AppProvider;
