import { useState, useEffect, useRef } from 'react';
import { Search, Mic, MicOff, Loader, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { createChart } from 'lightweight-charts';
import { API_BASE_URL } from '../services/api';

export default function NLPSearch({ theme = 'dark' }) {
  const [query, setQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [inputMethod, setInputMethod] = useState('text');

  const recognitionRef = useRef(null);
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);

  // Search suggestions
  const suggestions = [
    "Oversold cryptos",
    "Bitcoin hourly last 24 hours",
    "Top 10 stock gainers",
    "Stocks with bullish MACD",
    "High volume cryptos",
    "AAPL 5-minute",
    "Tesla today",
    "Ethereum vs Bitcoin",
    "Strong trend stocks",
    "Stocks with RSI below 40 and above 200 MA"
  ];

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setQuery(transcript);
        setIsListening(false);
        setInputMethod('voice');
        handleSearch(transcript, 'voice');
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setError(`Voice input error: ${event.error}`);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    // Fetch search history
    fetchSearchHistory();
  }, []);

  const fetchSearchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analysis/nlp-history?session_id=${sessionId}&limit=20`);
      const data = await response.json();

      if (data.success) {
        setSearchHistory(data.history);
      }
    } catch (err) {
      console.error('Error fetching search history:', err);
    }
  };

  const startListening = () => {
    if (recognitionRef.current) {
      setError(null);
      setIsListening(true);
      recognitionRef.current.start();
    } else {
      setError('Speech recognition not supported in this browser');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleSearch = async (searchQuery = query, method = inputMethod) => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults(null);
    setShowSuggestions(false);
    setShowHistory(false);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analysis/nlp-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: searchQuery,
          input_method: method,
          session_id: sessionId,
          user_id: null, // Will be populated from auth token if logged in
          email: null
        })
      });

      const data = await response.json();

      if (data.success) {
        setResults(data);

        // Refresh search history
        fetchSearchHistory();

        // Render chart if results contain time series data
        if (data.results.length > 5 && data.results[0].datetime) {
          renderChart(data.results);
        }
      } else {
        setError(data.error || 'Query failed');
      }
    } catch (err) {
      setError('Failed to process query: ' + err.message);
    } finally {
      setIsLoading(false);
      setInputMethod('text'); // Reset to text after search
    }
  };

  const renderChart = (data) => {
    if (!chartContainerRef.current) return;

    // Clean up existing chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: theme === 'dark' ? '#0f172a' : '#ffffff' },
        textColor: theme === 'dark' ? '#94a3b8' : '#1e293b',
      },
      grid: {
        vertLines: { color: theme === 'dark' ? '#1e293b' : '#e2e8f0' },
        horzLines: { color: theme === 'dark' ? '#1e293b' : '#e2e8f0' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Prepare candlestick data
    const candlestickData = data.map(item => ({
      time: new Date(item.datetime).getTime() / 1000,
      open: parseFloat(item.open || item.close),
      high: parseFloat(item.high || item.close),
      low: parseFloat(item.low || item.close),
      close: parseFloat(item.close)
    })).sort((a, b) => a.time - b.time);

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    candlestickSeries.setData(candlestickData);
    chart.timeScale().fitContent();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  const bgColor = theme === 'dark' ? '#0f172a' : '#ffffff';
  const cardBg = theme === 'dark' ? '#1e293b' : '#f8fafc';
  const textColor = theme === 'dark' ? '#f1f5f9' : '#0f172a';
  const borderColor = theme === 'dark' ? '#334155' : '#e2e8f0';

  return (
    <div style={{ padding: '24px', background: bgColor, minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ color: textColor, fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>
            🔍 Smart Search
          </h1>
          <p style={{ color: theme === 'dark' ? '#94a3b8' : '#64748b', fontSize: '16px' }}>
            Search using natural language or voice input
          </p>
        </div>

        {/* Search Bar */}
        <div style={{ marginBottom: '24px', position: 'relative' }}>
          <div style={{
            display: 'flex',
            gap: '12px',
            background: cardBg,
            padding: '16px',
            borderRadius: '12px',
            border: `2px solid ${borderColor}`,
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <Search size={24} color={theme === 'dark' ? '#94a3b8' : '#64748b'} style={{ flexShrink: 0 }} />

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => {
                if (searchHistory.length > 0) {
                  setShowHistory(true);
                  setShowSuggestions(false);
                } else {
                  setShowSuggestions(true);
                  setShowHistory(false);
                }
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  setInputMethod('text');
                  handleSearch();
                }
              }}
              placeholder="Ask anything... (e.g., 'oversold cryptos' or 'top 10 stock gainers')"
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: textColor,
                fontSize: '16px',
                fontFamily: 'inherit'
              }}
            />

            <button
              onClick={isListening ? stopListening : startListening}
              style={{
                padding: '8px 16px',
                background: isListening ? '#ef4444' : '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: '600',
                transition: 'all 0.2s'
              }}
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
              {isListening ? 'Listening...' : 'Voice'}
            </button>

            <button
              onClick={() => handleSearch()}
              disabled={isLoading || !query.trim()}
              style={{
                padding: '8px 24px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: isLoading || !query.trim() ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                opacity: isLoading || !query.trim() ? 0.5 : 1,
                transition: 'all 0.2s'
              }}
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Search History Dropdown */}
          {showHistory && searchHistory.length > 0 && !results && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              marginTop: '8px',
              background: cardBg,
              border: `1px solid ${borderColor}`,
              borderRadius: '12px',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
              maxHeight: '300px',
              overflowY: 'auto',
              zIndex: 10
            }}>
              <div style={{ padding: '12px 16px', borderBottom: `1px solid ${borderColor}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong style={{ color: textColor, fontSize: '14px' }}>Recent Searches:</strong>
                <button
                  onClick={() => setShowSuggestions(true)}
                  style={{
                    padding: '4px 8px',
                    background: 'transparent',
                    color: '#3b82f6',
                    border: 'none',
                    fontSize: '12px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  Show Suggestions
                </button>
              </div>
              {searchHistory.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    setQuery(item.query_text);
                    handleSearch(item.query_text, item.input_method);
                  }}
                  style={{
                    padding: '12px 16px',
                    cursor: 'pointer',
                    borderBottom: idx < searchHistory.length - 1 ? `1px solid ${borderColor}` : 'none',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = theme === 'dark' ? '#334155' : '#e2e8f0'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: textColor, fontSize: '14px', flex: 1 }}>{item.query_text}</span>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      {item.input_method === 'voice' && (
                        <span style={{ fontSize: '10px', padding: '2px 6px', background: '#10b981', color: 'white', borderRadius: '4px' }}>
                          🎤 Voice
                        </span>
                      )}
                      <span style={{ fontSize: '12px', color: theme === 'dark' ? '#94a3b8' : '#64748b' }}>
                        {item.result_count} results
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Suggestions Dropdown */}
          {showSuggestions && !showHistory && !results && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              marginTop: '8px',
              background: cardBg,
              border: `1px solid ${borderColor}`,
              borderRadius: '12px',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
              maxHeight: '300px',
              overflowY: 'auto',
              zIndex: 10
            }}>
              <div style={{ padding: '12px 16px', borderBottom: `1px solid ${borderColor}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong style={{ color: textColor, fontSize: '14px' }}>Try asking:</strong>
                {searchHistory.length > 0 && (
                  <button
                    onClick={() => { setShowSuggestions(false); setShowHistory(true); }}
                    style={{
                      padding: '4px 8px',
                      background: 'transparent',
                      color: '#3b82f6',
                      border: 'none',
                      fontSize: '12px',
                      cursor: 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    Show History
                  </button>
                )}
              </div>
              {suggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSuggestionClick(suggestion)}
                  style={{
                    padding: '12px 16px',
                    cursor: 'pointer',
                    borderBottom: idx < suggestions.length - 1 ? `1px solid ${borderColor}` : 'none',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = theme === 'dark' ? '#334155' : '#e2e8f0'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <span style={{ color: textColor, fontSize: '14px' }}>{suggestion}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Loading State */}
        {isLoading && (
          <div style={{
            textAlign: 'center',
            padding: '60px',
            background: cardBg,
            borderRadius: '16px',
            border: `1px solid ${borderColor}`
          }}>
            <Loader size={48} color="#3b82f6" style={{ animation: 'spin 1s linear infinite' }} />
            <p style={{ color: textColor, marginTop: '16px', fontSize: '16px' }}>
              Processing your query...
            </p>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div style={{
            padding: '20px',
            background: '#fee2e2',
            color: '#991b1b',
            borderRadius: '12px',
            border: '1px solid #fca5a5',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <AlertCircle size={24} />
            <span style={{ fontSize: '14px' }}>{error}</span>
          </div>
        )}

        {/* Results */}
        {results && !isLoading && (
          <div>
            {/* Interpretation */}
            <div style={{
              padding: '16px 20px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              color: 'white',
              borderRadius: '12px',
              marginBottom: '24px',
              fontSize: '16px',
              fontWeight: '500'
            }}>
              💡 {results.interpretation}
              <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '4px' }}>
                Found {results.count} result{results.count !== 1 ? 's' : ''}
              </div>
            </div>

            {/* Chart (if time series data) */}
            {results.results.length > 5 && results.results[0].datetime && (
              <div style={{
                background: cardBg,
                borderRadius: '16px',
                padding: '24px',
                marginBottom: '24px',
                border: `1px solid ${borderColor}`
              }}>
                <h3 style={{ color: textColor, marginBottom: '16px', fontSize: '18px', fontWeight: '600' }}>
                  Chart View
                </h3>
                <div ref={chartContainerRef} style={{ height: '400px', width: '100%' }} />
              </div>
            )}

            {/* Results Table */}
            <div style={{
              background: cardBg,
              borderRadius: '16px',
              padding: '24px',
              border: `1px solid ${borderColor}`
            }}>
              <h3 style={{ color: textColor, marginBottom: '16px', fontSize: '18px', fontWeight: '600' }}>
                Results ({results.count})
              </h3>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: `2px solid ${borderColor}` }}>
                      <th style={{ padding: '12px', textAlign: 'left', color: theme === 'dark' ? '#94a3b8' : '#64748b', fontSize: '14px' }}>
                        Symbol
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', color: theme === 'dark' ? '#94a3b8' : '#64748b', fontSize: '14px' }}>
                        Close
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', color: theme === 'dark' ? '#94a3b8' : '#64748b', fontSize: '14px' }}>
                        Change %
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', color: theme === 'dark' ? '#94a3b8' : '#64748b', fontSize: '14px' }}>
                        RSI
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', color: theme === 'dark' ? '#94a3b8' : '#64748b', fontSize: '14px' }}>
                        MACD
                      </th>
                      <th style={{ padding: '12px', textAlign: 'left', color: theme === 'dark' ? '#94a3b8' : '#64748b', fontSize: '14px' }}>
                        Volume
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.results.slice(0, 20).map((item, idx) => (
                      <tr key={idx} style={{ borderBottom: `1px solid ${borderColor}` }}>
                        <td style={{ padding: '12px', color: textColor, fontWeight: '600', fontSize: '14px' }}>
                          {item.pair || item.symbol}
                        </td>
                        <td style={{ padding: '12px', color: textColor, fontSize: '14px' }}>
                          ${parseFloat(item.close).toFixed(2)}
                        </td>
                        <td style={{ padding: '12px', fontSize: '14px' }}>
                          <span style={{
                            color: item.roc > 0 ? '#10b981' : '#ef4444',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}>
                            {item.roc > 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                            {parseFloat(item.roc).toFixed(2)}%
                          </span>
                        </td>
                        <td style={{ padding: '12px', fontSize: '14px' }}>
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '6px',
                            background: item.rsi < 30 ? '#fee2e2' : item.rsi > 70 ? '#dcfce7' : '#f1f5f9',
                            color: item.rsi < 30 ? '#991b1b' : item.rsi > 70 ? '#166534' : '#475569',
                            fontSize: '12px',
                            fontWeight: '600'
                          }}>
                            {parseFloat(item.rsi).toFixed(1)}
                          </span>
                        </td>
                        <td style={{ padding: '12px', color: textColor, fontSize: '14px' }}>
                          {parseFloat(item.macd).toFixed(4)}
                        </td>
                        <td style={{ padding: '12px', color: textColor, fontSize: '14px' }}>
                          {parseFloat(item.volume).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* SQL Query (Collapsible) */}
              <details style={{ marginTop: '24px' }}>
                <summary style={{
                  color: theme === 'dark' ? '#94a3b8' : '#64748b',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '600',
                  padding: '8px 0'
                }}>
                  View Generated SQL
                </summary>
                <pre style={{
                  background: theme === 'dark' ? '#0f172a' : '#f8fafc',
                  padding: '16px',
                  borderRadius: '8px',
                  overflow: 'auto',
                  fontSize: '12px',
                  color: theme === 'dark' ? '#10b981' : '#166534',
                  marginTop: '8px',
                  border: `1px solid ${borderColor}`
                }}>
                  {results.sql}
                </pre>
              </details>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
