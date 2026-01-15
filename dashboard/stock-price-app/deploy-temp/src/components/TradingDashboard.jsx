import { useState, useEffect, useRef } from 'react';
import { TrendingUp, TrendingDown, Activity, Check, ArrowUpDown, Sun, Moon, Search, Mic, MicOff, X } from 'lucide-react';
import { createChart } from 'lightweight-charts';
import apiService, { API_BASE_URL } from '../services/api';
import marketDataService from '../services/marketData';
import AdvancedTradingChart from './AdvancedTradingChart';
import MultiPanelChart from './MultiPanelChart';
import themes from '../theme';

export default function TradingDashboard({ searchQuery, searchMethod }) {
  const [activeMarket, setActiveMarket] = useState('crypto'); // crypto or stock
  const [activeTimeframe, setActiveTimeframe] = useState('daily'); // daily, hourly, 5min
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [selectedItem, setSelectedItem] = useState(null); // Currently selected item for chart
  const [theme, setTheme] = useState('dark'); // dark or light
  const [viewMode, setViewMode] = useState('multi'); // multi or single

  // Search state
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);

  const currentTheme = themes[theme];

  // Prevent auto-loading data when actively searching
  const [isActivelySearching, setIsActivelySearching] = useState(false);

  useEffect(() => {
    if (!isActivelySearching) {
      loadData();
    }
  }, [activeMarket, activeTimeframe]);

  // Handle incoming search queries from Navigation
  useEffect(() => {
    if (searchQuery && searchQuery.trim()) {
      handleNLPSearch(searchQuery, searchMethod || 'text');
    }
  }, [searchQuery, searchMethod]);

  const loadData = async () => {
    setLoading(true);
    try {
      let allData = [];

      if (activeMarket === 'crypto') {
        // Try to fetch all crypto pairs first
        allData = await marketDataService.getAllCryptoPairs();

        // If getAllCryptoPairs returns empty, fall back to summary
        if (!allData || allData.length === 0) {
          const summary = await marketDataService.getMarketSummary('crypto');
          const combinedData = [
            ...(summary.top_gainers || []),
            ...(summary.top_losers || []),
            ...(summary.highest_volume || [])
          ];
          allData = Array.from(
            new Map(combinedData.map(item => [item.pair || item.symbol, item])).values()
          );
        }
      } else {
        // Try to fetch all stock symbols first
        allData = await marketDataService.getAllStockSymbols();

        // If getAllStockSymbols returns empty, fall back to summary
        if (!allData || allData.length === 0) {
          const summary = await marketDataService.getMarketSummary('stock');
          const combinedData = [
            ...(summary.top_gainers || []),
            ...(summary.top_losers || []),
            ...(summary.highest_volume || [])
          ];
          allData = Array.from(
            new Map(combinedData.map(item => [item.pair || item.symbol, item])).values()
          );
        }
      }

      // Sort by ROC (rate of change) descending to get top performers
      const sortedData = [...allData].sort((a, b) => (b.roc || 0) - (a.roc || 0));

      console.log('Loaded market data:', sortedData.length, 'unique pairs/symbols');
      setData(sortedData);

      // Auto-select the first item (top performer)
      if (sortedData.length > 0) {
        setSelectedItem(sortedData[0]);
      }
    } catch (error) {
      console.error('Error loading market data:', error);
      setData([]);
      setSelectedItem(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });

    const sorted = [...data].sort((a, b) => {
      if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
      if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
      return 0;
    });
    setData(sorted);
  };

  const toggleRowSelection = (index) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedRows(newSelected);
  };

  const handleRowClick = (item, index) => {
    setSelectedItem(item);
    toggleRowSelection(index);
  };

  const toggleAllRows = () => {
    if (selectedRows.size === data.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(data.map((_, index) => index)));
    }
  };

  // NLP Search handler
  const handleNLPSearch = async (query, inputMethod = 'text') => {
    if (!query.trim()) {
      console.warn('❌ Empty query, skipping search');
      return;
    }

    console.log('🔍 ======= STARTING NLP SEARCH =======');
    console.log('📝 Query:', query);
    console.log('🎤 Input method:', inputMethod);
    setIsSearching(true);
    setLoading(true);
    setIsActivelySearching(true); // Prevent loadData() from interfering

    // Detect timeframe from query
    const queryLower = query.toLowerCase();
    let detectedTimeframe = null;
    let detectedViewMode = 'multi'; // Default to multi-panel

    if (queryLower.includes('daily')) {
      detectedTimeframe = 'daily';
      detectedViewMode = 'single';
    } else if (queryLower.includes('hourly') || queryLower.includes('hour')) {
      detectedTimeframe = 'hourly';
      detectedViewMode = 'single';
    } else if (queryLower.includes('5 minute') || queryLower.includes('5min') || queryLower.includes('5-minute')) {
      detectedTimeframe = '5min';
      detectedViewMode = 'single';
    }

    // Apply detected timeframe and view mode
    if (detectedTimeframe) {
      console.log(`📅 Detected timeframe: ${detectedTimeframe}, switching to ${detectedViewMode} view`);
      setActiveTimeframe(detectedTimeframe);
      setViewMode(detectedViewMode);
    } else {
      console.log('📊 No specific timeframe detected, using multi-panel view');
      setViewMode('multi');
    }

    // Detect market type (crypto vs stock)
    if (queryLower.includes('crypto') || queryLower.includes('cryptocurrency') || queryLower.includes('bitcoin') || queryLower.includes('btc') || queryLower.includes('eth')) {
      setActiveMarket('crypto');
    } else if (queryLower.includes('stock') || queryLower.includes('equity') || queryLower.includes('equities')) {
      setActiveMarket('stock');
    }

    try {
      console.log('🌐 Making API call to NLP endpoint...');
      const response = await fetch(`${API_BASE_URL}/api/analysis/nlp-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: query,
          input_method: inputMethod,
          session_id: sessionId,
          user_id: null,
          email: null
        })
      });

      console.log('📡 API Response status:', response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`API returned ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('📊 Full NLP Response:', JSON.stringify(result, null, 2));
      console.log('🔎 Generated SQL:', result.sql || result.generated_sql);
      console.log('📝 Interpretation:', result.interpretation);
      console.log('📦 Results count:', result.results?.length || 0);
      console.log('📋 Table queried:', result.table);

      if (result.success) {
        setSearchResults(result);
        console.log(`✅ NLP query completed. Found ${result.results?.length || 0} results`);

        // Update the data table with search results
        if (result.results && result.results.length > 0) {
          console.log('First result:', result.results[0]);
          console.log('Setting data and selected item...');
          setData(result.results);
          // Auto-select first result
          setSelectedItem(result.results[0]);
          console.log('Data and selected item set successfully');
        } else {
          console.warn('⚠️ No results from NLP query!');
          console.warn('Query:', query);
          console.warn('SQL:', result.sql);
          console.warn('Table:', result.table);
          console.warn('This might mean: 1) No data matches the criteria, or 2) Table is empty');
          // Set empty data instead of loading default
          setData([]);
          setSelectedItem(null);
        }
        // Reset flag after successfully setting data
        setIsActivelySearching(false);
      } else {
        console.error('❌ Search failed:', result.error);
        alert(`Search failed: ${result.error || 'Unknown error'}`);
        setIsActivelySearching(false);
      }
    } catch (error) {
      console.error('❌ Error performing NLP search:', error);
      alert(`Error: ${error.message}`);
      setIsActivelySearching(false);
    } finally {
      setIsSearching(false);
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', background: currentTheme.background, minHeight: '100vh' }}>
      {/* Header with Market Tabs and Theme Toggle */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        borderBottom: `2px solid ${currentTheme.cardBorder}`
      }}>
        {/* Market Tabs */}
        <div style={{ display: 'flex', gap: '16px' }}>
        <button
          onClick={() => setActiveMarket('crypto')}
          style={{
            padding: '16px 32px',
            background: activeMarket === 'crypto'
              ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
              : 'transparent',
            color: 'white',
            border: 'none',
            borderRadius: '12px 12px 0 0',
            fontSize: '18px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s',
            borderBottom: activeMarket === 'crypto' ? '3px solid #10b981' : '3px solid transparent'
          }}
        >
          🪙 Cryptocurrency
        </button>
        <button
          onClick={() => setActiveMarket('stock')}
          style={{
            padding: '16px 32px',
            background: activeMarket === 'stock'
              ? 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
              : 'transparent',
            color: 'white',
            border: 'none',
            borderRadius: '12px 12px 0 0',
            fontSize: '18px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s',
            borderBottom: activeMarket === 'stock' ? '3px solid #3b82f6' : '3px solid transparent'
          }}
        >
          📈 Stocks
        </button>
        </div>

        {/* Theme Selector and View Mode Toggle */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {/* Theme Toggle */}
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            style={{
              padding: '12px 20px',
              background: currentTheme.cardBg,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            {theme === 'dark' ? 'Light' : 'Dark'} Mode
          </button>

          {/* View Mode Toggle */}
          <button
            onClick={() => setViewMode(viewMode === 'multi' ? 'single' : 'multi')}
            style={{
              padding: '12px 20px',
              background: currentTheme.primary,
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
          >
            {viewMode === 'multi' ? 'Single' : 'Multi'} Panel View
          </button>
        </div>
      </div>

      {/* Timeframe Tabs - Only show in single panel mode */}
      {viewMode === 'single' && (
        <div style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '24px'
        }}>
          <button
            onClick={() => setActiveTimeframe('daily')}
            style={{
              padding: '12px 24px',
              background: activeTimeframe === 'daily'
                ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'
                : currentTheme.cardBg,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
          >
            📅 Daily
          </button>
          <button
            onClick={() => setActiveTimeframe('hourly')}
            style={{
              padding: '12px 24px',
              background: activeTimeframe === 'hourly'
                ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'
                : currentTheme.cardBg,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
          >
            ⏰ Hourly
          </button>
          <button
            onClick={() => setActiveTimeframe('5min')}
            style={{
              padding: '12px 24px',
              background: activeTimeframe === '5min'
                ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'
                : currentTheme.cardBg,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.cardBorder}`,
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
          >
            ⚡ 5 Minutes
          </button>
        </div>
      )}

      {/* Chart Display - Conditional based on viewMode */}
      {!loading && selectedItem && (
        <div style={{ marginBottom: '32px' }}>
          {viewMode === 'multi' ? (
            <MultiPanelChart
              symbol={activeMarket === 'crypto' ? selectedItem.pair : selectedItem.symbol}
              marketType={activeMarket}
              theme={theme}
            />
          ) : (
            <AdvancedTradingChart
              symbol={activeMarket === 'crypto' ? selectedItem.pair : selectedItem.symbol}
              marketType={activeMarket}
              timeframe={activeTimeframe}
              theme={theme}
            />
          )}
        </div>
      )}

      {!loading && !selectedItem && data.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: currentTheme.textSecondary,
          fontSize: '16px',
          marginBottom: '32px'
        }}>
          No data available for {activeMarket === 'crypto' ? 'cryptocurrency' : 'stocks'} - {activeTimeframe}
        </div>
      )}

      {!loading && !selectedItem && data.length > 0 && (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: currentTheme.textSecondary,
          fontSize: '16px',
          marginBottom: '32px',
          background: currentTheme.cardBg,
          borderRadius: '16px',
          border: `1px solid ${currentTheme.cardBorder}`
        }}>
          Select a {activeMarket === 'crypto' ? 'cryptocurrency' : 'stock'} from the table below to view its chart
        </div>
      )}

      {/* Data Table */}
      <div style={{
        background: currentTheme.cardBg,
        borderRadius: '16px',
        padding: '24px',
        border: `1px solid ${currentTheme.cardBorder}`
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ color: currentTheme.primary, fontSize: '20px', margin: 0 }}>
            {activeMarket === 'crypto' ? 'Cryptocurrency' : 'Stock'} Data ({data.length} {activeMarket === 'crypto' ? 'pairs' : 'symbols'}) - {viewMode === 'multi' ? 'ALL TIMEFRAMES' : activeTimeframe.toUpperCase()}
          </h3>
          {searchResults && (
            <div style={{
              padding: '8px 16px',
              background: currentTheme.primary + '22',
              borderRadius: '8px',
              fontSize: '14px',
              color: currentTheme.primary
            }}>
              🔍 Search Results: {searchResults.interpretation} ({data.length} found)
            </div>
          )}
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: currentTheme.text }}>
            Loading data...
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              color: currentTheme.text,
              fontSize: '14px'
            }}>
              <thead>
                <tr style={{ borderBottom: `2px solid ${currentTheme.cardBorder}` }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>
                    <input
                      type="checkbox"
                      checked={selectedRows.size === data.length && data.length > 0}
                      onChange={toggleAllRows}
                      style={{ cursor: 'pointer', width: '18px', height: '18px' }}
                    />
                  </th>
                  <SortableHeader label={activeMarket === 'crypto' ? 'Pair' : 'Symbol'} sortKey="pair" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="Close" sortKey="close" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="Change %" sortKey="roc" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="Volume" sortKey="volume" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="RSI" sortKey="rsi" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="MACD" sortKey="macd" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                  <SortableHeader label="ADX" sortKey="adx" sortConfig={sortConfig} onSort={handleSort} theme={currentTheme} />
                </tr>
              </thead>
              <tbody>
                {data.map((item, index) => {
                  const isSelected = selectedItem &&
                    (activeMarket === 'crypto' ? selectedItem.pair === item.pair : selectedItem.symbol === item.symbol);

                  return (
                    <tr key={index} style={{
                      borderBottom: `1px solid ${currentTheme.cardBorder}`,
                      background: isSelected ? `${currentTheme.primary}33` : 'transparent',
                      cursor: 'pointer',
                      transition: 'background 0.2s'
                    }}
                    onClick={() => handleRowClick(item, index)}
                    onMouseEnter={(e) => !isSelected && (e.currentTarget.style.background = `${currentTheme.primary}1A`)}
                    onMouseLeave={(e) => !isSelected && (e.currentTarget.style.background = 'transparent')}
                    >
                    <td style={{ padding: '12px' }}>
                      <div style={{
                        width: '18px',
                        height: '18px',
                        borderRadius: '50%',
                        background: isSelected ? currentTheme.primary : 'transparent',
                        border: `2px solid ${isSelected ? currentTheme.primary : currentTheme.textMuted}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        {isSelected && <Check size={12} color="white" />}
                      </div>
                    </td>
                    <td style={{ padding: '12px', fontWeight: '600', color: currentTheme.text }}>
                      {activeMarket === 'crypto' ? item.pair : item.symbol}
                    </td>
                    <td style={{ padding: '12px', color: currentTheme.text }}>
                      ${item.close?.toFixed(2) || 'N/A'}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{
                        color: item.roc > 0 ? currentTheme.chart.upColor : currentTheme.chart.downColor,
                        fontWeight: '600'
                      }}>
                        {item.roc > 0 ? '▲' : '▼'} {item.roc?.toFixed(2)}%
                      </span>
                    </td>
                    <td style={{ padding: '12px', color: currentTheme.text }}>
                      {item.volume?.toLocaleString() || 'N/A'}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        background: item.rsi < 30 ? currentTheme.danger : item.rsi > 70 ? currentTheme.primary : currentTheme.textMuted,
                        fontSize: '12px',
                        color: 'white'
                      }}>
                        {item.rsi?.toFixed(2) || 'N/A'}
                      </span>
                    </td>
                    <td style={{ padding: '12px', color: currentTheme.text }}>
                      {item.macd?.toFixed(4) || 'N/A'}
                    </td>
                    <td style={{ padding: '12px', color: currentTheme.text }}>
                      {item.adx?.toFixed(2) || 'N/A'}
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Data Source Footer */}
        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          background: currentTheme.background,
          borderRadius: '8px',
          border: `1px solid ${currentTheme.cardBorder}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: currentTheme.textSecondary, fontSize: '13px' }}>
              Data Source:
            </span>
            <span style={{
              padding: '4px 12px',
              borderRadius: '16px',
              fontSize: '12px',
              fontWeight: '600',
              background: activeMarket === 'crypto'
                ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)'
                : 'linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%)',
              color: 'white'
            }}>
              {activeMarket === 'crypto' ? 'Kraken Pro API' : 'Twelve Data API'}
            </span>
          </div>
          <div style={{
            color: currentTheme.textMuted,
            fontSize: '12px',
            display: 'flex',
            gap: '16px',
            alignItems: 'center'
          }}>
            <span>
              {activeMarket === 'crypto'
                ? '678 trading pairs | ~1.5 years historical data'
                : '100 symbols | ~1.5 years historical data'}
            </span>
            <span style={{
              padding: '2px 8px',
              borderRadius: '4px',
              background: currentTheme.primary + '22',
              color: currentTheme.primary,
              fontSize: '11px'
            }}>
              Updated: {new Date().toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
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
        <ArrowUpDown size={16} color={sortConfig.key === sortKey ? theme.primary : theme.textMuted} />
      </div>
    </th>
  );
}

// Candlestick Chart Component
function CandlestickChart({ data, symbol, timeframe }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data) return;

    try {
      // Clean up existing chart
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }

      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: 300,
        layout: {
          background: { color: '#0f172a' },
          textColor: '#94a3b8',
        },
        grid: {
          vertLines: { color: '#1e293b' },
          horzLines: { color: '#1e293b' },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      });

      chartRef.current = chart;

      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#10b981',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
      });

      // Create single candle data point
      const timestamp = data.datetime || data.timestamp;
      const time = timestamp ? Math.floor(new Date(timestamp).getTime() / 1000) : Math.floor(Date.now() / 1000);

      const candlestickData = [{
        time: time,
        open: Number(data.open || data.close || 0),
        high: Number(data.high || data.close || 0),
        low: Number(data.low || data.close || 0),
        close: Number(data.close || 0)
      }];

      candlestickSeries.setData(candlestickData);
      chart.timeScale().fitContent();

      // Handle window resize
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
    } catch (error) {
      console.error('Error creating chart:', error);
    }
  }, [data]);

  // Calculate price change percentage
  const priceChange = data?.roc || 0;
  const isPositive = priceChange >= 0;

  return (
    <div style={{
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      borderRadius: '12px',
      padding: '16px',
      border: '1px solid #334155'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '12px'
      }}>
        <h4 style={{ color: '#10b981', fontSize: '16px', margin: 0 }}>
          {symbol}
        </h4>
        <span style={{
          color: isPositive ? '#10b981' : '#ef4444',
          fontSize: '14px',
          fontWeight: '600'
        }}>
          {isPositive ? '▲' : '▼'} {Math.abs(priceChange).toFixed(2)}%
        </span>
      </div>
      <div ref={chartContainerRef} style={{ height: '300px' }} />
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
        marginTop: '12px',
        fontSize: '12px',
        color: '#94a3b8',
        padding: '12px',
        background: '#0a0e1a',
        borderRadius: '8px'
      }}>
        <div>
          <div style={{ color: '#64748b', marginBottom: '4px' }}>Open</div>
          <div style={{ color: 'white', fontWeight: '600' }}>${Number(data?.open || data?.close || 0).toFixed(2)}</div>
        </div>
        <div>
          <div style={{ color: '#64748b', marginBottom: '4px' }}>High</div>
          <div style={{ color: '#10b981', fontWeight: '600' }}>${Number(data?.high || data?.close || 0).toFixed(2)}</div>
        </div>
        <div>
          <div style={{ color: '#64748b', marginBottom: '4px' }}>Low</div>
          <div style={{ color: '#ef4444', fontWeight: '600' }}>${Number(data?.low || data?.close || 0).toFixed(2)}</div>
        </div>
        <div>
          <div style={{ color: '#64748b', marginBottom: '4px' }}>Close</div>
          <div style={{ color: 'white', fontWeight: '600' }}>${Number(data?.close || 0).toFixed(2)}</div>
        </div>
      </div>
      {data?.rsi && (
        <div style={{
          display: 'flex',
          gap: '12px',
          marginTop: '8px',
          fontSize: '11px',
          color: '#64748b'
        }}>
          <span>RSI: <strong style={{ color: data.rsi < 30 ? '#ef4444' : data.rsi > 70 ? '#10b981' : '#94a3b8' }}>{Number(data.rsi).toFixed(1)}</strong></span>
          <span>MACD: <strong style={{ color: '#94a3b8' }}>{Number(data.macd || 0).toFixed(4)}</strong></span>
          <span>ADX: <strong style={{ color: '#94a3b8' }}>{Number(data.adx || 0).toFixed(1)}</strong></span>
        </div>
      )}
    </div>
  );
}
