import { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import { Maximize, Minimize } from 'lucide-react';
import marketDataService from '../services/marketData';
import themes from '../theme';

export default function ProfessionalChart({ symbol, marketType, timeframe, theme = 'dark' }) {
  const currentTheme = themes[theme];
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [indicators, setIndicators] = useState({
    sma: true,
    ema: true,
    bollinger: true,
    volume: true,
    rsi: true,
    macd: true
  });

  // Fetch data
  useEffect(() => {
    if (!symbol) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const limit = timeframe === 'daily' ? 200 : 200;
        const data = marketType === 'crypto'
          ? await marketDataService.getCryptoData(symbol, timeframe, limit)
          : await marketDataService.getStockData(symbol, timeframe, limit);

        setHistoryData(data || []);
      } catch (error) {
        console.error('Error loading chart data:', error);
        setHistoryData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol, marketType, timeframe]);

  // Create/update chart
  useEffect(() => {
    if (!chartContainerRef.current || historyData.length === 0) return;

    // Clean up existing chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: isFullscreen ? window.innerHeight - 200 : 600,
      layout: {
        background: { type: 'solid', color: currentTheme.chart.background },
        textColor: currentTheme.chart.textColor,
      },
      grid: {
        vertLines: { color: currentTheme.chart.gridColor },
        horzLines: { color: currentTheme.chart.gridColor },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: currentTheme.chart.borderColor,
      },
      rightPriceScale: {
        borderColor: currentTheme.chart.borderColor,
      },
    });

    chartRef.current = chart;

    // Candlestick data
    const candlestickData = historyData
      .map(item => ({
        time: Number(item.time || 0),
        open: Number(item.open || item.close || 0),
        high: Number(item.high || item.close || 0),
        low: Number(item.low || item.close || 0),
        close: Number(item.close || 0)
      }))
      .filter(item => item.close > 0 && item.time > 0)
      .sort((a, b) => a.time - b.time);

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: currentTheme.chart.upColor,
      downColor: currentTheme.chart.downColor,
      borderVisible: false,
      wickUpColor: currentTheme.chart.upColor,
      wickDownColor: currentTheme.chart.downColor,
    });

    candlestickSeries.setData(candlestickData);

    // Volume
    if (indicators.volume) {
      const volumeSeries = chart.addHistogramSeries({
        color: currentTheme.textMuted,
        priceFormat: { type: 'volume' },
        priceScaleId: 'volume',
      });

      chart.priceScale('volume').applyOptions({
        scaleMargins: { top: 0.8, bottom: 0 },
      });

      const volumeData = historyData
        .map(item => ({
          time: Number(item.time || 0),
          value: Number(item.volume || 0),
          color: item.close >= item.open ? currentTheme.chart.volumeUpColor : currentTheme.chart.volumeDownColor
        }))
        .filter(item => item.time > 0)
        .sort((a, b) => a.time - b.time);

      volumeSeries.setData(volumeData);
    }

    // SMAs
    if (indicators.sma) {
      const sma20Series = chart.addLineSeries({
        color: currentTheme.indicators.sma20,
        lineWidth: 2,
        title: 'SMA 20',
      });

      const sma50Series = chart.addLineSeries({
        color: currentTheme.indicators.sma50,
        lineWidth: 2,
        title: 'SMA 50',
      });

      const sma20Data = historyData
        .filter(item => item.sma_20 && item.time)
        .map(item => ({ time: Number(item.time), value: Number(item.sma_20) }))
        .filter(item => item.time > 0)
        .sort((a, b) => a.time - b.time);

      const sma50Data = historyData
        .filter(item => item.sma_50 && item.time)
        .map(item => ({ time: Number(item.time), value: Number(item.sma_50) }))
        .filter(item => item.time > 0)
        .sort((a, b) => a.time - b.time);

      if (sma20Data.length > 0) sma20Series.setData(sma20Data);
      if (sma50Data.length > 0) sma50Series.setData(sma50Data);
    }

    // EMAs
    if (indicators.ema) {
      const ema12Series = chart.addLineSeries({
        color: currentTheme.indicators.ema12,
        lineWidth: 2,
        title: 'EMA 12',
      });

      const ema26Series = chart.addLineSeries({
        color: currentTheme.indicators.ema26,
        lineWidth: 2,
        title: 'EMA 26',
      });

      const ema12Data = historyData
        .filter(item => item.ema_12 && item.time)
        .map(item => ({ time: Number(item.time), value: Number(item.ema_12) }))
        .filter(item => item.time > 0)
        .sort((a, b) => a.time - b.time);

      const ema26Data = historyData
        .filter(item => item.ema_26 && item.time)
        .map(item => ({ time: Number(item.time), value: Number(item.ema_26) }))
        .filter(item => item.time > 0)
        .sort((a, b) => a.time - b.time);

      if (ema12Data.length > 0) ema12Series.setData(ema12Data);
      if (ema26Data.length > 0) ema26Series.setData(ema26Data);
    }

    // Bollinger Bands
    if (indicators.bollinger) {
      const bbUpperSeries = chart.addLineSeries({
        color: currentTheme.indicators.bollinger,
        lineWidth: 1,
        lineStyle: 2,
        title: 'BB Upper',
      });

      const bbLowerSeries = chart.addLineSeries({
        color: currentTheme.indicators.bollinger,
        lineWidth: 1,
        lineStyle: 2,
        title: 'BB Lower',
      });

      const bbUpperData = historyData
        .filter(item => item.bb_upper && item.time)
        .map(item => ({ time: Number(item.time), value: Number(item.bb_upper) }))
        .filter(item => item.time > 0)
        .sort((a, b) => a.time - b.time);

      const bbLowerData = historyData
        .filter(item => item.bb_lower && item.time)
        .map(item => ({ time: Number(item.time), value: Number(item.bb_lower) }))
        .filter(item => item.time > 0)
        .sort((a, b) => a.time - b.time);

      if (bbUpperData.length > 0) bbUpperSeries.setData(bbUpperData);
      if (bbLowerData.length > 0) bbLowerSeries.setData(bbLowerData);
    }

    // Set visible range - show last 100 candles or all if less
    if (candlestickData.length > 0) {
      if (candlestickData.length <= 100) {
        chart.timeScale().fitContent();
      } else {
        chart.timeScale().setVisibleLogicalRange({
          from: candlestickData.length - 100,
          to: candlestickData.length - 1
        });
      }
    }

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: isFullscreen ? window.innerHeight - 200 : 600,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [historyData, indicators, isFullscreen, theme]);

  const handleZoomIn = () => {
    if (!chartRef.current) return;
    const range = chartRef.current.timeScale().getVisibleLogicalRange();
    if (range) {
      const delta = (range.to - range.from) * 0.2;
      chartRef.current.timeScale().setVisibleLogicalRange({
        from: range.from + delta,
        to: range.to - delta
      });
    }
  };

  const handleZoomOut = () => {
    if (!chartRef.current) return;
    const range = chartRef.current.timeScale().getVisibleLogicalRange();
    if (range) {
      const delta = (range.to - range.from) * 0.2;
      chartRef.current.timeScale().setVisibleLogicalRange({
        from: Math.max(0, range.from - delta),
        to: range.to + delta
      });
    }
  };

  const handleResetZoom = () => {
    if (!chartRef.current) return;
    chartRef.current.timeScale().fitContent();
  };

  const toggleIndicator = (key) => {
    setIndicators({ ...indicators, [key]: !indicators[key] });
  };

  if (loading) {
    return (
      <div style={{ padding: '48px', textAlign: 'center', color: currentTheme.textSecondary }}>
        Loading chart...
      </div>
    );
  }

  const latestData = historyData[historyData.length - 1] || {};
  const timeframeLabel = timeframe === 'daily' ? 'DAILY' : timeframe === 'hourly' ? 'HOURLY' : '5-MINUTE';

  return (
    <div style={{
      position: isFullscreen ? 'fixed' : 'relative',
      top: isFullscreen ? 0 : 'auto',
      left: isFullscreen ? 0 : 'auto',
      right: isFullscreen ? 0 : 'auto',
      bottom: isFullscreen ? 0 : 'auto',
      width: isFullscreen ? '100vw' : '100%',
      height: isFullscreen ? '100vh' : 'auto',
      zIndex: isFullscreen ? 9999 : 'auto',
      background: isFullscreen ? currentTheme.background : 'transparent',
      padding: isFullscreen ? '16px' : '0',
      overflow: isFullscreen ? 'auto' : 'visible'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 24px',
        background: currentTheme.cardBg,
        borderRadius: '12px 12px 0 0',
        border: `1px solid ${currentTheme.cardBorder}`,
        borderBottom: 'none'
      }}>
        <div>
          <h2 style={{ color: currentTheme.primary, fontSize: '20px', margin: '0 0 4px 0' }}>
            {symbol} - {timeframeLabel}
          </h2>
          <div style={{ color: currentTheme.textSecondary, fontSize: '12px' }}>
            {historyData.length} candles | Last update: {latestData.time ? new Date(latestData.time * 1000).toLocaleString() : 'N/A'}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Zoom Controls */}
          <div style={{ display: 'flex', gap: '4px', background: '#0a0e1a', borderRadius: '8px', padding: '4px' }}>
            <button onClick={handleZoomOut} style={zoomButtonStyle}>−</button>
            <button onClick={handleResetZoom} style={zoomButtonStyle}>RESET</button>
            <button onClick={handleZoomIn} style={zoomButtonStyle}>+</button>
          </div>

          {/* Fullscreen */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            style={{
              ...indicatorButtonStyle(currentTheme),
              background: '#334155',
              color: 'white'
            }}
          >
            {isFullscreen ? <Minimize size={16} /> : <Maximize size={16} />}
            <span>Fullscreen</span>
          </button>

          {/* Indicator Toggles */}
          <button
            onClick={() => toggleIndicator('sma')}
            style={{
              ...indicatorButtonStyle(currentTheme),
              background: indicators.sma ? currentTheme.primary : 'transparent',
              border: `1px solid ${indicators.sma ? currentTheme.primary : currentTheme.cardBorder}`
            }}
          >
            SMA
          </button>
          <button
            onClick={() => toggleIndicator('ema')}
            style={{
              ...indicatorButtonStyle(currentTheme),
              background: indicators.ema ? currentTheme.primary : 'transparent',
              border: `1px solid ${indicators.ema ? currentTheme.primary : currentTheme.cardBorder}`
            }}
          >
            EMA
          </button>
          <button
            onClick={() => toggleIndicator('bollinger')}
            style={{
              ...indicatorButtonStyle(currentTheme),
              background: indicators.bollinger ? currentTheme.primary : 'transparent',
              border: `1px solid ${indicators.bollinger ? currentTheme.primary : currentTheme.cardBorder}`
            }}
          >
            BOLLINGER
          </button>
          <button
            onClick={() => toggleIndicator('volume')}
            style={{
              ...indicatorButtonStyle(currentTheme),
              background: indicators.volume ? currentTheme.primary : 'transparent',
              border: `1px solid ${indicators.volume ? currentTheme.primary : currentTheme.cardBorder}`
            }}
          >
            VOLUME
          </button>
          <button
            onClick={() => toggleIndicator('rsi')}
            style={{
              ...indicatorButtonStyle(currentTheme),
              background: indicators.rsi ? currentTheme.primary : 'transparent',
              border: `1px solid ${indicators.rsi ? currentTheme.primary : currentTheme.cardBorder}`
            }}
          >
            RSI
          </button>
          <button
            onClick={() => toggleIndicator('macd')}
            style={{
              ...indicatorButtonStyle(currentTheme),
              background: indicators.macd ? currentTheme.primary : 'transparent',
              border: `1px solid ${indicators.macd ? currentTheme.primary : currentTheme.cardBorder}`
            }}
          >
            MACD
          </button>
        </div>
      </div>

      {/* Chart and Indicators Row */}
      <div style={{
        display: 'flex',
        gap: '16px',
        background: currentTheme.cardBg,
        padding: '16px',
        border: `1px solid ${currentTheme.cardBorder}`,
        borderRadius: '0 0 12px 12px'
      }}>
        {/* Main Chart */}
        <div style={{ flex: 1 }}>
          <div ref={chartContainerRef} style={{ width: '100%', height: isFullscreen ? 'calc(100vh - 200px)' : '600px' }} />
        </div>

        {/* Right Indicator Panel */}
        <div style={{
          width: '200px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          <IndicatorCard
            title="RSI (14)"
            value={latestData.rsi?.toFixed(2) || '0.00'}
            subtitle="Oversold"
            theme={currentTheme}
            isDark={theme === 'dark'}
          />
          <IndicatorCard
            title="MACD"
            value={latestData.macd?.toFixed(4) || '0.0000'}
            subtitle={`Signal: ${latestData.macd_signal?.toFixed(4) || '0.0000'}`}
            theme={currentTheme}
            isDark={theme === 'dark'}
          />
          <IndicatorCard
            title="ADX"
            value={latestData.adx?.toFixed(2) || '0.00'}
            subtitle="Weak Trend"
            theme={currentTheme}
            isDark={theme === 'dark'}
          />
          <IndicatorCard
            title="ATR"
            value={latestData.atr?.toFixed(4) || '0.00'}
            subtitle="Volatility"
            theme={currentTheme}
            isDark={theme === 'dark'}
          />
        </div>
      </div>
    </div>
  );
}

// Helper component for indicator cards
function IndicatorCard({ title, value, subtitle, theme, isDark }) {
  return (
    <div style={{
      background: isDark ? '#1a1f2e' : '#f8fafc',
      borderRadius: '8px',
      padding: '16px',
      border: `1px solid ${theme.cardBorder}`
    }}>
      <div style={{
        color: theme.textSecondary,
        fontSize: '11px',
        marginBottom: '8px',
        fontWeight: '500'
      }}>
        {title}
      </div>
      <div style={{
        color: value === '0.00' || value === '0.0000' ? '#ef4444' : theme.primary,
        fontSize: '28px',
        fontWeight: '700',
        marginBottom: '4px'
      }}>
        {value}
      </div>
      <div style={{
        color: theme.textMuted,
        fontSize: '10px'
      }}>
        {subtitle}
      </div>
    </div>
  );
}

const zoomButtonStyle = {
  padding: '8px 12px',
  background: '#334155',
  color: 'white',
  border: 'none',
  borderRadius: '6px',
  fontSize: '12px',
  fontWeight: '600',
  cursor: 'pointer',
  minWidth: '40px'
};

const indicatorButtonStyle = (theme) => ({
  padding: '8px 12px',
  color: 'white',
  borderRadius: '6px',
  fontSize: '12px',
  fontWeight: '600',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  transition: 'all 0.2s'
});
