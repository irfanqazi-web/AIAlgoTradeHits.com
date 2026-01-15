import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, RefreshCw, Filter } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://trading-api-1075463475276.us-central1.run.app';

export default function MarketMovers({ theme = 'dark' }) {
  const [movers, setMovers] = useState({ gainers: [], losers: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [assetFilter, setAssetFilter] = useState('all');
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchMovers = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/market-movers?type=${assetFilter}`);
      const data = await response.json();

      if (data.success) {
        setMovers({
          gainers: data.gainers || [],
          losers: data.losers || []
        });
        setLastUpdated(new Date());
        setError(null);
      } else {
        setError(data.error || 'Failed to fetch market movers');
      }
    } catch (err) {
      setError('Failed to connect to API');
      console.error('Market movers error:', err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchMovers();
    const interval = setInterval(fetchMovers, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [assetFilter]);

  const formatNumber = (num) => {
    if (!num) return '-';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toLocaleString()}`;
  };

  const formatPercent = (num) => {
    if (!num) return '-';
    const sign = num >= 0 ? '+' : '';
    return `${sign}${num.toFixed(2)}%`;
  };

  const MoverCard = ({ mover, isGainer }) => (
    <div style={{
      background: isGainer
        ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)'
        : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%)',
      borderRadius: '12px',
      padding: '16px',
      border: `1px solid ${isGainer ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
      marginBottom: '12px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{
            fontSize: '16px',
            fontWeight: '600',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            {mover.symbol}
            <span style={{
              fontSize: '10px',
              padding: '2px 6px',
              borderRadius: '4px',
              background: mover.asset_type === 'stocks' ? '#3b82f6' :
                         mover.asset_type === 'crypto' ? '#f59e0b' : '#8b5cf6',
              color: 'white'
            }}>
              {mover.asset_type?.toUpperCase()}
            </span>
          </div>
          <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
            {mover.name?.substring(0, 30)}{mover.name?.length > 30 ? '...' : ''}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{
            fontSize: '18px',
            fontWeight: '700',
            color: isGainer ? '#10b981' : '#ef4444'
          }}>
            {formatPercent(mover.change_percent)}
          </div>
          <div style={{ fontSize: '14px', color: 'white' }}>
            ${mover.price?.toFixed(2)}
          </div>
        </div>
      </div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginTop: '12px',
        fontSize: '11px',
        color: '#64748b'
      }}>
        <span>Vol: {mover.volume?.toLocaleString()}</span>
        <span>MCap: {formatNumber(mover.market_cap)}</span>
      </div>
    </div>
  );

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: 'white',
            margin: 0
          }}>
            Market Movers
          </h1>
          <p style={{ color: '#64748b', marginTop: '4px' }}>
            Top gainers and losers across all markets
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {/* Asset Filter */}
          <div style={{ display: 'flex', gap: '8px' }}>
            {['all', 'stocks', 'etf', 'crypto'].map(type => (
              <button
                key={type}
                onClick={() => setAssetFilter(type)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: 'none',
                  background: assetFilter === type
                    ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                    : '#1e293b',
                  color: 'white',
                  fontSize: '13px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {type}
              </button>
            ))}
          </div>

          {/* Refresh Button */}
          <button
            onClick={fetchMovers}
            disabled={loading}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid #334155',
              background: 'transparent',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Last Updated */}
      {lastUpdated && (
        <div style={{
          fontSize: '12px',
          color: '#64748b',
          marginBottom: '16px'
        }}>
          Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '12px',
          padding: '16px',
          color: '#ef4444',
          marginBottom: '24px'
        }}>
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && movers.gainers.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px', color: '#64748b' }}>
          Loading market movers...
        </div>
      )}

      {/* Movers Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '24px'
      }}>
        {/* Gainers Column */}
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
            padding: '12px 16px',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%)',
            borderRadius: '12px',
            border: '1px solid rgba(16, 185, 129, 0.3)'
          }}>
            <TrendingUp size={20} color="#10b981" />
            <span style={{ fontSize: '16px', fontWeight: '600', color: '#10b981' }}>
              Top Gainers ({movers.gainers.length})
            </span>
          </div>

          {movers.gainers.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
              No gainers data available
            </div>
          ) : (
            movers.gainers.slice(0, 15).map((mover, idx) => (
              <MoverCard key={`gainer-${idx}`} mover={mover} isGainer={true} />
            ))
          )}
        </div>

        {/* Losers Column */}
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
            padding: '12px 16px',
            background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%)',
            borderRadius: '12px',
            border: '1px solid rgba(239, 68, 68, 0.3)'
          }}>
            <TrendingDown size={20} color="#ef4444" />
            <span style={{ fontSize: '16px', fontWeight: '600', color: '#ef4444' }}>
              Top Losers ({movers.losers.length})
            </span>
          </div>

          {movers.losers.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
              No losers data available
            </div>
          ) : (
            movers.losers.slice(0, 15).map((mover, idx) => (
              <MoverCard key={`loser-${idx}`} mover={mover} isGainer={false} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
