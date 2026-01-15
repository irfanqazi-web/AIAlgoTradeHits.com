import { useState } from 'react';
import { Download, Search, FileSpreadsheet, Loader, Calendar, FileText } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-1075463475276.us-central1.run.app'
);

const ASSET_TYPES = [
  { value: 'stocks', label: 'Stocks', icon: '📈', example: 'AAPL' },
  { value: 'crypto', label: 'Crypto', icon: '🪙', example: 'BTC/USD' },
  { value: 'etfs', label: 'ETFs', icon: '📊', example: 'SPY' },
  { value: 'forex', label: 'Forex', icon: '💱', example: 'EUR/USD' },
  { value: 'indices', label: 'Indices', icon: '📉', example: 'SPX' },
  { value: 'commodities', label: 'Commodities', icon: '🛢️', example: 'GOLD' },
  { value: 'interest_rates', label: 'Interest Rates', icon: '📋', example: 'FED' }
];

const TIMEFRAMES = [
  { value: 'daily', label: 'Daily' },
  { value: 'hourly', label: 'Hourly' },
  { value: '5min', label: '5 Minute' }
];

// PDF URL for asset status report
const ASSET_STATUS_PDF_URL = 'https://storage.googleapis.com/aialgotradehits-assets/TRADING_DATA_STATUS_REPORT.pdf';

export default function DataExportDownload({ theme = 'dark' }) {
  const [assetType, setAssetType] = useState('stocks');
  const [selectedTimeframes, setSelectedTimeframes] = useState(['daily']);
  const [symbols, setSymbols] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState({ current: 0, total: 0 });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const isDark = theme === 'dark';

  const toggleTimeframe = (tf) => {
    setSelectedTimeframes(prev => {
      if (prev.includes(tf)) {
        if (prev.length === 1) return prev;
        return prev.filter(t => t !== tf);
      } else {
        return [...prev, tf];
      }
    });
  };

  const downloadSingleSymbol = async (symbol, timeframe) => {
    const endpointMap = {
      'stocks': 'stocks',
      'crypto': 'crypto',
      'etfs': 'etfs',
      'forex': 'forex',
      'indices': 'indices',
      'commodities': 'commodities',
      'interest_rates': 'interest_rates'
    };
    const endpoint = endpointMap[assetType] || 'stocks';

    let downloadUrl = `${API_BASE_URL}/api/${endpoint}/reconciliation/${encodeURIComponent(symbol)}/download`;
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (timeframe !== 'daily') params.append('timeframe', timeframe);
    if (params.toString()) downloadUrl += `?${params.toString()}`;

    const response = await fetch(downloadUrl);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `HTTP ${response.status}`);
    }

    const blob = await response.blob();
    let filename = `${symbol}_${timeframe}_97_fields.csv`;

    if (startDate || endDate) {
      const dateRange = `${startDate || 'start'}_to_${endDate || 'end'}`;
      filename = filename.replace('.csv', `_${dateRange}.csv`);
    }

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    return { symbol, timeframe, size: blob.size };
  };

  const handleDownload = async () => {
    if (!symbols.trim()) {
      setError('Please enter at least one symbol');
      return;
    }

    if (selectedTimeframes.length === 0) {
      setError('Please select at least one timeframe');
      return;
    }

    const symbolList = symbols.split(',').map(s => s.trim().toUpperCase()).filter(s => s);

    if (symbolList.length === 0) {
      setError('Please enter valid symbols');
      return;
    }

    const downloadTasks = [];
    for (const sym of symbolList) {
      for (const tf of selectedTimeframes) {
        downloadTasks.push({ symbol: sym, timeframe: tf });
      }
    }

    setError(null);
    setSuccess(null);
    setDownloading(true);
    setDownloadProgress({ current: 0, total: downloadTasks.length });

    let successCount = 0;
    let failCount = 0;

    const batchSize = 5;
    for (let i = 0; i < downloadTasks.length; i += batchSize) {
      const batch = downloadTasks.slice(i, i + batchSize);
      const batchPromises = batch.map(async (task) => {
        try {
          await downloadSingleSymbol(task.symbol, task.timeframe);
          successCount++;
          setDownloadProgress(prev => ({ ...prev, current: prev.current + 1 }));
        } catch (err) {
          failCount++;
          setDownloadProgress(prev => ({ ...prev, current: prev.current + 1 }));
          console.error(`Failed to download ${task.symbol} (${task.timeframe}):`, err);
        }
      });

      await Promise.all(batchPromises);

      if (i + batchSize < downloadTasks.length) {
        await new Promise(resolve => setTimeout(resolve, 300));
      }
    }

    setDownloading(false);
    setDownloadProgress({ current: 0, total: 0 });

    if (failCount === 0) {
      setSuccess(`Successfully downloaded ${successCount} file(s)`);
    } else if (successCount === 0) {
      setError(`All ${failCount} downloads failed`);
    } else {
      setSuccess(`Downloaded ${successCount} file(s), ${failCount} failed`);
    }
  };

  return (
    <div style={{
      background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
      borderRadius: '16px',
      padding: '24px',
      border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
      maxWidth: '900px',
      margin: '0 auto'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '28px' }}>
        <div style={{
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          borderRadius: '12px',
          padding: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <FileSpreadsheet size={28} color="white" />
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{
            color: isDark ? '#f1f5f9' : '#1e293b',
            margin: 0,
            fontSize: '22px',
            fontWeight: '700'
          }}>
            Export Complete 97-Field Data
          </h2>
          <p style={{
            color: isDark ? '#94a3b8' : '#64748b',
            margin: '4px 0 0 0',
            fontSize: '14px'
          }}>
            Download complete historical data with all indicators in CSV format
          </p>
        </div>
        {/* PDF Download Link - Top Right */}
        <a
          href={ASSET_STATUS_PDF_URL}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 16px',
            borderRadius: '10px',
            border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
            background: isDark ? '#1e293b' : '#f8fafc',
            color: '#ef4444',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            textDecoration: 'none',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = isDark ? '#334155' : '#e2e8f0';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = isDark ? '#1e293b' : '#f8fafc';
          }}
        >
          <FileText size={18} />
          Asset Status (PDF)
        </a>
      </div>

      {/* Asset Type */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{
          display: 'block',
          color: isDark ? '#f1f5f9' : '#1e293b',
          marginBottom: '12px',
          fontSize: '15px',
          fontWeight: '600'
        }}>
          Asset Type
        </label>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '12px'
        }}>
          {ASSET_TYPES.map((type, idx) => (
            <button
              key={type.value}
              onClick={() => setAssetType(type.value)}
              style={{
                padding: '16px 12px',
                borderRadius: '12px',
                border: assetType === type.value
                  ? '2px solid #10b981'
                  : `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
                background: assetType === type.value
                  ? (isDark ? '#10b98120' : '#10b98110')
                  : (isDark ? '#1e293b' : '#f8fafc'),
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.2s',
                gridColumn: idx >= 4 ? 'auto' : 'auto'
              }}
            >
              <div style={{ fontSize: '24px', marginBottom: '6px' }}>{type.icon}</div>
              <div style={{
                color: isDark ? '#f1f5f9' : '#1e293b',
                fontWeight: '600',
                fontSize: '14px'
              }}>
                {type.label}
              </div>
              <div style={{
                color: isDark ? '#64748b' : '#94a3b8',
                fontSize: '11px',
                marginTop: '2px'
              }}>
                {type.example}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Timeframe Selection */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{
          display: 'block',
          color: isDark ? '#f1f5f9' : '#1e293b',
          marginBottom: '12px',
          fontSize: '15px',
          fontWeight: '600'
        }}>
          Timeframe (Select one or more)
        </label>
        <div style={{ display: 'flex', gap: '16px' }}>
          {TIMEFRAMES.map((tf) => (
            <label
              key={tf.value}
              style={{
                flex: 1,
                padding: '14px 20px',
                borderRadius: '10px',
                border: selectedTimeframes.includes(tf.value)
                  ? '2px solid #3b82f6'
                  : `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
                background: selectedTimeframes.includes(tf.value)
                  ? (isDark ? '#3b82f620' : '#3b82f610')
                  : (isDark ? '#1e293b' : '#f8fafc'),
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px',
                transition: 'all 0.2s'
              }}
            >
              <input
                type="checkbox"
                checked={selectedTimeframes.includes(tf.value)}
                onChange={() => toggleTimeframe(tf.value)}
                style={{
                  width: '18px',
                  height: '18px',
                  accentColor: '#3b82f6',
                  cursor: 'pointer'
                }}
              />
              <span style={{
                color: selectedTimeframes.includes(tf.value)
                  ? '#3b82f6'
                  : (isDark ? '#f1f5f9' : '#1e293b'),
                fontWeight: '600',
                fontSize: '14px'
              }}>
                {tf.label}
              </span>
            </label>
          ))}
        </div>
        <div style={{
          color: isDark ? '#64748b' : '#94a3b8',
          fontSize: '12px',
          marginTop: '8px'
        }}>
          {selectedTimeframes.length} timeframe(s) selected - {symbols.split(',').filter(s => s.trim()).length || 0} symbol(s) x {selectedTimeframes.length} = {(symbols.split(',').filter(s => s.trim()).length || 0) * selectedTimeframes.length} total files
        </div>
      </div>

      {/* Symbol Input */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{
          display: 'block',
          color: isDark ? '#f1f5f9' : '#1e293b',
          marginBottom: '12px',
          fontSize: '15px',
          fontWeight: '600'
        }}>
          Enter Symbols (comma-separated for bulk download)
        </label>
        <div style={{ position: 'relative' }}>
          <Search
            size={20}
            color={isDark ? '#64748b' : '#94a3b8'}
            style={{
              position: 'absolute',
              left: '16px',
              top: '50%',
              transform: 'translateY(-50%)'
            }}
          />
          <input
            type="text"
            value={symbols}
            onChange={(e) => setSymbols(e.target.value.toUpperCase())}
            placeholder="Enter symbols (e.g., AAPL, MSFT, NVDA, TSLA)"
            style={{
              width: '100%',
              padding: '16px 16px 16px 50px',
              borderRadius: '12px',
              border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
              background: isDark ? '#0f172a' : '#ffffff',
              color: isDark ? '#f1f5f9' : '#1e293b',
              fontSize: '15px',
              outline: 'none',
              boxSizing: 'border-box'
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && symbols) {
                handleDownload();
              }
            }}
          />
        </div>
      </div>

      {/* Date Range */}
      <div style={{
        background: isDark ? '#0f172a' : '#f8fafc',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Calendar size={18} color="#10b981" />
            <span style={{
              color: isDark ? '#f1f5f9' : '#1e293b',
              fontWeight: '600',
              fontSize: '15px'
            }}>
              Date Range (Optional)
            </span>
          </div>
          <span style={{
            color: isDark ? '#64748b' : '#94a3b8',
            fontSize: '13px'
          }}>
            Leave empty for all available data
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{
              display: 'block',
              color: isDark ? '#94a3b8' : '#64748b',
              marginBottom: '8px',
              fontSize: '13px'
            }}>
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{
                width: '100%',
                padding: '14px 16px',
                borderRadius: '10px',
                border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
                background: isDark ? '#1e293b' : '#ffffff',
                color: isDark ? '#f1f5f9' : '#1e293b',
                fontSize: '14px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
          </div>
          <div>
            <label style={{
              display: 'block',
              color: isDark ? '#94a3b8' : '#64748b',
              marginBottom: '8px',
              fontSize: '13px'
            }}>
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              style={{
                width: '100%',
                padding: '14px 16px',
                borderRadius: '10px',
                border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
                background: isDark ? '#1e293b' : '#ffffff',
                color: isDark ? '#f1f5f9' : '#1e293b',
                fontSize: '14px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
          </div>
        </div>
      </div>

      {/* Download Button */}
      <button
        onClick={handleDownload}
        disabled={!symbols.trim() || downloading}
        style={{
          width: '100%',
          padding: '18px',
          borderRadius: '12px',
          border: 'none',
          background: !symbols.trim() || downloading
            ? '#4b5563'
            : 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          color: 'white',
          fontWeight: '600',
          fontSize: '16px',
          cursor: !symbols.trim() || downloading ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px',
          transition: 'all 0.2s'
        }}
      >
        {downloading ? (
          <>
            <Loader size={20} style={{ animation: 'spin 1s linear infinite' }} />
            Downloading {downloadProgress.current}/{downloadProgress.total}...
          </>
        ) : (
          <>
            <Download size={20} />
            Download CSV
          </>
        )}
      </button>

      {/* Progress Bar */}
      {downloading && downloadProgress.total > 1 && (
        <div style={{ marginTop: '16px' }}>
          <div style={{
            height: '6px',
            background: isDark ? '#1e293b' : '#e2e8f0',
            borderRadius: '3px',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${(downloadProgress.current / downloadProgress.total) * 100}%`,
              background: 'linear-gradient(90deg, #10b981, #059669)',
              transition: 'width 0.3s ease'
            }} />
          </div>
        </div>
      )}

      {/* Error/Success Messages */}
      {error && (
        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          borderRadius: '8px',
          background: '#ef444420',
          border: '1px solid #ef4444',
          color: '#ef4444',
          fontSize: '14px'
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          borderRadius: '8px',
          background: '#10b98120',
          border: '1px solid #10b981',
          color: '#10b981',
          fontSize: '14px'
        }}>
          {success}
        </div>
      )}

      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
