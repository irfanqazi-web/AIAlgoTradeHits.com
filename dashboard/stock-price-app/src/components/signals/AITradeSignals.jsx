/**
 * AITradeSignals Component
 * @version 5.2.0 - Migrated to SSOT architecture
 */
import { useState, useEffect } from 'react'
import { Zap, Target, TrendingUp, TrendingDown, DollarSign, AlertTriangle, Loader } from 'lucide-react'
import { api } from '@/api'

// Signal strength helper (migrated from legacy aiService)
const getSignalStrength = (signal) => {
  const signals = {
    'STRONG_BUY': { color: '#10b981', emoji: '🚀', label: 'Strong Buy' },
    'BUY': { color: '#34d399', emoji: '📈', label: 'Buy' },
    'HOLD': { color: '#f59e0b', emoji: '⏸️', label: 'Hold' },
    'SELL': { color: '#f87171', emoji: '📉', label: 'Sell' },
    'STRONG_SELL': { color: '#ef4444', emoji: '🔻', label: 'Strong Sell' }
  }
  return signals[signal] || { color: '#6b7280', emoji: '❓', label: signal }
}

function AITradeSignals({ symbol = 'BTCUSD', timeframe = 'daily' }) {
  const [loading, setLoading] = useState(false)
  const [signals, setSignals] = useState(null)
  const [error, setError] = useState(null)
  const [selectedProvider, setSelectedProvider] = useState('both')

  useEffect(() => {
    fetchSignals()
  }, [symbol, timeframe, selectedProvider])

  const fetchSignals = async () => {
    setLoading(true)
    setError(null)

    const result = await api.ai.getTradingSignals({ symbol, timeframe, provider: selectedProvider })

    if (result.success) {
      setSignals(result.data)
    } else {
      setError(result.error)
    }

    setLoading(false)
  }

  const renderSignalCard = (providerName, signal) => {
    if (!signal) return null

    const signalInfo = getSignalStrength(signal.signal)

    return (
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
          <Zap size={24} style={{ color: '#10b981', marginRight: '12px' }} />
          <h3 style={{ color: 'white', margin: 0 }}>
            {providerName === 'claude' ? 'Claude Trading Signal' : 'Vertex AI Trading Signal'}
          </h3>
        </div>

        {/* Main Signal */}
        <div style={{
          background: `linear-gradient(135deg, ${signalInfo.color}20 0%, ${signalInfo.color}10 100%)`,
          border: `2px solid ${signalInfo.color}`,
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '12px' }}>
            {signalInfo.emoji}
          </div>
          <div style={{ color: signalInfo.color, fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
            {signalInfo.label}
          </div>
          <div style={{ color: '#9ca3af', fontSize: '14px' }}>
            AI-Generated Trading Signal
          </div>
        </div>

        {/* Entry and Exit Strategy */}
        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ color: '#10b981', marginBottom: '16px', fontSize: '16px', display: 'flex', alignItems: 'center' }}>
            <Target size={20} style={{ marginRight: '8px' }} />
            Entry & Exit Strategy
          </h4>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '16px' }}>
            {/* Entry Price */}
            <div style={{
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid #3b82f6',
              borderRadius: '12px',
              padding: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                <TrendingUp size={18} style={{ color: '#3b82f6', marginRight: '8px' }} />
                <span style={{ color: '#9ca3af', fontSize: '14px' }}>Entry Price</span>
              </div>
              <div style={{ color: '#3b82f6', fontSize: '24px', fontWeight: 'bold' }}>
                ${parseFloat(signal.entryPrice || signals.currentPrice).toFixed(2)}
              </div>
            </div>

            {/* Stop Loss */}
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid #ef4444',
              borderRadius: '12px',
              padding: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                <AlertTriangle size={18} style={{ color: '#ef4444', marginRight: '8px' }} />
                <span style={{ color: '#9ca3af', fontSize: '14px' }}>Stop Loss</span>
              </div>
              <div style={{ color: '#ef4444', fontSize: '24px', fontWeight: 'bold' }}>
                ${parseFloat(signal.stopLoss).toFixed(2)}
              </div>
            </div>
          </div>

          {/* Target Prices */}
          {signal.targetPrices && signal.targetPrices.length > 0 && (
            <div>
              <div style={{ color: '#10b981', fontSize: '14px', marginBottom: '12px', fontWeight: '600' }}>
                🎯 Target Prices
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                {signal.targetPrices.map((target, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(16, 185, 129, 0.1)',
                      border: '1px solid #10b981',
                      borderRadius: '8px',
                      padding: '12px',
                      textAlign: 'center'
                    }}
                  >
                    <div style={{ color: '#9ca3af', fontSize: '12px', marginBottom: '4px' }}>
                      Target {idx + 1}
                    </div>
                    <div style={{ color: '#10b981', fontSize: '18px', fontWeight: 'bold' }}>
                      ${parseFloat(target).toFixed(2)}
                    </div>
                    <div style={{ color: '#10b981', fontSize: '12px', marginTop: '4px' }}>
                      +{((target - (signal.entryPrice || signals.currentPrice)) / (signal.entryPrice || signals.currentPrice) * 100).toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Risk/Reward Analysis */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginBottom: '20px' }}>
          <div style={{
            background: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid #f59e0b',
            borderRadius: '12px',
            padding: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <DollarSign size={18} style={{ color: '#f59e0b', marginRight: '8px' }} />
              <span style={{ color: '#9ca3af', fontSize: '14px' }}>Risk/Reward Ratio</span>
            </div>
            <div style={{ color: '#f59e0b', fontSize: '28px', fontWeight: 'bold' }}>
              {signal.riskRewardRatio ? `1:${parseFloat(signal.riskRewardRatio).toFixed(2)}` : 'N/A'}
            </div>
          </div>

          <div style={{
            background: 'rgba(139, 92, 246, 0.1)',
            border: '1px solid #8b5cf6',
            borderRadius: '12px',
            padding: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <Target size={18} style={{ color: '#8b5cf6', marginRight: '8px' }} />
              <span style={{ color: '#9ca3af', fontSize: '14px' }}>Timeframe</span>
            </div>
            <div style={{ color: '#8b5cf6', fontSize: '20px', fontWeight: 'bold' }}>
              {signal.timeframe || 'Medium-term'}
            </div>
          </div>
        </div>

        {/* AI Reasoning */}
        {signal.reasoning && (
          <div style={{
            background: 'rgba(15, 23, 42, 0.5)',
            borderRadius: '12px',
            padding: '16px',
            border: '1px solid #334155'
          }}>
            <h4 style={{ color: '#10b981', marginBottom: '12px', fontSize: '14px' }}>
              💡 AI Analysis & Reasoning
            </h4>
            <p style={{ color: '#d1d5db', fontSize: '14px', lineHeight: '1.6', margin: 0 }}>
              {signal.reasoning}
            </p>
          </div>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div style={{
        minHeight: '400px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white'
      }}>
        <Loader size={48} className="spin" style={{ color: '#10b981', marginBottom: '16px' }} />
        <div>Generating AI trading signals...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '32px',
        border: '1px solid #334155',
        textAlign: 'center'
      }}>
        <AlertTriangle size={48} style={{ color: '#ef4444', marginBottom: '16px' }} />
        <h3 style={{ color: 'white', marginBottom: '8px' }}>Error Loading Trading Signals</h3>
        <p style={{ color: '#9ca3af', marginBottom: '20px' }}>{error}</p>
        <button
          onClick={fetchSignals}
          style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ color: 'white', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Zap size={32} style={{ color: '#10b981' }} />
          AI Trade Signals - {symbol}
        </h2>
        <p style={{ color: '#9ca3af', margin: 0 }}>
          AI-generated buy/sell signals with entry, exit, and risk management recommendations
        </p>
      </div>

      {/* Provider Selector */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '24px',
        padding: '8px',
        background: '#1e293b',
        borderRadius: '12px',
        width: 'fit-content'
      }}>
        {['both', 'claude', 'vertex'].map(provider => (
          <button
            key={provider}
            onClick={() => setSelectedProvider(provider)}
            style={{
              padding: '8px 20px',
              borderRadius: '8px',
              border: 'none',
              background: selectedProvider === provider
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : 'transparent',
              color: 'white',
              cursor: 'pointer',
              fontWeight: selectedProvider === provider ? '600' : '400',
              transition: 'all 0.3s'
            }}
          >
            {provider === 'both' ? 'Both AI' : provider === 'claude' ? 'Claude' : 'Vertex AI'}
          </button>
        ))}
      </div>

      {/* Current Price */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '12px',
        padding: '20px',
        border: '1px solid #334155',
        marginBottom: '24px',
        textAlign: 'center'
      }}>
        <div style={{ color: '#9ca3af', fontSize: '14px', marginBottom: '8px' }}>
          Current Market Price
        </div>
        <div style={{ color: 'white', fontSize: '36px', fontWeight: 'bold' }}>
          ${signals?.currentPrice?.toFixed(2)}
        </div>
      </div>

      {/* Trading Signals */}
      {signals?.signals?.claude && renderSignalCard('claude', signals.signals.claude)}
      {signals?.signals?.vertex && renderSignalCard('vertex', signals.signals.vertex)}
      {signals?.signals?.derived && (
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
            <Zap size={24} style={{ color: '#10b981', marginRight: '12px' }} />
            <h3 style={{ color: 'white', margin: 0 }}>Gemini AI Trading Analysis</h3>
          </div>

          {/* Signal Based on RSI */}
          <div style={{
            background: signals.signals.derived.signal === 'buy' ? 'rgba(16, 185, 129, 0.2)' :
                       signals.signals.derived.signal === 'sell' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
            border: `2px solid ${signals.signals.derived.signal === 'buy' ? '#10b981' :
                                  signals.signals.derived.signal === 'sell' ? '#ef4444' : '#f59e0b'}`,
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '8px' }}>
              {signals.signals.derived.signal === 'buy' ? '📈' : signals.signals.derived.signal === 'sell' ? '📉' : '⏸️'}
            </div>
            <div style={{
              color: signals.signals.derived.signal === 'buy' ? '#10b981' :
                     signals.signals.derived.signal === 'sell' ? '#ef4444' : '#f59e0b',
              fontSize: '24px',
              fontWeight: 'bold'
            }}>
              {signals.signals.derived.signal.toUpperCase()}
            </div>
            <div style={{ color: '#9ca3af', marginTop: '8px' }}>
              RSI: {signals.signals.derived.rsi?.toFixed(1) || 'N/A'} | MACD: {signals.signals.derived.macd?.toFixed(2) || 'N/A'}
            </div>
          </div>

          {/* AI Analysis Text */}
          {signals.signals.derived.reasoning && (
            <div style={{
              background: 'rgba(15, 23, 42, 0.5)',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid #334155'
            }}>
              <h4 style={{ color: '#10b981', marginBottom: '12px', fontSize: '14px' }}>
                💡 AI Analysis & Reasoning
              </h4>
              <pre style={{
                color: '#d1d5db',
                fontSize: '14px',
                lineHeight: '1.8',
                whiteSpace: 'pre-wrap',
                fontFamily: 'inherit',
                margin: 0
              }}>
                {signals.signals.derived.reasoning}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Show prediction text directly if available */}
      {signals?.prediction && !signals?.signals?.derived && (
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
            <Zap size={24} style={{ color: '#10b981', marginRight: '12px' }} />
            <h3 style={{ color: 'white', margin: 0 }}>Gemini AI Analysis</h3>
          </div>
          <pre style={{
            color: '#d1d5db',
            fontSize: '14px',
            lineHeight: '1.8',
            whiteSpace: 'pre-wrap',
            fontFamily: 'inherit',
            margin: 0
          }}>
            {signals.prediction}
          </pre>
        </div>
      )}

      {/* Consensus */}
      {signals?.consensus && (
        <div style={{
          background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '2px solid #a78bfa'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            <Zap size={24} style={{ color: 'white', marginRight: '12px' }} />
            <h3 style={{ color: 'white', margin: 0 }}>AI Consensus Signal</h3>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', justifyContent: 'center' }}>
            <div style={{
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '12px',
              padding: '24px',
              minWidth: '200px',
              textAlign: 'center'
            }}>
              <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: '14px', marginBottom: '8px' }}>
                Agreement Status
              </div>
              <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
                {signals.consensus.providers_agree ? '✓ Models Agree' : '⚠ Mixed Signals'}
              </div>
            </div>
            <div style={{
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '12px',
              padding: '24px',
              minWidth: '200px',
              textAlign: 'center'
            }}>
              <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: '14px', marginBottom: '8px' }}>
                Final Recommendation
              </div>
              <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
                {signals.consensus.recommendation?.replace(/_/g, ' ').toUpperCase()}
              </div>
            </div>
            <div style={{
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '12px',
              padding: '24px',
              minWidth: '200px',
              textAlign: 'center'
            }}>
              <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: '14px', marginBottom: '8px' }}>
                Confidence Level
              </div>
              <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
                {signals.consensus.confidence}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div style={{
        marginTop: '24px',
        padding: '16px',
        background: 'rgba(245, 158, 11, 0.1)',
        border: '1px solid #f59e0b',
        borderRadius: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
          <AlertTriangle size={20} style={{ color: '#f59e0b', marginTop: '2px', flexShrink: 0 }} />
          <div>
            <div style={{ color: '#f59e0b', fontWeight: '600', marginBottom: '4px' }}>
              Risk Disclaimer
            </div>
            <div style={{ color: '#d1d5db', fontSize: '14px', lineHeight: '1.5' }}>
              AI-generated signals are for informational purposes only and should not be considered as financial advice.
              Always conduct your own research and consider your risk tolerance before making trading decisions.
              Past performance does not guarantee future results.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AITradeSignals
