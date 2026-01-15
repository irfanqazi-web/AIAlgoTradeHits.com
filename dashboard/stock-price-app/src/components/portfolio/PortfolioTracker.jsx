import React, { useState } from 'react';
import {
  Briefcase, TrendingUp, TrendingDown, DollarSign, PieChart, Activity,
  Plus, Edit, Trash2, Eye, EyeOff, BarChart3, Target
} from 'lucide-react';

const PortfolioTracker = () => {
  const [portfolio, setPortfolio] = useState([
    {
      id: 1,
      symbol: 'BTC',
      name: 'Bitcoin',
      quantity: 0.5,
      avgBuyPrice: 87500,
      currentPrice: 93420,
      type: 'crypto'
    },
    {
      id: 2,
      symbol: 'ETH',
      name: 'Ethereum',
      quantity: 5,
      avgBuyPrice: 3200,
      currentPrice: 3356,
      type: 'crypto'
    },
    {
      id: 3,
      symbol: 'AAPL',
      name: 'Apple Inc.',
      quantity: 10,
      avgBuyPrice: 185,
      currentPrice: 192.50,
      type: 'stock'
    },
    {
      id: 4,
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      quantity: 5,
      avgBuyPrice: 245,
      currentPrice: 238.75,
      type: 'stock'
    },
  ]);

  const [showValues, setShowValues] = useState(true);
  const [filter, setFilter] = useState('all'); // all, crypto, stock

  const calculatePortfolioStats = () => {
    const filteredPortfolio = filter === 'all'
      ? portfolio
      : portfolio.filter(p => p.type === filter);

    const totalValue = filteredPortfolio.reduce((sum, item) =>
      sum + (item.quantity * item.currentPrice), 0
    );

    const totalCost = filteredPortfolio.reduce((sum, item) =>
      sum + (item.quantity * item.avgBuyPrice), 0
    );

    const totalGainLoss = totalValue - totalCost;
    const totalGainLossPercent = ((totalGainLoss / totalCost) * 100) || 0;

    return {
      totalValue,
      totalCost,
      totalGainLoss,
      totalGainLossPercent,
      positions: filteredPortfolio.length
    };
  };

  const calculateAssetStats = (item) => {
    const value = item.quantity * item.currentPrice;
    const cost = item.quantity * item.avgBuyPrice;
    const gainLoss = value - cost;
    const gainLossPercent = ((gainLoss / cost) * 100) || 0;

    return { value, cost, gainLoss, gainLossPercent };
  };

  const stats = calculatePortfolioStats();

  const formatCurrency = (value) => {
    if (!showValues) return '••••••';
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatPercent = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  return (
    <div style={{
      padding: '20px',
      background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
      minHeight: 'calc(100vh - 64px)',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px'
      }}>
        <div>
          <h1 style={{
            margin: 0,
            color: 'white',
            fontSize: '32px',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <Briefcase size={36} color="#10b981" />
            Portfolio
          </h1>
          <p style={{
            margin: '8px 0 0 0',
            color: '#94a3b8',
            fontSize: '16px'
          }}>
            {stats.positions} positions • Last updated: {new Date().toLocaleTimeString()}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={() => setShowValues(!showValues)}
            style={{
              padding: '10px',
              background: '#1e293b',
              color: 'white',
              border: '1px solid #334155',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
            title={showValues ? 'Hide values' : 'Show values'}
          >
            {showValues ? <Eye size={18} /> : <EyeOff size={18} />}
          </button>

          <button
            style={{
              padding: '12px 24px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 12px rgba(59, 130, 246, 0.4)',
            }}
          >
            <Plus size={20} />
            Add Position
          </button>
        </div>
      </div>

      {/* Portfolio Stats Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        marginBottom: '30px'
      }}>
        {/* Total Value */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #334155',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <DollarSign size={24} color="#10b981" />
            <span style={{ color: '#94a3b8', fontSize: '14px' }}>Total Value</span>
          </div>
          <div style={{ color: 'white', fontSize: '28px', fontWeight: 'bold' }}>
            {formatCurrency(stats.totalValue)}
          </div>
        </div>

        {/* Total Gain/Loss */}
        <div style={{
          background: `linear-gradient(135deg, ${stats.totalGainLoss >= 0 ? '#065f46' : '#7f1d1d'} 0%, ${stats.totalGainLoss >= 0 ? '#064e3b' : '#991b1b'} 100%)`,
          padding: '24px',
          borderRadius: '12px',
          border: `1px solid ${stats.totalGainLoss >= 0 ? '#10b981' : '#ef4444'}`,
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            {stats.totalGainLoss >= 0 ? <TrendingUp size={24} color="#10b981" /> : <TrendingDown size={24} color="#ef4444" />}
            <span style={{ color: '#e5e7eb', fontSize: '14px' }}>Total P&L</span>
          </div>
          <div style={{ color: 'white', fontSize: '28px', fontWeight: 'bold' }}>
            {formatCurrency(stats.totalGainLoss)}
          </div>
          <div style={{ color: '#e5e7eb', fontSize: '14px', marginTop: '4px' }}>
            {formatPercent(stats.totalGainLossPercent)}
          </div>
        </div>

        {/* Total Cost */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #334155',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <Activity size={24} color="#3b82f6" />
            <span style={{ color: '#94a3b8', fontSize: '14px' }}>Total Cost</span>
          </div>
          <div style={{ color: 'white', fontSize: '28px', fontWeight: 'bold' }}>
            {formatCurrency(stats.totalCost)}
          </div>
        </div>

        {/* Positions */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #334155',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <Target size={24} color="#f59e0b" />
            <span style={{ color: '#94a3b8', fontSize: '14px' }}>Positions</span>
          </div>
          <div style={{ color: 'white', fontSize: '28px', fontWeight: 'bold' }}>
            {stats.positions}
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{
        display: 'flex',
        gap: '10px',
        marginBottom: '20px'
      }}>
        {['all', 'crypto', 'stock'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '10px 20px',
              background: filter === f ? '#3b82f6' : '#1e293b',
              color: 'white',
              border: filter === f ? '1px solid #60a5fa' : '1px solid #334155',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: filter === f ? 'bold' : 'normal',
              textTransform: 'capitalize'
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Holdings Table */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '12px',
        border: '1px solid #334155',
        overflow: 'hidden',
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
      }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse'
        }}>
          <thead>
            <tr style={{ background: '#0f172a', borderBottom: '1px solid #334155' }}>
              <th style={{ padding: '15px', textAlign: 'left', color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>
                ASSET
              </th>
              <th style={{ padding: '15px', textAlign: 'right', color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>
                QUANTITY
              </th>
              <th style={{ padding: '15px', textAlign: 'right', color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>
                AVG BUY
              </th>
              <th style={{ padding: '15px', textAlign: 'right', color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>
                CURRENT
              </th>
              <th style={{ padding: '15px', textAlign: 'right', color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>
                VALUE
              </th>
              <th style={{ padding: '15px', textAlign: 'right', color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>
                P&L
              </th>
              <th style={{ padding: '15px', textAlign: 'right', color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>
                ACTIONS
              </th>
            </tr>
          </thead>
          <tbody>
            {portfolio
              .filter(item => filter === 'all' || item.type === filter)
              .map(item => {
                const itemStats = calculateAssetStats(item);
                const isPositive = itemStats.gainLoss >= 0;

                return (
                  <tr key={item.id} style={{
                    borderBottom: '1px solid #334155',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#1e293b'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '15px' }}>
                      <div>
                        <div style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
                          {item.symbol}
                        </div>
                        <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                          {item.name}
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '15px', textAlign: 'right', color: 'white', fontSize: '14px' }}>
                      {item.quantity}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'right', color: 'white', fontSize: '14px' }}>
                      {formatCurrency(item.avgBuyPrice)}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'right', color: 'white', fontSize: '14px' }}>
                      {formatCurrency(item.currentPrice)}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'right', color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
                      {formatCurrency(itemStats.value)}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'right' }}>
                      <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 12px',
                        background: isPositive ? '#065f4633' : '#7f1d1d33',
                        borderRadius: '6px',
                        border: `1px solid ${isPositive ? '#10b981' : '#ef4444'}`
                      }}>
                        {isPositive ? <TrendingUp size={14} color="#10b981" /> : <TrendingDown size={14} color="#ef4444" />}
                        <span style={{
                          color: isPositive ? '#10b981' : '#ef4444',
                          fontSize: '14px',
                          fontWeight: 'bold'
                        }}>
                          {formatCurrency(Math.abs(itemStats.gainLoss))}
                        </span>
                        <span style={{
                          color: isPositive ? '#10b981' : '#ef4444',
                          fontSize: '12px'
                        }}>
                          ({formatPercent(itemStats.gainLossPercent)})
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '15px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <button style={{
                          padding: '6px',
                          background: '#3b82f6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}>
                          <Edit size={14} />
                        </button>
                        <button style={{
                          padding: '6px',
                          background: '#ef4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PortfolioTracker;
