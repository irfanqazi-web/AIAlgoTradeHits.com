import React, { useState, useEffect } from 'react';
import {
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Database,
  Activity,
  Calendar,
  Timer,
  TrendingUp,
  Play
} from 'lucide-react';
import apiService from '../services/api';

export default function SchedulerMonitoring({ onClose }) {
  const [schedulerData, setSchedulerData] = useState([]);
  const [executionLogs, setExecutionLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedScheduler, setSelectedScheduler] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Scheduler definitions (6 existing + 2 weekly)
  const schedulerDefinitions = [
    {
      name: 'daily-crypto-fetcher',
      table: 'crypto_daily',
      schedule: 'Daily @ 12:00 AM ET',
      description: 'Daily cryptocurrency OHLC data',
      icon: '₿',
      type: 'daily'
    },
    {
      name: 'hourly-crypto-fetcher',
      table: 'crypto_hourly_data',
      schedule: 'Every hour',
      description: 'Hourly cryptocurrency OHLC data',
      icon: '⏰',
      type: 'hourly'
    },
    {
      name: 'fivemin-top10-fetcher',
      table: 'crypto_5min_top10_gainers',
      schedule: 'Every 5 minutes',
      description: '5-min data for top 10 gainers',
      icon: '⚡',
      type: '5min'
    },
    {
      name: 'daily-stock-fetcher',
      table: 'stocks_daily',
      schedule: 'Daily @ 6:00 PM ET',
      description: 'Daily stock OHLC data (Top 100)',
      icon: '📈',
      type: 'daily'
    },
    {
      name: 'hourly-stock-fetcher',
      table: 'stocks_hourly_data',
      schedule: 'Every hour (market hours)',
      description: 'Hourly stock OHLC data',
      icon: '📊',
      type: 'hourly'
    },
    {
      name: 'fivemin-stock-fetcher',
      table: 'stocks_5min_data',
      schedule: 'Every 5 minutes (market hours)',
      description: '5-min stock data',
      icon: '💹',
      type: '5min'
    },
    {
      name: 'weekly-stock-fetcher',
      table: 'stocks_weekly_summary',
      schedule: 'Sunday @ 11:00 PM ET',
      description: 'Weekly summary for ALL US stocks (~20,000)',
      icon: '🏢',
      type: 'weekly'
    },
    {
      name: 'weekly-crypto-fetcher',
      table: 'cryptos_weekly_summary',
      schedule: 'Sunday @ 10:00 PM ET',
      description: 'Weekly summary for ALL cryptos',
      icon: '🪙',
      type: 'weekly'
    }
  ];

  useEffect(() => {
    loadSchedulerData();
  }, []);

  const loadSchedulerData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiService.getSchedulerStatus();

      if (response.success) {
        setSchedulerData(response.schedulers || []);
        setExecutionLogs(response.recent_executions || []);
      } else {
        // If API not ready, show placeholder data
        setSchedulerData(schedulerDefinitions.map(s => ({
          ...s,
          last_execution: null,
          last_status: 'UNKNOWN',
          last_duration: null,
          total_runs_30d: 0,
          success_rate: 0
        })));
      }
    } catch (err) {
      console.error('Error loading scheduler data:', err);
      // Show placeholder data on error
      setSchedulerData(schedulerDefinitions.map(s => ({
        ...s,
        last_execution: null,
        last_status: 'UNKNOWN',
        last_duration: null,
        total_runs_30d: 0,
        success_rate: 0
      })));
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadSchedulerData();
    setRefreshing(false);
  };

  const handleTriggerScheduler = async (schedulerName) => {
    if (!confirm(`Are you sure you want to manually trigger ${schedulerName}?`)) return;

    try {
      const response = await apiService.triggerScheduler(schedulerName);
      if (response.success) {
        alert(`Scheduler ${schedulerName} triggered successfully!`);
        loadSchedulerData();
      } else {
        alert(`Failed to trigger: ${response.error}`);
      }
    } catch (err) {
      alert(`Error triggering scheduler: ${err.message}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'SUCCESS': return '#10b981';
      case 'FAILED': return '#ef4444';
      case 'PARTIAL': return '#f59e0b';
      case 'RUNNING': return '#3b82f6';
      default: return '#64748b';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toUpperCase()) {
      case 'SUCCESS': return <CheckCircle size={18} color="#10b981" />;
      case 'FAILED': return <XCircle size={18} color="#ef4444" />;
      case 'PARTIAL': return <AlertTriangle size={18} color="#f59e0b" />;
      case 'RUNNING': return <RefreshCw size={18} color="#3b82f6" className="spin" />;
      default: return <Clock size={18} color="#64748b" />;
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '-';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs.toFixed(0)}s`;
  };

  const formatDateTime = (dateStr) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Merge scheduler definitions with actual data
  const mergedSchedulers = schedulerDefinitions.map(def => {
    const actual = schedulerData.find(s => s.scheduler_name === def.name);
    return {
      ...def,
      ...actual,
      last_execution: actual?.last_execution_time || null,
      last_status: actual?.last_status || 'UNKNOWN',
      last_duration: actual?.last_duration_minutes ? actual.last_duration_minutes * 60 : null,
      success_rate: actual?.successful_runs_30d && actual?.total_executions_30d
        ? ((actual.successful_runs_30d / actual.total_executions_30d) * 100).toFixed(0)
        : 0,
      total_runs_30d: actual?.total_executions_30d || 0
    };
  });

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
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px',
          borderBottom: '2px solid #1e293b',
          paddingBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Activity size={32} color="#10b981" />
            <h1 style={{
              fontSize: '28px',
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              margin: 0
            }}>
              Scheduler Monitoring
            </h1>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              style={{
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 24px',
                fontSize: '14px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                opacity: refreshing ? 0.6 : 1
              }}
            >
              <RefreshCw size={18} className={refreshing ? 'spin' : ''} />
              Refresh
            </button>
            <button
              onClick={onClose}
              style={{
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 24px',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Close
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
          {[
            { label: 'Total Schedulers', value: schedulerDefinitions.length, icon: Calendar, color: '#3b82f6' },
            { label: 'Daily Jobs', value: schedulerDefinitions.filter(s => s.type === 'daily').length, icon: Clock, color: '#10b981' },
            { label: 'Hourly Jobs', value: schedulerDefinitions.filter(s => s.type === 'hourly').length, icon: Timer, color: '#f59e0b' },
            { label: 'Weekly Jobs', value: schedulerDefinitions.filter(s => s.type === 'weekly').length, icon: TrendingUp, color: '#8b5cf6' }
          ].map((stat, i) => (
            <div key={i} style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid #334155'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '4px' }}>{stat.label}</div>
                  <div style={{ color: 'white', fontSize: '28px', fontWeight: 'bold' }}>{stat.value}</div>
                </div>
                <stat.icon size={32} color={stat.color} />
              </div>
            </div>
          ))}
        </div>

        {/* Schedulers Grid */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155',
          marginBottom: '24px'
        }}>
          <h3 style={{ color: '#10b981', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={20} />
            Data Pipeline Schedulers
          </h3>

          {loading ? (
            <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>
              Loading scheduler data...
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
              {mergedSchedulers.map((scheduler, index) => (
                <div
                  key={index}
                  style={{
                    background: '#0f172a',
                    borderRadius: '12px',
                    padding: '20px',
                    border: `1px solid ${scheduler.type === 'weekly' ? '#8b5cf6' : '#334155'}`,
                    cursor: 'pointer',
                    transition: 'all 0.3s'
                  }}
                  onClick={() => setSelectedScheduler(scheduler)}
                  onMouseOver={(e) => e.currentTarget.style.borderColor = '#10b981'}
                  onMouseOut={(e) => e.currentTarget.style.borderColor = scheduler.type === 'weekly' ? '#8b5cf6' : '#334155'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '24px' }}>{scheduler.icon}</span>
                      <div>
                        <div style={{ color: 'white', fontWeight: 'bold', fontSize: '14px' }}>{scheduler.name}</div>
                        <div style={{ color: '#64748b', fontSize: '12px' }}>{scheduler.description}</div>
                      </div>
                    </div>
                    {getStatusIcon(scheduler.last_status)}
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '12px' }}>
                    <div>
                      <div style={{ color: '#64748b' }}>Schedule</div>
                      <div style={{ color: '#94a3b8' }}>{scheduler.schedule}</div>
                    </div>
                    <div>
                      <div style={{ color: '#64748b' }}>Table</div>
                      <div style={{ color: '#94a3b8' }}>{scheduler.table}</div>
                    </div>
                    <div>
                      <div style={{ color: '#64748b' }}>Last Run</div>
                      <div style={{ color: '#94a3b8' }}>{formatDateTime(scheduler.last_execution)}</div>
                    </div>
                    <div>
                      <div style={{ color: '#64748b' }}>Duration</div>
                      <div style={{ color: '#94a3b8' }}>{formatDuration(scheduler.last_duration)}</div>
                    </div>
                  </div>

                  <div style={{
                    marginTop: '12px',
                    paddingTop: '12px',
                    borderTop: '1px solid #1e293b',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div>
                        <span style={{ color: '#64748b', fontSize: '11px' }}>Success Rate: </span>
                        <span style={{
                          color: scheduler.success_rate >= 90 ? '#10b981' : scheduler.success_rate >= 70 ? '#f59e0b' : '#ef4444',
                          fontWeight: 'bold',
                          fontSize: '13px'
                        }}>
                          {scheduler.success_rate}%
                        </span>
                      </div>
                      <div>
                        <span style={{ color: '#64748b', fontSize: '11px' }}>Runs (30d): </span>
                        <span style={{ color: 'white', fontWeight: 'bold', fontSize: '13px' }}>
                          {scheduler.total_runs_30d}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTriggerScheduler(scheduler.name);
                      }}
                      style={{
                        background: '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '6px 12px',
                        fontSize: '11px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                      title="Manually trigger this scheduler"
                    >
                      <Play size={12} />
                      Run Now
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Execution Logs */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155'
        }}>
          <h3 style={{ color: '#10b981', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={20} />
            Recent Execution Log
          </h3>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', color: 'white', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #334155' }}>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Scheduler</th>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Date</th>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Duration</th>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Records</th>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#94a3b8' }}>Success/Failed</th>
                </tr>
              </thead>
              <tbody>
                {executionLogs.length > 0 ? executionLogs.slice(0, 20).map((log, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '12px' }}>{log.scheduler_name}</td>
                    <td style={{ padding: '12px' }}>{formatDateTime(log.start_time)}</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{
                        background: getStatusColor(log.status) + '20',
                        color: getStatusColor(log.status),
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 'bold'
                      }}>
                        {log.status}
                      </span>
                    </td>
                    <td style={{ padding: '12px' }}>{formatDuration(log.duration_seconds)}</td>
                    <td style={{ padding: '12px' }}>{log.records_inserted?.toLocaleString() || '-'}</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ color: '#10b981' }}>{log.successful_symbols || 0}</span>
                      {' / '}
                      <span style={{ color: '#ef4444' }}>{log.failed_symbols || 0}</span>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan="6" style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
                      No execution logs available yet. Logs will appear after schedulers run.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <style>{`
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
