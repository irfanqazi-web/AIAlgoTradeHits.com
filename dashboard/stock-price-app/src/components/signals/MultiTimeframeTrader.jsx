/**
 * MultiTimeframeTrader.jsx
 *
 * Advanced Multi-Timeframe Trading Analysis Component
 *
 * STRATEGY: Daily → Hourly → 5-Minute Cascade
 * 1. Daily: Identify high growth score opportunities (>= 75)
 * 2. Hourly: Track EMA 12/26 rise cycle for timing
 * 3. 5-Minute: Execute at optimal entry points
 *
 * Based on validated ML model with 68.5% UP accuracy
 * Key Features: Pivot flags (100% in top 3), Growth Score, EMA Cycles
 */

import { useState, useEffect, useCallback } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, AreaChart, Area, BarChart, Bar, ComposedChart,
  ReferenceLine, ReferenceArea
} from 'recharts';
import {
  TrendingUp, TrendingDown, Target, Zap, AlertTriangle,
  Clock, BarChart2, Activity, Eye, RefreshCw, ChevronDown,
  ChevronUp, ArrowUpRight, ArrowDownRight, Layers, Filter
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://trading-api-1075463475276.us-central1.run.app';

// Signal strength colors
const SIGNAL_COLORS = {
  STRONG_BUY: '#00ff88',
  BUY: '#10b981',
  HOLD: '#f59e0b',
  SELL: '#f97316',
  STRONG_SELL: '#ef4444'
};

// Timeframe configurations
const TIMEFRAMES = {
  daily: { label: 'Daily', interval: '1day', color: '#3b82f6', icon: '📅' },
  hourly: { label: 'Hourly', interval: '1h', color: '#8b5cf6', icon: '⏰' },
  fivemin: { label: '5-Minute', interval: '5min', color: '#ec4899', icon: '⚡' }
};

// Multi-Timeframe Trader Component
const MultiTimeframeTrader = ({ theme = 'dark' }) => {
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [hotStocks, setHotStocks] = useState([]);
  const [dailyData, setDailyData] = useState([]);
  const [hourlyData, setHourlyData] = useState([]);
  const [fiveMinData, setFiveMinData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [signalHistory, setSignalHistory] = useState([]);
  const [expandedPanel, setExpandedPanel] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Analysis state
  const [dailySignal, setDailySignal] = useState(null);
  const [hourlySignal, setHourlySignal] = useState(null);
  const [fiveMinSignal, setFiveMinSignal] = useState(null);
  const [combinedSignal, setCombinedSignal] = useState(null);

  // Fetch hot stocks (high growth score candidates)
  const fetchHotStocks = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/ai/growth-screener?min_score=50&limit=20`);
      const data = await response.json();

      if (data.success && data.data) {
        setHotStocks(data.data.sort((a, b) => (b.growth_score || 0) - (a.growth_score || 0)));
      }
    } catch (err) {
      console.error('Error fetching hot stocks:', err);
    }
  }, []);

  // Fetch data for a specific timeframe
  const fetchTimeframeData = useCallback(async (symbol, timeframe) => {
    try {
      const endpoint = timeframe === 'daily'
        ? `/api/history/${symbol}?interval=1day&limit=100`
        : timeframe === 'hourly'
        ? `/api/history/${symbol}?interval=1h&limit=100`
        : `/api/history/${symbol}?interval=5min&limit=100`;

      const response = await fetch(`${API_BASE}${endpoint}`);
      const data = await response.json();

      if (data.success && data.data) {
        return data.data.map(d => ({
          ...d,
          datetime: new Date(d.datetime).toLocaleString(),
          timestamp: new Date(d.datetime).getTime()
        })).sort((a, b) => a.timestamp - b.timestamp);
      }
      return [];
    } catch (err) {
      console.error(`Error fetching ${timeframe} data:`, err);
      return [];
    }
  }, []);

  // Analyze daily data for opportunity
  const analyzeDailySignal = (data) => {
    if (!data || data.length < 2) return null;

    const latest = data[data.length - 1];
    const prev = data[data.length - 2];

    const growthScore = latest.growth_score || 0;
    const rsi = latest.rsi || 50;
    const macdHist = latest.macd_histogram || 0;
    const inRiseCycle = latest.ema_12 > latest.ema_26;
    const pivotLow = latest.pivot_low_flag === 1;
    const pivotHigh = latest.pivot_high_flag === 1;
    const aboveSMA200 = latest.close > (latest.sma_200 || 0);

    // Calculate signal strength (0-100)
    let strength = 0;
    let factors = [];

    // Growth Score component (40 points max)
    strength += Math.min(growthScore * 0.4, 40);
    if (growthScore >= 75) factors.push('High Growth Score');

    // RSI sweet spot (20 points)
    if (rsi >= 40 && rsi <= 65) {
      strength += 20;
      factors.push('RSI Sweet Spot');
    }

    // MACD positive (15 points)
    if (macdHist > 0) {
      strength += 15;
      factors.push('MACD Bullish');
    }

    // In rise cycle (15 points)
    if (inRiseCycle) {
      strength += 15;
      factors.push('EMA Rise Cycle');
    }

    // Pivot low (10 points - potential bounce)
    if (pivotLow) {
      strength += 10;
      factors.push('Pivot Low Signal');
    }

    // Above SMA 200 (bonus)
    if (aboveSMA200) factors.push('Above 200 SMA');

    // Determine recommendation
    let recommendation = 'HOLD';
    if (strength >= 80) recommendation = 'STRONG_BUY';
    else if (strength >= 60) recommendation = 'BUY';
    else if (strength >= 40) recommendation = 'HOLD';
    else if (strength >= 20) recommendation = 'SELL';
    else recommendation = 'STRONG_SELL';

    return {
      timeframe: 'daily',
      strength,
      recommendation,
      factors,
      metrics: {
        growthScore,
        rsi,
        macdHist,
        inRiseCycle,
        pivotLow,
        pivotHigh,
        close: latest.close,
        volume: latest.volume
      },
      timestamp: new Date().toISOString()
    };
  };

  // Analyze hourly data for timing
  const analyzeHourlySignal = (data) => {
    if (!data || data.length < 3) return null;

    const latest = data[data.length - 1];
    const prev = data[data.length - 2];
    const prev2 = data[data.length - 3];

    const ema12 = latest.ema_12 || 0;
    const ema26 = latest.ema_26 || 0;
    const prevEma12 = prev.ema_12 || 0;
    const prevEma26 = prev.ema_26 || 0;

    const inRiseCycle = ema12 > ema26;
    const riseCycleStart = inRiseCycle && prevEma12 <= prevEma26;
    const fallCycleStart = !inRiseCycle && prevEma12 >= prevEma26;

    const rsi = latest.rsi || 50;
    const macdHist = latest.macd_histogram || 0;
    const volume = latest.volume || 0;
    const avgVolume = data.slice(-20).reduce((sum, d) => sum + (d.volume || 0), 0) / 20;
    const volumeSpike = volume > avgVolume * 1.5;

    let strength = 50; // Start neutral
    let factors = [];

    // Rise cycle start is the best timing (30 points)
    if (riseCycleStart) {
      strength += 30;
      factors.push('RISE CYCLE START!');
    } else if (inRiseCycle) {
      strength += 15;
      factors.push('In Rise Cycle');
    } else if (fallCycleStart) {
      strength -= 30;
      factors.push('Fall Cycle Start');
    } else {
      strength -= 15;
      factors.push('In Fall Cycle');
    }

    // RSI momentum (15 points)
    if (rsi > 50 && rsi < 70) {
      strength += 15;
      factors.push('RSI Bullish');
    } else if (rsi < 30) {
      strength += 10;
      factors.push('RSI Oversold');
    } else if (rsi > 70) {
      strength -= 15;
      factors.push('RSI Overbought');
    }

    // Volume confirmation (10 points)
    if (volumeSpike && inRiseCycle) {
      strength += 10;
      factors.push('Volume Spike');
    }

    // MACD acceleration
    if (macdHist > 0 && macdHist > prev.macd_histogram) {
      strength += 10;
      factors.push('MACD Accelerating');
    }

    let recommendation = 'HOLD';
    if (strength >= 80) recommendation = 'STRONG_BUY';
    else if (strength >= 60) recommendation = 'BUY';
    else if (strength >= 40) recommendation = 'HOLD';
    else if (strength >= 20) recommendation = 'SELL';
    else recommendation = 'STRONG_SELL';

    return {
      timeframe: 'hourly',
      strength,
      recommendation,
      factors,
      metrics: {
        ema12,
        ema26,
        inRiseCycle,
        riseCycleStart,
        fallCycleStart,
        rsi,
        volumeSpike,
        close: latest.close
      },
      timestamp: new Date().toISOString()
    };
  };

  // Analyze 5-minute data for execution
  const analyzeFiveMinSignal = (data) => {
    if (!data || data.length < 5) return null;

    const latest = data[data.length - 1];
    const prev = data[data.length - 2];

    const ema9 = latest.ema_9 || latest.ema_12 || latest.close;
    const ema21 = latest.ema_21 || latest.ema_26 || latest.close;
    const prevEma9 = prev.ema_9 || prev.ema_12 || prev.close;
    const prevEma21 = prev.ema_21 || prev.ema_26 || prev.close;

    const microTrendUp = ema9 > ema21;
    const microCrossUp = microTrendUp && prevEma9 <= prevEma21;
    const microCrossDown = !microTrendUp && prevEma9 >= prevEma21;

    const rsi = latest.rsi || 50;
    const macdHist = latest.macd_histogram || 0;
    const priceVsVwap = latest.vwap_daily ? (latest.close / latest.vwap_daily - 1) * 100 : 0;

    let strength = 50;
    let factors = [];
    let entrySignal = null;

    // Micro cross signals (25 points)
    if (microCrossUp) {
      strength += 25;
      factors.push('MICRO BUY SIGNAL!');
      entrySignal = 'BUY_NOW';
    } else if (microCrossDown) {
      strength -= 25;
      factors.push('MICRO SELL SIGNAL!');
      entrySignal = 'SELL_NOW';
    } else if (microTrendUp) {
      strength += 10;
      factors.push('Micro Uptrend');
    } else {
      strength -= 10;
      factors.push('Micro Downtrend');
    }

    // RSI for timing (15 points)
    if (rsi < 35) {
      strength += 15;
      factors.push('Oversold Entry');
      if (!entrySignal) entrySignal = 'CONSIDER_BUY';
    } else if (rsi > 65) {
      strength -= 15;
      factors.push('Overbought Exit');
      if (!entrySignal) entrySignal = 'CONSIDER_SELL';
    }

    // VWAP position (10 points)
    if (priceVsVwap < -0.5) {
      strength += 10;
      factors.push('Below VWAP');
    } else if (priceVsVwap > 0.5) {
      strength -= 5;
      factors.push('Above VWAP');
    }

    let recommendation = 'HOLD';
    if (strength >= 75) recommendation = 'STRONG_BUY';
    else if (strength >= 55) recommendation = 'BUY';
    else if (strength >= 45) recommendation = 'HOLD';
    else if (strength >= 25) recommendation = 'SELL';
    else recommendation = 'STRONG_SELL';

    return {
      timeframe: '5min',
      strength,
      recommendation,
      factors,
      entrySignal,
      metrics: {
        microTrendUp,
        microCrossUp,
        microCrossDown,
        rsi,
        priceVsVwap,
        close: latest.close,
        vwap: latest.vwap_daily
      },
      timestamp: new Date().toISOString()
    };
  };

  // Combine signals for final recommendation
  const combinedSignals = (daily, hourly, fiveMin) => {
    if (!daily && !hourly && !fiveMin) return null;

    const weights = { daily: 0.5, hourly: 0.3, fiveMin: 0.2 };

    let totalStrength = 0;
    let activeTimeframes = 0;
    let factors = [];

    if (daily) {
      totalStrength += daily.strength * weights.daily;
      activeTimeframes++;
      if (daily.recommendation === 'STRONG_BUY' || daily.recommendation === 'BUY') {
        factors.push('Daily: ' + daily.factors[0]);
      }
    }

    if (hourly) {
      totalStrength += hourly.strength * weights.hourly;
      activeTimeframes++;
      if (hourly.metrics?.riseCycleStart) {
        factors.push('Hourly: Rise Cycle Start!');
      }
    }

    if (fiveMin) {
      totalStrength += fiveMin.strength * weights.fiveMin;
      activeTimeframes++;
      if (fiveMin.entrySignal === 'BUY_NOW') {
        factors.push('5min: Buy Signal Active!');
      }
    }

    const avgStrength = activeTimeframes > 0 ? totalStrength / activeTimeframes : 50;

    // Check for aligned signals
    const dailyBullish = daily?.recommendation?.includes('BUY');
    const hourlyBullish = hourly?.recommendation?.includes('BUY');
    const fiveMinBullish = fiveMin?.recommendation?.includes('BUY');
    const allAligned = dailyBullish && hourlyBullish && fiveMinBullish;

    let recommendation = 'HOLD';
    let action = null;

    if (allAligned && avgStrength >= 60) {
      recommendation = 'STRONG_BUY';
      action = 'EXECUTE_BUY';
      factors.push('ALL TIMEFRAMES ALIGNED!');
    } else if (dailyBullish && hourlyBullish && avgStrength >= 55) {
      recommendation = 'BUY';
      action = 'PREPARE_BUY';
    } else if (avgStrength >= 45) {
      recommendation = 'HOLD';
      action = 'MONITOR';
    } else {
      recommendation = 'AVOID';
      action = 'STAY_OUT';
    }

    return {
      strength: avgStrength,
      recommendation,
      action,
      factors,
      alignment: {
        daily: dailyBullish,
        hourly: hourlyBullish,
        fiveMin: fiveMinBullish,
        allAligned
      },
      timestamp: new Date().toISOString()
    };
  };

  // Load all data for selected symbol
  const loadSymbolData = useCallback(async (symbol) => {
    setIsLoading(true);
    setError(null);

    try {
      const [daily, hourly, fiveMin] = await Promise.all([
        fetchTimeframeData(symbol, 'daily'),
        fetchTimeframeData(symbol, 'hourly'),
        fetchTimeframeData(symbol, 'fivemin')
      ]);

      setDailyData(daily);
      setHourlyData(hourly);
      setFiveMinData(fiveMin);

      // Analyze signals
      const dailySig = analyzeDailySignal(daily);
      const hourlySig = analyzeHourlySignal(hourly);
      const fiveMinSig = analyzeFiveMinSignal(fiveMin);

      setDailySignal(dailySig);
      setHourlySignal(hourlySig);
      setFiveMinSignal(fiveMinSig);
      setCombinedSignal(combinedSignals(dailySig, hourlySig, fiveMinSig));

      setLastUpdate(new Date());

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [fetchTimeframeData]);

  // Initial load
  useEffect(() => {
    fetchHotStocks();
    loadSymbolData(selectedSymbol);
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadSymbolData(selectedSymbol);
    }, 30000);

    return () => clearInterval(interval);
  }, [autoRefresh, selectedSymbol, loadSymbolData]);

  // Handle symbol selection
  const handleSymbolSelect = (symbol) => {
    setSelectedSymbol(symbol);
    loadSymbolData(symbol);
  };

  // Signal badge component
  const SignalBadge = ({ signal, size = 'normal' }) => {
    if (!signal) return null;

    const colors = SIGNAL_COLORS[signal.recommendation] || '#6b7280';
    const sizeClasses = size === 'large' ? 'text-2xl px-6 py-3' : 'text-sm px-3 py-1';

    return (
      <span
        style={{
          background: `${colors}22`,
          color: colors,
          border: `1px solid ${colors}`,
          borderRadius: '8px',
          padding: size === 'large' ? '12px 24px' : '4px 12px',
          fontSize: size === 'large' ? '18px' : '12px',
          fontWeight: '700',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px'
        }}
      >
        {signal.recommendation}
        <span style={{ fontSize: size === 'large' ? '14px' : '10px', opacity: 0.8 }}>
          ({Math.round(signal.strength)}%)
        </span>
      </span>
    );
  };

  // Timeframe panel component
  const TimeframePanel = ({ timeframe, data, signal, expanded, onToggle }) => {
    const config = TIMEFRAMES[timeframe];
    const chartData = data.slice(-50);

    return (
      <div
        style={{
          flex: expanded ? 2 : 1,
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          border: `2px solid ${config.color}44`,
          overflow: 'hidden',
          transition: 'all 0.3s ease'
        }}
      >
        {/* Header */}
        <div
          style={{
            background: `${config.color}22`,
            padding: '16px',
            borderBottom: `1px solid ${config.color}44`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer'
          }}
          onClick={() => onToggle(expanded ? null : timeframe)}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '24px' }}>{config.icon}</span>
            <div>
              <h3 style={{ color: config.color, margin: 0, fontSize: '18px' }}>{config.label}</h3>
              <span style={{ color: '#94a3b8', fontSize: '12px' }}>
                {data.length} candles
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {signal && <SignalBadge signal={signal} />}
            {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>
        </div>

        {/* Signal Factors */}
        {signal && (
          <div style={{ padding: '12px 16px', background: '#0f172a55' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {signal.factors.map((factor, i) => (
                <span
                  key={i}
                  style={{
                    background: factor.includes('!') ? '#10b98133' : '#334155',
                    color: factor.includes('!') ? '#10b981' : '#94a3b8',
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: factor.includes('!') ? '700' : '500'
                  }}
                >
                  {factor}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Chart */}
        <div style={{ height: expanded ? '400px' : '200px', padding: '16px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="datetime"
                tick={{ fill: '#64748b', fontSize: 10 }}
                tickFormatter={(val) => {
                  if (timeframe === 'daily') return val.split(',')[0];
                  return val.split(',')[1]?.trim().split(':').slice(0, 2).join(':') || val;
                }}
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fill: '#64748b', fontSize: 10 }}
                tickFormatter={(val) => `$${val.toFixed(2)}`}
              />
              <Tooltip
                contentStyle={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px'
                }}
              />

              {/* EMA lines */}
              <Line
                type="monotone"
                dataKey="ema_12"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                name="EMA 12"
              />
              <Line
                type="monotone"
                dataKey="ema_26"
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
                name="EMA 26"
              />

              {/* Price area */}
              <Area
                type="monotone"
                dataKey="close"
                stroke={config.color}
                fill={`${config.color}22`}
                strokeWidth={2}
                name="Price"
              />

              {/* Pivot flags */}
              {chartData.map((d, i) => (
                d.pivot_low_flag === 1 && (
                  <ReferenceLine
                    key={`low-${i}`}
                    x={d.datetime}
                    stroke="#10b981"
                    strokeDasharray="3 3"
                  />
                )
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Metrics */}
        {signal && expanded && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '12px',
            padding: '16px',
            borderTop: '1px solid #334155'
          }}>
            {Object.entries(signal.metrics).slice(0, 8).map(([key, value]) => (
              <div key={key} style={{ textAlign: 'center' }}>
                <div style={{ color: '#64748b', fontSize: '11px', marginBottom: '4px' }}>
                  {key.replace(/_/g, ' ').toUpperCase()}
                </div>
                <div style={{ color: 'white', fontSize: '14px', fontWeight: '600' }}>
                  {typeof value === 'boolean'
                    ? (value ? 'Yes' : 'No')
                    : typeof value === 'number'
                    ? value.toFixed(2)
                    : value}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: '24px', minHeight: '100vh', background: '#0a0e27' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div>
          <h1 style={{ color: 'white', margin: 0, fontSize: '28px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Layers style={{ color: '#3b82f6' }} />
            Multi-Timeframe Trade Analysis
          </h1>
          <p style={{ color: '#64748b', margin: '8px 0 0' }}>
            Daily opportunity detection | Hourly cycle timing | 5-minute execution
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            style={{
              background: autoRefresh ? '#10b98133' : '#33415555',
              color: autoRefresh ? '#10b981' : '#64748b',
              border: `1px solid ${autoRefresh ? '#10b981' : '#334155'}`,
              borderRadius: '8px',
              padding: '8px 16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <RefreshCw size={16} className={autoRefresh ? 'animate-spin' : ''} />
            Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
          </button>

          {lastUpdate && (
            <span style={{ color: '#64748b', fontSize: '12px' }}>
              Updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Combined Signal */}
      {combinedSignal && (
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px',
          border: combinedSignal.alignment.allAligned
            ? '2px solid #10b981'
            : '1px solid #334155'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ color: 'white', margin: 0, fontSize: '20px' }}>
                {selectedSymbol} - Combined Analysis
              </h2>
              <div style={{ display: 'flex', gap: '16px', marginTop: '12px' }}>
                {combinedSignal.factors.map((factor, i) => (
                  <span
                    key={i}
                    style={{
                      color: factor.includes('ALIGNED') ? '#10b981' : '#94a3b8',
                      fontWeight: factor.includes('ALIGNED') ? '700' : '500'
                    }}
                  >
                    {factor}
                  </span>
                ))}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <SignalBadge signal={combinedSignal} size="large" />
              {combinedSignal.action && (
                <div style={{
                  marginTop: '12px',
                  color: combinedSignal.action === 'EXECUTE_BUY' ? '#10b981' : '#f59e0b',
                  fontWeight: '700'
                }}>
                  Action: {combinedSignal.action.replace(/_/g, ' ')}
                </div>
              )}
            </div>
          </div>

          {/* Alignment indicator */}
          <div style={{
            display: 'flex',
            gap: '16px',
            marginTop: '16px',
            paddingTop: '16px',
            borderTop: '1px solid #334155'
          }}>
            {['daily', 'hourly', 'fiveMin'].map((tf) => (
              <div
                key={tf}
                style={{
                  flex: 1,
                  textAlign: 'center',
                  padding: '12px',
                  background: combinedSignal.alignment[tf] ? '#10b98122' : '#ef444422',
                  borderRadius: '8px',
                  border: `1px solid ${combinedSignal.alignment[tf] ? '#10b981' : '#ef4444'}`
                }}
              >
                <div style={{
                  color: combinedSignal.alignment[tf] ? '#10b981' : '#ef4444',
                  fontWeight: '700'
                }}>
                  {tf === 'fiveMin' ? '5-MIN' : tf.toUpperCase()}
                </div>
                <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                  {combinedSignal.alignment[tf] ? 'BULLISH' : 'NEUTRAL/BEARISH'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hot Stocks Selector */}
      <div style={{
        background: '#1e293b',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '24px',
        border: '1px solid #334155'
      }}>
        <h3 style={{ color: '#f59e0b', margin: '0 0 12px', fontSize: '14px' }}>
          Hot Stocks (Growth Score 50+)
        </h3>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {hotStocks.slice(0, 15).map((stock) => (
            <button
              key={stock.symbol}
              onClick={() => handleSymbolSelect(stock.symbol)}
              style={{
                background: selectedSymbol === stock.symbol ? '#3b82f6' : '#0f172a',
                color: selectedSymbol === stock.symbol ? 'white' : '#94a3b8',
                border: `1px solid ${selectedSymbol === stock.symbol ? '#3b82f6' : '#334155'}`,
                borderRadius: '8px',
                padding: '8px 16px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                minWidth: '80px'
              }}
            >
              <span style={{ fontWeight: '700' }}>{stock.symbol}</span>
              <span style={{
                fontSize: '10px',
                color: (stock.growth_score || 0) >= 75 ? '#10b981' : '#f59e0b'
              }}>
                GS: {stock.growth_score || 0}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Three-Panel View */}
      {isLoading ? (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '400px',
          color: '#64748b'
        }}>
          <RefreshCw className="animate-spin" style={{ marginRight: '12px' }} />
          Loading {selectedSymbol} data...
        </div>
      ) : (
        <div style={{
          display: 'flex',
          gap: '16px',
          transition: 'all 0.3s ease'
        }}>
          <TimeframePanel
            timeframe="daily"
            data={dailyData}
            signal={dailySignal}
            expanded={expandedPanel === 'daily'}
            onToggle={setExpandedPanel}
          />
          <TimeframePanel
            timeframe="hourly"
            data={hourlyData}
            signal={hourlySignal}
            expanded={expandedPanel === 'hourly'}
            onToggle={setExpandedPanel}
          />
          <TimeframePanel
            timeframe="fivemin"
            data={fiveMinData}
            signal={fiveMinSignal}
            expanded={expandedPanel === 'fivemin'}
            onToggle={setExpandedPanel}
          />
        </div>
      )}

      {/* Trading Strategy Guide */}
      <div style={{
        marginTop: '24px',
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155'
      }}>
        <h3 style={{ color: '#3b82f6', margin: '0 0 16px' }}>
          Multi-Timeframe Trading Strategy
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
          <div>
            <h4 style={{ color: '#10b981', margin: '0 0 8px' }}>Step 1: Daily Screening</h4>
            <ul style={{ color: '#94a3b8', margin: 0, paddingLeft: '20px', fontSize: '13px' }}>
              <li>Look for Growth Score 75+</li>
              <li>RSI between 40-65 (sweet spot)</li>
              <li>MACD histogram positive</li>
              <li>Price above SMA 200</li>
              <li>Watch for pivot_low_flag signals</li>
            </ul>
          </div>
          <div>
            <h4 style={{ color: '#8b5cf6', margin: '0 0 8px' }}>Step 2: Hourly Timing</h4>
            <ul style={{ color: '#94a3b8', margin: 0, paddingLeft: '20px', fontSize: '13px' }}>
              <li>Wait for EMA 12/26 rise cycle START</li>
              <li>Confirm with volume spike 1.5x</li>
              <li>RSI momentum above 50</li>
              <li>MACD accelerating positive</li>
              <li>Best entries: Rise Cycle Start</li>
            </ul>
          </div>
          <div>
            <h4 style={{ color: '#ec4899', margin: '0 0 8px' }}>Step 3: 5-Min Execution</h4>
            <ul style={{ color: '#94a3b8', margin: 0, paddingLeft: '20px', fontSize: '13px' }}>
              <li>Wait for micro EMA crossover UP</li>
              <li>Enter when RSI oversold 30-35</li>
              <li>Buy below VWAP for value</li>
              <li>Exit on overbought RSI 65+</li>
              <li>Stop loss: below recent pivot low</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MultiTimeframeTrader;
