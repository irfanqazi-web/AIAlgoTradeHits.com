import { useState, useCallback } from 'react';
import VoiceSearch from './VoiceSearch';

/**
 * Smart Search Bar Component
 * AI-powered natural language search with voice input
 * Connects to the Smart Search Cloud Function
 */

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-252370699783.us-central1.run.app'
);

// Smart Search API endpoint - uses main API endpoint
const SMART_SEARCH_URL = import.meta.env.VITE_SMART_SEARCH_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080/api/smart-search'
    : 'https://trading-api-252370699783.us-central1.run.app/api/smart-search'
);

// NLP Query API endpoint - BigQuery-based search (corrected endpoint)
const NLP_QUERY_URL = `${API_BASE_URL}/api/analysis/nlp-search`;

export default function SmartSearchBar({ onResults, onSymbolSelect, theme = 'dark' }) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const isDark = theme === 'dark';

  const handleSearch = useCallback(async (searchQuery) => {
    const trimmedQuery = (searchQuery || query).trim();
    if (!trimmedQuery) return;

    setIsLoading(true);
    setError(null);
    setShowResults(true);

    try {
      const response = await fetch(SMART_SEARCH_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: trimmedQuery,
          execute: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);

      if (onResults) {
        onResults(data);
      }
    } catch (err) {
      console.error('Smart search error:', err);
      setError(err.message || 'Search failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [query, onResults]);

  const handleVoiceTranscript = useCallback((transcript) => {
    setQuery(transcript);
  }, []);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  }, [handleSearch]);

  const handleResultClick = useCallback((symbol, assetType) => {
    if (onSymbolSelect) {
      onSymbolSelect(symbol, assetType);
    }
    setShowResults(false);
  }, [onSymbolSelect]);

  // Example queries for user guidance
  const exampleQueries = [
    "Show me oversold stocks",
    "Bitcoin price with indicators",
    "Top crypto gainers today",
    "Stocks with RSI below 30",
    "ETFs above 200-day moving average",
  ];

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      maxWidth: '800px',
      margin: '0 auto',
    }}>
      {/* Search Input Container */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px 16px',
        background: isDark ? '#1e293b' : '#f8fafc',
        borderRadius: '16px',
        border: `2px solid ${isDark ? '#334155' : '#e2e8f0'}`,
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        transition: 'all 0.3s ease',
      }}>
        {/* Search Icon */}
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke={isDark ? '#64748b' : '#94a3b8'}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>

        {/* Text Input */}
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask anything... e.g., 'Show me oversold crypto'"
          style={{
            flex: 1,
            border: 'none',
            background: 'transparent',
            color: isDark ? '#f1f5f9' : '#1e293b',
            fontSize: '16px',
            outline: 'none',
          }}
        />

        {/* Voice Search */}
        <VoiceSearch
          onSearch={handleSearch}
          onTranscript={handleVoiceTranscript}
          disabled={isLoading}
        />

        {/* Search Button */}
        <button
          onClick={() => handleSearch()}
          disabled={isLoading || !query.trim()}
          style={{
            padding: '10px 20px',
            background: isLoading
              ? '#64748b'
              : 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            cursor: isLoading || !query.trim() ? 'not-allowed' : 'pointer',
            fontWeight: '600',
            fontSize: '14px',
            transition: 'all 0.3s ease',
            opacity: isLoading || !query.trim() ? 0.6 : 1,
          }}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Example Queries */}
      {!showResults && (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          marginTop: '12px',
          justifyContent: 'center',
        }}>
          <span style={{ color: isDark ? '#64748b' : '#94a3b8', fontSize: '12px' }}>
            Try:
          </span>
          {exampleQueries.map((example, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(example);
                handleSearch(example);
              }}
              style={{
                padding: '4px 12px',
                background: isDark ? '#334155' : '#e2e8f0',
                color: isDark ? '#94a3b8' : '#64748b',
                border: 'none',
                borderRadius: '20px',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onMouseOver={(e) => {
                e.target.style.background = isDark ? '#475569' : '#cbd5e1';
              }}
              onMouseOut={(e) => {
                e.target.style.background = isDark ? '#334155' : '#e2e8f0';
              }}
            >
              {example}
            </button>
          ))}
        </div>
      )}

      {/* Results Panel */}
      {showResults && (
        <div style={{
          marginTop: '16px',
          background: isDark ? '#1e293b' : '#ffffff',
          borderRadius: '16px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)',
          overflow: 'hidden',
        }}>
          {/* Close button */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 16px',
            borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
          }}>
            <span style={{
              color: isDark ? '#94a3b8' : '#64748b',
              fontSize: '14px',
              fontWeight: '500',
            }}>
              Search Results
            </span>
            <button
              onClick={() => setShowResults(false)}
              style={{
                background: 'none',
                border: 'none',
                color: isDark ? '#64748b' : '#94a3b8',
                cursor: 'pointer',
                padding: '4px',
              }}
            >
              ✕
            </button>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div style={{
              padding: '40px',
              textAlign: 'center',
              color: isDark ? '#64748b' : '#94a3b8',
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                border: '3px solid transparent',
                borderTop: '3px solid #3b82f6',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 16px',
              }} />
              Analyzing your query with AI...
              <style>{`
                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
              `}</style>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div style={{
              padding: '20px',
              color: '#ef4444',
              textAlign: 'center',
            }}>
              {error}
            </div>
          )}

          {/* Results */}
          {results && !isLoading && (
            <div style={{ padding: '16px' }}>
              {/* AI Analysis */}
              {results.ai_analysis && (
                <div style={{ marginBottom: '16px' }}>
                  <div style={{
                    fontSize: '12px',
                    color: isDark ? '#64748b' : '#94a3b8',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    AI Understanding
                  </div>
                  <div style={{
                    padding: '12px',
                    background: isDark ? '#0f172a' : '#f1f5f9',
                    borderRadius: '8px',
                    fontSize: '14px',
                    color: isDark ? '#e2e8f0' : '#334155',
                  }}>
                    {results.ai_analysis.explanation || results.ai_analysis.query_understanding?.intent}
                  </div>

                  {results.ai_analysis.trading_insight && (
                    <div style={{
                      marginTop: '8px',
                      padding: '12px',
                      background: isDark ? '#1e3a5f' : '#dbeafe',
                      borderRadius: '8px',
                      fontSize: '13px',
                      color: isDark ? '#93c5fd' : '#1e40af',
                      borderLeft: '3px solid #3b82f6',
                    }}>
                      💡 {results.ai_analysis.trading_insight}
                    </div>
                  )}
                </div>
              )}

              {/* Data Results */}
              {results.results?.data && results.results.data.length > 0 && (
                <div>
                  <div style={{
                    fontSize: '12px',
                    color: isDark ? '#64748b' : '#94a3b8',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    Results ({results.results.count})
                  </div>
                  <div style={{
                    maxHeight: '300px',
                    overflowY: 'auto',
                  }}>
                    {results.results.data.map((item, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleResultClick(item.symbol, results.ai_analysis?.query_understanding?.asset_type)}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '12px',
                          borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
                          cursor: 'pointer',
                          transition: 'background 0.2s',
                        }}
                        onMouseOver={(e) => {
                          e.currentTarget.style.background = isDark ? '#334155' : '#f1f5f9';
                        }}
                        onMouseOut={(e) => {
                          e.currentTarget.style.background = 'transparent';
                        }}
                      >
                        <div>
                          <div style={{
                            fontWeight: '600',
                            color: isDark ? '#f1f5f9' : '#1e293b',
                          }}>
                            {item.symbol}
                          </div>
                          <div style={{
                            fontSize: '12px',
                            color: isDark ? '#64748b' : '#94a3b8',
                          }}>
                            {item.name || 'Click to view chart'}
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{
                            fontWeight: '600',
                            color: isDark ? '#f1f5f9' : '#1e293b',
                          }}>
                            ${item.close?.toFixed(2) || 'N/A'}
                          </div>
                          {item.rsi_14 && (
                            <div style={{
                              fontSize: '12px',
                              color: item.rsi_14 < 30 ? '#22c55e' : item.rsi_14 > 70 ? '#ef4444' : '#64748b',
                            }}>
                              RSI: {item.rsi_14.toFixed(1)}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* No Results */}
              {results.results?.data?.length === 0 && (
                <div style={{
                  padding: '20px',
                  textAlign: 'center',
                  color: isDark ? '#64748b' : '#94a3b8',
                }}>
                  No results found. Try a different query.
                </div>
              )}

              {/* Execution Time */}
              {results.execution_time_ms && (
                <div style={{
                  marginTop: '12px',
                  fontSize: '11px',
                  color: isDark ? '#475569' : '#cbd5e1',
                  textAlign: 'right',
                }}>
                  Query executed in {results.execution_time_ms}ms
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
