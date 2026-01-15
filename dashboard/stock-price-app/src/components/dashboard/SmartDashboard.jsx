import { useState, useEffect, useRef } from 'react';
import {
  TrendingUp, TrendingDown, Activity, Check, ArrowUpDown,
  Sun, Moon, Search, Mic, MicOff, X, ChevronDown, ChevronUp,
  BarChart3, Coins, DollarSign, Globe, PieChart, Package, Sparkles
} from 'lucide-react';
import themes from '../../theme';
import SmartSearchBar from '../shared/SmartSearchBar';
import TradingViewChart from '../charts/TradingViewChart';

// Asset type configuration - All 7 Market Types
const ASSET_TYPES = {
  stocks: {
    label: 'Stocks',
    icon: TrendingUp,
    color: '#3b82f6',
    description: 'US Stocks (S&P 500, NASDAQ)'
  },
  crypto: {
    label: 'Crypto',
    icon: Coins,
    color: '#f59e0b',
    description: 'Cryptocurrencies (BTC, ETH, etc.)'
  },
  forex: {
    label: 'Forex',
    icon: DollarSign,
    color: '#10b981',
    description: 'Currency Pairs (EUR/USD, etc.)'
  },
  etfs: {
    label: 'ETFs',
    icon: PieChart,
    color: '#8b5cf6',
    description: 'Exchange Traded Funds'
  },
  indices: {
    label: 'Indices',
    icon: Globe,
    color: '#ec4899',
    description: 'Market Indices (S&P 500, NASDAQ, etc.)'
  },
  commodities: {
    label: 'Commodities',
    icon: Package,
    color: '#f97316',
    description: 'Gold, Silver, Oil, etc.'
  },
  interest_rates: {
    label: 'Interest Rates',
    icon: Activity,
    color: '#14b8a6',
    description: 'G20 Central Bank Interest Rates'
  }
};

const TIMEFRAMES = {
  weekly: { label: 'Weekly', interval: '1week' },
  daily: { label: 'Daily', interval: '1day' },
  hourly: { label: 'Hourly', interval: '1h' },
  '5min': { label: '5 Min', interval: '5min' }
};

// All technical indicators to display
const INDICATOR_GROUPS = {
  momentum: {
    label: 'Momentum',
    indicators: ['rsi', 'stoch_k', 'stoch_d', 'willr', 'cci', 'roc', 'mom', 'ao', 'uo']
  },
  trend: {
    label: 'Trend',
    indicators: ['sma_20', 'sma_50', 'sma_200', 'ema_20', 'ema_50', 'adx', 'plus_di', 'minus_di', 'psar']
  },
  volatility: {
    label: 'Volatility',
    indicators: ['atr', 'bbands_upper', 'bbands_middle', 'bbands_lower', 'bbands_width']
  },
  volume: {
    label: 'Volume',
    indicators: ['obv', 'cmf', 'mfi', 'vwap']
  },
  macd: {
    label: 'MACD',
    indicators: ['macd', 'macd_signal', 'macd_hist']
  },
  pivots: {
    label: 'Pivots',
    indicators: ['pivot', 'r1', 'r2', 'r3', 's1', 's2', 's3']
  }
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-1075463475276.us-central1.run.app'
);

export default function SmartDashboard({ searchQuery, searchMethod, currentPage = 'dashboard' }) {
  const [activeAssetType, setActiveAssetType] = useState('stocks');
  const [activeTimeframe, setActiveTimeframe] = useState('daily');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortConfig, setSortConfig] = useState({ key: 'symbol', direction: 'asc' });
  const [selectedItem, setSelectedItem] = useState(null);
  const [theme, setTheme] = useState('dark');
  const [showIndicators, setShowIndicators] = useState(true);
  const [expandedIndicatorGroup, setExpandedIndicatorGroup] = useState('momentum');

  // Search state
  const [localSearchQuery, setLocalSearchQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [useAISearch, setUseAISearch] = useState(true); // AI-powered search toggle
  const [showSmartSearchBar, setShowSmartSearchBar] = useState(false); // Show enhanced AI search
  const recognitionRef = useRef(null);

  const currentTheme = themes[theme];

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let final = '';
        for (let i = 0; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            final = transcript;
          } else {
            setLocalSearchQuery(transcript);
          }
        }
        if (final) {
          setLocalSearchQuery(final);
          setIsListening(false);
          handleSearch(final);
        }
      };

      recognitionRef.current.onerror = () => setIsListening(false);
      recognitionRef.current.onend = () => setIsListening(false);
    }
  }, []);

  // Load data when asset type or timeframe changes
  useEffect(() => {
    loadData();
  }, [activeAssetType, activeTimeframe]);

  // Handle incoming search queries from parent
  useEffect(() => {
    if (searchQuery && searchQuery.trim()) {
      handleSearch(searchQuery);
    }
  }, [searchQuery]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Fetch from TwelveData BigQuery tables
      const response = await fetch(
        `${API_BASE_URL}/api/twelvedata/${activeAssetType}/${activeTimeframe}?limit=100`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success && result.data) {
        setData(result.data);
        if (result.data.length > 0) {
          // Auto-select first item with valid data (close > 0)
          const firstValidItem = result.data.find(item => {
            const close = parseFloat(item.close) || parseFloat(item.week_close) || 0;
            return close > 0;
          });
          setSelectedItem(firstValidItem || result.data[0]);
        }
      } else {
        setData([]);
        setSelectedItem(null);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      setData([]);
      setSelectedItem(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) return;

    setLoading(true);
    setSearchResults({ query, searching: true });

    // Detect asset type from query
    const queryLower = query.toLowerCase();
    let detectedAssetType = activeAssetType;

    if (queryLower.includes('stock') || queryLower.includes('equity')) {
      detectedAssetType = 'stocks';
    } else if (queryLower.includes('crypto') || queryLower.includes('bitcoin') || queryLower.includes('btc')) {
      detectedAssetType = 'crypto';
    } else if (queryLower.includes('forex') || queryLower.includes('currency')) {
      detectedAssetType = 'forex';
    } else if (queryLower.includes('etf')) {
      detectedAssetType = 'etfs';
    } else if (queryLower.includes('index') || queryLower.includes('indices')) {
      detectedAssetType = 'indices';
    } else if (queryLower.includes('commodity') || queryLower.includes('gold') || queryLower.includes('oil')) {
      detectedAssetType = 'commodities';
    }

    // Detect timeframe from query
    let detectedTimeframe = activeTimeframe;
    if (queryLower.includes('weekly')) detectedTimeframe = 'weekly';
    else if (queryLower.includes('daily')) detectedTimeframe = 'daily';
    else if (queryLower.includes('hourly') || queryLower.includes('hour')) detectedTimeframe = 'hourly';
    else if (queryLower.includes('5 minute') || queryLower.includes('5min')) detectedTimeframe = '5min';

    setActiveAssetType(detectedAssetType);
    setActiveTimeframe(detectedTimeframe);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analysis/nlp-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          asset_type: detectedAssetType,
          timeframe: detectedTimeframe
        })
      });

      const result = await response.json();

      if (result.success && result.results) {
        setData(result.results);
        setSearchResults({
          query,
          interpretation: result.interpretation,
          count: result.returned_count || result.results.length,
          totalCount: result.total_count || result.results.length,
          searching: false
        });
        if (result.results.length > 0) {
          // Auto-select first item with valid data
          const firstValidItem = result.results.find(item => {
            const close = parseFloat(item.close) || parseFloat(item.week_close) || 0;
            return close > 0;
          });
          setSelectedItem(firstValidItem || result.results[0]);
        }
      } else {
        setSearchResults({ query, error: result.error, searching: false });
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults({ query, error: error.message, searching: false });
    } finally {
      setLoading(false);
    }
  };

  const startListening = () => {
    if (recognitionRef.current) {
      setIsListening(true);
      setLocalSearchQuery('');
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleSort = (key) => {
    const direction = sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc';
    setSortConfig({ key, direction });

    const sorted = [...data].sort((a, b) => {
      const aVal = a[key] ?? 0;
      const bVal = b[key] ?? 0;
      if (aVal < bVal) return direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return direction === 'asc' ? 1 : -1;
      return 0;
    });
    setData(sorted);
  };

  const formatValue = (value, decimals = 2) => {
    if (value === null || value === undefined) return 'N/A';
    return typeof value === 'number' ? value.toFixed(decimals) : value;
  };

  const getIndicatorColor = (indicator, value) => {
    if (value === null || value === undefined) return currentTheme.textMuted;

    // RSI coloring
    if (indicator === 'rsi') {
      if (value < 30) return '#ef4444'; // Oversold - Red
      if (value > 70) return '#10b981'; // Overbought - Green
      return currentTheme.text;
    }

    // MACD coloring
    if (indicator === 'macd_hist') {
      return value > 0 ? '#10b981' : '#ef4444';
    }

    // ADX coloring
    if (indicator === 'adx') {
      if (value > 25) return '#10b981'; // Strong trend
      return currentTheme.textMuted; // Weak trend
    }

    return currentTheme.text;
  };

  // Handle AI Smart Search results
  const handleAISearchResults = (results) => {
    if (results?.results?.data) {
      setData(results.results.data);
      setSearchResults({
        query: results.query,
        interpretation: results.ai_analysis?.explanation || results.ai_analysis?.query_understanding?.intent,
        count: results.results.data.length,
        searching: false,
        aiPowered: true
      });
      if (results.results.data.length > 0) {
        // Auto-select first item with valid data
        const firstValidItem = results.results.data.find(item => {
          const close = parseFloat(item.close) || parseFloat(item.week_close) || 0;
          return close > 0;
        });
        setSelectedItem(firstValidItem || results.results.data[0]);
      }
    }
  };

  // Handle symbol selection from AI search
  const handleAISymbolSelect = (symbol, assetType) => {
    // Find the item in current data or search for it
    const item = data.find(d => d.symbol === symbol);
    if (item) {
      setSelectedItem(item);
    }
    // Switch asset type if different
    if (assetType && ASSET_TYPES[assetType]) {
      setActiveAssetType(assetType);
    }
  };

  return (
    <div style={{ padding: '24px', background: currentTheme.background, minHeight: '100vh' }}>
      {/* AI-Powered Smart Search Header */}
      {showSmartSearchBar && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={20} color="#8b5cf6" />
              <span style={{ color: currentTheme.text, fontWeight: '600' }}>AI Smart Search</span>
              <span style={{
                fontSize: '11px',
                background: '#8b5cf61a',
                color: '#8b5cf6',
                padding: '4px 8px',
                borderRadius: '12px'
              }}>
                Powered by Gemini AI
              </span>
            </div>
            <button
              onClick={() => setShowSmartSearchBar(false)}
              style={{
                background: 'none',
                border: 'none',
                color: currentTheme.textMuted,
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              <X size={18} />
            </button>
          </div>
          <SmartSearchBar
            onResults={handleAISearchResults}
            onSymbolSelect={handleAISymbolSelect}
            theme={theme}
            currentPage={currentPage}
          />
        </div>
      )}

      {/* Standard Smart Search Bar */}
      <div style={{
        background: currentTheme.cardBg,
        borderRadius: '16px',
        padding: '20px',
        marginBottom: '24px',
        border: `1px solid ${currentTheme.cardBorder}`
      }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <input
              type="text"
              placeholder={isListening ? "Listening..." : "Ask anything... (e.g., 'oversold stocks', 'top crypto gainers', 'gold price')"}
              value={localSearchQuery}
              onChange={(e) => setLocalSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch(localSearchQuery)}
              style={{
                width: '100%',
                padding: '16px 180px 16px 20px',
                background: theme === 'dark' ? '#1e293b' : 'white',
                border: isListening ? '2px solid #10b981' : `2px solid ${currentTheme.cardBorder}`,
                borderRadius: '12px',
                color: currentTheme.text,
                fontSize: '16px',
                outline: 'none'
              }}
            />
            <div style={{
              position: 'absolute',
              right: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              display: 'flex',
              gap: '8px'
            }}>
              {/* AI Search Toggle */}
              <button
                onClick={() => setShowSmartSearchBar(!showSmartSearchBar)}
                title="AI Smart Search"
                style={{
                  background: showSmartSearchBar ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' : currentTheme.cardBg,
                  border: `1px solid ${showSmartSearchBar ? '#8b5cf6' : currentTheme.cardBorder}`,
                  color: showSmartSearchBar ? 'white' : currentTheme.text,
                  padding: '10px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <Sparkles size={20} />
              </button>
              <button
                onClick={isListening ? stopListening : startListening}
                style={{
                  background: isListening ? '#ef4444' : '#10b981',
                  border: 'none',
                  color: 'white',
                  padding: '10px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                {isListening ? <MicOff size={20} /> : <Mic size={20} />}
              </button>
              <button
                onClick={() => handleSearch(localSearchQuery)}
                disabled={!localSearchQuery.trim()}
                style={{
                  background: localSearchQuery.trim() ? '#3b82f6' : '#64748b',
                  border: 'none',
                  color: 'white',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  cursor: localSearchQuery.trim() ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Search size={20} />
              </button>
            </div>
          </div>

          {/* Theme Toggle */}
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            style={{
              background: currentTheme.cardBg,
              border: `1px solid ${currentTheme.cardBorder}`,
              color: currentTheme.text,
              padding: '12px',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>

        {/* Search Results Info */}
        {searchResults && !searchResults.searching && (
          <div style={{
            marginTop: '12px',
            padding: '12px 16px',
            background: searchResults.error ? '#ef44441a' : searchResults.aiPowered ? '#8b5cf61a' : '#10b9811a',
            borderRadius: '8px',
            fontSize: '14px',
            color: searchResults.error ? '#ef4444' : searchResults.aiPowered ? '#8b5cf6' : '#10b981',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            {searchResults.aiPowered && <Sparkles size={16} />}
            {searchResults.error
              ? `Error: ${searchResults.error}`
              : `Found ${searchResults.totalCount || searchResults.count} results (showing ${searchResults.count}) for "${searchResults.interpretation || searchResults.query}"`
            }
          </div>
        )}
      </div>

      {/* 7 Market Types Section Header */}
      <div style={{
        background: `linear-gradient(135deg, ${currentTheme.cardBg} 0%, ${currentTheme.background} 100%)`,
        borderRadius: '12px',
        padding: '16px 20px',
        marginBottom: '16px',
        border: `1px solid ${currentTheme.cardBorder}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <BarChart3 size={22} color="white" />
          </div>
          <div>
            <h2 style={{ color: currentTheme.text, margin: 0, fontSize: '18px', fontWeight: '700' }}>
              7 Market Types Dashboard
            </h2>
            <p style={{ color: currentTheme.textMuted, margin: '4px 0 0 0', fontSize: '13px' }}>
              Stocks • Crypto • Forex • ETFs • Indices • Commodities • Interest Rates
            </p>
          </div>
        </div>
        <div style={{
          padding: '6px 14px',
          background: '#10b98122',
          borderRadius: '20px',
          color: '#10b981',
          fontSize: '12px',
          fontWeight: '600'
        }}>
          Live Data
        </div>
      </div>

      {/* Asset Type Tabs */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '16px',
        flexWrap: 'wrap'
      }}>
        {Object.entries(ASSET_TYPES).map(([key, config]) => {
          const Icon = config.icon;
          const isActive = activeAssetType === key;
          return (
            <button
              key={key}
              onClick={() => setActiveAssetType(key)}
              style={{
                padding: '12px 20px',
                background: isActive ? config.color : currentTheme.cardBg,
                color: isActive ? 'white' : currentTheme.text,
                border: `1px solid ${isActive ? config.color : currentTheme.cardBorder}`,
                borderRadius: '10px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: isActive ? '600' : '400',
                transition: 'all 0.2s'
              }}
            >
              <Icon size={18} />
              {config.label}
            </button>
          );
        })}
      </div>

      {/* Timeframe Tabs */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '16px'
      }}>
        {Object.entries(TIMEFRAMES).map(([key, config]) => {
          const isActive = activeTimeframe === key;
          return (
            <button
              key={key}
              onClick={() => setActiveTimeframe(key)}
              style={{
                padding: '10px 20px',
                background: isActive ? '#8b5cf6' : currentTheme.cardBg,
                color: isActive ? 'white' : currentTheme.text,
                border: `1px solid ${isActive ? '#8b5cf6' : currentTheme.cardBorder}`,
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: isActive ? '600' : '400'
              }}
            >
              {config.label}
            </button>
          );
        })}
      </div>

      {/* ============================================= */}
      {/* STOCK SELECTOR & SELECTED STOCK INFO SECTION */}
      {/* ============================================= */}
      <div style={{
        background: currentTheme.cardBg,
        borderRadius: '16px',
        padding: '20px',
        marginBottom: '24px',
        border: `1px solid ${currentTheme.cardBorder}`
      }}>
        {/* Row 1: Stock Selector Dropdown */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          marginBottom: '16px',
          flexWrap: 'wrap'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: currentTheme.textSecondary, fontSize: '14px', fontWeight: '600' }}>
              Select {ASSET_TYPES[activeAssetType]?.label || 'Asset'}:
            </span>
          </div>

          {/* Stock Selector Dropdown */}
          <select
            value={selectedItem?.symbol || selectedItem?.pair || ''}
            onChange={(e) => {
              const item = data.find(d => (d.symbol || d.pair) === e.target.value);
              if (item) setSelectedItem(item);
            }}
            style={{
              padding: '12px 40px 12px 16px',
              fontSize: '16px',
              fontWeight: '600',
              background: theme === 'dark' ? '#1e293b' : 'white',
              color: currentTheme.text,
              border: `2px solid ${currentTheme.primary}`,
              borderRadius: '10px',
              cursor: 'pointer',
              minWidth: '200px',
              appearance: 'none',
              backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%236366f1' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right 12px center',
              backgroundSize: '20px'
            }}
          >
            {loading ? (
              <option>Loading...</option>
            ) : data.length === 0 ? (
              <option>No data available</option>
            ) : (
              data.map((item, index) => (
                <option key={index} value={item.symbol || item.pair}>
                  {item.symbol || item.pair} {item.name ? `- ${item.name}` : ''}
                </option>
              ))
            )}
          </select>

          {/* Total Count Badge */}
          <div style={{
            padding: '8px 16px',
            background: '#3b82f622',
            borderRadius: '20px',
            color: '#3b82f6',
            fontSize: '13px',
            fontWeight: '600'
          }}>
            {data.length} {ASSET_TYPES[activeAssetType]?.label || 'items'} available
          </div>
        </div>

        {/* Row 2: Selected Stock Info Header */}
        {selectedItem && (
          <div style={{
            background: `linear-gradient(135deg, ${ASSET_TYPES[activeAssetType]?.color || '#3b82f6'}22 0%, ${currentTheme.background} 100%)`,
            borderRadius: '12px',
            padding: '20px',
            border: `1px solid ${ASSET_TYPES[activeAssetType]?.color || '#3b82f6'}44`
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '16px'
            }}>
              {/* Left: Ticker Symbol & Name */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '12px',
                  background: `linear-gradient(135deg, ${ASSET_TYPES[activeAssetType]?.color || '#3b82f6'} 0%, ${ASSET_TYPES[activeAssetType]?.color || '#3b82f6'}cc 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '18px',
                  fontWeight: '700'
                }}>
                  {(selectedItem.symbol || selectedItem.pair || '??').substring(0, 3)}
                </div>
                <div>
                  <div style={{
                    fontSize: '24px',
                    fontWeight: '700',
                    color: currentTheme.text,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    {selectedItem.symbol || selectedItem.pair}
                    <span style={{
                      fontSize: '12px',
                      padding: '4px 10px',
                      background: ASSET_TYPES[activeAssetType]?.color || '#3b82f6',
                      color: 'white',
                      borderRadius: '12px',
                      fontWeight: '600'
                    }}>
                      {TIMEFRAMES[activeTimeframe]?.label}
                    </span>
                  </div>
                  <div style={{ color: currentTheme.textSecondary, fontSize: '14px', marginTop: '4px' }}>
                    {selectedItem.name || ASSET_TYPES[activeAssetType]?.description || 'Market Data'}
                  </div>
                </div>
              </div>

              {/* Center: Price Info */}
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '32px',
                  fontWeight: '700',
                  color: currentTheme.text
                }}>
                  ${selectedItem.close?.toFixed(2) || selectedItem.price?.toFixed(2) || 'N/A'}
                </div>
                <div style={{
                  fontSize: '14px',
                  color: (selectedItem.change_percent || selectedItem.roc || 0) >= 0 ? '#10b981' : '#ef4444',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px'
                }}>
                  {(selectedItem.change_percent || selectedItem.roc || 0) >= 0 ? (
                    <TrendingUp size={16} />
                  ) : (
                    <TrendingDown size={16} />
                  )}
                  {(selectedItem.change_percent || selectedItem.roc || 0) >= 0 ? '+' : ''}
                  {(selectedItem.change_percent || selectedItem.roc || 0)?.toFixed(2)}%
                </div>
              </div>

              {/* Right: Key Stats */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '16px'
              }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ color: currentTheme.textMuted, fontSize: '11px', textTransform: 'uppercase' }}>Open</div>
                  <div style={{ color: currentTheme.text, fontSize: '14px', fontWeight: '600' }}>
                    ${selectedItem.open?.toFixed(2) || 'N/A'}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ color: currentTheme.textMuted, fontSize: '11px', textTransform: 'uppercase' }}>High</div>
                  <div style={{ color: '#10b981', fontSize: '14px', fontWeight: '600' }}>
                    ${selectedItem.high?.toFixed(2) || 'N/A'}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ color: currentTheme.textMuted, fontSize: '11px', textTransform: 'uppercase' }}>Low</div>
                  <div style={{ color: '#ef4444', fontSize: '14px', fontWeight: '600' }}>
                    ${selectedItem.low?.toFixed(2) || 'N/A'}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ color: currentTheme.textMuted, fontSize: '11px', textTransform: 'uppercase' }}>RSI</div>
                  <div style={{
                    color: selectedItem.rsi < 30 ? '#ef4444' : selectedItem.rsi > 70 ? '#10b981' : currentTheme.text,
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    {selectedItem.rsi?.toFixed(1) || 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: showIndicators ? '1fr 400px' : '1fr', gap: '24px', maxWidth: '100%', overflow: 'hidden' }}>
        {/* Left Column - Chart and Data Table */}
        <div style={{ minWidth: 0, overflow: 'hidden' }}>
          {/* Chart Display - Full TradingView Chart */}
          {!loading && selectedItem && (
            <div style={{ marginBottom: '24px' }}>
              {(() => {
                const close = parseFloat(selectedItem.close) || parseFloat(selectedItem.week_close) || 0;
                const hasValidData = close > 0;

                if (!hasValidData) {
                  // Show informative message instead of error
                  return (
                    <div style={{
                      padding: '40px 24px',
                      textAlign: 'center',
                      background: currentTheme.cardBg,
                      borderRadius: '12px',
                      border: `1px solid ${currentTheme.cardBorder}`,
                    }}>
                      <div style={{
                        fontSize: '48px',
                        marginBottom: '16px',
                        opacity: 0.5
                      }}>
                        📊
                      </div>
                      <div style={{
                        color: currentTheme.text,
                        fontSize: '18px',
                        fontWeight: '600',
                        marginBottom: '8px'
                      }}>
                        No {TIMEFRAMES[activeTimeframe]?.label} Data for {selectedItem.symbol || selectedItem.pair}
                      </div>
                      <div style={{
                        color: currentTheme.textMuted,
                        fontSize: '14px',
                        marginBottom: '16px'
                      }}>
                        This {ASSET_TYPES[activeAssetType]?.label?.toLowerCase() || 'asset'} doesn't have {activeTimeframe} data available yet.
                      </div>
                      <div style={{
                        display: 'flex',
                        gap: '8px',
                        justifyContent: 'center',
                        flexWrap: 'wrap'
                      }}>
                        {Object.entries(TIMEFRAMES).filter(([key]) => key !== activeTimeframe).map(([key, config]) => (
                          <button
                            key={key}
                            onClick={() => setActiveTimeframe(key)}
                            style={{
                              padding: '8px 16px',
                              background: currentTheme.cardBg,
                              border: `1px solid ${currentTheme.cardBorder}`,
                              borderRadius: '6px',
                              color: currentTheme.text,
                              cursor: 'pointer',
                              fontSize: '13px'
                            }}
                          >
                            Try {config.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                }

                return (
                  <TradingViewChart
                    symbol={selectedItem.symbol || selectedItem.pair}
                    assetType={activeAssetType}
                    timeframe={activeTimeframe === '5min' ? '5min' : activeTimeframe === 'hourly' ? 'hourly' : activeTimeframe === 'weekly' ? 'weekly' : 'daily'}
                    theme={theme}
                  />
                );
              })()}
            </div>
          )}

          {/* Data Table - All Fields Scrollable */}
          <div style={{
            background: currentTheme.cardBg,
            borderRadius: '16px',
            padding: '20px',
            border: `1px solid ${currentTheme.cardBorder}`
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ color: currentTheme.primary, fontSize: '18px', margin: 0 }}>
                {ASSET_TYPES[activeAssetType]?.label || activeAssetType} - {TIMEFRAMES[activeTimeframe].label} ({data.length} items)
              </h3>
              <button
                onClick={() => setShowIndicators(!showIndicators)}
                style={{
                  background: showIndicators ? '#10b981' : currentTheme.cardBg,
                  color: showIndicators ? 'white' : currentTheme.text,
                  border: `1px solid ${showIndicators ? '#10b981' : currentTheme.cardBorder}`,
                  padding: '8px 16px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {showIndicators ? 'Hide' : 'Show'} Indicators Panel
              </button>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px', color: currentTheme.text }}>
                Loading {ASSET_TYPES[activeAssetType]?.label || activeAssetType} data...
              </div>
            ) : data.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: currentTheme.textMuted }}>
                No data available for {ASSET_TYPES[activeAssetType]?.label || activeAssetType} - {TIMEFRAMES[activeTimeframe].label}
              </div>
            ) : (
              <>
                {/* Single Unified Table with Sticky First Columns */}
                <div style={{
                  overflowX: 'auto',
                  overflowY: 'auto',
                  maxHeight: '450px',
                  border: `1px solid ${currentTheme.cardBorder}`,
                  borderRadius: '6px',
                }}>
                  <table style={{ borderCollapse: 'separate', borderSpacing: 0, fontSize: '10px', width: '100%', minWidth: '900px' }}>
                    <thead style={{ position: 'sticky', top: 0, zIndex: 20 }}>
                      <tr style={{ background: theme === 'dark' ? '#0f172a' : '#e2e8f0' }}>
                        <th style={{ position: 'sticky', left: 0, zIndex: 30, width: '26px', padding: '6px 3px', textAlign: 'center', background: theme === 'dark' ? '#0f172a' : '#e2e8f0', borderBottom: `2px solid ${currentTheme.cardBorder}`, borderRight: `1px solid ${currentTheme.cardBorder}` }}></th>
                        <th onClick={() => handleSort('symbol')} style={{ position: 'sticky', left: '26px', zIndex: 30, width: '55px', padding: '6px 4px', textAlign: 'left', color: currentTheme.text, cursor: 'pointer', fontSize: '9px', fontWeight: '700', background: theme === 'dark' ? '#0f172a' : '#e2e8f0', borderBottom: `2px solid ${currentTheme.cardBorder}`, borderRight: `2px solid ${currentTheme.primary}` }}>SYM</th>
                        <th onClick={() => handleSort('close')} style={{ width: '55px', padding: '6px 4px', textAlign: 'right', color: currentTheme.text, cursor: 'pointer', fontSize: '9px', fontWeight: '700', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>CLOSE</th>
                        <th onClick={() => handleSort('open')} style={{ width: '50px', padding: '6px 4px', textAlign: 'right', color: currentTheme.textMuted, cursor: 'pointer', fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>OPEN</th>
                        <th onClick={() => handleSort('high')} style={{ width: '50px', padding: '6px 4px', textAlign: 'right', color: '#10b981', cursor: 'pointer', fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>HIGH</th>
                        <th onClick={() => handleSort('low')} style={{ width: '50px', padding: '6px 4px', textAlign: 'right', color: '#ef4444', cursor: 'pointer', fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>LOW</th>
                        <th style={{ width: '52px', padding: '6px 4px', textAlign: 'right', color: '#22c55e', fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>BUY</th>
                        <th style={{ width: '52px', padding: '6px 4px', textAlign: 'right', color: '#f59e0b', fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>SELL</th>
                        <th style={{ width: '45px', padding: '6px 4px', textAlign: 'right', color: currentTheme.textMuted, fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>H-L</th>
                        <th style={{ width: '38px', padding: '6px 4px', textAlign: 'right', color: currentTheme.textMuted, fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>%</th>
                        <th onClick={() => handleSort('rsi')} style={{ width: '36px', padding: '6px 4px', textAlign: 'right', color: '#a855f7', cursor: 'pointer', fontSize: '9px', fontWeight: '700', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>RSI</th>
                        <th onClick={() => handleSort('macd')} style={{ width: '52px', padding: '6px 4px', textAlign: 'right', color: '#3b82f6', cursor: 'pointer', fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>MACD</th>
                        <th style={{ width: '52px', padding: '6px 4px', textAlign: 'right', color: '#f97316', fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>SIG</th>
                        <th style={{ width: '42px', padding: '6px 4px', textAlign: 'center', fontSize: '9px', fontWeight: '700', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>B/S</th>
                        <th onClick={() => handleSort('name')} style={{ minWidth: '140px', padding: '6px 4px', textAlign: 'left', color: currentTheme.textMuted, cursor: 'pointer', fontSize: '9px', fontWeight: '600', borderBottom: `2px solid ${currentTheme.cardBorder}` }}>NAME</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(() => {
                        const uniqueSymbols = new Map();
                        data.forEach(item => {
                          const sym = item.symbol || item.pair;
                          if (!uniqueSymbols.has(sym)) uniqueSymbols.set(sym, item);
                        });
                        return Array.from(uniqueSymbols.values());
                      })().map((item, index) => {
                        const isSelected = (selectedItem?.symbol || selectedItem?.pair) === (item.symbol || item.pair);
                        const high = parseFloat(item.high) || parseFloat(item.week_high) || 0;
                        const low = parseFloat(item.low) || parseFloat(item.week_low) || 0;
                        const open = parseFloat(item.open) || parseFloat(item.week_open) || 0;
                        const close = parseFloat(item.close) || parseFloat(item.week_close) || 0;
                        const hiLo = high - low;
                        const pctHiLo = low > 0 ? ((hiLo / low) * 100) : 0;
                        const volume = parseFloat(item.volume) || parseFloat(item.week_volume) || 0;
                        const isBullish = close >= open;
                        const buyVol = isBullish ? volume : volume * 0.4;
                        const sellVol = isBullish ? volume * 0.4 : volume;
                        const macd = parseFloat(item.macd) || 0;
                        const macdSignal = parseFloat(item.macd_signal) || 0;
                        const macdHist = macd - macdSignal;
                        const rsi = parseFloat(item.rsi) || null;
                        const fmtVol = (v) => v >= 1e6 ? `${(v/1e6).toFixed(1)}M` : v >= 1e3 ? `${(v/1e3).toFixed(0)}K` : v.toFixed(0);
                        const fmtP = (p) => p >= 1000 ? p.toFixed(0) : p >= 100 ? p.toFixed(1) : p.toFixed(2);
                        const rowBg = isSelected ? `${currentTheme.primary}33` : index % 2 === 0 ? 'transparent' : `${currentTheme.cardBorder}18`;
                        const stickyBg = isSelected ? (theme === 'dark' ? '#1e3a5f' : '#dbeafe') : (theme === 'dark' ? (index % 2 === 0 ? '#1e293b' : '#273548') : (index % 2 === 0 ? '#f8fafc' : '#f1f5f9'));

                        return (
                          <tr key={item.symbol || item.pair || index} onClick={() => setSelectedItem(item)} style={{ background: rowBg, cursor: 'pointer', height: '28px' }}>
                            <td style={{ position: 'sticky', left: 0, zIndex: 10, padding: '4px 3px', textAlign: 'center', background: stickyBg, borderBottom: `1px solid ${currentTheme.cardBorder}22`, borderRight: `1px solid ${currentTheme.cardBorder}` }}>
                              <input type="radio" name="stockSelector" checked={isSelected} onChange={() => setSelectedItem(item)} style={{ cursor: 'pointer', accentColor: '#10b981', width: '12px', height: '12px', margin: 0 }} />
                            </td>
                            <td style={{ position: 'sticky', left: '26px', zIndex: 10, padding: '4px', color: isSelected ? currentTheme.primary : currentTheme.text, fontWeight: '700', fontSize: '10px', background: stickyBg, borderBottom: `1px solid ${currentTheme.cardBorder}22`, borderRight: `2px solid ${currentTheme.primary}44` }}>{item.symbol || item.pair || '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: close > 0 ? currentTheme.text : currentTheme.textMuted, fontWeight: '600', fontSize: '10px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{close > 0 ? fmtP(close) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: currentTheme.textMuted, fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{open > 0 ? fmtP(open) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: '#10b981', fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{high > 0 ? fmtP(high) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: '#ef4444', fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{low > 0 ? fmtP(low) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: '#22c55e', fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{volume > 0 ? fmtVol(buyVol) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: '#f59e0b', fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{volume > 0 ? fmtVol(sellVol) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: currentTheme.textMuted, fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{hiLo > 0 ? hiLo.toFixed(2) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: pctHiLo > 3 ? '#f59e0b' : currentTheme.textMuted, fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{pctHiLo > 0 ? pctHiLo.toFixed(1) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: rsi === null ? currentTheme.textMuted : rsi < 30 ? '#ef4444' : rsi > 70 ? '#10b981' : '#a855f7', fontWeight: rsi !== null && (rsi < 30 || rsi > 70) ? '700' : '400', fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{rsi !== null ? rsi.toFixed(0) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: '#3b82f6', fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{macd !== 0 ? macd.toFixed(2) : '-'}</td>
                            <td style={{ padding: '4px', textAlign: 'right', color: '#f97316', fontSize: '9px', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{macdSignal !== 0 ? macdSignal.toFixed(2) : '-'}</td>
                            <td style={{ padding: '3px', textAlign: 'center', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{close > 0 ? <span style={{ display: 'inline-block', padding: '2px 6px', borderRadius: '3px', background: macdHist > 0 ? '#10b98144' : '#ef444444', color: macdHist > 0 ? '#10b981' : '#ef4444', fontWeight: '700', fontSize: '8px' }}>{macdHist > 0 ? 'BUY' : 'SELL'}</span> : '-'}</td>
                            <td style={{ padding: '4px', color: currentTheme.textMuted, fontSize: '9px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', borderBottom: `1px solid ${currentTheme.cardBorder}22` }}>{item.name || '-'}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {/* Scroll hint */}
            {data.length > 0 && (
              <div style={{
                marginTop: '8px',
                fontSize: '11px',
                color: currentTheme.textMuted,
                textAlign: 'center'
              }}>
                ← Scroll horizontally to see all {Object.keys(data[0]).length} fields →
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Indicators Panel */}
        {showIndicators && selectedItem && (
          <div style={{
            background: currentTheme.cardBg,
            borderRadius: '16px',
            padding: '20px',
            border: `1px solid ${currentTheme.cardBorder}`,
            maxHeight: 'calc(100vh - 200px)',
            overflowY: 'auto'
          }}>
            <h3 style={{ color: currentTheme.primary, fontSize: '18px', margin: '0 0 16px 0' }}>
              Technical Indicators
            </h3>
            <p style={{ color: currentTheme.textSecondary, fontSize: '14px', margin: '0 0 20px 0' }}>
              {selectedItem.symbol || selectedItem.pair}
            </p>

            {Object.entries(INDICATOR_GROUPS).map(([groupKey, group]) => (
              <div key={groupKey} style={{ marginBottom: '12px' }}>
                <button
                  onClick={() => setExpandedIndicatorGroup(expandedIndicatorGroup === groupKey ? null : groupKey)}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    background: expandedIndicatorGroup === groupKey ? `${currentTheme.primary}22` : 'transparent',
                    border: `1px solid ${currentTheme.cardBorder}`,
                    borderRadius: '8px',
                    color: currentTheme.text,
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  {group.label}
                  {expandedIndicatorGroup === groupKey ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </button>

                {expandedIndicatorGroup === groupKey && (
                  <div style={{
                    padding: '12px',
                    background: currentTheme.background,
                    borderRadius: '0 0 8px 8px',
                    marginTop: '-1px'
                  }}>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        {group.indicators.map((indicator) => (
                          <tr key={indicator} style={{ borderBottom: `1px solid ${currentTheme.cardBorder}` }}>
                            <td style={{ padding: '8px 4px', color: currentTheme.textSecondary, textTransform: 'uppercase' }}>
                              {indicator.replace(/_/g, ' ')}
                            </td>
                            <td style={{
                              padding: '8px 4px',
                              textAlign: 'right',
                              fontWeight: '600',
                              color: getIndicatorColor(indicator, selectedItem[indicator])
                            }}>
                              {formatValue(selectedItem[indicator], indicator.includes('macd') ? 4 : 2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))}

            {/* Signals Summary */}
            <div style={{
              marginTop: '20px',
              padding: '16px',
              background: currentTheme.background,
              borderRadius: '12px'
            }}>
              <h4 style={{ color: currentTheme.text, margin: '0 0 12px 0', fontSize: '14px' }}>
                Signal Summary
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{
                  padding: '12px',
                  background: selectedItem.buy_signal ? '#10b98122' : 'transparent',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div style={{ color: '#10b981', fontWeight: 'bold', fontSize: '16px' }}>
                    {selectedItem.buy_signal ? 'BUY' : '-'}
                  </div>
                  <div style={{ color: currentTheme.textMuted, fontSize: '12px' }}>Buy Signal</div>
                </div>
                <div style={{
                  padding: '12px',
                  background: selectedItem.sell_signal ? '#ef444422' : 'transparent',
                  borderRadius: '8px',
                  textAlign: 'center'
                }}>
                  <div style={{ color: '#ef4444', fontWeight: 'bold', fontSize: '16px' }}>
                    {selectedItem.sell_signal ? 'SELL' : '-'}
                  </div>
                  <div style={{ color: currentTheme.textMuted, fontSize: '12px' }}>Sell Signal</div>
                </div>
              </div>
              <div style={{
                marginTop: '12px',
                padding: '12px',
                background: currentTheme.cardBg,
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <div style={{ color: currentTheme.text, fontWeight: 'bold', fontSize: '14px' }}>
                  {selectedItem.trend_direction || 'Neutral'}
                </div>
                <div style={{ color: currentTheme.textMuted, fontSize: '12px' }}>Trend Direction</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Data Source Footer */}
      <div style={{
        marginTop: '24px',
        padding: '16px',
        background: currentTheme.cardBg,
        borderRadius: '12px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ color: currentTheme.textSecondary, fontSize: '13px' }}>Data Source:</span>
          <span style={{
            padding: '4px 12px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
            color: 'white',
            fontSize: '12px',
            fontWeight: '600'
          }}>
            TwelveData API
          </span>
        </div>
        <div style={{ color: currentTheme.textMuted, fontSize: '12px' }}>
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>
    </div>
  );
}

// Stat Box Component
function StatBox({ label, value, color, theme }) {
  return (
    <div style={{
      background: theme.background,
      padding: '12px',
      borderRadius: '8px',
      textAlign: 'center'
    }}>
      <div style={{ color: theme.textMuted, fontSize: '12px', marginBottom: '4px' }}>{label}</div>
      <div style={{ color: color || theme.text, fontWeight: '600', fontSize: '14px' }}>{value}</div>
    </div>
  );
}

// Sortable Header Component
function SortableHeader({ label, sortKey, sortConfig, onSort, theme }) {
  return (
    <th
      onClick={() => onSort(sortKey)}
      style={{
        padding: '12px',
        textAlign: 'left',
        color: theme.textSecondary,
        cursor: 'pointer',
        userSelect: 'none'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {label}
        <ArrowUpDown size={14} color={sortConfig.key === sortKey ? theme.primary : theme.textMuted} />
      </div>
    </th>
  );
}


