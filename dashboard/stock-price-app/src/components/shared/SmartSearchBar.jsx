import { useState, useCallback, useEffect } from 'react';
import VoiceSearch from './VoiceSearch';
import {
  TrendingUp, Building2, Coins, DollarSign, Globe, BarChart3,
  Fuel, Clock, Calendar, CalendarDays, Timer, Sparkles, Search,
  X, ChevronDown, Zap, Target, AlertCircle, Brain
} from 'lucide-react';

/**
 * Enhanced Smart Search Bar Component
 * AI-powered context-sensitive search with asset type and period selectors
 * Uses Gemini 3 for intelligent query parsing
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-1075463475276.us-central1.run.app'
);

const SMART_SEARCH_URL = `${API_BASE_URL}/api/ai/smart-search`;

// Asset type configurations with icons and colors
const ASSET_TYPES = [
  { id: 'all', label: 'All Assets', icon: Globe, color: '#6366f1', emoji: '🌐' },
  { id: 'stocks', label: 'Stocks', icon: Building2, color: '#ef4444', emoji: '🏢' },
  { id: 'crypto', label: 'Crypto', icon: Coins, color: '#f59e0b', emoji: '🪙' },
  { id: 'forex', label: 'Forex', icon: DollarSign, color: '#10b981', emoji: '💱' },
  { id: 'etfs', label: 'ETFs', icon: BarChart3, color: '#3b82f6', emoji: '📊' },
  { id: 'indices', label: 'Indices', icon: TrendingUp, color: '#8b5cf6', emoji: '📈' },
  { id: 'commodities', label: 'Commodities', icon: Fuel, color: '#f97316', emoji: '🛢️' },
];

// Time period configurations
const TIME_PERIODS = [
  { id: '5min', label: '5 Min', icon: Timer, color: '#ec4899', description: 'Intraday scalping' },
  { id: 'hourly', label: 'Hourly', icon: Clock, color: '#8b5cf6', description: 'Day trading' },
  { id: 'daily', label: 'Daily', icon: Calendar, color: '#3b82f6', description: 'Swing trading' },
  { id: 'weekly', label: 'Weekly', icon: CalendarDays, color: '#10b981', description: 'Position trading' },
];

// Map page routes to default context
const PAGE_CONTEXT_MAP = {
  'dashboard': { assetType: 'all', period: 'daily' },
  'markets': { assetType: 'all', period: 'daily' },
  'markets-stocks': { assetType: 'stocks', period: 'daily' },
  'markets-crypto': { assetType: 'crypto', period: 'daily' },
  'markets-forex': { assetType: 'forex', period: 'daily' },
  'markets-etfs': { assetType: 'etfs', period: 'daily' },
  'markets-indices': { assetType: 'indices', period: 'daily' },
  'markets-commodities': { assetType: 'commodities', period: 'daily' },
  'weekly': { assetType: 'all', period: 'weekly' },
  'weekly-dashboard': { assetType: 'all', period: 'weekly' },
  'weekly-stocks': { assetType: 'stocks', period: 'weekly' },
  'weekly-cryptos': { assetType: 'crypto', period: 'weekly' },
  'weekly-etfs': { assetType: 'etfs', period: 'weekly' },
  'weekly-forex': { assetType: 'forex', period: 'weekly' },
  'weekly-indices': { assetType: 'indices', period: 'weekly' },
  'weekly-commodities': { assetType: 'commodities', period: 'weekly' },
  'charts': { assetType: 'all', period: 'daily' },
  'analysis': { assetType: 'all', period: 'daily' },
  'analysis-stocks': { assetType: 'stocks', period: 'daily' },
  'analysis-cryptos': { assetType: 'crypto', period: 'daily' },
  'ai-signals': { assetType: 'all', period: 'daily' },
  'ai-signals-predictions': { assetType: 'all', period: 'daily' },
  'ai-signals-patterns': { assetType: 'all', period: 'daily' },
  'strategies': { assetType: 'all', period: 'daily' },
};

// Example queries based on context
const CONTEXTUAL_EXAMPLES = {
  stocks: [
    "Tech stocks over $100",
    "Top gainers today",
    "Oversold with RSI below 30",
    "Near 52-week high",
    "High volume healthcare",
  ],
  crypto: [
    "Top crypto gainers",
    "DeFi tokens oversold",
    "Bitcoin momentum analysis",
    "Meme coins with volume",
    "Layer 2 projects",
  ],
  forex: [
    "Major pairs trending up",
    "EUR/USD analysis",
    "High volatility pairs",
    "Safe haven currencies",
    "Emerging market FX",
  ],
  etfs: [
    "Tech ETFs trending",
    "Bond ETFs oversold",
    "Sector rotation leaders",
    "High dividend ETFs",
    "Growth vs Value ETFs",
  ],
  indices: [
    "S&P 500 momentum",
    "Nasdaq vs Dow",
    "Global indices comparison",
    "Emerging markets indices",
    "Volatility index analysis",
  ],
  commodities: [
    "Gold price analysis",
    "Oil trending up",
    "Agricultural commodities",
    "Precious metals momentum",
    "Energy sector analysis",
  ],
  all: [
    "Top gainers across markets",
    "Oversold opportunities",
    "High momentum assets",
    "Safe haven assets",
    "Trending breakouts",
  ],
};

export default function SmartSearchBar({
  onResults,
  onSymbolSelect,
  theme = 'dark',
  currentPage = 'dashboard'
}) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false);

  // Context state
  const [selectedAssetType, setSelectedAssetType] = useState('all');
  const [selectedPeriod, setSelectedPeriod] = useState('daily');
  const [showAssetDropdown, setShowAssetDropdown] = useState(false);
  const [showPeriodDropdown, setShowPeriodDropdown] = useState(false);

  const isDark = theme === 'dark';

  // Update context based on current page
  useEffect(() => {
    const pageContext = PAGE_CONTEXT_MAP[currentPage] || { assetType: 'all', period: 'daily' };
    setSelectedAssetType(pageContext.assetType);
    setSelectedPeriod(pageContext.period);
  }, [currentPage]);

  // Get current asset and period config
  const currentAsset = ASSET_TYPES.find(a => a.id === selectedAssetType) || ASSET_TYPES[0];
  const currentPeriod = TIME_PERIODS.find(p => p.id === selectedPeriod) || TIME_PERIODS[2];

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
          context: {
            page: currentPage,
            assetType: selectedAssetType,
            period: selectedPeriod,
          },
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
  }, [query, currentPage, selectedAssetType, selectedPeriod, onResults]);

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

  // Get contextual examples
  const exampleQueries = CONTEXTUAL_EXAMPLES[selectedAssetType] || CONTEXTUAL_EXAMPLES.all;

  const AssetIcon = currentAsset.icon;
  const PeriodIcon = currentPeriod.icon;

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      maxWidth: '900px',
      margin: '0 auto',
    }}>
      {/* Main Search Container */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 12px',
        background: isDark
          ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)'
          : 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
        borderRadius: '16px',
        border: `2px solid ${isDark ? '#334155' : '#e2e8f0'}`,
        boxShadow: isDark
          ? '0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.05)'
          : '0 4px 24px rgba(0, 0, 0, 0.1)',
        transition: 'all 0.3s ease',
      }}>
        {/* AI Brain Icon */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
          boxShadow: '0 2px 8px rgba(139, 92, 246, 0.4)',
        }}>
          <Brain size={18} color="white" />
        </div>

        {/* Asset Type Selector */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => { setShowAssetDropdown(!showAssetDropdown); setShowPeriodDropdown(false); }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              background: `${currentAsset.color}22`,
              border: `1px solid ${currentAsset.color}`,
              borderRadius: '10px',
              cursor: 'pointer',
              color: currentAsset.color,
              fontSize: '13px',
              fontWeight: '600',
              transition: 'all 0.2s',
            }}
          >
            <span style={{ fontSize: '16px' }}>{currentAsset.emoji}</span>
            <span>{currentAsset.label}</span>
            <ChevronDown size={14} />
          </button>

          {/* Asset Dropdown */}
          {showAssetDropdown && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              marginTop: '4px',
              background: isDark ? '#1e293b' : '#ffffff',
              border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
              zIndex: 1000,
              overflow: 'hidden',
              minWidth: '160px',
            }}>
              {ASSET_TYPES.map(asset => {
                const Icon = asset.icon;
                return (
                  <button
                    key={asset.id}
                    onClick={() => { setSelectedAssetType(asset.id); setShowAssetDropdown(false); }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      width: '100%',
                      padding: '10px 14px',
                      background: selectedAssetType === asset.id ? `${asset.color}22` : 'transparent',
                      border: 'none',
                      borderLeft: selectedAssetType === asset.id ? `3px solid ${asset.color}` : '3px solid transparent',
                      cursor: 'pointer',
                      color: isDark ? '#e2e8f0' : '#1e293b',
                      fontSize: '13px',
                      textAlign: 'left',
                      transition: 'all 0.2s',
                    }}
                    onMouseOver={(e) => e.currentTarget.style.background = `${asset.color}11`}
                    onMouseOut={(e) => e.currentTarget.style.background = selectedAssetType === asset.id ? `${asset.color}22` : 'transparent'}
                  >
                    <span style={{ fontSize: '16px' }}>{asset.emoji}</span>
                    <span>{asset.label}</span>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Period Selector */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => { setShowPeriodDropdown(!showPeriodDropdown); setShowAssetDropdown(false); }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              background: `${currentPeriod.color}22`,
              border: `1px solid ${currentPeriod.color}`,
              borderRadius: '10px',
              cursor: 'pointer',
              color: currentPeriod.color,
              fontSize: '13px',
              fontWeight: '600',
              transition: 'all 0.2s',
            }}
          >
            <PeriodIcon size={14} />
            <span>{currentPeriod.label}</span>
            <ChevronDown size={14} />
          </button>

          {/* Period Dropdown */}
          {showPeriodDropdown && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              marginTop: '4px',
              background: isDark ? '#1e293b' : '#ffffff',
              border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
              zIndex: 1000,
              overflow: 'hidden',
              minWidth: '180px',
            }}>
              {TIME_PERIODS.map(period => {
                const Icon = period.icon;
                return (
                  <button
                    key={period.id}
                    onClick={() => { setSelectedPeriod(period.id); setShowPeriodDropdown(false); }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      width: '100%',
                      padding: '10px 14px',
                      background: selectedPeriod === period.id ? `${period.color}22` : 'transparent',
                      border: 'none',
                      borderLeft: selectedPeriod === period.id ? `3px solid ${period.color}` : '3px solid transparent',
                      cursor: 'pointer',
                      color: isDark ? '#e2e8f0' : '#1e293b',
                      fontSize: '13px',
                      textAlign: 'left',
                      transition: 'all 0.2s',
                    }}
                    onMouseOver={(e) => e.currentTarget.style.background = `${period.color}11`}
                    onMouseOut={(e) => e.currentTarget.style.background = selectedPeriod === period.id ? `${period.color}22` : 'transparent'}
                  >
                    <Icon size={16} color={period.color} />
                    <div>
                      <div style={{ fontWeight: '600' }}>{period.label}</div>
                      <div style={{ fontSize: '11px', color: isDark ? '#64748b' : '#94a3b8' }}>
                        {period.description}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Divider */}
        <div style={{
          width: '1px',
          height: '28px',
          background: isDark ? '#334155' : '#e2e8f0',
        }} />

        {/* Search Input */}
        <div style={{ flex: 1, position: 'relative' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => { setShowAssetDropdown(false); setShowPeriodDropdown(false); }}
            placeholder={`Search ${currentAsset.label} (${currentPeriod.label})...`}
            style={{
              width: '100%',
              border: 'none',
              background: 'transparent',
              color: isDark ? '#f1f5f9' : '#1e293b',
              fontSize: '15px',
              outline: 'none',
              padding: '8px 4px',
            }}
          />
        </div>

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
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '10px 18px',
            background: isLoading
              ? '#64748b'
              : 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            cursor: isLoading || !query.trim() ? 'not-allowed' : 'pointer',
            fontWeight: '600',
            fontSize: '14px',
            transition: 'all 0.3s ease',
            opacity: isLoading || !query.trim() ? 0.6 : 1,
            boxShadow: isLoading ? 'none' : '0 2px 12px rgba(139, 92, 246, 0.4)',
          }}
        >
          {isLoading ? (
            <>
              <Sparkles size={16} style={{ animation: 'pulse 1s infinite' }} />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Search size={16} />
              <span>Search</span>
            </>
          )}
        </button>
      </div>

      {/* Contextual Example Queries */}
      {!showResults && (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          marginTop: '12px',
          justifyContent: 'center',
          alignItems: 'center',
        }}>
          <span style={{
            color: isDark ? '#64748b' : '#94a3b8',
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            <Zap size={12} /> Try:
          </span>
          {exampleQueries.slice(0, 4).map((example, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(example);
                handleSearch(example);
              }}
              style={{
                padding: '6px 14px',
                background: isDark ? '#334155' : '#e2e8f0',
                color: isDark ? '#94a3b8' : '#64748b',
                border: 'none',
                borderRadius: '20px',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onMouseOver={(e) => {
                e.target.style.background = currentAsset.color;
                e.target.style.color = 'white';
              }}
              onMouseOut={(e) => {
                e.target.style.background = isDark ? '#334155' : '#e2e8f0';
                e.target.style.color = isDark ? '#94a3b8' : '#64748b';
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
          {/* Results Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 16px',
            borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
            background: isDark ? '#0f172a' : '#f8fafc',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{
                color: isDark ? '#94a3b8' : '#64748b',
                fontSize: '14px',
                fontWeight: '500',
              }}>
                AI Search Results
              </span>
              {results?.model_used && (
                <span style={{
                  padding: '2px 8px',
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
                  color: 'white',
                  borderRadius: '4px',
                  fontSize: '10px',
                  fontWeight: '600',
                }}>
                  {results.model_used}
                </span>
              )}
              <span style={{
                padding: '2px 8px',
                background: `${currentAsset.color}22`,
                color: currentAsset.color,
                borderRadius: '4px',
                fontSize: '10px',
                fontWeight: '600',
              }}>
                {currentAsset.emoji} {currentAsset.label}
              </span>
              <span style={{
                padding: '2px 8px',
                background: `${currentPeriod.color}22`,
                color: currentPeriod.color,
                borderRadius: '4px',
                fontSize: '10px',
                fontWeight: '600',
              }}>
                {currentPeriod.label}
              </span>
            </div>
            <button
              onClick={() => setShowResults(false)}
              style={{
                background: 'none',
                border: 'none',
                color: isDark ? '#64748b' : '#94a3b8',
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '4px',
              }}
            >
              <X size={18} />
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
                width: '48px',
                height: '48px',
                border: '3px solid transparent',
                borderTop: '3px solid #8b5cf6',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 16px',
              }} />
              <div style={{ fontSize: '16px', fontWeight: '500', marginBottom: '8px' }}>
                AI is analyzing your query...
              </div>
              <div style={{ fontSize: '13px' }}>
                Searching {currentAsset.label} ({currentPeriod.label} data)
              </div>
              <style>{`
                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
                @keyframes pulse {
                  0%, 100% { opacity: 1; }
                  50% { opacity: 0.5; }
                }
              `}</style>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div style={{
              padding: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              color: '#ef4444',
              background: '#ef444411',
            }}>
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {/* Results Content */}
          {results && !isLoading && (
            <div style={{ padding: '16px' }}>
              {/* AI Analysis */}
              {results.ai_summary && (
                <div style={{ marginBottom: '16px' }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '8px',
                  }}>
                    <Brain size={16} color="#8b5cf6" />
                    <span style={{
                      fontSize: '12px',
                      color: isDark ? '#64748b' : '#94a3b8',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                      fontWeight: '600',
                    }}>
                      AI Analysis
                    </span>
                  </div>
                  <div style={{
                    padding: '14px',
                    background: isDark ? '#0f172a' : '#f1f5f9',
                    borderRadius: '10px',
                    fontSize: '14px',
                    color: isDark ? '#e2e8f0' : '#334155',
                    lineHeight: '1.6',
                    borderLeft: '3px solid #8b5cf6',
                  }}>
                    {results.ai_summary}
                  </div>
                </div>
              )}

              {/* Parsed Filters Debug */}
              {results.parsed_filters && Object.keys(results.parsed_filters).length > 0 && (
                <div style={{
                  marginBottom: '16px',
                  padding: '10px',
                  background: isDark ? '#0f172a' : '#f1f5f9',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}>
                  <span style={{ color: isDark ? '#64748b' : '#94a3b8' }}>
                    Filters applied: {JSON.stringify(results.parsed_filters)}
                  </span>
                </div>
              )}

              {/* Data Results */}
              {results.results && results.results.length > 0 && (
                <div>
                  <div style={{
                    fontSize: '12px',
                    color: isDark ? '#64748b' : '#94a3b8',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    Found {results.count} results {results.total_matches > results.count && `(${results.total_matches} total)`}
                  </div>
                  <div style={{
                    maxHeight: '350px',
                    overflowY: 'auto',
                    borderRadius: '10px',
                    border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
                  }}>
                    {results.results.slice(0, 50).map((item, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleResultClick(item.symbol, item.asset_type)}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '12px 14px',
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
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <div style={{
                            width: '36px',
                            height: '36px',
                            borderRadius: '8px',
                            background: `${currentAsset.color}22`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '16px',
                          }}>
                            {currentAsset.emoji}
                          </div>
                          <div>
                            <div style={{
                              fontWeight: '600',
                              color: isDark ? '#f1f5f9' : '#1e293b',
                              fontSize: '14px',
                            }}>
                              {item.symbol}
                            </div>
                            <div style={{
                              fontSize: '12px',
                              color: isDark ? '#64748b' : '#94a3b8',
                              maxWidth: '200px',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}>
                              {item.name || item.sector || 'Click to view'}
                            </div>
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{
                            fontWeight: '600',
                            color: isDark ? '#f1f5f9' : '#1e293b',
                            fontSize: '14px',
                          }}>
                            ${(item.close || item.current_price || 0).toLocaleString(undefined, {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 4,
                            })}
                          </div>
                          {(item.percent_change !== undefined || item.weekly_change_percent !== undefined) && (
                            <div style={{
                              fontSize: '12px',
                              fontWeight: '600',
                              color: (item.percent_change || item.weekly_change_percent || 0) >= 0 ? '#10b981' : '#ef4444',
                            }}>
                              {(item.percent_change || item.weekly_change_percent || 0) >= 0 ? '▲' : '▼'}
                              {Math.abs(item.percent_change || item.weekly_change_percent || 0).toFixed(2)}%
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* No Results */}
              {(!results.results || results.results.length === 0) && (
                <div style={{
                  padding: '30px',
                  textAlign: 'center',
                  color: isDark ? '#64748b' : '#94a3b8',
                }}>
                  <Target size={32} style={{ marginBottom: '12px', opacity: 0.5 }} />
                  <div style={{ fontSize: '14px' }}>No results found for your query.</div>
                  <div style={{ fontSize: '12px', marginTop: '8px' }}>
                    Try different keywords or adjust your filters.
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

