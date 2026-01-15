/**
 * Theme configurations for Dark and Light modes
 */

export const themes = {
  dark: {
    name: 'dark',
    background: '#0a0e27',
    cardBg: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
    cardBorder: '#334155',
    text: '#e2e8f0',
    textSecondary: '#94a3b8',
    textMuted: '#64748b',
    primary: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    info: '#06b6d4',

    // Chart colors
    chart: {
      background: '#0f172a',
      textColor: '#94a3b8',
      gridColor: '#1e293b',
      borderColor: '#334155',
      upColor: '#10b981',
      downColor: '#ef4444',
      volumeUpColor: 'rgba(16, 185, 129, 0.5)',
      volumeDownColor: 'rgba(239, 68, 68, 0.5)',
    },

    // Indicator colors
    indicators: {
      sma20: '#eab308',
      sma50: '#f97316',
      ema12: '#06b6d4',
      ema26: '#8b5cf6',
      bollinger: '#a855f7',
      rsi: '#3b82f6',
      macd: '#ec4899',
    }
  },

  light: {
    name: 'light',
    background: '#e5e7eb',
    cardBg: 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)',
    cardBorder: '#cbd5e1',
    text: '#0f172a',
    textSecondary: '#475569',
    textMuted: '#94a3b8',
    primary: '#059669',
    danger: '#dc2626',
    warning: '#d97706',
    info: '#0891b2',

    // Chart colors
    chart: {
      background: '#f3f4f6',
      textColor: '#475569',
      gridColor: '#d1d5db',
      borderColor: '#cbd5e1',
      upColor: '#059669',
      downColor: '#dc2626',
      volumeUpColor: 'rgba(5, 150, 105, 0.3)',
      volumeDownColor: 'rgba(220, 38, 38, 0.3)',
    },

    // Indicator colors
    indicators: {
      sma20: '#ca8a04',
      sma50: '#ea580c',
      ema12: '#0e7490',
      ema26: '#7c3aed',
      bollinger: '#9333ea',
      rsi: '#2563eb',
      macd: '#db2777',
    }
  }
};

export default themes;
