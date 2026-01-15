import { useState, useEffect } from 'react';
import { PieChart, TrendingUp, DollarSign, Percent, Search, BarChart3 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://trading-api-1075463475276.us-central1.run.app';

export default function ETFAnalytics({ theme = 'dark' }) {
  const [etfs, setEtfs] = useState([]);
  const [selectedETF, setSelectedETF] = useState(null);
  const [profile, setProfile] = useState(null);
  const [performance, setPerformance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('total_assets');

  useEffect(() => {
    fetchETFList();
  }, []);

  const fetchETFList = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/etf/list?limit=100`);
      const data = await response.json();
      if (data.success) {
        setEtfs(data.etfs || []);
      }
    } catch (err) {
      console.error('Error fetching ETFs:', err);
    }
    setLoading(false);
  };

  const fetchETFDetails = async (symbol) => {
    setSelectedETF(symbol);
    try {
      const [profileRes, perfRes] = await Promise.all([
        fetch(`${API_BASE}/api/etf/profile/${symbol}`),
        fetch(`${API_BASE}/api/etf/performance/${symbol}`)
      ]);

      const profileData = await profileRes.json();
      const perfData = await perfRes.json();

      if (profileData.success) setProfile(profileData.profile);
      if (perfData.success) setPerformance(perfData.performance || []);
    } catch (err) {
      console.error('Error fetching ETF details:', err);
    }
  };

  const formatNumber = (num) => {
    if (!num) return '-';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toLocaleString()}`;
  };

  const formatPercent = (num) => {
    if (num === null || num === undefined) return '-';
    const sign = num >= 0 ? '+' : '';
    return `${sign}${num.toFixed(2)}%`;
  };

  const filteredETFs = etfs
    .filter(e =>
      e.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.name?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'total_assets') return (b.total_assets || 0) - (a.total_assets || 0);
      if (sortBy === 'expense_ratio') return (a.expense_ratio || 0) - (b.expense_ratio || 0);
      if (sortBy === 'return_1d') return (b.return_1d || 0) - (a.return_1d || 0);
      return 0;
    });

  const StatCard = ({ label, value, icon: Icon, color = '#10b981', suffix = '' }) => (
    <div style={{
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      borderRadius: '12px',
      padding: '16px',
      border: '1px solid #334155'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        {Icon && <Icon size={16} color={color} />}
        <span style={{ fontSize: '12px', color: '#64748b' }}>{label}</span>
      </div>
      <div style={{ fontSize: '20px', fontWeight: '700', color: 'white' }}>
        {value}{suffix}
      </div>
    </div>
  );

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: 'white', margin: 0 }}>
          ETF Analytics
        </h1>
        <p style={{ color: '#64748b', marginTop: '4px' }}>
          Exchange-Traded Fund profiles, performance, and analytics
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '24px' }}>
        {/* ETF List */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '20px',
          border: '1px solid #334155',
          maxHeight: 'calc(100vh - 180px)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* Search */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px',
            background: '#0f172a',
            borderRadius: '8px',
            marginBottom: '12px'
          }}>
            <Search size={16} color="#64748b" />
            <input
              type="text"
              placeholder="Search ETFs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                color: 'white',
                fontSize: '14px',
                outline: 'none'
              }}
            />
          </div>

          {/* Sort Options */}
          <div style={{
            display: 'flex',
            gap: '8px',
            marginBottom: '16px'
          }}>
            {[
              { key: 'total_assets', label: 'AUM' },
              { key: 'expense_ratio', label: 'Expense' },
              { key: 'return_1d', label: 'Return' }
            ].map(opt => (
              <button
                key={opt.key}
                onClick={() => setSortBy(opt.key)}
                style={{
                  flex: 1,
                  padding: '8px',
                  borderRadius: '6px',
                  border: 'none',
                  background: sortBy === opt.key ? '#10b981' : '#0f172a',
                  color: 'white',
                  fontSize: '11px',
                  cursor: 'pointer'
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>

          {/* ETF List */}
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {loading ? (
              <div style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
                Loading ETFs...
              </div>
            ) : (
              filteredETFs.map(etf => (
                <div
                  key={etf.symbol}
                  onClick={() => fetchETFDetails(etf.symbol)}
                  style={{
                    padding: '14px',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    marginBottom: '8px',
                    background: selectedETF === etf.symbol
                      ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%)'
                      : 'transparent',
                    border: selectedETF === etf.symbol
                      ? '1px solid rgba(139, 92, 246, 0.3)'
                      : '1px solid transparent',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '15px', fontWeight: '600', color: 'white' }}>
                        {etf.symbol}
                      </div>
                      <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                        {etf.name?.substring(0, 28)}{etf.name?.length > 28 ? '...' : ''}
                      </div>
                      <div style={{ fontSize: '10px', color: '#8b5cf6', marginTop: '4px' }}>
                        {etf.category || etf.fund_type}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: (etf.return_1d || 0) >= 0 ? '#10b981' : '#ef4444'
                      }}>
                        {formatPercent(etf.return_1d)}
                      </div>
                      <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                        {formatNumber(etf.total_assets)}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* ETF Details */}
        <div>
          {!selectedETF ? (
            <div style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              borderRadius: '16px',
              padding: '48px',
              border: '1px solid #334155',
              textAlign: 'center'
            }}>
              <PieChart size={48} color="#64748b" style={{ marginBottom: '16px' }} />
              <h3 style={{ color: 'white', marginBottom: '8px' }}>Select an ETF</h3>
              <p style={{ color: '#64748b' }}>
                Choose an ETF from the list to view detailed analytics
              </p>
            </div>
          ) : (
            <div>
              {/* ETF Header */}
              {profile && (
                <div style={{
                  background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid #334155',
                  marginBottom: '20px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h2 style={{ fontSize: '24px', fontWeight: '700', color: 'white', margin: 0 }}>
                        {profile.symbol}
                      </h2>
                      <p style={{ color: '#94a3b8', marginTop: '4px', fontSize: '16px' }}>
                        {profile.name}
                      </p>
                      <div style={{ display: 'flex', gap: '12px', marginTop: '12px', flexWrap: 'wrap' }}>
                        {profile.fund_family && (
                          <span style={{
                            padding: '4px 12px',
                            borderRadius: '6px',
                            background: '#3b82f6',
                            color: 'white',
                            fontSize: '12px'
                          }}>
                            {profile.fund_family}
                          </span>
                        )}
                        {profile.fund_type && (
                          <span style={{
                            padding: '4px 12px',
                            borderRadius: '6px',
                            background: '#8b5cf6',
                            color: 'white',
                            fontSize: '12px'
                          }}>
                            {profile.fund_type}
                          </span>
                        )}
                        {profile.category && (
                          <span style={{
                            padding: '4px 12px',
                            borderRadius: '6px',
                            background: '#10b981',
                            color: 'white',
                            fontSize: '12px'
                          }}>
                            {profile.category}
                          </span>
                        )}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '28px', fontWeight: '700', color: '#8b5cf6' }}>
                        {formatNumber(profile.total_assets)}
                      </div>
                      <div style={{ fontSize: '12px', color: '#64748b' }}>Total Assets</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Key Metrics */}
              {profile && (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(4, 1fr)',
                  gap: '16px',
                  marginBottom: '20px'
                }}>
                  <StatCard
                    label="NAV"
                    value={profile.nav ? `$${profile.nav.toFixed(2)}` : '-'}
                    icon={DollarSign}
                    color="#10b981"
                  />
                  <StatCard
                    label="Expense Ratio"
                    value={profile.expense_ratio ? `${(profile.expense_ratio * 100).toFixed(2)}%` : '-'}
                    icon={Percent}
                    color="#f59e0b"
                  />
                  <StatCard
                    label="Avg Volume"
                    value={profile.average_volume?.toLocaleString() || '-'}
                    icon={BarChart3}
                    color="#3b82f6"
                  />
                  <StatCard
                    label="Inception"
                    value={profile.inception_date || '-'}
                    icon={TrendingUp}
                    color="#8b5cf6"
                  />
                </div>
              )}

              {/* Performance History */}
              {performance.length > 0 && (
                <div style={{
                  background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid #334155',
                  marginBottom: '20px'
                }}>
                  <h3 style={{ color: 'white', marginBottom: '16px', fontSize: '16px' }}>
                    Performance Returns
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }}>
                    {[
                      { label: '1 Day', key: 'return_1d' },
                      { label: '1 Week', key: 'return_1w' },
                      { label: '1 Month', key: 'return_1m' },
                      { label: 'YTD', key: 'return_ytd' },
                      { label: '1 Year', key: 'return_1y' }
                    ].map(period => {
                      const value = performance[0]?.[period.key];
                      return (
                        <div
                          key={period.key}
                          style={{
                            padding: '16px',
                            borderRadius: '10px',
                            background: '#0f172a',
                            textAlign: 'center'
                          }}
                        >
                          <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '8px' }}>
                            {period.label}
                          </div>
                          <div style={{
                            fontSize: '18px',
                            fontWeight: '700',
                            color: value && value >= 0 ? '#10b981' : '#ef4444'
                          }}>
                            {formatPercent(value)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* ETF Info */}
              {profile && (
                <div style={{
                  background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid #334155'
                }}>
                  <h3 style={{ color: 'white', marginBottom: '16px', fontSize: '16px' }}>
                    Fund Information
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
                    <div>
                      <div style={{ fontSize: '12px', color: '#64748b' }}>Exchange</div>
                      <div style={{ color: 'white', marginTop: '4px' }}>{profile.exchange || '-'}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', color: '#64748b' }}>Currency</div>
                      <div style={{ color: 'white', marginTop: '4px' }}>{profile.currency || 'USD'}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', color: '#64748b' }}>Benchmark</div>
                      <div style={{ color: 'white', marginTop: '4px' }}>{profile.benchmark || '-'}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '12px', color: '#64748b' }}>Strategy</div>
                      <div style={{ color: 'white', marginTop: '4px' }}>
                        {profile.investment_strategy?.substring(0, 50) || '-'}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
