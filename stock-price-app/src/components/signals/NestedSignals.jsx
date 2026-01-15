/**
 * NestedSignals Component
 * @version 5.2.0 - Migrated to SSOT architecture
 */
import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, Target, Layers, CheckCircle, AlertCircle, Clock, Zap } from 'lucide-react';
import { api } from '@/api';

const ACTION_COLORS = {
  EXECUTE: { bg: '#10b981', text: '#ffffff', icon: Zap },
  READY: { bg: '#3b82f6', text: '#ffffff', icon: Target },
  WATCH: { bg: '#f59e0b', text: '#000000', icon: Clock },
  WAIT: { bg: '#6b7280', text: '#ffffff', icon: AlertCircle }
};

const SIGNAL_COLORS = {
  ULTRA_BUY: { bg: '#059669', text: '#ffffff' },
  STRONG_BUY: { bg: '#10b981', text: '#ffffff' },
  BUY: { bg: '#34d399', text: '#000000' },
  WEAK_BUY: { bg: '#6ee7b7', text: '#000000' },
  HOLD: { bg: '#6b7280', text: '#ffffff' }
};

export default function NestedSignals({ onSymbolSelect, theme = 'dark' }) {
  const [signals, setSignals] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, EXECUTE, READY, WATCH
  const [alignedOnly, setAlignedOnly] = useState(false);

  const isDark = theme === 'dark';
  const colors = {
    bg: isDark ? '#0f172a' : '#ffffff',
    cardBg: isDark ? '#1e293b' : '#f8fafc',
    border: isDark ? '#334155' : '#e2e8f0',
    text: isDark ? '#f1f5f9' : '#1e293b',
    textSecondary: isDark ? '#94a3b8' : '#64748b',
    primary: '#3b82f6',
    success: '#10b981',
    danger: '#ef4444'
  };

  useEffect(() => {
    loadData();
  }, [filter, alignedOnly]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [signalsRes, summaryRes] = await Promise.all([
        api.ai.getNestedSignals({
          action: filter !== 'all' ? filter : null,
          aligned_only: alignedOnly,
          limit: 100
        }),
        api.ai.getNestedSummary()
      ]);

      setSignals(signalsRes.signals || []);
      setSummary(summaryRes);
    } catch (error) {
      console.error('Error loading nested signals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRowClick = (signal) => {
    if (onSymbolSelect) {
      onSymbolSelect(signal.symbol);
    }
  };

  return (
    <div style={{
      background: colors.cardBg,
      borderRadius: '16px',
      padding: '24px',
      border: `1px solid ${colors.border}`
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <h3 style={{
            color: colors.primary,
            fontSize: '20px',
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Layers size={24} />
            Nested Multi-Timeframe Signals
          </h3>
          <p style={{ color: colors.textSecondary, fontSize: '13px', margin: '4px 0 0' }}>
            Daily &gt; Hourly &gt; 5-Min Alignment | 66.2% UP Accuracy | 6.2x Better Than Single-TF
          </p>
        </div>

        {/* Model Performance Badge */}
        {summary?.model_summary && (
          <div style={{
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap'
          }}>
            <span style={{
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '600',
              background: `${colors.success}22`,
              color: colors.success
            }}>
              {summary.model_summary.accuracy} Accuracy
            </span>
            <span style={{
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '600',
              background: `${colors.primary}22`,
              color: colors.primary
            }}>
              ROC AUC: {summary.model_summary.roc_auc}
            </span>
          </div>
        )}
      </div>

      {/* Filters */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '20px',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <span style={{ color: colors.textSecondary, fontSize: '14px' }}>Filter by Action:</span>
        {['all', 'EXECUTE', 'READY', 'WATCH'].map(action => (
          <button
            key={action}
            onClick={() => setFilter(action)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: 'none',
              fontSize: '13px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: filter === action
                ? (action === 'all' ? colors.primary : ACTION_COLORS[action]?.bg || colors.primary)
                : colors.bg,
              color: filter === action ? '#ffffff' : colors.textSecondary
            }}
          >
            {action === 'all' ? 'All Signals' : action}
          </button>
        ))}

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: 'pointer',
            color: colors.textSecondary,
            fontSize: '13px'
          }}>
            <input
              type="checkbox"
              checked={alignedOnly}
              onChange={(e) => setAlignedOnly(e.target.checked)}
              style={{ width: '16px', height: '16px', cursor: 'pointer' }}
            />
            All Timeframes Aligned Only
          </label>
        </div>
      </div>

      {/* Action Legend */}
      <div style={{
        display: 'flex',
        gap: '16px',
        marginBottom: '16px',
        padding: '12px',
        background: colors.bg,
        borderRadius: '8px',
        flexWrap: 'wrap'
      }}>
        {Object.entries(ACTION_COLORS).map(([action, style]) => {
          const Icon = style.icon;
          return (
            <div key={action} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '600',
                background: style.bg,
                color: style.text,
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <Icon size={12} />
                {action}
              </span>
              <span style={{ color: colors.textSecondary, fontSize: '11px' }}>
                {action === 'EXECUTE' && 'All aligned + ready'}
                {action === 'READY' && 'All aligned'}
                {action === 'WATCH' && 'Partial aligned'}
                {action === 'WAIT' && 'No alignment'}
              </span>
            </div>
          );
        })}
      </div>

      {/* Signals Table */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: colors.text }}>
          <Activity size={24} style={{ animation: 'spin 1s linear infinite' }} />
          <p>Loading nested signals...</p>
        </div>
      ) : signals.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: colors.textSecondary }}>
          No signals found for current filters
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            color: colors.text,
            fontSize: '13px'
          }}>
            <thead>
              <tr style={{ borderBottom: `2px solid ${colors.border}` }}>
                <th style={{ padding: '12px', textAlign: 'left', color: colors.textSecondary }}>Symbol</th>
                <th style={{ padding: '12px', textAlign: 'left', color: colors.textSecondary }}>Date/Hour</th>
                <th style={{ padding: '12px', textAlign: 'center', color: colors.textSecondary }}>Action</th>
                <th style={{ padding: '12px', textAlign: 'center', color: colors.textSecondary }}>Signal</th>
                <th style={{ padding: '12px', textAlign: 'center', color: colors.textSecondary }}>Daily</th>
                <th style={{ padding: '12px', textAlign: 'center', color: colors.textSecondary }}>Hourly</th>
                <th style={{ padding: '12px', textAlign: 'center', color: colors.textSecondary }}>5-Min</th>
                <th style={{ padding: '12px', textAlign: 'center', color: colors.textSecondary }}>Aligned</th>
                <th style={{ padding: '12px', textAlign: 'center', color: colors.textSecondary }}>Outcome</th>
                <th style={{ padding: '12px', textAlign: 'right', color: colors.textSecondary }}>Change %</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((signal, index) => {
                const actionStyle = ACTION_COLORS[signal.action_status] || ACTION_COLORS.WAIT;
                const signalStyle = SIGNAL_COLORS[signal.nested_signal] || SIGNAL_COLORS.HOLD;
                const ActionIcon = actionStyle.icon;
                const isUp = signal.actual_outcome === 'UP';

                return (
                  <tr
                    key={index}
                    onClick={() => handleRowClick(signal)}
                    style={{
                      borderBottom: `1px solid ${colors.border}`,
                      cursor: 'pointer',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = `${colors.primary}11`}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '12px', fontWeight: '600' }}>
                      {signal.symbol}
                    </td>
                    <td style={{ padding: '12px', color: colors.textSecondary }}>
                      {signal.trade_date} @ {signal.trade_hour}:00
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{
                        padding: '4px 10px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: '600',
                        background: actionStyle.bg,
                        color: actionStyle.text,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <ActionIcon size={12} />
                        {signal.action_status}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{
                        padding: '4px 10px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: '600',
                        background: signalStyle.bg,
                        color: signalStyle.text
                      }}>
                        {signal.nested_signal}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <ScoreBar score={signal.scores?.daily || 0} max={8} color={colors.primary} />
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <ScoreBar score={signal.scores?.hourly || 0} max={10} color={colors.success} />
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <ScoreBar score={signal.scores?.fivemin || 0} max={10} color="#f59e0b" />
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      {signal.alignment?.all_tf_aligned ? (
                        <CheckCircle size={18} color={colors.success} />
                      ) : (
                        <AlertCircle size={18} color={colors.textSecondary} />
                      )}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        color: isUp ? colors.success : colors.danger,
                        fontWeight: '600'
                      }}>
                        {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                        {signal.actual_outcome}
                      </span>
                    </td>
                    <td style={{
                      padding: '12px',
                      textAlign: 'right',
                      fontWeight: '600',
                      color: signal.hour_pct_change >= 0 ? colors.success : colors.danger
                    }}>
                      {signal.hour_pct_change >= 0 ? '+' : ''}{signal.hour_pct_change?.toFixed(3)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary Stats */}
      {summary?.data_summary && (
        <div style={{
          marginTop: '20px',
          padding: '16px',
          background: colors.bg,
          borderRadius: '12px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '16px'
        }}>
          <StatCard
            label="Total Records"
            value={summary.data_summary.total_records?.toLocaleString()}
            colors={colors}
          />
          <StatCard
            label="Aligned Signals"
            value={summary.data_summary.aligned_signals?.toLocaleString()}
            colors={colors}
          />
          <StatCard
            label="UP Rate"
            value={`${summary.data_summary.up_down_split?.up_pct?.toFixed(1)}%`}
            colors={colors}
            highlight={true}
          />
          <StatCard
            label="Date Range"
            value={summary.data_summary.date_range}
            colors={colors}
            small={true}
          />
          <StatCard
            label="Symbols"
            value={summary.data_summary.unique_symbols}
            colors={colors}
          />
        </div>
      )}

      {/* Hypothesis Validation */}
      {summary?.hypothesis?.validated && (
        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          background: `${colors.success}11`,
          borderRadius: '8px',
          border: `1px solid ${colors.success}44`,
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <CheckCircle size={20} color={colors.success} />
          <div>
            <div style={{ color: colors.success, fontWeight: '600', fontSize: '13px' }}>
              Hypothesis Validated
            </div>
            <div style={{ color: colors.textSecondary, fontSize: '12px' }}>
              {summary.hypothesis.evidence}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Score Bar Component
function ScoreBar({ score, max, color }) {
  const pct = Math.min((score / max) * 100, 100);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
      <div style={{
        width: '40px',
        height: '6px',
        background: '#374151',
        borderRadius: '3px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${pct}%`,
          height: '100%',
          background: color,
          borderRadius: '3px'
        }} />
      </div>
      <span style={{ fontSize: '11px', color: '#9ca3af', minWidth: '24px' }}>
        {typeof score === 'number' ? score.toFixed(1) : score}
      </span>
    </div>
  );
}

// Stat Card Component
function StatCard({ label, value, colors, highlight = false, small = false }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        color: colors.textSecondary,
        fontSize: '11px',
        marginBottom: '4px',
        textTransform: 'uppercase'
      }}>
        {label}
      </div>
      <div style={{
        color: highlight ? colors.success : colors.text,
        fontSize: small ? '13px' : '18px',
        fontWeight: '600'
      }}>
        {value}
      </div>
    </div>
  );
}
