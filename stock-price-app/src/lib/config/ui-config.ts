/**
 * UI CONFIG - Single Source of Truth (SSOT)
 * All UI-related configuration in one place
 *
 * @version 3.0.0
 * @lastModified January 13, 2026
 */

// ============================================================================
// § 1. COLOR PALETTE
// ============================================================================
export const COLORS = {
  // Brand Colors
  primary: "#3b82f6",
  primaryDark: "#2563eb",
  primaryLight: "#60a5fa",

  // Status Colors
  success: "#10b981",
  successDark: "#059669",
  successLight: "#34d399",

  warning: "#f59e0b",
  warningDark: "#d97706",
  warningLight: "#fbbf24",

  danger: "#ef4444",
  dangerDark: "#dc2626",
  dangerLight: "#f87171",

  // Neutral Colors
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
  },

  // Signal Colors
  signals: {
    strongBuy: "#059669",
    buy: "#10b981",
    hold: "#6b7280",
    sell: "#f59e0b",
    strongSell: "#ef4444",
  },

  // Chart Colors
  chart: {
    up: "#10b981",
    down: "#ef4444",
    volume: "#3b82f6",
    ma20: "#f59e0b",
    ma50: "#8b5cf6",
    ma200: "#ec4899",
    bollinger: "#6366f1",
    grid: "#374151",
  },
} as const;

// ============================================================================
// § 2. THEME CONFIGURATIONS
// ============================================================================
export const THEMES = {
  dark: {
    name: "dark",
    background: "#0f172a",
    backgroundSecondary: "#1e293b",
    surface: "#1e293b",
    surfaceHover: "#334155",
    border: "#334155",
    text: "#f1f5f9",
    textSecondary: "#94a3b8",
    textMuted: "#64748b",
  },
  light: {
    name: "light",
    background: "#ffffff",
    backgroundSecondary: "#f8fafc",
    surface: "#f8fafc",
    surfaceHover: "#f1f5f9",
    border: "#e2e8f0",
    text: "#1e293b",
    textSecondary: "#64748b",
    textMuted: "#94a3b8",
  },
} as const;

export type ThemeName = keyof typeof THEMES;
export type Theme = typeof THEMES[ThemeName];

// ============================================================================
// § 3. CHART CONFIGURATION
// ============================================================================
export const CHART_CONFIG = {
  // Default dimensions
  defaultHeight: 400,
  miniChartHeight: 200,
  volumeChartHeight: 100,

  // Candlestick colors
  candlestick: {
    upColor: "#10b981",
    downColor: "#ef4444",
    borderUpColor: "#10b981",
    borderDownColor: "#ef4444",
    wickUpColor: "#10b981",
    wickDownColor: "#ef4444",
  },

  // Grid settings
  grid: {
    vertLines: {
      color: "#334155",
      style: 1, // Solid
    },
    horzLines: {
      color: "#334155",
      style: 1,
    },
  },

  // Time scale
  timeScale: {
    borderColor: "#334155",
    timeVisible: true,
    secondsVisible: false,
  },

  // Price scale
  priceScale: {
    borderColor: "#334155",
    autoScale: true,
  },

  // Crosshair
  crosshair: {
    mode: 1, // Normal
    vertLine: {
      color: "#6b7280",
      width: 1,
      style: 2, // Dashed
      labelBackgroundColor: "#1e293b",
    },
    horzLine: {
      color: "#6b7280",
      width: 1,
      style: 2,
      labelBackgroundColor: "#1e293b",
    },
  },

  // Moving averages
  movingAverages: {
    sma20: { color: "#f59e0b", lineWidth: 1 },
    sma50: { color: "#8b5cf6", lineWidth: 1 },
    sma200: { color: "#ec4899", lineWidth: 2 },
    ema12: { color: "#3b82f6", lineWidth: 1 },
    ema26: { color: "#ef4444", lineWidth: 1 },
  },
} as const;

// ============================================================================
// § 4. LAYOUT CONFIGURATION
// ============================================================================
export const LAYOUT_CONFIG = {
  // Sidebar
  sidebar: {
    width: 280,
    collapsedWidth: 64,
    breakpoint: 1024,
  },

  // Header
  header: {
    height: 64,
  },

  // Content
  content: {
    maxWidth: 1920,
    padding: 24,
    gap: 16,
  },

  // Card
  card: {
    borderRadius: 12,
    padding: 16,
  },

  // Modal
  modal: {
    maxWidth: 600,
    borderRadius: 16,
  },
} as const;

// ============================================================================
// § 5. ANIMATION CONFIGURATION
// ============================================================================
export const ANIMATION_CONFIG = {
  duration: {
    fast: 150,
    normal: 200,
    slow: 300,
  },
  easing: {
    default: "ease-in-out",
    bounce: "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
  },
} as const;

// ============================================================================
// § 6. BREAKPOINTS
// ============================================================================
export const BREAKPOINTS = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
} as const;

// ============================================================================
// § 7. Z-INDEX LAYERS
// ============================================================================
export const Z_INDEX = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
  toast: 1080,
} as const;

// ============================================================================
// § 8. TABLE CONFIGURATION
// ============================================================================
export const TABLE_CONFIG = {
  defaultPageSize: 25,
  pageSizeOptions: [10, 25, 50, 100],
  stickyHeader: true,
  rowHeight: 48,
  headerHeight: 56,
} as const;

// ============================================================================
// § 9. ICON SIZES
// ============================================================================
export const ICON_SIZES = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
} as const;

// ============================================================================
// § 10. HELPER FUNCTIONS
// ============================================================================

/**
 * Get color for signal type
 */
export function getSignalColor(signal: string): string {
  const signalMap: Record<string, string> = {
    STRONG_BUY: COLORS.signals.strongBuy,
    BUY: COLORS.signals.buy,
    HOLD: COLORS.signals.hold,
    SELL: COLORS.signals.sell,
    STRONG_SELL: COLORS.signals.strongSell,
    UP: COLORS.chart.up,
    DOWN: COLORS.chart.down,
  };
  return signalMap[signal.toUpperCase()] || COLORS.gray[500];
}

/**
 * Get theme colors
 */
export function getThemeColors(themeName: ThemeName = "dark"): Theme {
  return THEMES[themeName];
}

/**
 * Check if screen is mobile
 */
export function isMobile(width: number): boolean {
  return width < BREAKPOINTS.md;
}

/**
 * Check if screen is tablet
 */
export function isTablet(width: number): boolean {
  return width >= BREAKPOINTS.md && width < BREAKPOINTS.lg;
}

/**
 * Check if screen is desktop
 */
export function isDesktop(width: number): boolean {
  return width >= BREAKPOINTS.lg;
}
