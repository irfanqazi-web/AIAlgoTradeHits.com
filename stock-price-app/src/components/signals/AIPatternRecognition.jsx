/**
 * AIPatternRecognition Component
 * @version 5.2.0 - Migrated to SSOT architecture
 */
import { useState, useEffect } from 'react'
import { Target, TrendingUp, AlertTriangle, Loader, Eye, Search, Mic, MicOff, Trophy } from 'lucide-react'
import { api } from '@/api'
import { API_CONFIG } from '@/lib/config'

function AIPatternRecognition({ symbol = 'BTCUSD', timeframe = 'daily' }) {
  const [loading, setLoading] = useState(false)
  const [patterns, setPatterns] = useState(null)
  const [error, setError] = useState(null)
  const [selectedProvider, setSelectedProvider] = useState('both')

  // NLP Search State
  const [analysisMode, setAnalysisMode] = useState('nlp_search') // 'nlp_search' or 'pattern_recognition'
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const [stockCount, setStockCount] = useState(0)

  // Voice recognition
  const startVoiceSearch = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice search not supported in this browser')
      return
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setSearchQuery(transcript)
      handleNLPSearch(transcript)
    }
    recognition.onerror = () => setIsListening(false)

    recognition.start()
  }

  const handleNLPSearch = async (query = searchQuery) => {
    if (!query.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/api/analysis/nlp-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          asset_type: 'stocks',
          timeframe: 'daily',
          limit: 100
        })
      })

      const data = await response.json()

      if (data.success && data.results && Array.isArray(data.results)) {
        // Sort by percent_change or close descending
        const ranked = data.results.sort((a, b) =>
          (parseFloat(b.percent_change) || parseFloat(b.close) || 0) -
          (parseFloat(a.percent_change) || parseFloat(a.close) || 0)
        ).map((item, idx) => ({ ...item, rank: idx + 1 }))

        setSearchResults(ranked)
        setStockCount(ranked.length)
      } else if (data.success && data.results?.data) {
        // Fallback if results has data property
        const resultsArray = Array.isArray(data.results.data) ? data.results.data : []
        const ranked = resultsArray.sort((a, b) =>
          (parseFloat(b.percent_change) || 0) - (parseFloat(a.percent_change) || 0)
        ).map((item, idx) => ({ ...item, rank: idx + 1 }))

        setSearchResults(ranked)
        setStockCount(ranked.length)
      } else {
        setError(data.error || data.interpretation || 'Search failed - no results returned')
      }
    } catch (err) {
      setError('Failed to connect to search service: ' + err.message)
    }

    setLoading(false)
  }

  useEffect(() => {
    if (analysisMode === 'pattern_recognition') {
      fetchPatterns()
    }
  }, [symbol, timeframe, selectedProvider, analysisMode])

  const fetchPatterns = async () => {
    setLoading(true)
    setError(null)

    const result = await aiService.getPatternAnalysis(symbol, timeframe, selectedProvider)

    if (result.success) {
      setPatterns(result.data)
    } else {
      setError(result.error)
    }

    setLoading(false)
  }

  // Render NLP Search Results Table
  const renderSearchResults = () => {
    if (!searchResults || searchResults.length === 0) return null

    return (
      <div style={{ marginTop: '20px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px',
          padding: '12px 16px',
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          borderRadius: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Trophy size={20} color="white" />
            <span style={{ color: 'white', fontWeight: 'bold' }}>
              {stockCount} Stocks Found - Ranked by Performance
            </span>
          </div>
        </div>

        <div style={{
          overflowX: 'auto',
          background: '#0f172a',
          borderRadius: '12px',
          border: '1px solid #334155'
        }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '12px'
          }}>
            <thead>
              <tr style={{ background: '#1e293b' }}>
                {['#', 'Symbol', 'Exchange', 'Type', 'Country', 'Open', 'High', 'Low', 'Close',
                  'Hi-Lo', '%Range', 'Volume', 'Prev Close', 'Change', '%Chg', 'Avg Vol',
                  '52W Hi', '52W Lo', 'Name'].map((header, idx) => (
                  <th key={idx} style={{
                    padding: '10px 6px',
                    color: '#10b981',
                    textAlign: idx < 5 ? 'left' : 'right',
                    whiteSpace: 'nowrap',
                    borderBottom: '1px solid #334155',
                    fontSize: '11px',
                    fontWeight: '600'
                  }}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {searchResults.map((stock, idx) => {
                const hiLo = (parseFloat(stock.high) - parseFloat(stock.low)) || 0
                const pctRange = stock.low > 0 ? ((hiLo / parseFloat(stock.low)) * 100).toFixed(2) : '0.00'
                const pctChange = parseFloat(stock.percent_change) || 0
                const changeColor = pctChange >= 0 ? '#10b981' : '#ef4444'

                return (
                  <tr key={idx} style={{
                    borderBottom: '1px solid #1e293b',
                    background: idx % 2 === 0 ? '#0f172a' : '#1e293b'
                  }}>
                    <td style={{ padding: '8px 6px', color: '#f59e0b', fontWeight: 'bold' }}>
                      {stock.rank}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#3b82f6', fontWeight: 'bold' }}>
                      {stock.symbol}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#9ca3af' }}>{stock.exchange}</td>
                    <td style={{ padding: '8px 6px', color: '#9ca3af', fontSize: '10px' }}>
                      {stock.type?.substring(0, 6)}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#9ca3af', fontSize: '10px' }}>US</td>
                    <td style={{ padding: '8px 6px', color: 'white', textAlign: 'right' }}>
                      {parseFloat(stock.open)?.toFixed(2) || '-'}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#10b981', textAlign: 'right' }}>
                      {parseFloat(stock.high)?.toFixed(2) || '-'}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#ef4444', textAlign: 'right' }}>
                      {parseFloat(stock.low)?.toFixed(2) || '-'}
                    </td>
                    <td style={{ padding: '8px 6px', color: 'white', textAlign: 'right', fontWeight: 'bold' }}>
                      {parseFloat(stock.close)?.toFixed(2) || '-'}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#f59e0b', textAlign: 'right' }}>
                      {hiLo.toFixed(2)}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#a855f7', textAlign: 'right' }}>
                      {pctRange}%
                    </td>
                    <td style={{ padding: '8px 6px', color: 'white', textAlign: 'right' }}>
                      {parseInt(stock.volume)?.toLocaleString() || '-'}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#9ca3af', textAlign: 'right' }}>
                      {parseFloat(stock.previous_close)?.toFixed(2) || '-'}
                    </td>
                    <td style={{ padding: '8px 6px', color: changeColor, textAlign: 'right' }}>
                      {parseFloat(stock.change)?.toFixed(2) || '0.00'}
                    </td>
                    <td style={{
                      padding: '8px 6px',
                      color: changeColor,
                      textAlign: 'right',
                      fontWeight: 'bold'
                    }}>
                      {pctChange.toFixed(2)}%
                    </td>
                    <td style={{ padding: '8px 6px', color: '#9ca3af', textAlign: 'right' }}>
                      {parseInt(stock.average_volume)?.toLocaleString() || '-'}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#10b981', textAlign: 'right' }}>
                      {parseFloat(stock.week_52_high)?.toFixed(2) || '-'}
                    </td>
                    <td style={{ padding: '8px 6px', color: '#ef4444', textAlign: 'right' }}>
                      {parseFloat(stock.week_52_low)?.toFixed(2) || '-'}
                    </td>
                    <td style={{
                      padding: '8px 6px',
                      color: 'white',
                      maxWidth: '150px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {stock.name}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  const renderPatternCard = (providerName, pattern) => {
    if (!pattern) return null

    return (
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
          <Target size={24} style={{ color: '#10b981', marginRight: '12px' }} />
          <h3 style={{ color: 'white', margin: 0 }}>
            {providerName === 'claude' ? 'Claude Pattern Analysis' : 'Vertex AI Pattern Analysis'}
          </h3>
        </div>

        {pattern.detected && pattern.detected.length > 0 && (
          <div style={{ marginBottom: '24px' }}>
            <h4 style={{ color: '#10b981', marginBottom: '16px', fontSize: '16px' }}>
              Detected Chart Patterns
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
              {pattern.detected.map((patternName, idx) => (
                <div key={idx} style={{
                  background: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid #10b981',
                  borderRadius: '8px',
                  padding: '12px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '24px', marginBottom: '8px' }}>
                    {getPatternEmoji(patternName)}
                  </div>
                  <div style={{ color: 'white', fontSize: '14px', fontWeight: '600' }}>
                    {formatPatternName(patternName)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
          <div style={{
            background: 'rgba(16, 185, 129, 0.1)',
            borderRadius: '12px',
            padding: '16px',
            border: '1px solid #10b981'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
              <TrendingUp size={20} style={{ color: '#10b981', marginRight: '8px' }} />
              <h4 style={{ color: '#10b981', margin: 0 }}>Support Levels</h4>
            </div>
            {pattern.supportLevels && pattern.supportLevels.length > 0 ? (
              <div>
                {pattern.supportLevels.map((level, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    background: 'rgba(15, 23, 42, 0.5)',
                    borderRadius: '6px',
                    marginBottom: '8px'
                  }}>
                    <span style={{ color: '#9ca3af', fontSize: '14px' }}>Level {idx + 1}</span>
                    <span style={{ color: '#10b981', fontSize: '14px', fontWeight: 'bold' }}>
                      ${parseFloat(level).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: '#9ca3af', fontSize: '14px' }}>No support levels detected</div>
            )}
          </div>

          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            borderRadius: '12px',
            padding: '16px',
            border: '1px solid #ef4444'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
              <TrendingUp size={20} style={{ color: '#ef4444', marginRight: '8px', transform: 'rotate(180deg)' }} />
              <h4 style={{ color: '#ef4444', margin: 0 }}>Resistance Levels</h4>
            </div>
            {pattern.resistanceLevels && pattern.resistanceLevels.length > 0 ? (
              <div>
                {pattern.resistanceLevels.map((level, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    background: 'rgba(15, 23, 42, 0.5)',
                    borderRadius: '6px',
                    marginBottom: '8px'
                  }}>
                    <span style={{ color: '#9ca3af', fontSize: '14px' }}>Level {idx + 1}</span>
                    <span style={{ color: '#ef4444', fontSize: '14px', fontWeight: 'bold' }}>
                      ${parseFloat(level).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: '#9ca3af', fontSize: '14px' }}>No resistance levels detected</div>
            )}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '20px' }}>
          <MetricCard title="Pattern Reliability" value={pattern.reliability || 'N/A'} suffix="%" color="#10b981" />
          <MetricCard title="Breakout Probability" value={pattern.breakoutProbability || 'N/A'} suffix="%" color="#f59e0b" />
          <MetricCard title="Recommended Action" value={pattern.recommendedAction || 'N/A'} color="#3b82f6" isText={true} />
        </div>

        <div style={{
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid #3b82f6',
          borderRadius: '12px',
          padding: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
            <Eye size={20} style={{ color: '#3b82f6', marginRight: '8px' }} />
            <h4 style={{ color: '#3b82f6', margin: 0 }}>Current Price Position</h4>
          </div>
          <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
            ${patterns?.currentPrice?.toFixed(2)}
          </div>
          <div style={{ color: '#9ca3af', fontSize: '14px', marginTop: '8px' }}>
            Price is positioned {calculatePricePosition(patterns?.currentPrice, pattern.supportLevels, pattern.resistanceLevels)}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', maxWidth: '100%', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ color: 'white', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Target size={32} style={{ color: '#10b981' }} />
          AI Stock Analysis
        </h2>
        <p style={{ color: '#9ca3af', margin: 0 }}>
          Powered by Gemini 2.5 - NLP Search & Pattern Recognition
        </p>
      </div>

      {/* Mode Selector - NLP Search is FIRST */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '24px',
        padding: '8px',
        background: '#1e293b',
        borderRadius: '12px',
        width: 'fit-content'
      }}>
        <button
          onClick={() => setAnalysisMode('nlp_search')}
          style={{
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            background: analysisMode === 'nlp_search'
              ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
              : 'transparent',
            color: 'white',
            cursor: 'pointer',
            fontWeight: analysisMode === 'nlp_search' ? '600' : '400',
            transition: 'all 0.3s',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Search size={18} />
          NLP Stock Search
        </button>
        <button
          onClick={() => setAnalysisMode('pattern_recognition')}
          style={{
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            background: analysisMode === 'pattern_recognition'
              ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
              : 'transparent',
            color: 'white',
            cursor: 'pointer',
            fontWeight: analysisMode === 'pattern_recognition' ? '600' : '400',
            transition: 'all 0.3s',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Target size={18} />
          Pattern Recognition
        </button>
      </div>

      {/* NLP Search Mode */}
      {analysisMode === 'nlp_search' && (
        <div>
          {/* Search Input */}
          <div style={{
            display: 'flex',
            gap: '12px',
            marginBottom: '24px',
            alignItems: 'center'
          }}>
            <div style={{
              flex: 1,
              position: 'relative'
            }}>
              <Search size={20} style={{
                position: 'absolute',
                left: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#9ca3af'
              }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleNLPSearch()}
                placeholder="Ask anything... e.g., 'Show me tech stocks with high volume' or 'Find stocks near 52-week high'"
                style={{
                  width: '100%',
                  padding: '16px 16px 16px 48px',
                  borderRadius: '12px',
                  border: '2px solid #334155',
                  background: '#1e293b',
                  color: 'white',
                  fontSize: '16px',
                  outline: 'none'
                }}
              />
            </div>

            <button
              onClick={() => handleNLPSearch()}
              disabled={loading}
              style={{
                padding: '16px 32px',
                borderRadius: '12px',
                border: 'none',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                fontSize: '16px',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              {loading ? <Loader size={20} className="spin" /> : <Search size={20} />}
              Search
            </button>

            <button
              onClick={startVoiceSearch}
              disabled={isListening}
              style={{
                padding: '16px',
                borderRadius: '12px',
                border: '2px solid #334155',
                background: isListening ? '#ef4444' : '#1e293b',
                color: 'white',
                cursor: 'pointer'
              }}
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
          </div>

          {/* Quick Search Suggestions */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
            {[
              'Top gainers today',
              'High volume stocks',
              'Stocks near 52-week high',
              'NASDAQ stocks over $100',
              'NYSE blue chips'
            ].map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setSearchQuery(suggestion)
                  handleNLPSearch(suggestion)
                }}
                style={{
                  padding: '8px 16px',
                  borderRadius: '20px',
                  border: '1px solid #334155',
                  background: '#1e293b',
                  color: '#9ca3af',
                  fontSize: '13px',
                  cursor: 'pointer'
                }}
              >
                {suggestion}
              </button>
            ))}
          </div>

          {/* Error */}
          {error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid #ef4444',
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <AlertTriangle size={24} color="#ef4444" />
              <span style={{ color: '#ef4444' }}>{error}</span>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              padding: '48px',
              color: 'white'
            }}>
              <Loader size={48} className="spin" style={{ color: '#10b981', marginBottom: '16px' }} />
              <div>Analyzing stocks with Gemini 3 Pro...</div>
            </div>
          )}

          {/* Results */}
          {!loading && renderSearchResults()}
        </div>
      )}

      {/* Pattern Recognition Mode */}
      {analysisMode === 'pattern_recognition' && (
        <div>
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

          {loading && (
            <div style={{
              minHeight: '400px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white'
            }}>
              <Loader size={48} className="spin" style={{ color: '#10b981', marginBottom: '16px' }} />
              <div>Analyzing patterns with AI...</div>
            </div>
          )}

          {error && (
            <div style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              borderRadius: '16px',
              padding: '32px',
              border: '1px solid #334155',
              textAlign: 'center'
            }}>
              <AlertTriangle size={48} style={{ color: '#ef4444', marginBottom: '16px' }} />
              <h3 style={{ color: 'white', marginBottom: '8px' }}>Error Loading Pattern Analysis</h3>
              <p style={{ color: '#9ca3af', marginBottom: '20px' }}>{error}</p>
              <button
                onClick={fetchPatterns}
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
          )}

          {!loading && !error && (
            <>
              {patterns?.patterns?.claude && renderPatternCard('claude', patterns.patterns.claude)}
              {patterns?.patterns?.vertex && renderPatternCard('vertex', patterns.patterns.vertex)}
            </>
          )}
        </div>
      )}
    </div>
  )
}

function MetricCard({ title, value, suffix = '', color, isText = false }) {
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
      <div style={{ color: color, fontSize: isText ? '16px' : '24px', fontWeight: 'bold' }}>
        {isText ? value?.replace(/_/g, ' ').toUpperCase() : `${value}${suffix}`}
      </div>
    </div>
  )
}

function getPatternEmoji(patternName) {
  const patterns = {
    'head_and_shoulders': '👤',
    'inverse_head_and_shoulders': '🙃',
    'double_top': '⚠️',
    'double_bottom': '✓',
    'triple_top': '🔺',
    'triple_bottom': '🔻',
    'ascending_triangle': '📈',
    'descending_triangle': '📉',
    'symmetrical_triangle': '🔷',
    'bull_flag': '🚩',
    'bear_flag': '⛳',
    'wedge': '⬆️',
    'channel': '📊',
    'cup_and_handle': '☕',
    'rounding_bottom': '🌙'
  }
  return patterns[patternName] || '📊'
}

function formatPatternName(patternName) {
  return patternName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function calculatePricePosition(currentPrice, supportLevels, resistanceLevels) {
  if (!currentPrice || !supportLevels || !resistanceLevels) {
    return 'between key levels'
  }

  const nearestSupport = supportLevels.reduce((prev, curr) =>
    Math.abs(curr - currentPrice) < Math.abs(prev - currentPrice) ? curr : prev
  , supportLevels[0])

  const nearestResistance = resistanceLevels.reduce((prev, curr) =>
    Math.abs(curr - currentPrice) < Math.abs(prev - currentPrice) ? curr : prev
  , resistanceLevels[0])

  const distToSupport = ((currentPrice - nearestSupport) / nearestSupport * 100).toFixed(2)
  const distToResistance = ((nearestResistance - currentPrice) / currentPrice * 100).toFixed(2)

  return `${distToSupport}% above nearest support, ${distToResistance}% below nearest resistance`
}

export default AIPatternRecognition

