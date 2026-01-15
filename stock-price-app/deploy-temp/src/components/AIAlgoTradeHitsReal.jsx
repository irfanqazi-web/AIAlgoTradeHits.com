import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, Settings, Maximize2, X, Shield } from 'lucide-react';
import apiService from '../services/api';
import AdminPanel from './AdminPanel';

// Analytics Window with Real Data
const AnalyticsWindow = ({ timeframe, marketType, onClose }) => {
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [timeframe, marketType]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Fetch data based on market type and timeframe
      let result;
      if (marketType === 'crypto') {
        result = await apiService.getCryptoData(timeframe, 50);
      } else {
        result = await apiService.getStockData(50);
      }

      // Fetch summary
      const summaryResult = await apiService.getMarketSummary(marketType);

      if (result.success) {
        setData(result.data);
      }

      if (summaryResult.success) {
        setSummary(summaryResult.summary);
      }
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

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
      <div style={{ maxWidth: '1800px', margin: '0 auto' }}>
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
            {timeframe} {marketType.toUpperCase()} Analytics
          </h1>
          <button onClick={onClose} style={{
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <X size={20} />
            Close
          </button>
        </div>

        {loading ? (
          <div style={{ color: 'white', textAlign: 'center', padding: '40px', fontSize: '18px' }}>
            Loading real-time data from BigQuery...
          </div>
        ) : (
          <>
            {/* Market Summary */}
            {summary && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '20px',
                marginBottom: '30px'
              }}>
                <div style={{
                  background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid #334155'
                }}>
                  <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>Total {marketType === 'crypto' ? 'Pairs' : 'Symbols'}</p>
                  <p style={{ color: 'white', fontSize: '32px', fontWeight: 'bold' }}>{summary.total_pairs}</p>
                </div>
                <div style={{
                  background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid #334155'
                }}>
                  <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>Oversold (RSI &lt; 30)</p>
                  <p style={{ color: '#10b981', fontSize: '32px', fontWeight: 'bold' }}>{summary.oversold_count}</p>
                </div>
                <div style={{
                  background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid #334155'
                }}>
                  <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>Overbought (RSI &gt; 70)</p>
                  <p style={{ color: '#ef4444', fontSize: '32px', fontWeight: 'bold' }}>{summary.overbought_count}</p>
                </div>
                <div style={{
                  background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid #334155'
                }}>
                  <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>Bullish MACD</p>
                  <p style={{ color: '#10b981', fontSize: '32px', fontWeight: 'bold' }}>{summary.bullish_macd}</p>
                </div>
              </div>
            )}

            {/* Data Table */}
            <div style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              borderRadius: '16px',
              padding: '24px',
              border: '1px solid #334155'
            }}>
              <h3 style={{ color: 'white', marginBottom: '20px', fontSize: '24px' }}>
                Recent Data ({data.length} records)
              </h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', color: 'white' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #334155' }}>
                      <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>
                        {marketType === 'crypto' ? 'Pair' : 'Symbol'}
                      </th>
                      <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>Close</th>
                      <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>RSI</th>
                      <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>MACD</th>
                      <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>ADX</th>
                      <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.slice(0, 20).map((row, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #334155' }}>
                        <td style={{ padding: '12px', fontWeight: 'bold' }}>
                          {marketType === 'crypto' ? row.pair : row.symbol}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'right' }}>
                          ${row.close ? row.close.toFixed(2) : 'N/A'}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          color: row.rsi < 30 ? '#10b981' : row.rsi > 70 ? '#ef4444' : 'white'
                        }}>
                          {row.rsi ? row.rsi.toFixed(1) : 'N/A'}
                        </td>
                        <td style={{
                          padding: '12px',
                          textAlign: 'right',
                          color: row.macd > 0 ? '#10b981' : '#ef4444'
                        }}>
                          {row.macd ? row.macd.toFixed(4) : 'N/A'}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'right' }}>
                          {row.adx ? row.adx.toFixed(1) : 'N/A'}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'right', fontSize: '12px' }}>
                          {row.volume ? row.volume.toLocaleString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// Main Component
export default function AIAlgoTradeHits() {
  const [marketType, setMarketType] = useState('crypto');
  const [expandedView, setExpandedView] = useState(null);
  const [showAdmin, setShowAdmin] = useState(false);
  const [cryptoData, setCryptoData] = useState([]);
  const [stockData, setStockData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [marketType]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      if (marketType === 'crypto') {
        // Load crypto data for all three timeframes
        const daily = await apiService.getCryptoData('daily', 10);
        if (daily.success) {
          setCryptoData(daily.data);
        }
      } else {
        // Load stock data
        const stocks = await apiService.getStockData(10);
        if (stocks.success) {
          setStockData(stocks.data);
        }
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (showAdmin) {
    return <AdminPanel onClose={() => setShowAdmin(false)} />;
  }

  if (expandedView) {
    return (
      <AnalyticsWindow
        timeframe={expandedView}
        marketType={marketType}
        onClose={() => setExpandedView(null)}
      />
    );
  }

  const currentData = marketType === 'crypto' ? cryptoData : stockData;

  return (
    <div className="trading-app" style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{
        maxWidth: '1800px',
        margin: '0 auto',
        marginBottom: '30px',
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{
            fontSize: '36px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: 0,
            marginBottom: '8px'
          }}>
            AIAlgoTradeHits.com
          </h1>
          <p style={{ color: '#94a3b8', margin: 0 }}>
            Real-time Trading Analytics powered by BigQuery
          </p>
        </div>
        <button
          onClick={() => setShowAdmin(true)}
          style={{
            background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontWeight: 'bold'
          }}
        >
          <Shield size={20} />
          Admin Panel
        </button>
      </div>

      <div style={{ maxWidth: '1800px', margin: '0 auto' }}>
        {/* Market Type Tabs */}
        <div style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '24px'
        }}>
          <button
            onClick={() => setMarketType('crypto')}
            style={{
              background: marketType === 'crypto'
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              color: 'white',
              border: marketType === 'crypto' ? '2px solid #10b981' : '2px solid #334155',
              borderRadius: '12px',
              padding: '12px 32px',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
          >
            Crypto Markets
          </button>
          <button
            onClick={() => setMarketType('stock')}
            style={{
              background: marketType === 'stock'
                ? 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
                : 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              color: 'white',
              border: marketType === 'stock' ? '2px solid #3b82f6' : '2px solid #334155',
              borderRadius: '12px',
              padding: '12px 32px',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
          >
            Stock Markets
          </button>
        </div>

        {/* Timeframe Cards */}
        {marketType === 'crypto' && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
            gap: '20px',
            marginBottom: '30px'
          }}>
            {['Daily', 'Hourly', '5-Minute'].map((timeframe) => (
              <div key={timeframe} style={{
                background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                borderRadius: '16px',
                padding: '24px',
                border: '1px solid #334155'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '20px'
                }}>
                  <h3 style={{ color: '#10b981', margin: 0, fontSize: '20px' }}>
                    {timeframe} View
                  </h3>
                  <button
                    onClick={() => setExpandedView(timeframe.toLowerCase())}
                    style={{
                      background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '8px 16px',
                      fontSize: '14px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <Maximize2 size={16} />
                    Expand
                  </button>
                </div>
                <p style={{ color: '#94a3b8', fontSize: '14px' }}>
                  Click Expand for detailed {timeframe.toLowerCase()} analytics with real-time BigQuery data
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Quick Stats */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155',
          marginBottom: '30px'
        }}>
          <h3 style={{ color: 'white', marginBottom: '20px', fontSize: '24px' }}>
            Latest {marketType === 'crypto' ? 'Crypto' : 'Stock'} Data
          </h3>

          {loading ? (
            <div style={{ color: '#94a3b8', textAlign: 'center', padding: '20px' }}>
              Loading data from BigQuery...
            </div>
          ) : currentData.length === 0 ? (
            <div style={{ color: '#94a3b8', textAlign: 'center', padding: '20px' }}>
              No data available. Click "Expand" above to view detailed analytics.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', color: 'white' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #334155' }}>
                    <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>
                      {marketType === 'crypto' ? 'Pair' : 'Symbol'}
                    </th>
                    {marketType === 'stock' && (
                      <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Company</th>
                    )}
                    <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>Price</th>
                    <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>RSI</th>
                    <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>MACD</th>
                    <th style={{ padding: '12px', textAlign: 'right', color: '#94a3b8' }}>Signal</th>
                  </tr>
                </thead>
                <tbody>
                  {currentData.slice(0, 10).map((row, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #334155' }}>
                      <td style={{ padding: '12px', fontWeight: 'bold' }}>
                        {marketType === 'crypto' ? row.pair : row.symbol}
                      </td>
                      {marketType === 'stock' && (
                        <td style={{ padding: '12px', color: '#94a3b8', fontSize: '14px' }}>
                          {row.company_name || 'N/A'}
                        </td>
                      )}
                      <td style={{ padding: '12px', textAlign: 'right', fontSize: '16px' }}>
                        ${row.close ? row.close.toFixed(2) : 'N/A'}
                      </td>
                      <td style={{
                        padding: '12px',
                        textAlign: 'right',
                        color: row.rsi < 30 ? '#10b981' : row.rsi > 70 ? '#ef4444' : 'white',
                        fontWeight: 'bold'
                      }}>
                        {row.rsi ? row.rsi.toFixed(1) : 'N/A'}
                      </td>
                      <td style={{
                        padding: '12px',
                        textAlign: 'right',
                        color: row.macd > 0 ? '#10b981' : '#ef4444'
                      }}>
                        {row.macd ? row.macd.toFixed(4) : 'N/A'}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        {row.rsi < 30 ? (
                          <span style={{
                            background: '#10b981',
                            color: 'white',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            BUY
                          </span>
                        ) : row.rsi > 70 ? (
                          <span style={{
                            background: '#ef4444',
                            color: 'white',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            SELL
                          </span>
                        ) : (
                          <span style={{
                            background: '#64748b',
                            color: 'white',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            HOLD
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '20px',
          border: '1px solid #334155',
          textAlign: 'center'
        }}>
          <p style={{ color: '#94a3b8', margin: 0 }}>
            Data powered by BigQuery | Real-time technical analysis | 67 indicators per asset
          </p>
        </div>
      </div>
    </div>
  );
}
