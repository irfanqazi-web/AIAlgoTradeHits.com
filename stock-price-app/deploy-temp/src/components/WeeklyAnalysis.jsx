import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Search, Filter, RefreshCw, Download, ArrowUp, ArrowDown, Activity } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://trading-api-252370699783.us-central1.run.app';

const WeeklyAnalysis = ({ assetType = 'stocks' }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    volatility: '',
    category: '',
    region: ''
  });
  const [sortBy, setSortBy] = useState('week_close');
  const [sortDir, setSortDir] = useState('desc');
  const [searchTerm, setSearchTerm] = useState('');

  const assetConfig = {
    stocks: {
      title: 'Stocks Weekly Analysis',
      endpoint: '/api/analysis/stocks/weekly',
      idField: 'symbol',
      nameField: 'name',
      filters: ['volatility', 'sector', 'market_cap'],
      color: '#10b981'
    },
    cryptos: {
      title: 'Cryptos Weekly Analysis',
      endpoint: '/api/analysis/cryptos/weekly',
      idField: 'symbol',
      nameField: 'name',
      filters: ['volatility', 'category'],
      color: '#f59e0b'
    },
    etfs: {
      title: 'ETFs Weekly Analysis',
      endpoint: '/api/analysis/etfs/weekly',
      idField: 'symbol',
      nameField: 'name',
      filters: ['volatility', 'category', 'subcategory'],
      color: '#8b5cf6'
    },
    forex: {
      title: 'Forex Weekly Analysis',
      endpoint: '/api/analysis/forex/weekly',
      idField: 'symbol',
      nameField: 'name',
      filters: ['volatility', 'category', 'base_currency'],
      color: '#3b82f6'
    },
    indices: {
      title: 'Indices Weekly Analysis',
      endpoint: '/api/analysis/indices/weekly',
      idField: 'symbol',
      nameField: 'name',
      filters: ['volatility', 'region', 'country'],
      color: '#ef4444'
    },
    commodities: {
      title: 'Commodities Weekly Analysis',
      endpoint: '/api/analysis/commodities/weekly',
      idField: 'symbol',
      nameField: 'name',
      filters: ['volatility', 'category', 'subcategory'],
      color: '#f97316'
    }
  };

  const config = assetConfig[assetType] || assetConfig.stocks;

  useEffect(() => {
    fetchData();
  }, [assetType, filters]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append('limit', '100');
      if (filters.volatility) params.append('volatility_category', filters.volatility);
      if (filters.category) params.append('category', filters.category);
      if (filters.region) params.append('region', filters.region);

      const response = await fetch(`${API_BASE}${config.endpoint}?${params.toString()}`);
      const result = await response.json();

      if (result.success) {
        setData(result.data || []);
      } else {
        setError(result.error || 'Failed to fetch data');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortDir('desc');
    }
  };

  const sortedData = [...data]
    .filter(item => {
      if (!searchTerm) return true;
      const search = searchTerm.toLowerCase();
      return (
        (item.symbol || '').toLowerCase().includes(search) ||
        (item.name || '').toLowerCase().includes(search)
      );
    })
    .sort((a, b) => {
      const aVal = a[sortBy] || 0;
      const bVal = b[sortBy] || 0;
      return sortDir === 'asc' ? aVal - bVal : bVal - aVal;
    });

  const formatPrice = (price) => {
    if (price === null || price === undefined) return '-';
    return price < 1 ? price.toFixed(6) : price.toFixed(2);
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return '-';
    const formatted = value.toFixed(2);
    const color = value >= 0 ? '#10b981' : '#ef4444';
    const icon = value >= 0 ? <ArrowUp size={12} /> : <ArrowDown size={12} />;
    return (
      <span style={{ color, display: 'flex', alignItems: 'center', gap: '4px' }}>
        {icon} {formatted}%
      </span>
    );
  };

  const exportToCSV = () => {
    const headers = ['Symbol', 'Name', 'Price', 'Weekly Change %', 'Volatility', 'Day Trade Score', 'Momentum'];
    const rows = sortedData.map(item => [
      item.symbol,
      item.name,
      item.current_price,
      item.weekly_change_percent,
      item.volatility_category,
      item.day_trade_score,
      item.momentum_category
    ]);

    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${assetType}_weekly_analysis.csv`;
    a.click();
  };

  return (
    <div style={{ padding: '24px', maxWidth: '100%' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div>
          <h1 style={{
            color: 'white',
            fontSize: '28px',
            fontWeight: 'bold',
            marginBottom: '8px'
          }}>
            {config.title}
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '14px' }}>
            Weekly performance metrics and trading scores for {assetType}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={fetchData}
            style={{
              background: '#334155',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 16px',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
          <button
            onClick={exportToCSV}
            style={{
              background: config.color,
              border: 'none',
              borderRadius: '8px',
              padding: '10px 16px',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Download size={16} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Filters */}
      <div style={{
        background: '#1e293b',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '24px',
        display: 'flex',
        gap: '16px',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '200px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: '#64748b' }} />
          <input
            type="text"
            placeholder="Search by symbol or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 10px 10px 40px',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: 'white',
              fontSize: '14px'
            }}
          />
        </div>

        <select
          value={filters.volatility}
          onChange={(e) => setFilters({ ...filters, volatility: e.target.value })}
          style={{
            padding: '10px 16px',
            background: '#0f172a',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: 'white',
            fontSize: '14px',
            minWidth: '150px'
          }}
        >
          <option value="">All Volatility</option>
          <option value="high">High Volatility</option>
          <option value="medium">Medium Volatility</option>
          <option value="low">Low Volatility</option>
        </select>

        {(assetType === 'stocks' || assetType === 'cryptos' || assetType === 'etfs' || assetType === 'commodities') && (
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            style={{
              padding: '10px 16px',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: 'white',
              fontSize: '14px',
              minWidth: '150px'
            }}
          >
            <option value="">All Categories</option>
            {assetType === 'stocks' && (
              <>
                <option value="Technology">Technology</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Financial Services">Financial Services</option>
                <option value="Energy">Energy</option>
                <option value="Consumer Cyclical">Consumer Cyclical</option>
              </>
            )}
            {assetType === 'cryptos' && (
              <>
                <option value="Smart Contract Platform">Smart Contract</option>
                <option value="DeFi">DeFi</option>
                <option value="Meme">Meme</option>
                <option value="Layer 2">Layer 2</option>
              </>
            )}
            {assetType === 'etfs' && (
              <>
                <option value="Equity">Equity</option>
                <option value="Bond">Bond</option>
                <option value="Leveraged">Leveraged</option>
                <option value="Sector">Sector</option>
              </>
            )}
            {assetType === 'commodities' && (
              <>
                <option value="Metals">Metals</option>
                <option value="Energy">Energy</option>
                <option value="Agriculture">Agriculture</option>
              </>
            )}
          </select>
        )}

        {assetType === 'indices' && (
          <select
            value={filters.region}
            onChange={(e) => setFilters({ ...filters, region: e.target.value })}
            style={{
              padding: '10px 16px',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: 'white',
              fontSize: '14px',
              minWidth: '150px'
            }}
          >
            <option value="">All Regions</option>
            <option value="North America">North America</option>
            <option value="Europe">Europe</option>
            <option value="Asia">Asia</option>
            <option value="Asia Pacific">Asia Pacific</option>
          </select>
        )}
      </div>

      {/* Stats Summary */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          background: '#1e293b',
          borderRadius: '12px',
          padding: '20px',
          borderLeft: `4px solid ${config.color}`
        }}>
          <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>Total Assets</div>
          <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>{sortedData.length}</div>
        </div>
        <div style={{
          background: '#1e293b',
          borderRadius: '12px',
          padding: '20px',
          borderLeft: '4px solid #10b981'
        }}>
          <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>Gaining</div>
          <div style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold' }}>
            {sortedData.filter(d => (d.weekly_change_percent || 0) > 0).length}
          </div>
        </div>
        <div style={{
          background: '#1e293b',
          borderRadius: '12px',
          padding: '20px',
          borderLeft: '4px solid #ef4444'
        }}>
          <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>Declining</div>
          <div style={{ color: '#ef4444', fontSize: '24px', fontWeight: 'bold' }}>
            {sortedData.filter(d => (d.weekly_change_percent || 0) < 0).length}
          </div>
        </div>
        <div style={{
          background: '#1e293b',
          borderRadius: '12px',
          padding: '20px',
          borderLeft: '4px solid #f59e0b'
        }}>
          <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>High Volatility</div>
          <div style={{ color: '#f59e0b', fontSize: '24px', fontWeight: 'bold' }}>
            {sortedData.filter(d => d.volatility_category === 'high').length}
          </div>
        </div>
      </div>

      {/* Data Table */}
      {loading ? (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '300px',
          background: '#1e293b',
          borderRadius: '12px'
        }}>
          <RefreshCw size={32} style={{ color: config.color, animation: 'spin 1s linear infinite' }} />
        </div>
      ) : error ? (
        <div style={{
          background: '#1e293b',
          borderRadius: '12px',
          padding: '40px',
          textAlign: 'center',
          color: '#ef4444'
        }}>
          {error}
        </div>
      ) : (
        <div style={{
          background: '#1e293b',
          borderRadius: '12px',
          overflow: 'hidden'
        }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              minWidth: '1400px',
              borderCollapse: 'collapse',
              fontSize: '13px'
            }}>
              <thead>
                <tr style={{ background: '#0f172a' }}>
                  <th style={{ ...headerStyle, width: '40px', textAlign: 'center' }}>SEL</th>
                  <th style={{ ...headerStyle, width: '80px' }} onClick={() => handleSort('symbol')}>
                    SYMBOL {sortBy === 'symbol' && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                  <th style={{ ...headerStyle, width: '140px' }}>NAME</th>
                  <th style={{ ...headerStyle, width: '90px' }} onClick={() => handleSort('week_start')}>
                    DATE {sortBy === 'week_start' && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                  <th style={{ ...headerStyle, width: '80px', textAlign: 'right' }} onClick={() => handleSort('week_open')}>
                    OPEN {sortBy === 'week_open' && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                  <th style={{ ...headerStyle, width: '80px', textAlign: 'right' }} onClick={() => handleSort('week_close')}>
                    CLOSE {sortBy === 'week_close' && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                  <th style={{ ...headerStyle, width: '80px', textAlign: 'right', color: '#10b981' }} onClick={() => handleSort('week_high')}>
                    HIGH {sortBy === 'week_high' && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                  <th style={{ ...headerStyle, width: '80px', textAlign: 'right', color: '#ef4444' }} onClick={() => handleSort('week_low')}>
                    LOW {sortBy === 'week_low' && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                  <th style={{ ...headerStyle, width: '80px', textAlign: 'right', color: '#10b981' }}>BUY VOL</th>
                  <th style={{ ...headerStyle, width: '80px', textAlign: 'right', color: '#ef4444' }}>SELL VOL</th>
                  <th style={{ ...headerStyle, width: '70px', textAlign: 'right' }}>HI-LO</th>
                  <th style={{ ...headerStyle, width: '70px', textAlign: 'right' }}>%HI-LO</th>
                  <th style={{ ...headerStyle, width: '60px', textAlign: 'right', color: '#a855f7' }} onClick={() => handleSort('rsi')}>
                    RSI {sortBy === 'rsi' && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                  <th style={{ ...headerStyle, width: '80px', textAlign: 'right', color: '#2196f3' }} onClick={() => handleSort('macd')}>
                    MACD {sortBy === 'macd' && (sortDir === 'asc' ? '↑' : '↓')}
                  </th>
                  <th style={{ ...headerStyle, width: '80px', textAlign: 'right', color: '#ff9800' }}>SIGNAL</th>
                  <th style={{ ...headerStyle, width: '100px', textAlign: 'center' }}>MACD HIST</th>
                </tr>
              </thead>
              <tbody>
                {sortedData.map((item, idx) => {
                  // Calculate derived values
                  const high = parseFloat(item.week_high) || parseFloat(item.high) || 0;
                  const low = parseFloat(item.week_low) || parseFloat(item.low) || 0;
                  const open = parseFloat(item.week_open) || parseFloat(item.open) || 0;
                  const close = parseFloat(item.week_close) || parseFloat(item.close) || 0;
                  const hiLo = high - low;
                  const pctHiLo = low > 0 ? ((hiLo / low) * 100) : 0;
                  const volume = parseFloat(item.week_volume) || parseFloat(item.volume) || 0;
                  const isBullish = close >= open;
                  const buyVol = isBullish ? volume : volume * 0.4;
                  const sellVol = isBullish ? volume * 0.4 : volume;
                  const macd = parseFloat(item.macd) || 0;
                  const macdSignal = parseFloat(item.macd_signal) || 0;
                  const macdHist = macd - macdSignal;
                  const rsi = item.rsi != null ? parseFloat(item.rsi) : null;
                  const dateStr = item.week_start || item.datetime || '';
                  const formattedDate = dateStr ? new Date(dateStr).toLocaleDateString() : '-';

                  return (
                    <tr key={item.symbol || idx} style={{
                      borderBottom: '1px solid #334155',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#334155'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <td style={{ ...cellStyle, textAlign: 'center' }}>
                        <input type="radio" name="selectedAsset" style={{ cursor: 'pointer', accentColor: config.color }} />
                      </td>
                      <td style={cellStyle}>
                        <span style={{ fontWeight: 'bold', color: config.color }}>{item.symbol}</span>
                      </td>
                      <td style={cellStyle}>
                        <span style={{ color: '#94a3b8', fontSize: '11px' }}>{(item.name || '').substring(0, 25)}</span>
                      </td>
                      <td style={{ ...cellStyle, fontSize: '11px', color: '#64748b' }}>{formattedDate}</td>
                      <td style={{ ...cellStyle, textAlign: 'right', fontFamily: 'monospace' }}>${formatPrice(open)}</td>
                      <td style={{ ...cellStyle, textAlign: 'right', fontFamily: 'monospace', fontWeight: '600' }}>${formatPrice(close)}</td>
                      <td style={{ ...cellStyle, textAlign: 'right', color: '#10b981', fontFamily: 'monospace' }}>${formatPrice(high)}</td>
                      <td style={{ ...cellStyle, textAlign: 'right', color: '#ef4444', fontFamily: 'monospace' }}>${formatPrice(low)}</td>
                      <td style={{ ...cellStyle, textAlign: 'right', color: '#10b981', fontSize: '11px' }}>
                        {buyVol >= 1000000 ? `${(buyVol/1000000).toFixed(1)}M` : buyVol >= 1000 ? `${(buyVol/1000).toFixed(0)}K` : buyVol.toFixed(0)}
                      </td>
                      <td style={{ ...cellStyle, textAlign: 'right', color: '#ef4444', fontSize: '11px' }}>
                        {sellVol >= 1000000 ? `${(sellVol/1000000).toFixed(1)}M` : sellVol >= 1000 ? `${(sellVol/1000).toFixed(0)}K` : sellVol.toFixed(0)}
                      </td>
                      <td style={{ ...cellStyle, textAlign: 'right', fontSize: '11px' }}>${hiLo.toFixed(2)}</td>
                      <td style={{ ...cellStyle, textAlign: 'right', fontSize: '11px', color: pctHiLo > 5 ? '#f59e0b' : '#64748b' }}>
                        {pctHiLo.toFixed(2)}%
                      </td>
                      <td style={{
                        ...cellStyle,
                        textAlign: 'right',
                        color: rsi === null ? '#64748b' : rsi < 30 ? '#ef4444' : rsi > 70 ? '#10b981' : '#a855f7',
                        fontWeight: (rsi !== null && (rsi < 30 || rsi > 70)) ? '600' : '400'
                      }}>
                        {rsi !== null ? rsi.toFixed(1) : '-'}
                      </td>
                      <td style={{ ...cellStyle, textAlign: 'right', color: '#2196f3', fontSize: '11px' }}>{macd.toFixed(4)}</td>
                      <td style={{ ...cellStyle, textAlign: 'right', color: '#ff9800', fontSize: '11px' }}>{macdSignal.toFixed(4)}</td>
                      <td style={{
                        ...cellStyle,
                        textAlign: 'center',
                        background: macdHist > 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                        color: macdHist > 0 ? '#10b981' : '#ef4444',
                        fontWeight: '700',
                        fontSize: '11px'
                      }}>
                        {macdHist > 0 ? `+${macdHist.toFixed(4)} BUY` : `${macdHist.toFixed(4)} SELL`}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {sortedData.length === 0 && (
            <div style={{
              padding: '40px',
              textAlign: 'center',
              color: '#64748b'
            }}>
              No data available. Data will be populated after the next scheduled run on Saturday.
            </div>
          )}
        </div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

const headerStyle = {
  padding: '16px',
  textAlign: 'left',
  color: '#94a3b8',
  fontWeight: '600',
  cursor: 'pointer',
  whiteSpace: 'nowrap',
  borderBottom: '1px solid #334155'
};

const cellStyle = {
  padding: '14px 16px',
  color: 'white'
};

export default WeeklyAnalysis;
