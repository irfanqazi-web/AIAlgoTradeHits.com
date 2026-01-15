import { useState, useEffect } from 'react';
import { Database, RefreshCw, TrendingUp, Clock, CheckCircle, AlertTriangle, Loader, HardDrive, Activity } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-252370699783.us-central1.run.app'
);

export default function DataWarehouseStatus({ theme = 'dark' }) {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const isDark = theme === 'dark';

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/data-warehouse-status`);
      const data = await response.json();
      if (data.success) {
        setStatus(data);
        setLastRefresh(new Date());
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();

    // Auto-refresh every 30 seconds
    const interval = autoRefresh ? setInterval(fetchStatus, 30000) : null;
    return () => interval && clearInterval(interval);
  }, [autoRefresh]);

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toLocaleString() || '0';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = (percentage) => {
    if (percentage >= 80) return '#10b981';
    if (percentage >= 50) return '#f59e0b';
    return '#ef4444';
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px',
        color: isDark ? '#94a3b8' : '#64748b'
      }}>
        <Loader size={32} style={{ animation: 'spin 1s linear infinite', marginRight: '12px' }} />
        Loading data warehouse status...
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  const tables = status?.tables || [];
  const summary = status?.summary || {};

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Database size={32} color="#10b981" />
          <div>
            <h2 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: 0, fontSize: '24px' }}>
              Data Warehouse Status
            </h2>
            <p style={{ color: isDark ? '#64748b' : '#94a3b8', margin: '4px 0 0 0', fontSize: '14px' }}>
              Real-time monitoring of data collection progress
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          <button
            onClick={fetchStatus}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              background: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
          borderRadius: '16px',
          padding: '20px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <Database size={24} color="#3b82f6" />
            <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>Total Tables</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: isDark ? '#f1f5f9' : '#1e293b' }}>
            {summary.total_tables || tables.length}
          </div>
        </div>

        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
          borderRadius: '16px',
          padding: '20px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <TrendingUp size={24} color="#10b981" />
            <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>Total Records</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#10b981' }}>
            {formatNumber(summary.total_rows)}
          </div>
        </div>

        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
          borderRadius: '16px',
          padding: '20px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <HardDrive size={24} color="#8b5cf6" />
            <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>Storage Used</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#8b5cf6' }}>
            {((summary.total_size_mb || 0) / 1024).toFixed(2)} GB
          </div>
        </div>

        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
          borderRadius: '16px',
          padding: '20px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <Clock size={24} color="#f59e0b" />
            <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>Last Updated</span>
          </div>
          <div style={{ fontSize: '16px', fontWeight: '600', color: isDark ? '#f1f5f9' : '#1e293b' }}>
            {lastRefresh ? formatDate(lastRefresh.toISOString()) : 'N/A'}
          </div>
        </div>
      </div>

      {/* Weekly Data Progress - All 6 Asset Types */}
      <div style={{
        background: isDark ? '#1e293b' : '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '24px',
        border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
      }}>
        <h3 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: '0 0 20px 0', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={20} color="#10b981" />
          Week-by-Week Data Collection Progress
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          {[
            { key: 'stocks', label: 'Stocks', color: '#10b981', gradient: 'linear-gradient(90deg, #10b981 0%, #059669 100%)' },
            { key: 'crypto', label: 'Crypto', color: '#f59e0b', gradient: 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)' },
            { key: 'forex', label: 'Forex', color: '#3b82f6', gradient: 'linear-gradient(90deg, #3b82f6 0%, #2563eb 100%)' },
            { key: 'etfs', label: 'ETFs', color: '#8b5cf6', gradient: 'linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%)' },
            { key: 'indices', label: 'Indices', color: '#ec4899', gradient: 'linear-gradient(90deg, #ec4899 0%, #db2777 100%)' },
            { key: 'commodities', label: 'Commodities', color: '#14b8a6', gradient: 'linear-gradient(90deg, #14b8a6 0%, #0d9488 100%)' }
          ].map(asset => {
            const progress = status?.weekly_progress?.[asset.key] || {};
            const current = progress.current || 0;
            const target = progress.target || 1;
            const records = progress.records || 0;
            const weeks = progress.weeks || 0;
            const pct = Math.min((current / target) * 100, 100);

            return (
              <div key={asset.key} style={{
                background: isDark ? '#0f172a' : '#f8fafc',
                borderRadius: '12px',
                padding: '16px',
                border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ color: isDark ? '#f1f5f9' : '#1e293b', fontWeight: '600', fontSize: '14px' }}>
                    {asset.label}
                  </span>
                  <span style={{ color: asset.color, fontWeight: '600', fontSize: '14px' }}>
                    {formatNumber(current)} / {formatNumber(target)}
                  </span>
                </div>
                <div style={{
                  height: '8px',
                  background: isDark ? '#1e293b' : '#e2e8f0',
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${pct}%`,
                    background: asset.gradient,
                    borderRadius: '4px',
                    transition: 'width 0.5s ease'
                  }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: '11px', color: isDark ? '#64748b' : '#94a3b8' }}>
                  <span>{formatNumber(records)} records</span>
                  <span>{weeks} weeks</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tables List */}
      <div style={{
        background: isDark ? '#1e293b' : '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
      }}>
        <h3 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: '0 0 20px 0', fontSize: '18px' }}>
          All Data Tables
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}` }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', color: isDark ? '#94a3b8' : '#64748b', fontWeight: '600' }}>Table Name</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#94a3b8' : '#64748b', fontWeight: '600' }}>Rows</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#94a3b8' : '#64748b', fontWeight: '600' }}>Size (MB)</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#94a3b8' : '#64748b', fontWeight: '600' }}>Last Modified</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', color: isDark ? '#94a3b8' : '#64748b', fontWeight: '600' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {tables.map((table, idx) => (
                <tr key={table.name} style={{
                  borderBottom: idx < tables.length - 1 ? `1px solid ${isDark ? '#334155' : '#e2e8f0'}` : 'none',
                  background: idx % 2 === 0 ? 'transparent' : (isDark ? '#0f172a22' : '#f8fafc')
                }}>
                  <td style={{ padding: '12px 16px', color: isDark ? '#f1f5f9' : '#1e293b', fontWeight: '500' }}>
                    {table.name}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right', color: '#10b981', fontWeight: '600' }}>
                    {formatNumber(table.rows)}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#94a3b8' : '#64748b' }}>
                    {table.size_mb?.toFixed(2) || '0.00'}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#64748b' : '#94a3b8', fontSize: '12px' }}>
                    {formatDate(table.last_modified)}
                  </td>
                  <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                    {table.rows > 0 ? (
                      <CheckCircle size={18} color="#10b981" />
                    ) : (
                      <AlertTriangle size={18} color="#f59e0b" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
