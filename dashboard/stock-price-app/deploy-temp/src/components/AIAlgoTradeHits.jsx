import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, Settings, History, Clock, Users, Target, Zap, Brain, AlertCircle, Maximize2, X } from 'lucide-react';

// Separate window component for expanded analytics
const AnalyticsWindow = ({ timeframe, onClose }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    // TODO: Fetch real data from BigQuery based on timeframe
    // For now, using mock data
    setData(generateMockData(timeframe));
  }, [timeframe]);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: '#0a0e27',
      zIndex: 9999,
      overflow: 'auto',
      padding: '20px'
    }}>
      <div style={{
        maxWidth: '1800px',
        margin: '0 auto'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px',
          borderBottom: '2px solid #1e293b',
          paddingBottom: '20px'
        }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: 0
          }}>
            {timeframe} Analytics - Deep Dive
          </h1>
          <button
            onClick={onClose}
            style={{
              background: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 24px',
              fontSize: '16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.3s'
            }}
            onMouseOver={(e) => e.target.style.background = '#dc2626'}
            onMouseOut={(e) => e.target.style.background = '#ef4444'}
          >
            <X size={20} />
            Close
          </button>
        </div>

        {/* Analytics Content */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '20px',
          marginBottom: '30px'
        }}>
          {/* Stats Overview */}
          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #334155'
          }}>
            <h3 style={{ color: '#10b981', marginBottom: '16px', fontSize: '20px' }}>Market Overview</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>Total Pairs</p>
                <p style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>675</p>
              </div>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>Active</p>
                <p style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold' }}>652</p>
              </div>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>Gainers</p>
                <p style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold' }}>387</p>
              </div>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>Losers</p>
                <p style={{ color: '#ef4444', fontSize: '24px', fontWeight: 'bold' }}>265</p>
              </div>
            </div>
          </div>

          {/* Technical Indicators Summary */}
          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #334155'
          }}>
            <h3 style={{ color: '#3b82f6', marginBottom: '16px', fontSize: '20px' }}>Technical Signals</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>Oversold (RSI &lt; 30)</p>
                <p style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold' }}>42</p>
              </div>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>Overbought (RSI &gt; 70)</p>
                <p style={{ color: '#ef4444', fontSize: '24px', fontWeight: 'bold' }}>28</p>
              </div>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>MACD Bullish</p>
                <p style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold' }}>358</p>
              </div>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>Strong Trend (ADX &gt; 25)</p>
                <p style={{ color: '#f59e0b', fontSize: '24px', fontWeight: 'bold' }}>156</p>
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #334155'
          }}>
            <h3 style={{ color: '#a855f7', marginBottom: '16px', fontSize: '20px' }}>AI Recommendations</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Strong Buy</span>
                <span style={{ color: '#10b981', fontWeight: 'bold' }}>23 pairs</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Buy</span>
                <span style={{ color: '#22c55e', fontWeight: 'bold' }}>89 pairs</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Hold</span>
                <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>412 pairs</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Sell</span>
                <span style={{ color: '#ef4444', fontWeight: 'bold' }}>151 pairs</span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Charts and Data Tables */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155',
          marginBottom: '30px'
        }}>
          <h3 style={{ color: 'white', marginBottom: '20px', fontSize: '24px' }}>
            {timeframe} Price Action
          </h3>
          <div style={{
            background: '#0f172a',
            borderRadius: '12px',
            padding: '20px',
            height: '400px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid #1e293b'
          }}>
            <p style={{ color: '#64748b', fontSize: '18px' }}>
              Advanced charting component will be integrated here
            </p>
          </div>
        </div>

        {/* Top Performers Table */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155'
        }}>
          <h3 style={{ color: 'white', marginBottom: '20px', fontSize: '24px' }}>
            Top Performers
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #334155' }}>
                  <th style={{ color: '#94a3b8', padding: '12px', textAlign: 'left' }}>Symbol</th>
                  <th style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>Price</th>
                  <th style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>Change %</th>
                  <th style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>Volume</th>
                  <th style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>RSI</th>
                  <th style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>MACD</th>
                  <th style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>ADX</th>
                  <th style={{ color: '#94a3b8', padding: '12px', textAlign: 'center' }}>Signal</th>
                </tr>
              </thead>
              <tbody>
                {data.slice(0, 20).map((item, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ color: 'white', padding: '12px', fontWeight: 'bold' }}>{item.symbol}</td>
                    <td style={{ color: 'white', padding: '12px', textAlign: 'right' }}>${item.price.toLocaleString()}</td>
                    <td style={{
                      color: item.change >= 0 ? '#10b981' : '#ef4444',
                      padding: '12px',
                      textAlign: 'right',
                      fontWeight: 'bold'
                    }}>
                      {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}%
                    </td>
                    <td style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>${item.volume}M</td>
                    <td style={{
                      color: item.rsi < 30 ? '#10b981' : item.rsi > 70 ? '#ef4444' : '#f59e0b',
                      padding: '12px',
                      textAlign: 'right'
                    }}>
                      {item.rsi.toFixed(1)}
                    </td>
                    <td style={{
                      color: item.macd >= 0 ? '#10b981' : '#ef4444',
                      padding: '12px',
                      textAlign: 'right'
                    }}>
                      {item.macd >= 0 ? '+' : ''}{item.macd.toFixed(2)}
                    </td>
                    <td style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>{item.adx.toFixed(1)}</td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{
                        background: item.signal === 'BUY' ? '#10b981' : item.signal === 'SELL' ? '#ef4444' : '#64748b',
                        color: 'white',
                        padding: '4px 12px',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {item.signal}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to generate mock data
const generateMockData = (timeframe) => {
  const symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'AVAX/USD', 'MATIC/USD', 'DOT/USD', 'ADA/USD', 'XRP/USD', 'BNB/USD', 'LINK/USD'];
  return symbols.map((symbol, idx) => ({
    symbol,
    price: (Math.random() * 10000) + 100,
    change: (Math.random() - 0.5) * 10,
    volume: (Math.random() * 1000).toFixed(1),
    rsi: Math.random() * 100,
    macd: (Math.random() - 0.5) * 50,
    adx: Math.random() * 50,
    signal: idx % 3 === 0 ? 'BUY' : idx % 3 === 1 ? 'SELL' : 'HOLD'
  }));
};

export default function AIAlgoTradeHits() {
  const [activeTab, setActiveTab] = useState('crypto');
  const [autoTrading, setAutoTrading] = useState(false);
  const [expandedView, setExpandedView] = useState(null);

  // Mock data for crypto
  const cryptoData = [
    { symbol: 'BTC', name: 'Bitcoin', price: 43250.50, daily: 2.34, hourly: 0.45, monthly: 15.2, trades: 1234, buy: 678, sell: 556, traders: 3421, atLowest: false, sentiment: 73 },
    { symbol: 'ETH', name: 'Ethereum', price: 2280.75, daily: 1.89, hourly: 0.32, monthly: 12.8, trades: 2341, buy: 1203, sell: 1138, traders: 2890, atLowest: true, sentiment: 68 },
    { symbol: 'BNB', name: 'Binance', price: 312.40, daily: 0.92, hourly: -0.15, monthly: 8.5, trades: 876, buy: 445, sell: 431, traders: 1567, atLowest: false, sentiment: 65 },
    { symbol: 'SOL', name: 'Gainer #1', price: 98.35, daily: 8.45, hourly: 2.34, monthly: 45.2, trades: 1567, buy: 989, sell: 578, traders: 2134, atLowest: true, sentiment: 85 },
    { symbol: 'AVAX', name: 'Gainer #2', price: 36.78, daily: 6.23, hourly: 1.87, monthly: 32.1, trades: 892, buy: 567, sell: 325, traders: 1456, atLowest: false, sentiment: 78 },
    { symbol: 'MATIC', name: 'Gainer #3', price: 0.89, daily: 5.67, hourly: 1.23, monthly: 28.4, trades: 1234, buy: 756, sell: 478, traders: 1789, atLowest: true, sentiment: 72 },
    { symbol: 'DOT', name: 'Gainer #4', price: 7.23, daily: 4.91, hourly: 0.98, monthly: 22.6, trades: 678, buy: 401, sell: 277, traders: 987, atLowest: false, sentiment: 70 },
    { symbol: 'ADA', name: 'Loser #1', price: 0.52, daily: -3.21, hourly: -0.87, monthly: -12.3, trades: 1567, buy: 623, sell: 944, traders: 1345, atLowest: false, sentiment: 35 },
    { symbol: 'XRP', name: 'Loser #2', price: 0.61, daily: -2.87, hourly: -0.65, monthly: -8.9, trades: 2345, buy: 891, sell: 1454, traders: 1892, atLowest: false, sentiment: 42 },
    { symbol: 'DOGE', name: 'Loser #3', price: 0.08, daily: -2.34, hourly: -0.43, monthly: -15.6, trades: 3456, buy: 1234, sell: 2222, traders: 2567, atLowest: false, sentiment: 38 },
  ];

  // Mock data for stocks
  const stockData = [
    { symbol: 'SPY', name: 'S&P 500 ETF', price: 445.23, daily: 0.87, hourly: 0.23, monthly: 5.2, trades: 5234, buy: 2878, sell: 2356, traders: 8421, atLowest: false, sentiment: 65 },
    { symbol: 'QQQ', name: 'Nasdaq ETF', price: 378.45, daily: 1.23, hourly: 0.45, monthly: 8.7, trades: 4567, buy: 2534, sell: 2033, traders: 6890, atLowest: false, sentiment: 72 },
    { symbol: 'DIA', name: 'Dow ETF', price: 356.78, daily: 0.56, hourly: 0.12, monthly: 3.4, trades: 2341, buy: 1203, sell: 1138, traders: 4230, atLowest: false, sentiment: 58 },
    { symbol: 'NVDA', name: 'Gainer #1', price: 485.67, daily: 5.34, hourly: 1.87, monthly: 22.3, trades: 6789, buy: 4234, sell: 2555, traders: 9876, atLowest: true, sentiment: 88 },
    { symbol: 'TSLA', name: 'Gainer #2', price: 245.89, daily: 4.23, hourly: 1.34, monthly: 18.9, trades: 8901, buy: 5234, sell: 3667, traders: 12345, atLowest: false, sentiment: 82 },
    { symbol: 'AMD', name: 'Gainer #3', price: 167.34, daily: 3.67, hourly: 1.12, monthly: 15.4, trades: 3456, buy: 2134, sell: 1322, traders: 6543, atLowest: true, sentiment: 76 },
    { symbol: 'AAPL', name: 'Gainer #4', price: 178.23, daily: 2.89, hourly: 0.87, monthly: 12.6, trades: 5678, buy: 3234, sell: 2444, traders: 8765, atLowest: false, sentiment: 74 },
    { symbol: 'META', name: 'Loser #1', price: 387.45, daily: -2.34, hourly: -0.76, monthly: -8.3, trades: 4321, buy: 1876, sell: 2445, traders: 7654, atLowest: false, sentiment: 42 },
    { symbol: 'NFLX', name: 'Loser #2', price: 456.12, daily: -1.87, hourly: -0.54, monthly: -6.7, trades: 2345, buy: 987, sell: 1358, traders: 4567, atLowest: false, sentiment: 38 },
    { symbol: 'DIS', name: 'Loser #3', price: 98.76, daily: -1.45, hourly: -0.43, monthly: -5.2, trades: 3210, buy: 1234, sell: 1976, traders: 5432, atLowest: false, sentiment: 35 },
  ];

  const currentData = activeTab === 'crypto' ? cryptoData : stockData;

  if (expandedView) {
    return <AnalyticsWindow timeframe={expandedView} onClose={() => setExpandedView(null)} />;
  }

  return (
    <div className="trading-app">
      {/* New Simplified Header */}
      <header className="header" style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        borderBottom: '2px solid #10b981',
        padding: '20px 40px'
      }}>
        <div style={{
          maxWidth: '1800px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
              borderRadius: '12px',
              padding: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <TrendingUp size={32} color="white" strokeWidth={3} />
            </div>
            <div>
              <h1 style={{
                fontSize: '28px',
                fontWeight: 'bold',
                background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                margin: 0
              }}>
                AIAlgoTradeHits.com
              </h1>
              <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>
                AI-Powered Trading Intelligence
              </p>
            </div>
          </div>

          {/* Stats */}
          <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
            <div>
              <p style={{ color: '#94a3b8', fontSize: '12px', margin: 0 }}>Portfolio</p>
              <p style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold', margin: 0 }}>$25,687</p>
            </div>
            <div>
              <p style={{ color: '#94a3b8', fontSize: '12px', margin: 0 }}>Today P&L</p>
              <p style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold', margin: 0 }}>+$567</p>
            </div>
            <div>
              <p style={{ color: '#94a3b8', fontSize: '12px', margin: 0 }}>AI Confidence</p>
              <p style={{ color: '#f59e0b', fontSize: '24px', fontWeight: 'bold', margin: 0 }}>87%</p>
            </div>
          </div>
        </div>
      </header>

      <div className="main-layout">
        {/* Main Content */}
        <main className="main-content" style={{ padding: '40px', maxWidth: '1800px', margin: '0 auto' }}>
          {/* Tab Selector */}
          <div className="tab-selector" style={{ marginBottom: '30px' }}>
            <div className="tabs">
              <button
                onClick={() => setActiveTab('crypto')}
                className={`tab-btn ${activeTab === 'crypto' ? 'tab-btn-active tab-btn-crypto' : ''}`}
              >
                <span className="tab-content">
                  <Activity className="tab-icon" />
                  CRYPTOCURRENCY
                </span>
              </button>
              <button
                onClick={() => setActiveTab('stock')}
                className={`tab-btn ${activeTab === 'stock' ? 'tab-btn-active tab-btn-stock' : ''}`}
              >
                <span className="tab-content">
                  <TrendingUp className="tab-icon" />
                  STOCKS
                </span>
              </button>
            </div>
          </div>

          {/* Multi-Timeframe Charts with Expand Buttons */}
          <div className="charts-grid" style={{ marginBottom: '40px' }}>
            {['Daily', 'Hourly', '5-Minute'].map((timeframe, idx) => (
              <div key={timeframe} className={`chart-card ${idx === 2 ? 'chart-active' : ''}`}>
                <div className="chart-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 className="chart-title">{timeframe} Chart</h3>
                  <button
                    onClick={() => setExpandedView(timeframe)}
                    style={{
                      background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '8px 16px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      transition: 'all 0.3s'
                    }}
                    onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                  >
                    <Maximize2 size={16} />
                    Expand
                  </button>
                </div>
                <div className="chart-area">
                  <div className="chart-bars">
                    {[...Array(idx === 2 ? 20 : idx === 1 ? 16 : 12)].map((_, i) => {
                      const height = 40 + Math.random() * 60;
                      const isLowest = idx === 2 && (i === 14 || i === 8);
                      return (
                        <div key={i} className="chart-bar-wrapper" style={{width: `${100/(idx === 2 ? 20 : idx === 1 ? 16 : 12)}%`}}>
                          <div
                            className={`chart-bar ${i % 3 === 0 ? 'bar-green' : 'bar-red'} ${isLowest ? 'bar-lowest' : ''}`}
                            style={{height: `${height}%`}}
                          ></div>
                          {isLowest && (
                            <div className="buy-indicator">BUY</div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
                <div className="chart-stats">
                  <div className="chart-stat-item"><p className="chart-stat-label">Vol</p><p className="chart-stat-value">$2.1B</p></div>
                  <div className="chart-stat-item"><p className="chart-stat-label">Buy</p><p className="chart-stat-value stat-green">1.2K</p></div>
                  <div className="chart-stat-item"><p className="chart-stat-label">Sell</p><p className="chart-stat-value stat-red">987</p></div>
                  <div className="chart-stat-item"><p className="chart-stat-label">Traders</p><p className="chart-stat-value">3.4K</p></div>
                </div>
              </div>
            ))}
          </div>

          {/* Asset Performance Grid */}
          <div className="assets-section">
            <h2 className="assets-title">
              <Target className="icon-medium" />
              {activeTab === 'crypto' ? 'Cryptocurrency' : 'Stock'} Performance Dashboard
            </h2>
            <div className="assets-grid">
              {currentData.map((asset, index) => (
                <div
                  key={asset.symbol}
                  className={`asset-card ${asset.atLowest ? 'asset-lowest' : asset.daily >= 0 ? '' : 'asset-negative'}`}
                >
                  <div className="asset-header">
                    <div className="asset-info">
                      <div className={`asset-icon ${asset.atLowest ? 'asset-icon-lowest' : asset.daily >= 0 ? 'asset-icon-green' : 'asset-icon-red'}`}>
                        {asset.symbol.substring(0, 2)}
                      </div>
                      <div className="asset-names">
                        <p className="asset-symbol">{asset.symbol}</p>
                        <p className="asset-name">{asset.name}</p>
                      </div>
                    </div>
                    {asset.atLowest && (
                      <div className="asset-low-badge">
                        <TrendingUp className="icon-bounce" />
                        <span className="low-text">LOW</span>
                      </div>
                    )}
                  </div>

                  {/* Mini Chart */}
                  <div className="mini-chart">
                    {[...Array(10)].map((_, i) => (
                      <div
                        key={i}
                        className={`mini-bar ${asset.daily >= 0 ? 'mini-bar-green' : 'mini-bar-red'}`}
                        style={{height: `${40 + Math.random() * 60}%`}}
                      ></div>
                    ))}
                  </div>

                  <p className="asset-price">${asset.price.toLocaleString()}</p>
                  <p className={`asset-change ${asset.daily >= 0 ? 'stat-green' : 'stat-red'}`}>
                    {asset.daily >= 0 ? '+' : ''}{asset.daily}% (24h)
                  </p>

                  {/* Sentiment Bar */}
                  <div className="asset-sentiment">
                    <div className="sentiment-bar-header">
                      <span className="sentiment-bar-label">Sentiment</span>
                      <span className={`sentiment-bar-value ${asset.sentiment > 60 ? 'stat-green' : asset.sentiment > 40 ? 'stat-yellow' : 'stat-red'}`}>
                        {asset.sentiment}%
                      </span>
                    </div>
                    <div className="progress-bar progress-bar-small">
                      <div
                        className={`progress-fill ${asset.sentiment > 60 ? 'progress-green' : asset.sentiment > 40 ? 'progress-yellow' : 'progress-red'}`}
                        style={{width: `${asset.sentiment}%`}}
                      ></div>
                    </div>
                  </div>

                  <div className="asset-timeframes">
                    <div className="timeframe-item">
                      <p className="timeframe-label">Day</p>
                      <p className={`timeframe-value ${asset.daily >= 0 ? 'stat-green' : 'stat-red'}`}>
                        {asset.daily >= 0 ? '+' : ''}{asset.daily}%
                      </p>
                    </div>
                    <div className="timeframe-item">
                      <p className="timeframe-label">Hour</p>
                      <p className={`timeframe-value ${asset.hourly >= 0 ? 'stat-green' : 'stat-red'}`}>
                        {asset.hourly >= 0 ? '+' : ''}{asset.hourly}%
                      </p>
                    </div>
                    <div className="timeframe-item">
                      <p className="timeframe-label">Month</p>
                      <p className={`timeframe-value ${asset.monthly >= 0 ? 'stat-green' : 'stat-red'}`}>
                        {asset.monthly >= 0 ? '+' : ''}{asset.monthly}%
                      </p>
                    </div>
                  </div>

                  <div className="asset-trades">
                    <div className="trade-stat"><p className="trade-label">Trades</p><p className="trade-value">{asset.trades}</p></div>
                    <div className="trade-stat"><p className="trade-label">Traders</p><p className="trade-value">{asset.traders}</p></div>
                    <div className="trade-stat"><p className="trade-label">Buy</p><p className="trade-value stat-green">{asset.buy}</p></div>
                    <div className="trade-stat"><p className="trade-label">Sell</p><p className="trade-value stat-red">{asset.sell}</p></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
