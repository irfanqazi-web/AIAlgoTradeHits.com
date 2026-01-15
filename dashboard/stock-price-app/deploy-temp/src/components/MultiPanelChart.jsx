import { useState } from 'react';
import { Maximize, Minimize } from 'lucide-react';
import TradingViewChart from './TradingViewChart';
import themes from '../theme';

export default function MultiPanelChart({ symbol, marketType, assetType, theme = 'dark' }) {
  const [fullscreenPanel, setFullscreenPanel] = useState(null); // null, 'daily', 'hourly', or '5min'
  const currentTheme = themes[theme];

  // Use assetType if provided, otherwise derive from marketType for backwards compatibility
  const effectiveAssetType = assetType || (marketType === 'crypto' ? 'crypto' : 'stocks');

  if (!symbol) {
    return (
      <div style={{
        padding: '48px',
        textAlign: 'center',
        color: currentTheme.textSecondary,
      }}>
        Please select a symbol to view charts
      </div>
    );
  }

  // Helper to render a chart panel with fullscreen capability
  const renderChartPanel = (timeframe, timeframeLabel) => {
    const isFullscreen = fullscreenPanel === timeframe;

    if (isFullscreen) {
      // Fullscreen mode
      return (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          width: '100vw',
          height: '100vh',
          zIndex: 9999,
          background: currentTheme.background,
          overflow: 'auto',
          padding: '24px'
        }}>
          {/* Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
            padding: '16px 24px',
            background: currentTheme.cardBg,
            borderRadius: '12px',
            border: `1px solid ${currentTheme.cardBorder}`,
          }}>
            <div>
              <h2 style={{ color: currentTheme.primary, fontSize: '24px', margin: '0 0 4px 0', textAlign: 'left' }}>
                {symbol} - {timeframeLabel}
              </h2>
              <div style={{ color: currentTheme.textSecondary, fontSize: '14px', textAlign: 'left' }}>
                {effectiveAssetType.charAt(0).toUpperCase() + effectiveAssetType.slice(1)} | Full Screen View
              </div>
            </div>
            <button
              onClick={() => setFullscreenPanel(null)}
              style={{
                padding: '14px 28px',
                background: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontSize: '16px',
                fontWeight: '700',
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4)',
                transition: 'all 0.3s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#059669';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#10b981';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              <Minimize size={20} />
              ← Back to Multi-Panel
            </button>
          </div>

          {/* Fullscreen Chart */}
          <TradingViewChart
            symbol={symbol}
            assetType={effectiveAssetType}
            timeframe={timeframe}
            theme={theme}
          />
        </div>
      );
    }

    // Normal panel mode
    return (
      <div style={{
        background: currentTheme.cardBg,
        borderRadius: '12px',
        padding: '12px',
        border: `1px solid ${currentTheme.cardBorder}`,
        position: 'relative',
        minWidth: 0, // Allow flex/grid shrinking
        overflow: 'hidden', // Prevent content overflow
      }}>
        <div style={{
          marginBottom: '12px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingLeft: '12px',
        }}>
          <h3 style={{
            color: currentTheme.text,
            fontSize: '16px',
            margin: 0,
            fontWeight: '600',
            textAlign: 'left',
          }}>
            {timeframeLabel}
          </h3>
          <button
            onClick={() => setFullscreenPanel(timeframe)}
            title="Expand to Fullscreen"
            style={{
              padding: '8px 12px',
              background: currentTheme.primary,
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '12px',
              fontWeight: '600'
            }}
          >
            <Maximize size={14} />
            Expand
          </button>
        </div>

        <div style={{
          height: '600px', // Matches total chart height: 250+80+150+120
          width: '100%',
          maxWidth: '100%',
          overflow: 'hidden',
        }}>
          <TradingViewChart
            symbol={symbol}
            assetType={effectiveAssetType}
            timeframe={timeframe}
            theme={theme}
          />
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header */}
      {!fullscreenPanel && (
        <div style={{
          padding: '16px 24px',
          background: currentTheme.cardBg,
          borderRadius: '12px',
          border: `1px solid ${currentTheme.cardBorder}`,
        }}>
          <h2 style={{ color: currentTheme.primary, fontSize: '28px', margin: '0', textAlign: 'left' }}>
            {symbol} - Multi-Timeframe Analysis
          </h2>
          <div style={{ color: currentTheme.textSecondary, fontSize: '14px', marginTop: '4px', textAlign: 'left' }}>
            {effectiveAssetType.charAt(0).toUpperCase() + effectiveAssetType.slice(1)} | Daily, Hourly & 5-Minute Charts with RSI & MACD
          </div>
        </div>
      )}

      {/* Three Chart Panels */}
      <div style={{
        display: fullscreenPanel ? 'block' : 'grid',
        gridTemplateColumns: fullscreenPanel ? '1fr' : 'repeat(3, 1fr)',
        gap: '16px'
      }}>
        {(!fullscreenPanel || fullscreenPanel === 'daily') && renderChartPanel('daily', 'Daily Chart')}
        {(!fullscreenPanel || fullscreenPanel === 'hourly') && renderChartPanel('hourly', 'Hourly Chart')}
        {(!fullscreenPanel || fullscreenPanel === '5min') && renderChartPanel('5min', '5-Minute Chart')}
      </div>
    </div>
  );
}
