/**
 * Theme Context - Global theme state management
 *
 * Provides theme switching functionality with persistence.
 * Uses Tailwind CSS dark mode class strategy.
 *
 * @version 5.1.0
 */

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { UI_CONFIG, ThemeName } from '@/lib/config';

// ============================================================================
// § 1. TYPES
// ============================================================================

interface ThemeContextValue {
  theme: ThemeName;
  isDark: boolean;
  colors: typeof UI_CONFIG.themes.dark;
  setTheme: (theme: ThemeName) => void;
  toggleTheme: () => void;
}

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: ThemeName;
}

// ============================================================================
// § 2. CONTEXT
// ============================================================================

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

// Storage key for persistence
const THEME_STORAGE_KEY = 'aialgotradehits-theme';

// ============================================================================
// § 3. PROVIDER
// ============================================================================

export function ThemeProvider({ children, defaultTheme = 'dark' }: ThemeProviderProps) {
  // Initialize from localStorage or default
  const [theme, setThemeState] = useState<ThemeName>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(THEME_STORAGE_KEY);
      if (stored === 'dark' || stored === 'light') {
        return stored;
      }
    }
    return defaultTheme;
  });

  // Apply theme class to document
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  // Theme setter with validation
  const setTheme = useCallback((newTheme: ThemeName) => {
    if (newTheme === 'dark' || newTheme === 'light') {
      setThemeState(newTheme);
    }
  }, []);

  // Toggle between dark and light
  const toggleTheme = useCallback(() => {
    setThemeState(prev => prev === 'dark' ? 'light' : 'dark');
  }, []);

  // Get current theme colors
  const colors = UI_CONFIG.themes[theme];
  const isDark = theme === 'dark';

  const value: ThemeContextValue = {
    theme,
    isDark,
    colors,
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// ============================================================================
// § 4. HOOK
// ============================================================================

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

export default ThemeContext;
