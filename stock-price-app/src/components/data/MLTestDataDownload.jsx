import { useState } from 'react';
import { Download, FileSpreadsheet, Loader, CheckCircle, AlertCircle,
         FlaskConical, Target, TrendingUp, Zap, Clock, Database } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-1075463475276.us-central1.run.app'
);

// ML Test Data Presets based on Model Testing Data.docx
const ML_TEST_PRESETS = {
  groupA: {
    name: 'Group A: Time Period Tests',
    description: 'Same Ticker (SPY) - Different time windows',
    purpose: 'Test if model works on different time windows, handles COVID crash, works with varying training data lengths',
    icon: Clock,
    color: '#3b82f6',
    tests: [
      {
        id: 1,
        name: 'Test 1: Standard Split',
        symbol: 'SPY',
        trainStart: '2015-01-01',
        trainEnd: '2022-12-31',
        testStart: '2023-01-01',
        testEnd: '2024-12-31',
        purpose: 'Last 2 years only - Standard validation'
      },
      {
        id: 2,
        name: 'Test 2: Extended Training',
        symbol: 'SPY',
        trainStart: '2010-01-01',
        trainEnd: '2022-12-31',
        testStart: '2023-01-01',
        testEnd: '2024-12-31',
        purpose: '10+ years training - More historical context'
      },
      {
        id: 3,
        name: 'Test 3: Recent Focus',
        symbol: 'SPY',
        trainStart: '2018-01-01',
        trainEnd: '2023-12-31',
        testStart: '2024-01-01',
        testEnd: '2024-12-31',
        purpose: 'Recent 5yr train, 1yr test - Current market behavior'
      },
      {
        id: 4,
        name: 'Test 4: Pre/Post COVID',
        symbol: 'SPY',
        trainStart: '2006-01-01',
        trainEnd: '2020-02-28',
        testStart: '2021-01-01',
        testEnd: '2024-12-31',
        purpose: 'Pre-COVID train, Post-COVID test - Regime change test'
      }
    ]
  },
  groupB: {
    name: 'Group B: Ticker Tests',
    description: 'Same Time Period (2015-2024) - Different assets',
    purpose: 'Test if model generalizes beyond SPY to individual stocks and crypto',
    icon: Target,
    color: '#10b981',
    tests: [
      {
        id: 5,
        name: 'Test 5: Tech ETF (QQQ)',
        symbol: 'QQQ',
        trainStart: '2015-01-01',
        trainEnd: '2023-12-31',
        valEnd: '2024-09-30',
        testStart: '2024-10-01',
        testEnd: '2024-12-31',
        purpose: 'Tech-heavy ETF - Different sector dynamics'
      },
      {
        id: 6,
        name: 'Test 6: Individual Stock (AAPL)',
        symbol: 'AAPL',
        trainStart: '2015-01-01',
        trainEnd: '2023-12-31',
        valEnd: '2024-09-30',
        testStart: '2024-10-01',
        testEnd: '2024-12-31',
        purpose: 'Single stock - Company-specific behavior'
      },
      {
        id: 7,
        name: 'Test 7: Crypto (BTC)',
        symbol: 'BTC/USD',
        trainStart: '2018-01-01',
        trainEnd: '2023-12-31',
        valEnd: '2024-09-30',
        testStart: '2024-10-01',
        testEnd: '2024-12-31',
        purpose: 'Crypto - Very different volatility profile'
      }
    ]
  },
  groupC: {
    name: 'Group C: Stress Tests',
    description: 'Extreme market conditions',
    purpose: 'Test model survival during black swan events and bear markets',
    icon: Zap,
    color: '#ef4444',
    tests: [
      {
        id: 8,
        name: 'Test 8: COVID Crash',
        symbol: 'SPY',
        trainStart: '2006-01-01',
        trainEnd: '2019-12-31',
        testStart: '2020-01-01',
        testEnd: '2020-12-31',
        purpose: 'COVID crash - Extreme volatility survival'
      },
      {
        id: 9,
        name: 'Test 9: Bear Market 2022',
        symbol: 'SPY',
        trainStart: '2006-01-01',
        trainEnd: '2021-12-31',
        testStart: '2022-01-01',
        testEnd: '2022-12-31',
        purpose: 'Bear market year - Fed rate hikes'
      },
      {
        id: 10,
        name: 'Test 10: Multi-Asset Combined',
        symbols: ['SPY', 'QQQ', 'AAPL'],
        trainStart: '2015-01-01',
        trainEnd: '2023-12-31',
        testStart: '2024-01-01',
        testEnd: '2024-12-31',
        purpose: 'Combined training - Multi-asset model'
      }
    ]
  }
};

export default function MLTestDataDownload({ theme = 'dark' }) {
  const [selectedTests, setSelectedTests] = useState([]);
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState({});
  const [downloadResults, setDownloadResults] = useState({});
  const [fileFormat, setFileFormat] = useState('csv');
  const [expandedGroup, setExpandedGroup] = useState('groupA');

  const isDark = theme === 'dark';

  // Toggle test selection
  const toggleTest = (testId) => {
    if (selectedTests.includes(testId)) {
      setSelectedTests(selectedTests.filter(id => id !== testId));
    } else {
      setSelectedTests([...selectedTests, testId]);
    }
  };

  // Select all tests
  const selectAllTests = () => {
    const allTestIds = Object.values(ML_TEST_PRESETS).flatMap(g => g.tests.map(t => t.id));
    setSelectedTests(allTestIds);
  };

  // Clear selection
  const clearSelection = () => {
    setSelectedTests([]);
  };

  // Get all tests flat
  const getAllTests = () => {
    return Object.values(ML_TEST_PRESETS).flatMap(g => g.tests);
  };

  // Download a single test dataset
  const downloadTest = async (test) => {
    const testKey = `test_${test.id}`;
    setDownloadProgress(prev => ({ ...prev, [testKey]: 'downloading' }));

    try {
      // Prepare symbols array
      const symbols = test.symbols || [test.symbol];

      // Build query params
      const params = new URLSearchParams({
        symbols: symbols.join(','),
        train_start: test.trainStart,
        train_end: test.trainEnd,
        test_start: test.testStart,
        test_end: test.testEnd,
        format: fileFormat,
        include_indicators: 'true',
        test_id: test.id,
        test_name: test.name
      });

      if (test.valEnd) {
        params.append('val_end', test.valEnd);
      }

      const res = await fetch(`${API_BASE_URL}/api/download/ml-test-data?${params}`);

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Download failed');
      }

      // Get blob and trigger download
      const blob = await res.blob();
      const contentDisposition = res.headers.get('Content-Disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
        : `ml_test_${test.id}_${test.symbol || 'combined'}.${fileFormat}`;

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      setDownloadProgress(prev => ({ ...prev, [testKey]: 'complete' }));
      setDownloadResults(prev => ({ ...prev, [testKey]: { success: true, filename } }));

    } catch (err) {
      setDownloadProgress(prev => ({ ...prev, [testKey]: 'error' }));
      setDownloadResults(prev => ({ ...prev, [testKey]: { success: false, error: err.message } }));
    }
  };

  // Download all selected tests
  const downloadSelected = async () => {
    if (selectedTests.length === 0) return;

    setDownloading(true);
    const allTests = getAllTests();
    const testsToDownload = allTests.filter(t => selectedTests.includes(t.id));

    for (const test of testsToDownload) {
      await downloadTest(test);
      // Small delay between downloads
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setDownloading(false);
  };

  // Styles
  const cardStyle = {
    background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
    borderRadius: '16px',
    padding: '24px',
    border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
  };

  const groupHeaderStyle = (color, isExpanded) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '16px',
    background: isExpanded ? `${color}15` : (isDark ? '#0f172a' : '#f8fafc'),
    borderRadius: '12px',
    cursor: 'pointer',
    border: `2px solid ${isExpanded ? color : 'transparent'}`,
    marginBottom: isExpanded ? '12px' : '0',
    transition: 'all 0.2s'
  });

  const testCardStyle = (isSelected, status) => ({
    background: isSelected ? (isDark ? '#3b82f620' : '#3b82f610') : (isDark ? '#0f172a' : '#f8fafc'),
    borderRadius: '10px',
    padding: '14px',
    marginBottom: '8px',
    border: `2px solid ${
      status === 'complete' ? '#10b981' :
      status === 'error' ? '#ef4444' :
      status === 'downloading' ? '#f59e0b' :
      isSelected ? '#3b82f6' : 'transparent'
    }`,
    cursor: 'pointer',
    transition: 'all 0.2s'
  });

  const buttonStyle = (active, disabled = false) => ({
    padding: '10px 20px',
    borderRadius: '8px',
    border: active ? '2px solid #3b82f6' : `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
    background: disabled ? '#6b7280' : (active ? (isDark ? '#3b82f620' : '#3b82f610') : (isDark ? '#0f172a' : '#f8fafc')),
    color: disabled ? '#9ca3af' : (isDark ? '#f1f5f9' : '#1e293b'),
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontWeight: active ? '600' : '400',
    transition: 'all 0.2s'
  });

  return (
    <div style={cardStyle}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <div style={{
          background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
          borderRadius: '12px',
          padding: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <FlaskConical size={24} color="white" />
        </div>
        <div>
          <h3 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: 0, fontSize: '18px' }}>
            ML Model Test Data
          </h3>
          <p style={{ color: isDark ? '#64748b' : '#94a3b8', margin: '4px 0 0 0', fontSize: '13px' }}>
            10 pre-configured test datasets for ML model validation
          </p>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
          <button onClick={selectAllTests} style={{ ...buttonStyle(false), fontSize: '12px', padding: '8px 12px' }}>
            Select All 10
          </button>
          <button onClick={clearSelection} style={{ ...buttonStyle(false), fontSize: '12px', padding: '8px 12px' }}>
            Clear
          </button>
        </div>
      </div>

      {/* Info Box */}
      <div style={{
        background: isDark ? '#8b5cf620' : '#8b5cf610',
        borderRadius: '10px',
        padding: '14px',
        marginBottom: '20px',
        fontSize: '13px',
        color: isDark ? '#c4b5fd' : '#7c3aed'
      }}>
        <Database size={16} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} />
        Each download includes: OHLCV data + 24 technical indicators (RSI, MACD, EMA, SMA, Bollinger Bands, ATR, ADX, etc.)
      </div>

      {/* Test Groups */}
      {Object.entries(ML_TEST_PRESETS).map(([groupKey, group]) => {
        const GroupIcon = group.icon;
        const isExpanded = expandedGroup === groupKey;

        return (
          <div key={groupKey} style={{ marginBottom: '16px' }}>
            {/* Group Header */}
            <div
              style={groupHeaderStyle(group.color, isExpanded)}
              onClick={() => setExpandedGroup(isExpanded ? null : groupKey)}
            >
              <div style={{
                background: group.color,
                borderRadius: '8px',
                padding: '8px',
                display: 'flex'
              }}>
                <GroupIcon size={18} color="white" />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ color: isDark ? '#f1f5f9' : '#1e293b', fontWeight: '600' }}>
                  {group.name}
                </div>
                <div style={{ color: isDark ? '#64748b' : '#94a3b8', fontSize: '12px' }}>
                  {group.description}
                </div>
              </div>
              <div style={{
                background: group.color,
                borderRadius: '20px',
                padding: '4px 12px',
                color: 'white',
                fontSize: '12px',
                fontWeight: '600'
              }}>
                {group.tests.length} Tests
              </div>
              <span style={{ color: isDark ? '#64748b' : '#94a3b8', fontSize: '20px' }}>
                {isExpanded ? '−' : '+'}
              </span>
            </div>

            {/* Expanded Tests */}
            {isExpanded && (
              <div style={{ paddingLeft: '16px' }}>
                <div style={{
                  fontSize: '12px',
                  color: isDark ? '#94a3b8' : '#64748b',
                  marginBottom: '12px',
                  fontStyle: 'italic'
                }}>
                  {group.purpose}
                </div>

                {group.tests.map(test => {
                  const testKey = `test_${test.id}`;
                  const status = downloadProgress[testKey];
                  const isSelected = selectedTests.includes(test.id);

                  return (
                    <div
                      key={test.id}
                      style={testCardStyle(isSelected, status)}
                      onClick={() => toggleTest(test.id)}
                    >
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                        {/* Checkbox */}
                        <div style={{
                          width: '22px',
                          height: '22px',
                          borderRadius: '6px',
                          border: `2px solid ${isSelected ? '#3b82f6' : (isDark ? '#334155' : '#e2e8f0')}`,
                          background: isSelected ? '#3b82f6' : 'transparent',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                          marginTop: '2px'
                        }}>
                          {isSelected && <CheckCircle size={14} color="white" />}
                        </div>

                        {/* Test Info */}
                        <div style={{ flex: 1 }}>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            marginBottom: '6px'
                          }}>
                            <span style={{
                              color: isDark ? '#f1f5f9' : '#1e293b',
                              fontWeight: '600',
                              fontSize: '14px'
                            }}>
                              {test.name}
                            </span>
                            <span style={{
                              background: isDark ? '#334155' : '#e2e8f0',
                              borderRadius: '4px',
                              padding: '2px 8px',
                              fontSize: '11px',
                              color: isDark ? '#94a3b8' : '#64748b',
                              fontWeight: '500'
                            }}>
                              {test.symbols ? test.symbols.join(' + ') : test.symbol}
                            </span>
                          </div>

                          <div style={{
                            fontSize: '12px',
                            color: isDark ? '#64748b' : '#94a3b8',
                            marginBottom: '8px'
                          }}>
                            {test.purpose}
                          </div>

                          <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(2, 1fr)',
                            gap: '8px',
                            fontSize: '11px'
                          }}>
                            <div>
                              <span style={{ color: isDark ? '#64748b' : '#94a3b8' }}>Train: </span>
                              <span style={{ color: isDark ? '#94a3b8' : '#475569', fontWeight: '500' }}>
                                {test.trainStart} → {test.trainEnd}
                              </span>
                            </div>
                            <div>
                              <span style={{ color: isDark ? '#64748b' : '#94a3b8' }}>Test: </span>
                              <span style={{ color: isDark ? '#94a3b8' : '#475569', fontWeight: '500' }}>
                                {test.testStart} → {test.testEnd}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Status Indicator */}
                        <div style={{ flexShrink: 0 }}>
                          {status === 'downloading' && (
                            <Loader size={18} color="#f59e0b" style={{ animation: 'spin 1s linear infinite' }} />
                          )}
                          {status === 'complete' && (
                            <CheckCircle size={18} color="#10b981" />
                          )}
                          {status === 'error' && (
                            <AlertCircle size={18} color="#ef4444" />
                          )}
                        </div>
                      </div>

                      {/* Download Result */}
                      {downloadResults[testKey] && (
                        <div style={{
                          marginTop: '8px',
                          padding: '8px',
                          borderRadius: '6px',
                          fontSize: '11px',
                          background: downloadResults[testKey].success ? '#10b98120' : '#ef444420',
                          color: downloadResults[testKey].success ? '#10b981' : '#ef4444'
                        }}>
                          {downloadResults[testKey].success
                            ? `Downloaded: ${downloadResults[testKey].filename}`
                            : `Error: ${downloadResults[testKey].error}`
                          }
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}

      {/* File Format & Download */}
      <div style={{
        marginTop: '24px',
        paddingTop: '20px',
        borderTop: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
          <label style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '13px' }}>Format:</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setFileFormat('csv')}
              style={buttonStyle(fileFormat === 'csv')}
            >
              CSV (Recommended for ML)
            </button>
            <button
              onClick={() => setFileFormat('xlsx')}
              style={buttonStyle(fileFormat === 'xlsx')}
            >
              Excel (.xlsx)
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={downloadSelected}
            disabled={downloading || selectedTests.length === 0}
            style={{
              flex: 1,
              padding: '16px',
              borderRadius: '10px',
              border: 'none',
              background: downloading || selectedTests.length === 0
                ? '#6b7280'
                : 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
              color: 'white',
              fontWeight: '600',
              fontSize: '15px',
              cursor: downloading || selectedTests.length === 0 ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            {downloading ? (
              <>
                <Loader size={20} style={{ animation: 'spin 1s linear infinite' }} />
                Downloading {selectedTests.length} Test Datasets...
              </>
            ) : (
              <>
                <Download size={20} />
                Download {selectedTests.length} Selected Test{selectedTests.length !== 1 ? 's' : ''}
              </>
            )}
          </button>
        </div>

        {selectedTests.length > 0 && (
          <div style={{
            marginTop: '12px',
            fontSize: '12px',
            color: isDark ? '#64748b' : '#94a3b8',
            textAlign: 'center'
          }}>
            Selected: {getAllTests().filter(t => selectedTests.includes(t.id)).map(t => `Test ${t.id}`).join(', ')}
          </div>
        )}
      </div>

      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
