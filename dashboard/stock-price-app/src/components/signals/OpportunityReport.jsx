/**
 * OpportunityReport.jsx
 *
 * Daily Opportunity Report - Ranked analysis of ALL asset types
 *
 * Features:
 * - Daily rankings from highest to lowest opportunity score
 * - Filter by asset type (Stocks, Crypto, ETFs, Forex, Indices, Commodities)
 * - Visual indicators for Growth Score, RSI, EMA Cycles
 * - Based on validated 68.5% UP accuracy ML model
 */

import { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp, TrendingDown, Target, Zap, RefreshCw,
  Filter, Download, Calendar, Award, AlertTriangle,
  ArrowUpRight, ArrowDownRight, ChevronDown, ChevronUp,
  BarChart2, Activity, Star, Clock
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://trading-api-1075463475276.us-central1.run.app';

// Asset type colors and icons
const ASSET_COLORS = {
  stocks: { bg: '#3b82f622', border: '#3b82f6', text: '#3b82f6' },
  crypto: { bg: '#f59e0b22', border: '#f59e0b', text: '#f59e0b' },
  etfs: { bg: '#8b5cf622', border: '#8b5cf6', text: '#8b5cf6' },
  forex: { bg: '#10b98122', border: '#10b981', text: '#10b981' },
  indices: { bg: '#ec489922', border: '#ec4899', text: '#ec4899' },
  commodities: { bg: '#06b6d422', border: '#06b6d4', text: '#06b6d4' }
};

// Recommendation colors
const RECOMMENDATION_COLORS = {
  STRONG_BUY: { bg: '#00ff8833', border: '#00ff88', text: '#00ff88' },
  BUY: { bg: '#10b98133', border: '#10b981', text: '#10b981' },
  HOLD: { bg: '#f59e0b33', border: '#f59e0b', text: '#f59e0b' },
  SELL: { bg: '#f9731633', border: '#f97316', text: '#f97316' },
  STRONG_SELL: { bg: '#ef444433', border: '#ef4444', text: '#ef4444' }
};

const OpportunityReport = ({ theme = 'dark' }) => {
  const [reportData, setReportData] = useState(null);
  const [filteredData, setFilteredData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAssetType, setSelectedAssetType] = useState('all');
  const [selectedRecommendation, setSelectedRecommendation] = useState('all');
  const [sortBy, setSortBy] = useState('opportunity_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [lastUpdate, setLastUpdate] = useState(null);
  const [expandedRows, setExpandedRows] = useState({});

  // Fetch opportunity report
  const fetchReport = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/opportunity-report`);
      const data = await response.json();

      if (data.success) {
        setReportData(data);
        setLastUpdate(new Date());
      } else {
        // If API not available, try to fetch from BigQuery via another endpoint
        const fallbackResponse = await fetch(`${API_BASE}/api/ai/growth-screener?limit=500`);
        const fallbackData = await fallbackResponse.json();

        if (fallbackData.success && fallbackData.data) {
          // Transform to opportunity report format
          const transformed = fallbackData.data.map((item, index) => ({
            symbol: item.symbol,
            asset_type: item.asset_type || 'stocks',
            close: item.close || 0,
            daily_change_pct: item.daily_change_pct || 0,
            volume: item.volume || 0,
            opportunity_score: item.growth_score || 0,
            rank_overall: index + 1,
            recommendation: item.recommendation || calculateRecommendation(item.growth_score || 0),
            confidence: 0.7,
            growth_score: item.growth_score || 0,
            rsi: item.rsi || 50,
            in_rise_cycle: item.ema_12 > item.ema_26,
            pivot_low_signal: item.pivot_low_flag === 1,
            pivot_high_signal: item.pivot_high_flag === 1,
            macd_histogram: item.macd_histogram || 0,
            factors: generateFactors(item)
          }));

          setReportData({
            success: true,
            data: transformed,
            summary: generateSummary(transformed)
          });
          setLastUpdate(new Date());
        }
      }
    } catch (err) {
      console.error('Error fetching report:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Calculate recommendation from score
  const calculateRecommendation = (score) => {
    if (score >= 80) return 'STRONG_BUY';
    if (score >= 60) return 'BUY';
    if (score >= 40) return 'HOLD';
    if (score >= 20) return 'SELL';
    return 'STRONG_SELL';
  };

  // Generate factors from data
  const generateFactors = (item) => {
    const factors = [];
    if ((item.growth_score || 0) >= 75) factors.push('Growth Score EXCELLENT');
    if ((item.rsi || 50) >= 40 && (item.rsi || 50) <= 65) factors.push('RSI Sweet Spot');
    if (item.ema_12 > item.ema_26) factors.push('EMA Rise Cycle');
    if ((item.macd_histogram || 0) > 0) factors.push('MACD Bullish');
    if (item.pivot_low_flag === 1) factors.push('PIVOT LOW Signal');
    return factors.join('|');
  };

  // Generate summary
  const generateSummary = (data) => {
    const summary = {
      total_assets_analyzed: data.length,
      strong_buy_count: data.filter(d => d.recommendation === 'STRONG_BUY').length,
      buy_count: data.filter(d => d.recommendation === 'BUY').length,
      hold_count: data.filter(d => d.recommendation === 'HOLD').length,
      avg_opportunity_score: Math.round(data.reduce((sum, d) => sum + (d.opportunity_score || 0), 0) / data.length),
      rise_cycle_count: data.filter(d => d.in_rise_cycle).length,
      by_asset_type: {}
    };

    const assetTypes = [...new Set(data.map(d => d.asset_type))];
    assetTypes.forEach(type => {
      const typeData = data.filter(d => d.asset_type === type);
      summary.by_asset_type[type] = {
        count: typeData.length,
        strong_buy: typeData.filter(d => d.recommendation === 'STRONG_BUY').length,
        buy: typeData.filter(d => d.recommendation === 'BUY').length
      };
    });

    return summary;
  };

  // Initial load
  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  // Filter and sort data
  useEffect(() => {
    if (!reportData?.data) return;

    let filtered = [...reportData.data];

    // Filter by asset type
    if (selectedAssetType !== 'all') {
      filtered = filtered.filter(d => d.asset_type === selectedAssetType);
    }

    // Filter by recommendation
    if (selectedRecommendation !== 'all') {
      filtered = filtered.filter(d => d.recommendation === selectedRecommendation);
    }

    // Sort
    filtered.sort((a, b) => {
      let aVal = a[sortBy] || 0;
      let bVal = b[sortBy] || 0;

      if (typeof aVal === 'string') {
        return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }

      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });

    setFilteredData(filtered);
  }, [reportData, selectedAssetType, selectedRecommendation, sortBy, sortOrder]);

  // Toggle row expansion
  const toggleRow = (symbol) => {
    setExpandedRows(prev => ({
      ...prev,
      [symbol]: !prev[symbol]
    }));
  };

  // Export to CSV
  const exportToCSV = () => {
    if (!filteredData.length) return;

    const headers = [
      'Rank', 'Symbol', 'Asset Type', 'Close', 'Change %', 'Opportunity Score',
      'Recommendation', 'Growth Score', 'RSI', 'In Rise Cycle', 'Factors'
    ];

    const rows = filteredData.map((d, i) => [
      i + 1,
      d.symbol,
      d.asset_type,
      d.close?.toFixed(2) || '',
      d.daily_change_pct?.toFixed(2) || '',
      d.opportunity_score,
      d.recommendation,
      d.growth_score?.toFixed(0) || '',
      d.rsi?.toFixed(1) || '',
      d.in_rise_cycle ? 'Yes' : 'No',
      d.factors?.replace(/\|/g, ', ') || ''
    ]);

    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `opportunity_report_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  // Summary card component
  const SummaryCard = ({ title, value, subtitle, color, icon: Icon }) => (
    <div style={{
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      borderRadius: '12px',
      padding: '20px',
      border: `1px solid ${color}44`,
      flex: 1,
      minWidth: '150px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>{title}</div>
          <div style={{ color, fontSize: '28px', fontWeight: '700' }}>{value}</div>
          {subtitle && <div style={{ color: '#64748b', fontSize: '11px', marginTop: '4px' }}>{subtitle}</div>}
        </div>
        {Icon && <Icon size={24} style={{ color }} />}
      </div>
    </div>
  );

  // Opportunity score bar
  const ScoreBar = ({ score }) => {
    const getColor = (s) => {
      if (s >= 80) return '#00ff88';
      if (s >= 60) return '#10b981';
      if (s >= 40) return '#f59e0b';
      if (s >= 20) return '#f97316';
      return '#ef4444';
    };

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          width: '60px',
          height: '8px',
          background: '#334155',
          borderRadius: '4px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${score}%`,
            height: '100%',
            background: getColor(score),
            borderRadius: '4px',
            transition: 'width 0.3s ease'
          }} />
        </div>
        <span style={{ color: getColor(score), fontWeight: '700', fontSize: '14px', minWidth: '30px' }}>
          {score}
        </span>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '400px',
        color: '#64748b'
      }}>
        <RefreshCw className="animate-spin" style={{ marginRight: '12px' }} />
        Loading Opportunity Report...
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', minHeight: '100vh', background: '#0a0e27' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div>
          <h1 style={{
            color: 'white',
            margin: 0,
            fontSize: '28px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <Award style={{ color: '#f59e0b' }} />
            Daily Opportunity Report
          </h1>
          <p style={{ color: '#64748b', margin: '8px 0 0' }}>
            Ranked analysis of all assets based on validated ML model (68.5% UP accuracy)
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {lastUpdate && (
            <span style={{ color: '#64748b', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={14} />
              Updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}

          <button
            onClick={fetchReport}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: '600'
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>

          <button
            onClick={exportToCSV}
            style={{
              background: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: '600'
            }}
          >
            <Download size={16} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {reportData?.summary && (
        <div style={{
          display: 'flex',
          gap: '16px',
          marginBottom: '24px',
          flexWrap: 'wrap'
        }}>
          <SummaryCard
            title="Total Assets"
            value={reportData.summary.total_assets_analyzed}
            subtitle="Analyzed today"
            color="#3b82f6"
            icon={BarChart2}
          />
          <SummaryCard
            title="Strong Buy"
            value={reportData.summary.strong_buy_count}
            subtitle={`${((reportData.summary.strong_buy_count / reportData.summary.total_assets_analyzed) * 100).toFixed(1)}% of total`}
            color="#00ff88"
            icon={TrendingUp}
          />
          <SummaryCard
            title="Buy Signals"
            value={reportData.summary.buy_count}
            subtitle="Actionable opportunities"
            color="#10b981"
            icon={Target}
          />
          <SummaryCard
            title="Rise Cycles"
            value={reportData.summary.rise_cycle_count}
            subtitle="EMA 12 > EMA 26"
            color="#8b5cf6"
            icon={Activity}
          />
          <SummaryCard
            title="Avg Score"
            value={reportData.summary.avg_opportunity_score}
            subtitle="Opportunity score"
            color="#f59e0b"
            icon={Star}
          />
        </div>
      )}

      {/* Filters */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '24px',
        border: '1px solid #334155',
        display: 'flex',
        gap: '16px',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={16} style={{ color: '#64748b' }} />
          <span style={{ color: '#94a3b8', fontSize: '14px' }}>Filters:</span>
        </div>

        {/* Asset Type Filter */}
        <select
          value={selectedAssetType}
          onChange={(e) => setSelectedAssetType(e.target.value)}
          style={{
            background: '#0f172a',
            color: 'white',
            border: '1px solid #334155',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: 'pointer'
          }}
        >
          <option value="all">All Asset Types</option>
          <option value="stocks">Stocks</option>
          <option value="crypto">Crypto</option>
          <option value="etfs">ETFs</option>
          <option value="forex">Forex</option>
          <option value="indices">Indices</option>
          <option value="commodities">Commodities</option>
        </select>

        {/* Recommendation Filter */}
        <select
          value={selectedRecommendation}
          onChange={(e) => setSelectedRecommendation(e.target.value)}
          style={{
            background: '#0f172a',
            color: 'white',
            border: '1px solid #334155',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: 'pointer'
          }}
        >
          <option value="all">All Recommendations</option>
          <option value="STRONG_BUY">Strong Buy Only</option>
          <option value="BUY">Buy Only</option>
          <option value="HOLD">Hold Only</option>
          <option value="SELL">Sell Only</option>
        </select>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{
            background: '#0f172a',
            color: 'white',
            border: '1px solid #334155',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: 'pointer'
          }}
        >
          <option value="opportunity_score">Sort by Opportunity Score</option>
          <option value="growth_score">Sort by Growth Score</option>
          <option value="daily_change_pct">Sort by Daily Change</option>
          <option value="rsi">Sort by RSI</option>
          <option value="symbol">Sort by Symbol</option>
        </select>

        <button
          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          style={{
            background: '#334155',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '8px 12px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          {sortOrder === 'desc' ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
          {sortOrder === 'desc' ? 'High to Low' : 'Low to High'}
        </button>

        <span style={{ color: '#64748b', fontSize: '12px', marginLeft: 'auto' }}>
          Showing {filteredData.length} of {reportData?.data?.length || 0} assets
        </span>
      </div>

      {/* Data Table */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        border: '1px solid #334155',
        overflow: 'hidden'
      }}>
        {/* Table Header */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '60px 100px 80px 90px 80px 100px 120px 80px 60px 80px',
          gap: '8px',
          padding: '16px',
          background: '#0f172a',
          borderBottom: '1px solid #334155',
          fontWeight: '600',
          fontSize: '12px',
          color: '#94a3b8'
        }}>
          <div>RANK</div>
          <div>SYMBOL</div>
          <div>TYPE</div>
          <div>PRICE</div>
          <div>CHANGE</div>
          <div>OPP. SCORE</div>
          <div>RECOMMENDATION</div>
          <div>GROWTH</div>
          <div>RSI</div>
          <div>CYCLE</div>
        </div>

        {/* Table Body */}
        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
          {filteredData.map((item, index) => {
            const assetColor = ASSET_COLORS[item.asset_type] || ASSET_COLORS.stocks;
            const recColor = RECOMMENDATION_COLORS[item.recommendation] || RECOMMENDATION_COLORS.HOLD;
            const isExpanded = expandedRows[item.symbol];

            return (
              <div key={`${item.symbol}-${index}`}>
                <div
                  onClick={() => toggleRow(item.symbol)}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '60px 100px 80px 90px 80px 100px 120px 80px 60px 80px',
                    gap: '8px',
                    padding: '12px 16px',
                    borderBottom: '1px solid #1e293b',
                    cursor: 'pointer',
                    transition: 'background 0.2s',
                    background: isExpanded ? '#1e293b' : 'transparent'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#1e293b'}
                  onMouseLeave={(e) => e.currentTarget.style.background = isExpanded ? '#1e293b' : 'transparent'}
                >
                  {/* Rank */}
                  <div style={{ color: '#64748b', fontWeight: '600' }}>
                    #{index + 1}
                  </div>

                  {/* Symbol */}
                  <div style={{ color: 'white', fontWeight: '700' }}>
                    {item.symbol}
                  </div>

                  {/* Asset Type */}
                  <div>
                    <span style={{
                      background: assetColor.bg,
                      color: assetColor.text,
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '10px',
                      fontWeight: '600',
                      textTransform: 'uppercase'
                    }}>
                      {item.asset_type}
                    </span>
                  </div>

                  {/* Price */}
                  <div style={{ color: 'white', fontFamily: 'monospace' }}>
                    ${item.close?.toFixed(2) || '0.00'}
                  </div>

                  {/* Daily Change */}
                  <div style={{
                    color: (item.daily_change_pct || 0) >= 0 ? '#10b981' : '#ef4444',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontFamily: 'monospace'
                  }}>
                    {(item.daily_change_pct || 0) >= 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                    {Math.abs(item.daily_change_pct || 0).toFixed(2)}%
                  </div>

                  {/* Opportunity Score */}
                  <div>
                    <ScoreBar score={item.opportunity_score || 0} />
                  </div>

                  {/* Recommendation */}
                  <div>
                    <span style={{
                      background: recColor.bg,
                      color: recColor.text,
                      border: `1px solid ${recColor.border}`,
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '10px',
                      fontWeight: '700'
                    }}>
                      {item.recommendation}
                    </span>
                  </div>

                  {/* Growth Score */}
                  <div style={{
                    color: (item.growth_score || 0) >= 75 ? '#10b981' : (item.growth_score || 0) >= 50 ? '#f59e0b' : '#64748b',
                    fontWeight: '600'
                  }}>
                    {item.growth_score?.toFixed(0) || '0'}
                  </div>

                  {/* RSI */}
                  <div style={{
                    color: ((item.rsi || 50) >= 40 && (item.rsi || 50) <= 65) ? '#10b981' : '#64748b'
                  }}>
                    {item.rsi?.toFixed(0) || '50'}
                  </div>

                  {/* Rise Cycle */}
                  <div>
                    {item.in_rise_cycle ? (
                      <span style={{ color: '#10b981' }}>RISE</span>
                    ) : (
                      <span style={{ color: '#64748b' }}>FALL</span>
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div style={{
                    padding: '16px',
                    background: '#0f172a',
                    borderBottom: '1px solid #334155'
                  }}>
                    <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                      {/* Factors */}
                      <div style={{ flex: 1, minWidth: '300px' }}>
                        <h4 style={{ color: '#94a3b8', margin: '0 0 8px', fontSize: '12px' }}>
                          KEY FACTORS
                        </h4>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {(item.factors?.split('|') || []).map((factor, i) => (
                            <span
                              key={i}
                              style={{
                                background: factor.includes('EXCELLENT') || factor.includes('Signal') || factor.includes('Cycle')
                                  ? '#10b98133'
                                  : '#33415533',
                                color: factor.includes('EXCELLENT') || factor.includes('Signal') || factor.includes('Cycle')
                                  ? '#10b981'
                                  : '#94a3b8',
                                padding: '4px 10px',
                                borderRadius: '12px',
                                fontSize: '11px'
                              }}
                            >
                              {factor}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Metrics */}
                      <div style={{ display: 'flex', gap: '24px' }}>
                        <div>
                          <div style={{ color: '#64748b', fontSize: '11px' }}>MACD Hist</div>
                          <div style={{
                            color: (item.macd_histogram || 0) > 0 ? '#10b981' : '#ef4444',
                            fontWeight: '600'
                          }}>
                            {item.macd_histogram?.toFixed(4) || '0'}
                          </div>
                        </div>
                        <div>
                          <div style={{ color: '#64748b', fontSize: '11px' }}>Pivot Low</div>
                          <div style={{ color: item.pivot_low_signal ? '#10b981' : '#64748b', fontWeight: '600' }}>
                            {item.pivot_low_signal ? 'YES' : 'No'}
                          </div>
                        </div>
                        <div>
                          <div style={{ color: '#64748b', fontSize: '11px' }}>Volume</div>
                          <div style={{ color: 'white' }}>
                            {(item.volume || 0).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Asset Type Summary */}
      {reportData?.summary?.by_asset_type && (
        <div style={{
          marginTop: '24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          {Object.entries(reportData.summary.by_asset_type).map(([type, stats]) => {
            const color = ASSET_COLORS[type] || ASSET_COLORS.stocks;
            return (
              <div
                key={type}
                style={{
                  background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                  borderRadius: '12px',
                  padding: '16px',
                  border: `1px solid ${color.border}44`
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{
                    color: color.text,
                    fontWeight: '700',
                    textTransform: 'uppercase',
                    fontSize: '14px'
                  }}>
                    {type}
                  </span>
                  <span style={{ color: '#64748b', fontSize: '12px' }}>
                    {stats.count} assets
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '16px' }}>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '10px' }}>STRONG BUY</div>
                    <div style={{ color: '#00ff88', fontWeight: '700', fontSize: '20px' }}>{stats.strong_buy}</div>
                  </div>
                  <div>
                    <div style={{ color: '#64748b', fontSize: '10px' }}>BUY</div>
                    <div style={{ color: '#10b981', fontWeight: '700', fontSize: '20px' }}>{stats.buy}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default OpportunityReport;
