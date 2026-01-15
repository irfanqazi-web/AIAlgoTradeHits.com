import { useState, useEffect, useRef } from 'react';
import { TrendingUp, TrendingDown, Activity, Check, ArrowUpDown, Sun, Moon, RefreshCw } from 'lucide-react';
import { createChart } from 'lightweight-charts';
import themes from '../theme';

const API_BASE = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-252370699783.us-central1.run.app'
);

// Asset type configurations
const ASSET_TYPES = [
  { id: 'etfs', label: 'ETFs', icon: '📊', color: '#3b82f6', table: 'etfs_weekly_summary' },
  { id: 'forex', label: 'Forex', icon: '💱', color: '#10b981', table: 'forex_weekly_summary' },
  { id: 'indices', label: 'Indices', icon: '📈', color: '#8b5cf6', table: 'indices_weekly_summary' },
  { id: 'commodities', label: 'Commodities', icon: '🛢️', color: '#f59e0b', table: 'commodities_weekly_summary' },
  { id: 'stocks', label: 'Stocks', icon: '🏢', color: '#ef4444', table: 'stocks_weekly_summary' },
  { id: 'cryptos', label: 'Cryptos', icon: '🪙', color: '#06b6d4', table: 'cryptos_weekly_summary' },
];

export default function WeeklyDashboard() {
  const [activeAssetType, setActiveAssetType] = useState('etfs');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [summaryStats, setSummaryStats] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: 'weekly_change_percent', direction: 'desc' });
  const [selectedItem, setSelectedItem] = useState(null);
  const [theme, setTheme] = useState('dark');
  const [lastUpdated, setLastUpdated] = useState(null);

  const currentTheme = themes[theme];

  useEffect(() => {
    loadWeeklyData();
    loadAllSummaryStats();
  }, [activeAssetType]);

  const loadAllSummaryStats = async () => {
    const stats = {};
    for (const assetType of ASSET_TYPES) {
      try {
        const response = await fetch(`${API_BASE}/api/weekly/${assetType.id}/summary`);
        if (response.ok) {
          const data = await response.json();
          stats[assetType.id] = data;
        }
      } catch (error) {
        console.log(`Error loading ${assetType.id} summary:`, error);
        stats[assetType.id] = { count: 0, avg_change: 0 };
      }
    }
    setSummaryStats(stats);
  };

  const loadWeeklyData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/weekly/${activeAssetType}`);
      if (response.ok) {
        const result = await response.json();
        const sortedData = [...(result.data || [])].sort((a, b) =>
          (b.weekly_change_percent || 0) - (a.weekly_change_percent || 0)
        );
        setData(sortedData);
        if (sortedData.length > 0) {
          setSelectedItem(sortedData[0]);
        }
        setLastUpdated(new Date().toLocaleString());
      } else {
        // Fallback: Try direct BigQuery query through NLP endpoint
        await loadDataDirectly();
      }
    } catch (error) {
      console.error('Error loading weekly data:', error);
      await loadDataDirectly();
    } finally {
      setLoading(false);
    }
  };

  const loadDataDirectly = async () => {
    try {
      const assetConfig = ASSET_TYPES.find(a => a.id === activeAssetType);
      const response = await fetch(`${API_BASE}/api/analysis/nlp-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `SELECT * FROM \`cryptobot-462709.crypto_trading_data.${assetConfig.table}\` ORDER BY weekly_change_percent DESC LIMIT 200`,
          input_method: 'direct'
        })
      });
      if (response.ok) {
        const result = await response.json();
        setData(result.results || []);
        if (result.results?.length > 0) {
          setSelectedItem(result.results[0]);
        }
      }
    } catch (error) {
      console.error('Direct query failed:', error);
      setData([]);
    }
  };

  const handleSort = (key) => {
    let direction = 'desc';
    if (sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc';
    }
    setSortConfig({ key, direction });

    const sorted = [...data].sort((a, b) => {
      const aVal = a[key] || 0;
      const bVal = b[key] || 0;
      return direction === 'asc' ? aVal - bVal : bVal - aVal;
    });
    setData(sorted);
  };

  const handleRowClick = (item) => {
    setSelectedItem(item);
  };

  const getAssetConfig = () => ASSET_TYPES.find(a => a.id === activeAssetType);

  return (
    <div style={{ padding: '24px', background: currentTheme.background, minHeight: '100vh' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <h1 style={{ color: currentTheme.text, fontSize: '28px', margin: 0 }}>
          📅 Weekly Market Dashboard
        </h1>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            onClick={() => { loadWeeklyData(); loadAllSummaryStats(); }}
            style={{
              padding: '10px 16px',
              background: currentTheme.primary,
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <RefreshCw size={16} /> Refresh
          </button>
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            style={{
              padding: '10px 16px',
              background: currentTheme.cardBg,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            {theme === 'dark' ? 'Light' : 'Dark'}
          </button>
        </div>
      </div>

      {/* 6 Asset Type Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(6, 1fr)',
        gap: '16px',
        marginBottom: '24px'
      }}>
        {ASSET_TYPES.map(asset => {
          const stats = summaryStats[asset.id] || {};
          const isActive = activeAssetType === asset.id;
          return (
            <div
              key={asset.id}
              onClick={() => setActiveAssetType(asset.id)}
              style={{
                background: isActive
                  ? `linear-gradient(135deg, ${asset.color}22, ${asset.color}44)`
                  : currentTheme.cardBg,
                borderRadius: '16px',
                padding: '20px',
                border: isActive ? `2px solid ${asset.color}` : `1px solid ${currentTheme.cardBorder}`,
                cursor: 'pointer',
                transition: 'all 0.3s',
                transform: isActive ? 'scale(1.02)' : 'scale(1)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontSize: '28px' }}>{asset.icon}</span>
                <span style={{
                  padding: '4px 10px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: '600',
                  background: asset.color,
                  color: 'white'
                }}>
                  {stats.count || 0}
                </span>
              </div>
              <div style={{ color: currentTheme.text, fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
                {asset.label}
              </div>
              <div style={{
                color: (stats.avg_change || 0) >= 0 ? '#10b981' : '#ef4444',
                fontSize: '14px',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                {(stats.avg_change || 0) >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {(stats.avg_change || 0).toFixed(2)}% avg
              </div>
            </div>
          );
        })}
      </div>

      {/* Chart Section */}
      {selectedItem && (
        <div style={{
          background: currentTheme.cardBg,
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px',
          border: `1px solid ${currentTheme.cardBorder}`
        }}>
          <WeeklyChart item={selectedItem} theme={theme} assetType={activeAssetType} />
        </div>
      )}

      {/* Data Table */}
      <div style={{
        background: currentTheme.cardBg,
        borderRadius: '16px',
        padding: '24px',
        border: `1px solid ${currentTheme.cardBorder}`
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ color: getAssetConfig()?.color, fontSize: '20px', margin: 0 }}>
            {getAssetConfig()?.icon} {getAssetConfig()?.label} Weekly Summary ({data.length} items)
          </h3>
          {lastUpdated && (
            <span style={{ color: currentTheme.textMuted, fontSize: '12px' }}>
              Last updated: {lastUpdated}
            </span>
          )}
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: currentTheme.text }}>
            <RefreshCw size={32} style={{ animation: 'spin 1s linear infinite' }} />
            <div style={{ marginTop: '12px' }}>Loading weekly data...</div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              color: currentTheme.text,
              fontSize: '14px'
            }}>
              <thead>
                <tr style={{ borderBottom: `2px solid ${currentTheme.cardBorder}` }}>
                  <th style={{ padding: '12px', textAlign: 'left', color: currentTheme.textSecondary }}>#</th>
                  <SortableHeader label="Symbol" sortKey="symbol" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="Name" sortKey="name" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="Price" sortKey="current_price" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="Weekly %" sortKey="weekly_change_percent" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="Monthly %" sortKey="monthly_change_percent" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="52W High" sortKey="week_52_high" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="52W Low" sortKey="week_52_low" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="Volatility" sortKey="volatility_weekly" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <th style={{ padding: '12px', textAlign: 'left', color: currentTheme.textSecondary }}>Trend</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item, index) => {
                  const isSelected = selectedItem?.symbol === item.symbol;
                  return (
                    <tr
                      key={index}
                      onClick={() => handleRowClick(item)}
                      style={{
                        borderBottom: `1px solid ${currentTheme.cardBorder}`,
                        background: isSelected ? `${getAssetConfig()?.color}22` : 'transparent',
                        cursor: 'pointer',
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => !isSelected && (e.currentTarget.style.background = `${currentTheme.primary}11`)}
                      onMouseLeave={(e) => !isSelected && (e.currentTarget.style.background = 'transparent')}
                    >
                      <td style={{ padding: '12px', color: currentTheme.textMuted }}>{index + 1}</td>
                      <td style={{ padding: '12px', fontWeight: '600' }}>{item.symbol}</td>
                      <td style={{ padding: '12px', color: currentTheme.textSecondary, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {item.name || '-'}
                      </td>
                      <td style={{ padding: '12px' }}>
                        ${(item.current_price || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          color: (item.weekly_change_percent || 0) >= 0 ? '#10b981' : '#ef4444',
                          fontWeight: '600',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}>
                          {(item.weekly_change_percent || 0) >= 0 ? '▲' : '▼'}
                          {Math.abs(item.weekly_change_percent || 0).toFixed(2)}%
                        </span>
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          color: (item.monthly_change_percent || 0) >= 0 ? '#10b981' : '#ef4444',
                          fontWeight: '600'
                        }}>
                          {(item.monthly_change_percent || 0).toFixed(2)}%
                        </span>
                      </td>
                      <td style={{ padding: '12px', color: '#10b981' }}>
                        ${(item.week_52_high || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                      </td>
                      <td style={{ padding: '12px', color: '#ef4444' }}>
                        ${(item.week_52_low || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          background: item.volatility_category === 'high' ? '#ef4444'
                            : item.volatility_category === 'medium' ? '#f59e0b' : '#10b981',
                          color: 'white'
                        }}>
                          {item.volatility_category || 'low'}
                        </span>
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          background: item.trend_short === 'bullish' ? '#10b981' : '#ef4444',
                          color: 'white'
                        }}>
                          {item.trend_short || '-'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer */}
        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          background: currentTheme.background,
          borderRadius: '8px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span style={{ color: currentTheme.textSecondary, fontSize: '13px' }}>
            Data Source: <strong style={{ color: '#3b82f6' }}>Twelve Data API</strong> | Updated Weekly (Saturdays)
          </span>
          <span style={{ color: currentTheme.textMuted, fontSize: '12px' }}>
            {data.length} {getAssetConfig()?.label} tracked
          </span>
        </div>
      </div>
    </div>
  );
}

// Weekly Chart Component
function WeeklyChart({ item, theme, assetType }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const currentTheme = themes[theme];
  const assetConfig = ASSET_TYPES.find(a => a.id === assetType);

  useEffect(() => {
    if (!chartContainerRef.current || !item) return;

    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 350,
      layout: {
        background: { color: currentTheme.cardBg },
        textColor: currentTheme.text,
      },
      grid: {
        vertLines: { color: currentTheme.cardBorder },
        horzLines: { color: currentTheme.cardBorder },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Create price line series
    const lineSeries = chart.addLineSeries({
      color: assetConfig?.color || '#3b82f6',
      lineWidth: 3,
    });

    // Generate sample weekly data points based on current values
    const now = Date.now();
    const weekMs = 7 * 24 * 60 * 60 * 1000;
    const currentPrice = item.current_price || 0;
    const weeklyChange = item.weekly_change_percent || 0;
    const startPrice = currentPrice / (1 + weeklyChange / 100);

    const dataPoints = [];
    for (let i = 4; i >= 0; i--) {
      const time = Math.floor((now - i * weekMs) / 1000);
      const progress = (4 - i) / 4;
      const price = startPrice + (currentPrice - startPrice) * progress + (Math.random() - 0.5) * currentPrice * 0.02;
      dataPoints.push({ time, value: price });
    }

    lineSeries.setData(dataPoints);
    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
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
  }, [item, theme, assetType]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ color: assetConfig?.color, margin: 0, fontSize: '22px' }}>
            {assetConfig?.icon} {item.symbol}
          </h3>
          <p style={{ color: currentTheme.textSecondary, margin: '4px 0 0 0', fontSize: '14px' }}>
            {item.name || item.symbol}
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ color: currentTheme.text, fontSize: '28px', fontWeight: '700' }}>
            ${(item.current_price || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
          </div>
          <div style={{
            color: (item.weekly_change_percent || 0) >= 0 ? '#10b981' : '#ef4444',
            fontSize: '16px',
            fontWeight: '600'
          }}>
            {(item.weekly_change_percent || 0) >= 0 ? '▲' : '▼'} {Math.abs(item.weekly_change_percent || 0).toFixed(2)}% this week
          </div>
        </div>
      </div>

      <div ref={chartContainerRef} style={{ height: '350px' }} />

      {/* Stats Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(6, 1fr)',
        gap: '12px',
        marginTop: '16px',
        padding: '16px',
        background: currentTheme.background,
        borderRadius: '12px'
      }}>
        <StatBox label="Open" value={`$${(item.open_price || 0).toFixed(2)}`} theme={currentTheme} />
        <StatBox label="High" value={`$${(item.high_price || 0).toFixed(2)}`} theme={currentTheme} color="#10b981" />
        <StatBox label="Low" value={`$${(item.low_price || 0).toFixed(2)}`} theme={currentTheme} color="#ef4444" />
        <StatBox label="52W High" value={`$${(item.week_52_high || 0).toFixed(2)}`} theme={currentTheme} color="#10b981" />
        <StatBox label="52W Low" value={`$${(item.week_52_low || 0).toFixed(2)}`} theme={currentTheme} color="#ef4444" />
        <StatBox label="Volatility" value={`${(item.volatility_weekly || 0).toFixed(2)}%`} theme={currentTheme} />
      </div>
    </div>
  );
}

function StatBox({ label, value, theme, color }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ color: theme.textMuted, fontSize: '12px', marginBottom: '4px' }}>{label}</div>
      <div style={{ color: color || theme.text, fontSize: '14px', fontWeight: '600' }}>{value}</div>
    </div>
  );
}

function SortableHeader({ label, sortKey, sortConfig, onSort, theme }) {
  return (
    <th
      onClick={() => onSort(sortKey)}
      style={{
        padding: '12px',
        textAlign: 'left',
        color: theme.textSecondary,
        cursor: 'pointer',
        userSelect: 'none'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {label}
        <ArrowUpDown size={14} color={sortConfig.key === sortKey ? theme.primary : theme.textMuted} />
      </div>
    </th>
  );
}
