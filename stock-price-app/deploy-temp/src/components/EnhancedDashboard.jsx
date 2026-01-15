import React, { useState, useEffect } from 'react';
import {
  TrendingUp, TrendingDown, Star, Bell, Activity, BarChart3,
  Clock, DollarSign, Zap, AlertCircle, Eye, Plus, Search,
  RefreshCw, Maximize2, ChevronUp, ChevronDown, Brain
} from 'lucide-react';
import apiService from '../services/api';

const EnhancedDashboard = () => {
  const [marketType, setMarketType] = useState('crypto');
  const [cryptoData, setCryptoData] = useState([]);
  const [stockData, setStockData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [watchlist, setWatchlist] = useState(['BTCUSD', 'ETHUSD', 'SOLUSD', 'AAPL', 'MSFT']);
  const [marketSummary, setMarketSummary] = useState(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      loadData();
      setLastUpdate(new Date());
    }, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [marketType]);

  const loadData = async () => {
    try {
      setLoading(true);
      if (marketType === 'crypto') {
        const [daily, summary] = await Promise.all([
          apiService.getCryptoData('daily', 20),
          apiService.getMarketSummary('crypto')
        ]);
        if (daily.success) setCryptoData(daily.data);
        if (summary.success) setMarketSummary(summary.summary);
      } else {
        const [stocks, summary] = await Promise.all([
          apiService.getStockData(20),
          apiService.getMarketSummary('stock')
        ]);
        if (stocks.success) setStockData(stocks.data);
        if (summary.success) setMarketSummary(summary.summary);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentData = marketType === 'crypto' ? cryptoData : stockData;
  const watchlistData = currentData.filter(item =>
    watchlist.includes(marketType === 'crypto' ? item.pair : item.symbol)
  );

  return (
    <div style={{
      display: 'flex',
      height: 'calc(100vh - 64px)',
      background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
      overflow: 'hidden'
    }}>
      {/* LEFT PANEL - Watchlist & Quick Stats */}
      <div style={{
        width: '300px',
        background: 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)',
        borderRight: '1px solid #334155',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Watchlist Header */}
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #334155'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px'
          }}>
            <h3 style={{
              margin: 0,
              color: 'white',
              fontSize: '18px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Star size={20} color="#10b981" />
              Watchlist
            </h3>
            <button style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center'
            }}>
              <Plus size={16} />
            </button>
          </div>
          <div style={{
            position: 'relative'
          }}>
            <Search size={16} style={{
              position: 'absolute',
              left: '10px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#94a3b8'
            }} />
            <input
              type="text"
              placeholder="Search assets..."
              style={{
                width: '100%',
                padding: '8px 8px 8px 36px',
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '6px',
                color: 'white',
                fontSize: '14px',
                outline: 'none'
              }}
            />
          </div>
        </div>

        {/* Watchlist Items */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '10px'
        }}>
          {watchlistData.map((item, index) => {
            const symbol = marketType === 'crypto' ? item.pair : item.symbol;
            const price = item.close;
            const change = item.rsi > 50 ? 2.5 : -1.8; // Simulated change
            const isPositive = change >= 0;

            return (
              <div key={index} style={{
                background: '#1e293b',
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '8px',
                cursor: 'pointer',
                border: '1px solid transparent',
                transition: 'all 0.2s'
              }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = '#3b82f6'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = 'transparent'}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '8px'
                }}>
                  <div>
                    <div style={{
                      fontWeight: 'bold',
                      color: 'white',
                      fontSize: '14px'
                    }}>
                      {symbol}
                    </div>
                    {marketType === 'stock' && (
                      <div style={{
                        fontSize: '11px',
                        color: '#94a3b8'
                      }}>
                        {item.company_name?.substring(0, 20)}
                      </div>
                    )}
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    color: isPositive ? '#10b981' : '#ef4444'
                  }}>
                    {isPositive ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    {Math.abs(change).toFixed(2)}%
                  </div>
                </div>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div style={{
                    fontSize: '16px',
                    fontWeight: 'bold',
                    color: 'white'
                  }}>
                    ${price?.toFixed(2)}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: '#94a3b8'
                  }}>
                    RSI: {item.rsi?.toFixed(0)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div style={{
          padding: '15px',
          borderTop: '1px solid #334155',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '8px'
        }}>
          <button style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            padding: '10px',
            fontSize: '13px',
            fontWeight: 'bold',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px'
          }}>
            <Bell size={14} />
            Alerts
          </button>
          <button style={{
            background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            padding: '10px',
            fontSize: '13px',
            fontWeight: 'bold',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px'
          }}>
            <Activity size={14} />
            Portfolio
          </button>
        </div>
      </div>

      {/* CENTER PANEL - Main Content */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Market Header */}
        <div style={{
          padding: '20px',
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderBottom: '1px solid #334155'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '15px'
          }}>
            <div style={{
              display: 'flex',
              gap: '12px'
            }}>
              <button
                onClick={() => setMarketType('crypto')}
                style={{
                  background: marketType === 'crypto'
                    ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                    : '#1e293b',
                  color: 'white',
                  border: marketType === 'crypto' ? '2px solid #10b981' : '2px solid #334155',
                  borderRadius: '8px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'all 0.3s'
                }}
              >
                Cryptocurrency
              </button>
              <button
                onClick={() => setMarketType('stock')}
                style={{
                  background: marketType === 'stock'
                    ? 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
                    : '#1e293b',
                  color: 'white',
                  border: marketType === 'stock' ? '2px solid #3b82f6' : '2px solid #334155',
                  borderRadius: '8px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  transition: 'all 0.3s'
                }}
              >
                Stock Market
              </button>
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: '#94a3b8',
                fontSize: '13px'
              }}>
                <Clock size={14} />
                {lastUpdate.toLocaleTimeString()}
              </div>
              <button
                onClick={loadData}
                style={{
                  background: '#334155',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '13px'
                }}
              >
                <RefreshCw size={14} />
                Refresh
              </button>
            </div>
          </div>

          {/* Market Stats */}
          {marketSummary && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '12px'
            }}>
              <div style={{
                background: '#0f172a',
                borderRadius: '8px',
                padding: '12px',
                border: '1px solid #334155'
              }}>
                <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '4px' }}>
                  Total {marketType === 'crypto' ? 'Pairs' : 'Symbols'}
                </div>
                <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
                  {marketSummary.total_pairs || 0}
                </div>
              </div>
              <div style={{
                background: '#0f172a',
                borderRadius: '8px',
                padding: '12px',
                border: '1px solid #334155'
              }}>
                <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '4px' }}>
                  Oversold (RSI &lt; 30)
                </div>
                <div style={{ color: '#10b981', fontSize: '20px', fontWeight: 'bold' }}>
                  {marketSummary.oversold_count || 0}
                </div>
              </div>
              <div style={{
                background: '#0f172a',
                borderRadius: '8px',
                padding: '12px',
                border: '1px solid #334155'
              }}>
                <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '4px' }}>
                  Overbought (RSI &gt; 70)
                </div>
                <div style={{ color: '#ef4444', fontSize: '20px', fontWeight: 'bold' }}>
                  {marketSummary.overbought_count || 0}
                </div>
              </div>
              <div style={{
                background: '#0f172a',
                borderRadius: '8px',
                padding: '12px',
                border: '1px solid #334155'
              }}>
                <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '4px' }}>
                  Bullish MACD
                </div>
                <div style={{ color: '#10b981', fontSize: '20px', fontWeight: 'bold' }}>
                  {marketSummary.bullish_macd || 0}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Data Table */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px'
        }}>
          {loading ? (
            <div style={{
              textAlign: 'center',
              padding: '60px',
              color: '#94a3b8'
            }}>
              <RefreshCw size={40} style={{ animation: 'spin 1s linear infinite' }} />
              <div style={{ marginTop: '20px', fontSize: '16px' }}>
                Loading {marketType} data from BigQuery...
              </div>
            </div>
          ) : (
            <div style={{
              background: '#1e293b',
              borderRadius: '12px',
              overflow: 'hidden',
              border: '1px solid #334155'
            }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse'
              }}>
                <thead>
                  <tr style={{
                    background: '#0f172a',
                    borderBottom: '2px solid #334155'
                  }}>
                    <th style={{ padding: '16px', textAlign: 'left', color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
                      {marketType === 'crypto' ? 'PAIR' : 'SYMBOL'}
                    </th>
                    {marketType === 'stock' && (
                      <th style={{ padding: '16px', textAlign: 'left', color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
                        COMPANY
                      </th>
                    )}
                    <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
                      PRICE
                    </th>
                    <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
                      RSI
                    </th>
                    <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
                      MACD
                    </th>
                    <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
                      ADX
                    </th>
                    <th style={{ padding: '16px', textAlign: 'center', color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
                      SIGNAL
                    </th>
                    <th style={{ padding: '16px', textAlign: 'center', color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
                      ACTION
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {currentData.slice(0, 15).map((row, index) => {
                    const symbol = marketType === 'crypto' ? row.pair : row.symbol;
                    const rsiColor = row.rsi < 30 ? '#10b981' : row.rsi > 70 ? '#ef4444' : 'white';
                    const macdColor = row.macd > 0 ? '#10b981' : '#ef4444';
                    const signal = row.rsi < 30 ? 'BUY' : row.rsi > 70 ? 'SELL' : 'HOLD';
                    const signalColor = signal === 'BUY' ? '#10b981' : signal === 'SELL' ? '#ef4444' : '#64748b';

                    return (
                      <tr key={index} style={{
                        borderBottom: '1px solid #334155',
                        transition: 'background 0.2s'
                      }}
                        onMouseEnter={(e) => e.currentTarget.style.background = '#0f172a'}
                        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                      >
                        <td style={{ padding: '16px', color: 'white', fontWeight: 'bold', fontSize: '14px' }}>
                          {symbol}
                        </td>
                        {marketType === 'stock' && (
                          <td style={{ padding: '16px', color: '#94a3b8', fontSize: '13px' }}>
                            {row.company_name?.substring(0, 25)}
                          </td>
                        )}
                        <td style={{ padding: '16px', textAlign: 'right', color: 'white', fontWeight: 'bold', fontSize: '15px' }}>
                          ${row.close?.toFixed(2)}
                        </td>
                        <td style={{ padding: '16px', textAlign: 'right', color: rsiColor, fontWeight: 'bold', fontSize: '14px' }}>
                          {row.rsi?.toFixed(1)}
                        </td>
                        <td style={{ padding: '16px', textAlign: 'right', color: macdColor, fontSize: '13px' }}>
                          {row.macd?.toFixed(4)}
                        </td>
                        <td style={{ padding: '16px', textAlign: 'right', color: 'white', fontSize: '13px' }}>
                          {row.adx?.toFixed(1)}
                        </td>
                        <td style={{ padding: '16px', textAlign: 'center' }}>
                          <span style={{
                            background: signalColor,
                            color: 'white',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '11px',
                            fontWeight: 'bold'
                          }}>
                            {signal}
                          </span>
                        </td>
                        <td style={{ padding: '16px', textAlign: 'center' }}>
                          <button style={{
                            background: 'none',
                            border: '1px solid #334155',
                            color: '#94a3b8',
                            borderRadius: '6px',
                            padding: '6px 12px',
                            cursor: 'pointer',
                            fontSize: '12px',
                            transition: 'all 0.2s'
                          }}
                            onMouseEnter={(e) => {
                              e.target.style.borderColor = '#3b82f6';
                              e.target.style.color = '#3b82f6';
                            }}
                            onMouseLeave={(e) => {
                              e.target.style.borderColor = '#334155';
                              e.target.style.color = '#94a3b8';
                            }}
                          >
                            <Eye size={14} style={{ display: 'inline' }} /> View
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* RIGHT PANEL - Market Insights */}
      <div style={{
        width: '320px',
        background: 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)',
        borderLeft: '1px solid #334155',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* AI Insights Header */}
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #334155'
        }}>
          <h3 style={{
            margin: 0,
            color: 'white',
            fontSize: '18px',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Brain size={20} color="#3b82f6" />
            AI Insights
          </h3>
        </div>

        {/* Insights Content */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '15px'
        }}>
          {/* Top Movers */}
          <div style={{
            background: '#1e293b',
            borderRadius: '8px',
            padding: '15px',
            marginBottom: '15px',
            border: '1px solid #334155'
          }}>
            <h4 style={{
              margin: '0 0 12px 0',
              color: '#10b981',
              fontSize: '14px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <TrendingUp size={16} />
              Top Gainers (24h)
            </h4>
            {currentData.slice(0, 3).map((item, index) => (
              <div key={index} style={{
                padding: '8px 0',
                borderBottom: index < 2 ? '1px solid #334155' : 'none'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{ color: 'white', fontSize: '13px', fontWeight: 'bold' }}>
                    {marketType === 'crypto' ? item.pair : item.symbol}
                  </span>
                  <span style={{ color: '#10b981', fontSize: '13px', fontWeight: 'bold' }}>
                    +{(Math.random() * 10 + 2).toFixed(2)}%
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Top Losers */}
          <div style={{
            background: '#1e293b',
            borderRadius: '8px',
            padding: '15px',
            marginBottom: '15px',
            border: '1px solid #334155'
          }}>
            <h4 style={{
              margin: '0 0 12px 0',
              color: '#ef4444',
              fontSize: '14px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <TrendingDown size={16} />
              Top Losers (24h)
            </h4>
            {currentData.slice(3, 6).map((item, index) => (
              <div key={index} style={{
                padding: '8px 0',
                borderBottom: index < 2 ? '1px solid #334155' : 'none'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{ color: 'white', fontSize: '13px', fontWeight: 'bold' }}>
                    {marketType === 'crypto' ? item.pair : item.symbol}
                  </span>
                  <span style={{ color: '#ef4444', fontSize: '13px', fontWeight: 'bold' }}>
                    -{(Math.random() * 8 + 1).toFixed(2)}%
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* AI Recommendations */}
          <div style={{
            background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            borderRadius: '8px',
            padding: '15px',
            marginBottom: '15px',
            color: 'white'
          }}>
            <h4 style={{
              margin: '0 0 10px 0',
              fontSize: '14px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <Zap size={16} />
              AI Recommendation
            </h4>
            <p style={{
              margin: '0 0 10px 0',
              fontSize: '13px',
              lineHeight: '1.5',
              opacity: 0.9
            }}>
              Based on current indicators, consider {currentData[0] && (marketType === 'crypto' ? currentData[0].pair : currentData[0].symbol)} for a potential long position.
            </p>
            <div style={{
              fontSize: '12px',
              opacity: 0.8
            }}>
              Confidence: 78%
            </div>
          </div>

          {/* Market Alerts */}
          <div style={{
            background: '#1e293b',
            borderRadius: '8px',
            padding: '15px',
            border: '1px solid #334155'
          }}>
            <h4 style={{
              margin: '0 0 12px 0',
              color: 'white',
              fontSize: '14px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <AlertCircle size={16} color="#f59e0b" />
              Active Alerts
            </h4>
            <div style={{
              padding: '10px',
              background: '#0f172a',
              borderRadius: '6px',
              marginBottom: '8px',
              borderLeft: '3px solid #f59e0b'
            }}>
              <div style={{ color: 'white', fontSize: '13px', fontWeight: 'bold', marginBottom: '4px' }}>
                BTC/USD - Price Alert
              </div>
              <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                Price crossed $45,000
              </div>
            </div>
            <div style={{
              padding: '10px',
              background: '#0f172a',
              borderRadius: '6px',
              borderLeft: '3px solid #10b981'
            }}>
              <div style={{ color: 'white', fontSize: '13px', fontWeight: 'bold', marginBottom: '4px' }}>
                ETH/USD - RSI Alert
              </div>
              <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                RSI dropped below 30 (Oversold)
              </div>
            </div>
          </div>
        </div>

        {/* Upgrade CTA */}
        <div style={{
          padding: '15px',
          borderTop: '1px solid #334155'
        }}>
          <div style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            borderRadius: '8px',
            padding: '15px',
            textAlign: 'center',
            color: 'white'
          }}>
            <div style={{
              fontSize: '14px',
              fontWeight: 'bold',
              marginBottom: '8px'
            }}>
              Unlock AI Features
            </div>
            <div style={{
              fontSize: '12px',
              opacity: 0.9,
              marginBottom: '12px'
            }}>
              Get price predictions, advanced signals, and more
            </div>
            <button style={{
              background: 'white',
              color: '#059669',
              border: 'none',
              borderRadius: '6px',
              padding: '10px 20px',
              fontSize: '13px',
              fontWeight: 'bold',
              cursor: 'pointer',
              width: '100%'
            }}>
              Upgrade to PRO - $29/mo
            </button>
          </div>
        </div>
      </div>

      {/* Add CSS animation */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default EnhancedDashboard;
