/**
 * AIPredictions Component
 * @version 5.2.0 - Migrated to SSOT architecture
 */
import { useState, useEffect } from 'react'
import { Brain, TrendingUp, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import { api } from '@/api'

// Helper functions (migrated from legacy aiService)
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

const getTrendIndicator = (trend) => {
  const trends = {
    'BULLISH': { color: '#10b981', emoji: '📈', label: 'Bullish' },
    'BEARISH': { color: '#ef4444', emoji: '📉', label: 'Bearish' },
    'NEUTRAL': { color: '#f59e0b', emoji: '➡️', label: 'Neutral' }
  }
  return trends[trend] || { color: '#6b7280', emoji: '❓', label: trend }
}

function AIPredictions({ symbol = 'BTCUSD', timeframe = 'daily' }) {
  const [loading, setLoading] = useState(false)
  const [predictions, setPredictions] = useState(null)
  const [error, setError] = useState(null)
  const [selectedProvider, setSelectedProvider] = useState('both')

  useEffect(() => {
    fetchPredictions()
  }, [symbol, timeframe, selectedProvider])

  const fetchPredictions = async () => {
    setLoading(true)
    setError(null)

    const result = await api.ai.getMLPredictions({ symbol, timeframe, provider: selectedProvider })

    if (result.success) {
      setPredictions(result.data)
    } else {
      setError(result.error)
    }

    setLoading(false)
  }

  const formatPrice = (price) => {
    if (!price) return 'N/A'
    return `$${parseFloat(price).toFixed(2)}`
  }

  const calculatePriceChange = (current, predicted) => {
    if (!current || !predicted) return 0
    return ((predicted - current) / current * 100).toFixed(2)
  }

  const renderPredictionCard = (providerName, prediction) => {
    if (!prediction) return null

    const trend = getTrendIndicator(prediction.trend)
    const signal = getSignalStrength(prediction.recommendation)

    return (
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
          <Brain size={24} style={{ color: '#10b981', marginRight: '12px' }} />
          <h3 style={{ color: 'white', margin: 0 }}>
            {providerName === 'claude' ? 'Claude Analysis' : 'Vertex AI Analysis'}
          </h3>
        </div>

        {/* Current Price and Trend */}
        <div style={{
          background: 'rgba(16, 185, 129, 0.1)',
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '16px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ color: '#9ca3af', fontSize: '14px', marginBottom: '4px' }}>
                Current Price
              </div>
              <div style={{ color: 'white', fontSize: '28px', fontWeight: 'bold' }}>
                {formatPrice(predictions.currentPrice)}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '8px',
                background: trend.color + '20',
                border: `1px solid ${trend.color}`
              }}>
                <span style={{ fontSize: '24px' }}>{trend.emoji}</span>
                <span style={{ color: trend.color, fontWeight: 'bold', fontSize: '16px' }}>
                  {trend.label}
                </span>
                <span style={{ fontSize: '20px' }}>{trend.direction}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Price Predictions */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '20px' }}>
          <PredictionBox
            title="1 Hour"
            current={predictions.currentPrice}
            predicted={prediction.prediction_1h}
          />
          <PredictionBox
            title="24 Hours"
            current={predictions.currentPrice}
            predicted={prediction.prediction_24h}
          />
          <PredictionBox
            title="7 Days"
            current={predictions.currentPrice}
            predicted={prediction.prediction_7d}
          />
        </div>

        {/* Trading Signal */}
        <div style={{
          background: signal.color + '20',
          border: `2px solid ${signal.color}`,
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ color: '#9ca3af', fontSize: '14px', marginBottom: '4px' }}>
                AI Recommendation
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '32px' }}>{signal.emoji}</span>
                <span style={{ color: signal.color, fontSize: '24px', fontWeight: 'bold' }}>
                  {signal.label}
                </span>
              </div>
            </div>
            <div style={{
              width: '120px',
              height: '120px',
              borderRadius: '50%',
              border: `8px solid ${signal.color}`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              background: '#0a0e27'
            }}>
              <div style={{ color: signal.color, fontSize: '32px', fontWeight: 'bold' }}>
                {prediction.confidence}%
              </div>
              <div style={{ color: '#9ca3af', fontSize: '12px' }}>Confidence</div>
            </div>
          </div>
        </div>

        {/* Key Factors */}
        {prediction.keyFactors && prediction.keyFactors.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            <h4 style={{ color: '#10b981', marginBottom: '12px', fontSize: '14px' }}>
              Key Factors
            </h4>
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              {prediction.keyFactors.map((factor, idx) => (
                <li key={idx} style={{ color: '#d1d5db', marginBottom: '8px', fontSize: '14px' }}>
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risk Level */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px',
          borderRadius: '8px',
          background: getRiskColor(prediction.riskLevel) + '20',
          border: `1px solid ${getRiskColor(prediction.riskLevel)}`
        }}>
          <AlertCircle size={20} style={{ color: getRiskColor(prediction.riskLevel) }} />
          <span style={{ color: getRiskColor(prediction.riskLevel), fontWeight: '600' }}>
            Risk Level: {prediction.riskLevel?.toUpperCase()}
          </span>
        </div>
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
        <div>Loading AI predictions...</div>
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
        <AlertCircle size={48} style={{ color: '#ef4444', marginBottom: '16px' }} />
        <h3 style={{ color: 'white', marginBottom: '8px' }}>Error Loading Predictions</h3>
        <p style={{ color: '#9ca3af', marginBottom: '20px' }}>{error}</p>
        <button
          onClick={fetchPredictions}
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
          <Brain size={32} style={{ color: '#10b981' }} />
          AI Price Predictions - {symbol}
        </h2>
        <p style={{ color: '#9ca3af', margin: 0 }}>
          Advanced machine learning predictions powered by Claude and Vertex AI
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

      {/* Predictions */}
      {predictions?.predictions?.claude && renderPredictionCard('claude', predictions.predictions.claude)}
      {predictions?.predictions?.vertex && renderPredictionCard('vertex', predictions.predictions.vertex)}

      {/* AI Prediction Text (from Gemini/Vertex AI) */}
      {predictions?.prediction && (
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
            <Brain size={24} style={{ color: '#10b981', marginRight: '12px' }} />
            <h3 style={{ color: 'white', margin: 0 }}>
              Gemini AI Analysis
            </h3>
          </div>
          <div style={{
            background: 'rgba(16, 185, 129, 0.1)',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '16px'
          }}>
            <pre style={{
              color: '#d1d5db',
              fontSize: '14px',
              lineHeight: '1.8',
              whiteSpace: 'pre-wrap',
              fontFamily: 'inherit',
              margin: 0
            }}>
              {predictions.prediction}
            </pre>
          </div>
          {predictions.disclaimer && (
            <div style={{
              background: 'rgba(245, 158, 11, 0.1)',
              border: '1px solid #f59e0b',
              borderRadius: '8px',
              padding: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <AlertCircle size={16} style={{ color: '#f59e0b' }} />
              <span style={{ color: '#f59e0b', fontSize: '12px' }}>{predictions.disclaimer}</span>
            </div>
          )}
        </div>
      )}

      {/* Consensus */}
      {predictions?.consensus && (
        <div style={{
          background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '2px solid #a78bfa'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
            <CheckCircle size={24} style={{ color: 'white', marginRight: '12px' }} />
            <h3 style={{ color: 'white', margin: 0 }}>AI Consensus</h3>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div>
              <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: '14px', marginBottom: '4px' }}>
                Agreement Status
              </div>
              <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
                {predictions.consensus.providers_agree ? '✓ AI Models Agree' : '⚠ Mixed Signals'}
              </div>
            </div>
            <div style={{ borderLeft: '2px solid rgba(255,255,255,0.3)', paddingLeft: '20px' }}>
              <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: '14px', marginBottom: '4px' }}>
                Consensus Recommendation
              </div>
              <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
                {predictions.consensus.recommendation?.toUpperCase()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function PredictionBox({ title, current, predicted }) {
  const change = ((predicted - current) / current * 100).toFixed(2)
  const isPositive = change >= 0

  return (
    <div style={{
      background: 'rgba(15, 23, 42, 0.5)',
      borderRadius: '12px',
      padding: '16px',
      border: '1px solid #334155'
    }}>
      <div style={{ color: '#9ca3af', fontSize: '12px', marginBottom: '8px' }}>
        {title}
      </div>
      <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', marginBottom: '4px' }}>
        ${parseFloat(predicted).toFixed(2)}
      </div>
      <div style={{
        color: isPositive ? '#10b981' : '#ef4444',
        fontSize: '14px',
        fontWeight: '600'
      }}>
        {isPositive ? '↗' : '↘'} {Math.abs(change)}%
      </div>
    </div>
  )
}

function getRiskColor(riskLevel) {
  const colors = {
    'low': '#10b981',
    'medium': '#f59e0b',
    'high': '#ef4444'
  }
  return colors[riskLevel?.toLowerCase()] || '#f59e0b'
}

export default AIPredictions
