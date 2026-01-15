import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import {
  TrendingUp, Activity, BarChart3, Maximize2, Download,
  Settings, Plus, Minus, RefreshCw
} from 'lucide-react';
import apiService from '../services/api';

const AdvancedChart = ({ symbol, marketType = 'crypto' }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const candlestickSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const rsiSeriesRef = useRef(null);
  const macdSeriesRef = useRef(null);

  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('daily');
  const [indicators, setIndicators] = useState({
    sma20: true,
    sma50: true,
    bb: true,
    rsi: true,
    macd: true,
    volume: true
  });

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 600,
      layout: {
        background: { color: '#0f172a' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#1e293b' },
        horzLines: { color: '#1e293b' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#334155',
      },
      timeScale: {
        borderColor: '#334155',
        timeVisible: true,
      },
    });

    chartRef.current = chart;

    // Create candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderUpColor: '#10b981',
      borderDownColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    candlestickSeriesRef.current = candlestickSeries;

    // Create volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#3b82f6',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  useEffect(() => {
    loadChartData();
  }, [symbol, timeframe, marketType]);

  const loadChartData = async () => {
    try {
      setLoading(true);
      let data;

      if (marketType === 'crypto') {
        const result = await apiService.getCryptoData(timeframe, 100);
        if (result.success) {
          data = result.data.filter(d =>
            d.pair === symbol || d.pair.replace('/', '') === symbol
          );
        }
      } else {
        const result = await apiService.getStockData(100);
        if (result.success) {
          data = result.data.filter(d => d.symbol === symbol);
        }
      }

      if (data && data.length > 0) {
        setChartData(data);
        updateChart(data);
      }
    } catch (error) {
      console.error('Error loading chart data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateChart = (data) => {
    if (!candlestickSeriesRef.current || !volumeSeriesRef.current) return;

    // Prepare candlestick data
    const candleData = data.map(d => ({
      time: new Date(d.datetime).getTime() / 1000,
      open: parseFloat(d.open),
      high: parseFloat(d.high),
      low: parseFloat(d.low),
      close: parseFloat(d.close),
    })).sort((a, b) => a.time - b.time);

    // Prepare volume data
    const volumeData = data.map(d => ({
      time: new Date(d.datetime).getTime() / 1000,
      value: parseFloat(d.volume),
      color: parseFloat(d.close) >= parseFloat(d.open) ? '#10b98166' : '#ef444466',
    })).sort((a, b) => a.time - b.time);

    candlestickSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);

    // Add SMA lines if enabled
    if (indicators.sma20 && data[0]?.sma_20) {
      const sma20Series = chartRef.current.addLineSeries({
        color: '#3b82f6',
        lineWidth: 2,
        title: 'SMA 20',
      });
      const sma20Data = data
        .filter(d => d.sma_20)
        .map(d => ({
          time: new Date(d.datetime).getTime() / 1000,
          value: parseFloat(d.sma_20),
        }))
        .sort((a, b) => a.time - b.time);
      sma20Series.setData(sma20Data);
    }

    if (indicators.sma50 && data[0]?.sma_50) {
      const sma50Series = chartRef.current.addLineSeries({
        color: '#f59e0b',
        lineWidth: 2,
        title: 'SMA 50',
      });
      const sma50Data = data
        .filter(d => d.sma_50)
        .map(d => ({
          time: new Date(d.datetime).getTime() / 1000,
          value: parseFloat(d.sma_50),
        }))
        .sort((a, b) => a.time - b.time);
      sma50Series.setData(sma50Data);
    }

    // Add Bollinger Bands if enabled
    if (indicators.bb && data[0]?.bb_upper) {
      const bbUpperSeries = chartRef.current.addLineSeries({
        color: '#8b5cf6',
        lineWidth: 1,
        lineStyle: 2,
        title: 'BB Upper',
      });
      const bbLowerSeries = chartRef.current.addLineSeries({
        color: '#8b5cf6',
        lineWidth: 1,
        lineStyle: 2,
        title: 'BB Lower',
      });

      const bbUpperData = data
        .filter(d => d.bb_upper)
        .map(d => ({
          time: new Date(d.datetime).getTime() / 1000,
          value: parseFloat(d.bb_upper),
        }))
        .sort((a, b) => a.time - b.time);

      const bbLowerData = data
        .filter(d => d.bb_lower)
        .map(d => ({
          time: new Date(d.datetime).getTime() / 1000,
          value: parseFloat(d.bb_lower),
        }))
        .sort((a, b) => a.time - b.time);

      bbUpperSeries.setData(bbUpperData);
      bbLowerSeries.setData(bbLowerData);
    }
  };

  const toggleIndicator = (indicator) => {
    setIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator]
    }));
    // Reload chart with new indicator settings
    if (chartData.length > 0) {
      updateChart(chartData);
    }
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
    }}>
      {/* Chart Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        paddingBottom: '15px',
        borderBottom: '1px solid #334155'
      }}>
        <div>
          <h2 style={{
            margin: 0,
            color: 'white',
            fontSize: '24px',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <BarChart3 size={28} color="#10b981" />
            {symbol || 'Select Asset'}
          </h2>
          <p style={{
            margin: '5px 0 0 0',
            color: '#94a3b8',
            fontSize: '14px'
          }}>
            {marketType === 'crypto' ? 'Cryptocurrency' : 'Stock'} • {timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}
          </p>
        </div>

        {/* Timeframe Selector */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {['5min', 'hourly', 'daily'].map(tf => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              style={{
                padding: '8px 16px',
                background: timeframe === tf ? '#3b82f6' : '#1e293b',
                color: 'white',
                border: timeframe === tf ? '1px solid #60a5fa' : '1px solid #334155',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: timeframe === tf ? 'bold' : 'normal',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                if (timeframe !== tf) e.target.style.background = '#334155';
              }}
              onMouseLeave={(e) => {
                if (timeframe !== tf) e.target.style.background = '#1e293b';
              }}
            >
              {tf === '5min' ? '5m' : tf === 'hourly' ? '1h' : '1d'}
            </button>
          ))}

          <button
            onClick={loadChartData}
            style={{
              padding: '8px',
              background: '#1e293b',
              color: 'white',
              border: '1px solid #334155',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center'
            }}
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Indicator Toggles */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '15px',
        flexWrap: 'wrap'
      }}>
        {Object.keys(indicators).map(ind => (
          <button
            key={ind}
            onClick={() => toggleIndicator(ind)}
            style={{
              padding: '6px 12px',
              background: indicators[ind] ? '#10b981' : '#1e293b',
              color: 'white',
              border: indicators[ind] ? '1px solid #34d399' : '1px solid #334155',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: indicators[ind] ? 'bold' : 'normal',
              transition: 'all 0.2s',
              textTransform: 'uppercase'
            }}
          >
            {ind === 'sma20' ? 'SMA 20' :
             ind === 'sma50' ? 'SMA 50' :
             ind === 'bb' ? 'Bollinger Bands' :
             ind.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Chart Container */}
      <div
        ref={chartContainerRef}
        style={{
          position: 'relative',
          width: '100%',
          height: '600px',
          background: '#0f172a',
          borderRadius: '8px',
          overflow: 'hidden'
        }}
      >
        {loading && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: 'white',
            fontSize: '18px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <RefreshCw size={24} className="spin" />
            Loading chart data...
          </div>
        )}
      </div>

      {/* Chart Stats */}
      {chartData.length > 0 && (
        <div style={{
          marginTop: '20px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '15px'
        }}>
          {['open', 'high', 'low', 'close', 'volume'].map(field => {
            const latestData = chartData[chartData.length - 1];
            return (
              <div key={field} style={{
                background: '#1e293b',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #334155'
              }}>
                <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '4px' }}>
                  {field.toUpperCase()}
                </div>
                <div style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
                  {field === 'volume'
                    ? parseFloat(latestData[field]).toLocaleString(undefined, { maximumFractionDigits: 0 })
                    : '$' + parseFloat(latestData[field]).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                  }
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AdvancedChart;
