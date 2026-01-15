import React, { useState, useEffect } from 'react';
import {
  Bell, Plus, Trash2, CheckCircle, AlertCircle, TrendingUp, TrendingDown,
  Target, Activity, Mail, MessageSquare, Smartphone, Volume2
} from 'lucide-react';

const PriceAlerts = ({ marketType = 'crypto' }) => {
  const [alerts, setAlerts] = useState([
    {
      id: 1,
      symbol: 'BTCUSD',
      type: 'price_above',
      value: 95000,
      currentPrice: 93420,
      status: 'active',
      channel: 'email',
      created: new Date('2025-11-10'),
    },
    {
      id: 2,
      symbol: 'ETHUSD',
      type: 'price_below',
      value: 3200,
      currentPrice: 3356,
      status: 'active',
      channel: 'sms',
      created: new Date('2025-11-10'),
    },
    {
      id: 3,
      symbol: 'SOLUSD',
      type: 'percent_change',
      value: 5,
      currentPrice: 201.45,
      status: 'triggered',
      channel: 'push',
      created: new Date('2025-11-09'),
      triggered: new Date('2025-11-11'),
    },
  ]);

  const [showAddAlert, setShowAddAlert] = useState(false);
  const [newAlert, setNewAlert] = useState({
    symbol: '',
    type: 'price_above',
    value: '',
    channel: 'email'
  });

  const alertTypes = [
    { id: 'price_above', label: 'Price Above', icon: TrendingUp, color: '#10b981' },
    { id: 'price_below', label: 'Price Below', icon: TrendingDown, color: '#ef4444' },
    { id: 'percent_change', label: '% Change', icon: Activity, color: '#3b82f6' },
    { id: 'indicator_cross', label: 'Indicator Cross', icon: Target, color: '#f59e0b' },
  ];

  const channels = [
    { id: 'email', label: 'Email', icon: Mail },
    { id: 'sms', label: 'SMS', icon: MessageSquare },
    { id: 'push', label: 'Push', icon: Smartphone },
    { id: 'sound', label: 'Sound', icon: Volume2 },
  ];

  const handleAddAlert = () => {
    if (!newAlert.symbol || !newAlert.value) return;

    const alert = {
      id: Date.now(),
      ...newAlert,
      value: parseFloat(newAlert.value),
      currentPrice: Math.random() * 10000, // Mock current price
      status: 'active',
      created: new Date(),
    };

    setAlerts([alert, ...alerts]);
    setNewAlert({ symbol: '', type: 'price_above', value: '', channel: 'email' });
    setShowAddAlert(false);
  };

  const handleDeleteAlert = (id) => {
    setAlerts(alerts.filter(a => a.id !== id));
  };

  const getAlertProgress = (alert) => {
    if (alert.type === 'price_above') {
      return Math.min(100, (alert.currentPrice / alert.value) * 100);
    } else if (alert.type === 'price_below') {
      return Math.min(100, (alert.value / alert.currentPrice) * 100);
    }
    return 50;
  };

  const activeAlerts = alerts.filter(a => a.status === 'active');
  const triggeredAlerts = alerts.filter(a => a.status === 'triggered');

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
            <Bell size={36} color="#10b981" />
            Price Alerts
          </h1>
          <p style={{
            margin: '8px 0 0 0',
            color: '#94a3b8',
            fontSize: '16px'
          }}>
            {activeAlerts.length} active alerts • {triggeredAlerts.length} triggered
          </p>
        </div>

        <button
          onClick={() => setShowAddAlert(!showAddAlert)}
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
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 6px 16px rgba(59, 130, 246, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.4)';
          }}
        >
          <Plus size={20} />
          Create Alert
        </button>
      </div>

      {/* Add Alert Form */}
      {showAddAlert && (
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          padding: '24px',
          borderRadius: '12px',
          marginBottom: '24px',
          border: '1px solid #334155',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
        }}>
          <h3 style={{ color: 'white', marginTop: 0 }}>Create New Alert</h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px',
            marginTop: '15px'
          }}>
            {/* Symbol Input */}
            <div>
              <label style={{ color: '#94a3b8', fontSize: '14px', display: 'block', marginBottom: '8px' }}>
                Symbol
              </label>
              <input
                type="text"
                placeholder="e.g., BTCUSD, AAPL"
                value={newAlert.symbol}
                onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value.toUpperCase() })}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: 'white',
                  fontSize: '14px'
                }}
              />
            </div>

            {/* Alert Type */}
            <div>
              <label style={{ color: '#94a3b8', fontSize: '14px', display: 'block', marginBottom: '8px' }}>
                Alert Type
              </label>
              <select
                value={newAlert.type}
                onChange={(e) => setNewAlert({ ...newAlert, type: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: 'white',
                  fontSize: '14px'
                }}
              >
                {alertTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.label}</option>
                ))}
              </select>
            </div>

            {/* Value Input */}
            <div>
              <label style={{ color: '#94a3b8', fontSize: '14px', display: 'block', marginBottom: '8px' }}>
                Trigger Value
              </label>
              <input
                type="number"
                placeholder="Enter value"
                value={newAlert.value}
                onChange={(e) => setNewAlert({ ...newAlert, value: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: 'white',
                  fontSize: '14px'
                }}
              />
            </div>

            {/* Channel */}
            <div>
              <label style={{ color: '#94a3b8', fontSize: '14px', display: 'block', marginBottom: '8px' }}>
                Notification
              </label>
              <select
                value={newAlert.channel}
                onChange={(e) => setNewAlert({ ...newAlert, channel: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: 'white',
                  fontSize: '14px'
                }}
              >
                {channels.map(ch => (
                  <option key={ch.id} value={ch.id}>{ch.label}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleAddAlert}
            style={{
              marginTop: '15px',
              padding: '10px 20px',
              background: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold'
            }}
          >
            Add Alert
          </button>
        </div>
      )}

      {/* Active Alerts */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ color: 'white', fontSize: '20px', marginBottom: '15px' }}>
          Active Alerts ({activeAlerts.length})
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '15px'
        }}>
          {activeAlerts.map(alert => {
            const alertType = alertTypes.find(t => t.id === alert.type);
            const channel = channels.find(c => c.id === alert.channel);
            const progress = getAlertProgress(alert);

            return (
              <div key={alert.id} style={{
                background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                padding: '20px',
                borderRadius: '12px',
                border: '1px solid #334155',
                position: 'relative'
              }}>
                {/* Alert Icon & Symbol */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {alertType && <alertType.icon size={24} color={alertType.color} />}
                    <div>
                      <div style={{ color: 'white', fontSize: '18px', fontWeight: 'bold' }}>
                        {alert.symbol}
                      </div>
                      <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                        {alertType?.label}
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleDeleteAlert(alert.id)}
                    style={{
                      background: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      padding: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>

                {/* Target & Current Price */}
                <div style={{
                  background: '#0f172a',
                  padding: '12px',
                  borderRadius: '8px',
                  marginBottom: '12px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ color: '#94a3b8', fontSize: '12px' }}>Target</span>
                    <span style={{ color: alertType?.color, fontSize: '14px', fontWeight: 'bold' }}>
                      ${alert.value.toLocaleString()}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#94a3b8', fontSize: '12px' }}>Current</span>
                    <span style={{ color: 'white', fontSize: '14px', fontWeight: 'bold' }}>
                      ${alert.currentPrice.toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div style={{
                  width: '100%',
                  height: '6px',
                  background: '#0f172a',
                  borderRadius: '3px',
                  overflow: 'hidden',
                  marginBottom: '12px'
                }}>
                  <div style={{
                    width: `${progress}%`,
                    height: '100%',
                    background: alertType?.color,
                    transition: 'width 0.3s'
                  }} />
                </div>

                {/* Channel & Date */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#94a3b8', fontSize: '12px' }}>
                    {channel && <channel.icon size={14} />}
                    {channel?.label}
                  </div>
                  <div style={{ color: '#94a3b8', fontSize: '11px' }}>
                    {alert.created.toLocaleDateString()}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Triggered Alerts */}
      {triggeredAlerts.length > 0 && (
        <div>
          <h2 style={{ color: 'white', fontSize: '20px', marginBottom: '15px' }}>
            Recently Triggered ({triggeredAlerts.length})
          </h2>

          <div style={{
            display: 'grid',
            gap: '12px'
          }}>
            {triggeredAlerts.map(alert => (
              <div key={alert.id} style={{
                background: 'linear-gradient(135deg, #065f46 0%, #064e3b 100%)',
                padding: '15px 20px',
                borderRadius: '8px',
                border: '1px solid #10b981',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <CheckCircle size={24} color="#10b981" />
                  <div>
                    <div style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
                      {alert.symbol} - {alertTypes.find(t => t.id === alert.type)?.label}
                    </div>
                    <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                      Triggered at ${alert.value.toLocaleString()} • {alert.triggered?.toLocaleString()}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDeleteAlert(alert.id)}
                  style={{
                    background: 'transparent',
                    color: '#94a3b8',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  Dismiss
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PriceAlerts;
