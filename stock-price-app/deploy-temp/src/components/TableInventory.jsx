import { useState, useEffect } from 'react';
import { Database, Table, RefreshCw, TrendingUp, HardDrive, Calendar, ChevronDown, ChevronRight, Eye, X, Columns, Brain, Sparkles, AlertTriangle, Lightbulb, Download, FileSpreadsheet } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-252370699783.us-central1.run.app'
);

const CATEGORY_COLORS = {
  stocks: '#ef4444',
  crypto: '#f59e0b',
  forex: '#10b981',
  etfs: '#3b82f6',
  indices: '#8b5cf6',
  commodities: '#ec4899',
  other: '#6b7280'
};

const CATEGORY_ICONS = {
  stocks: '🏢',
  crypto: '🪙',
  forex: '💱',
  etfs: '📊',
  indices: '📈',
  commodities: '🛢️',
  other: '📁'
};

export default function TableInventory({ theme = 'dark' }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [lastRefresh, setLastRefresh] = useState(null);
  const [selectedTable, setSelectedTable] = useState(null);
  const [schemaData, setSchemaData] = useState(null);
  const [schemaLoading, setSchemaLoading] = useState(false);

  // AI Analysis state
  const [aiInsights, setAiInsights] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);
  const [analysisType, setAnalysisType] = useState('overview');
  const [showAiPanel, setShowAiPanel] = useState(false);

  // Download state
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [fullTableData, setFullTableData] = useState(null);

  const isDark = theme === 'dark';

  // Download full table data
  const fetchFullTableData = async (tableName, limit = 1000) => {
    setDownloadLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/table-data/${tableName}?limit=${limit}`);
      const result = await response.json();
      if (result.success) {
        setFullTableData(result.data);
        return result.data;
      }
      throw new Error(result.error || 'Failed to fetch data');
    } catch (err) {
      alert('Error fetching data: ' + err.message);
      return null;
    } finally {
      setDownloadLoading(false);
    }
  };

  // Download as CSV
  const downloadCSV = async (tableName) => {
    let dataToExport = fullTableData;
    if (!dataToExport || dataToExport.length === 0) {
      dataToExport = await fetchFullTableData(tableName);
    }
    if (!dataToExport || dataToExport.length === 0) {
      // Use sample data if full data not available
      dataToExport = schemaData?.sample_data;
    }
    if (!dataToExport || dataToExport.length === 0) {
      alert('No data available to export');
      return;
    }

    const headers = Object.keys(dataToExport[0]);
    const csvContent = [
      headers.join(','),
      ...dataToExport.map(row =>
        headers.map(h => {
          const val = row[h];
          if (val === null || val === undefined) return '';
          const str = String(val);
          return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str;
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${tableName}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  // Download as Excel (XLSX) with 2 tabs: Structure + Data
  const downloadXLSX = async (tableName) => {
    setDownloadLoading(true);
    let dataError = null;

    try {
      // Fetch data if not already loaded (increase limit to 50000)
      let dataToExport = fullTableData;
      if (!dataToExport || dataToExport.length === 0) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/admin/table-data/${tableName}?limit=50000`);
          const result = await response.json();
          if (result.success && result.data && result.data.length > 0) {
            dataToExport = result.data;
            setFullTableData(result.data);
            console.log(`Excel: Fetched ${result.data.length} rows for ${tableName}`);
          } else {
            dataError = result.error || 'No data returned from API';
            console.error('Excel download API error:', dataError);
          }
        } catch (fetchErr) {
          dataError = fetchErr.message;
          console.error('Excel download fetch error:', fetchErr);
        }
      }

      // Use schemaData for structure
      const schema = schemaData?.schema || [];

      // Create Excel-compatible XML with 2 worksheets
      let xmlContent = `<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">`;

      // TAB 1: Structure (Schema)
      xmlContent += `
 <Worksheet ss:Name="Structure">
  <Table>
   <Row>
    <Cell><Data ss:Type="String">#</Data></Cell>
    <Cell><Data ss:Type="String">Field Name</Data></Cell>
    <Cell><Data ss:Type="String">Type</Data></Cell>
    <Cell><Data ss:Type="String">Mode</Data></Cell>
    <Cell><Data ss:Type="String">Description</Data></Cell>
   </Row>`;

      schema.forEach((field, idx) => {
        xmlContent += `
   <Row>
    <Cell><Data ss:Type="Number">${idx + 1}</Data></Cell>
    <Cell><Data ss:Type="String">${field.name}</Data></Cell>
    <Cell><Data ss:Type="String">${field.type}</Data></Cell>
    <Cell><Data ss:Type="String">${field.mode || 'NULLABLE'}</Data></Cell>
    <Cell><Data ss:Type="String">${field.description || ''}</Data></Cell>
   </Row>`;
      });

      xmlContent += `
  </Table>
 </Worksheet>`;

      // TAB 2: Data - Always create this tab
      xmlContent += `
 <Worksheet ss:Name="Data">
  <Table>`;

      if (dataToExport && dataToExport.length > 0) {
        const headers = Object.keys(dataToExport[0]);
        xmlContent += `
   <Row>`;

        headers.forEach(h => {
          const escaped = h.replace(/[<>&'"]/g, c => ({
            '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;'
          }[c]));
          xmlContent += `<Cell><Data ss:Type="String">${escaped}</Data></Cell>`;
        });
        xmlContent += '</Row>';

        dataToExport.forEach(row => {
          xmlContent += '<Row>';
          headers.forEach(h => {
            const val = row[h];
            const type = typeof val === 'number' ? 'Number' : 'String';
            const cellVal = val === null || val === undefined ? '' : String(val).replace(/[<>&'"]/g, c => ({
              '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;'
            }[c]));
            xmlContent += `<Cell><Data ss:Type="${type}">${cellVal}</Data></Cell>`;
          });
          xmlContent += '</Row>';
        });
      } else {
        // Show error message if no data
        xmlContent += `
   <Row>
    <Cell><Data ss:Type="String">Status</Data></Cell>
    <Cell><Data ss:Type="String">Message</Data></Cell>
   </Row>
   <Row>
    <Cell><Data ss:Type="String">Error</Data></Cell>
    <Cell><Data ss:Type="String">${dataError || 'No data available for this table. The table may be empty or data fetch timed out.'}</Data></Cell>
   </Row>
   <Row>
    <Cell><Data ss:Type="String">Table</Data></Cell>
    <Cell><Data ss:Type="String">${tableName}</Data></Cell>
   </Row>
   <Row>
    <Cell><Data ss:Type="String">Suggestion</Data></Cell>
    <Cell><Data ss:Type="String">Try the CSV Stream download for large tables (up to 100k rows)</Data></Cell>
   </Row>`;
      }

      xmlContent += `
  </Table>
 </Worksheet>`;

      xmlContent += '</Workbook>';

      const blob = new Blob([xmlContent], { type: 'application/vnd.ms-excel' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${tableName}_${new Date().toISOString().split('T')[0]}.xls`;
      link.click();
      URL.revokeObjectURL(link.href);

      // Show notification if there was an error but file was still created
      if (dataError) {
        alert(`Excel file created but data fetch failed: ${dataError}\n\nThe Data tab contains error information. Try the CSV Stream download for large tables.`);
      }
    } catch (err) {
      alert('Error creating Excel file: ' + err.message);
    } finally {
      setDownloadLoading(false);
    }
  };

  // Direct CSV stream download for large tables
  const downloadCSVStream = (tableName) => {
    const limit = 100000; // Max 100k rows
    const url = `${API_BASE_URL}/api/admin/table-export/${tableName}?limit=${limit}`;
    window.open(url, '_blank');
  };

  const fetchInventory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/table-inventory`);
      if (!response.ok) throw new Error('Failed to fetch inventory');
      const result = await response.json();
      if (result.success) {
        setData(result);
        setLastRefresh(new Date());
      } else {
        throw new Error(result.error || 'Unknown error');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchTableSchema = async (tableName) => {
    setSchemaLoading(true);
    setSelectedTable(tableName);
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/table-schema/${tableName}`);
      if (!response.ok) throw new Error('Failed to fetch schema');
      const result = await response.json();
      if (result.success) {
        setSchemaData(result);
      } else {
        throw new Error(result.error || 'Unknown error');
      }
    } catch (err) {
      setSchemaData({ error: err.message });
    } finally {
      setSchemaLoading(false);
    }
  };

  const closeSchemaModal = () => {
    setSelectedTable(null);
    setSchemaData(null);
  };

  // AI Analysis function
  const fetchAiAnalysis = async (type = 'overview') => {
    if (!data) return;

    setAiLoading(true);
    setAiError(null);
    setAnalysisType(type);
    setShowAiPanel(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/table-inventory/ai-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          inventory_data: {
            summary: data.summary,
            categories: data.categories
          },
          analysis_type: type
        })
      });

      const result = await response.json();

      if (result.success) {
        setAiInsights({
          text: result.insights,
          model: result.model,
          type: result.analysis_type,
          timestamp: result.timestamp
        });
      } else {
        setAiError(result.error || 'Failed to get AI analysis');
        if (result.fallback_insights) {
          setAiInsights({
            fallback: true,
            tips: result.fallback_insights.tips,
            message: result.fallback_insights.message
          });
        }
      }
    } catch (err) {
      setAiError(err.message);
    } finally {
      setAiLoading(false);
    }
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toLocaleString();
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px',
        color: isDark ? '#94a3b8' : '#64748b'
      }}>
        <RefreshCw size={32} style={{ animation: 'spin 1s linear infinite', marginRight: '12px' }} />
        Loading table inventory...
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: '40px',
        textAlign: 'center',
        color: '#ef4444',
        background: isDark ? '#1e293b' : '#fef2f2',
        borderRadius: '12px'
      }}>
        Error: {error}
        <button onClick={fetchInventory} style={{
          marginLeft: '12px',
          padding: '8px 16px',
          background: '#ef4444',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer'
        }}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Database size={32} color="#10b981" />
          <div>
            <h2 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: 0, fontSize: '24px' }}>
              BigQuery Table Inventory
            </h2>
            <p style={{ color: isDark ? '#64748b' : '#94a3b8', margin: '4px 0 0 0', fontSize: '14px' }}>
              Systematic tracking of all trading data tables
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => fetchAiAnalysis('overview')}
            disabled={!data || aiLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              background: aiLoading ? '#6366f1' : 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: data && !aiLoading ? 'pointer' : 'not-allowed',
              fontSize: '14px',
              fontWeight: '600',
              opacity: data ? 1 : 0.5
            }}
          >
            <Brain size={16} style={aiLoading ? { animation: 'spin 1s linear infinite' } : {}} />
            {aiLoading ? 'Analyzing...' : 'AI Analysis'}
          </button>
          <button
            onClick={fetchInventory}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              background: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
          borderRadius: '16px',
          padding: '20px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <Table size={24} color="#3b82f6" />
            <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>Total Tables</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: isDark ? '#f1f5f9' : '#1e293b' }}>
            {data?.summary?.total_tables}
          </div>
        </div>

        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
          borderRadius: '16px',
          padding: '20px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <TrendingUp size={24} color="#10b981" />
            <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>Total Rows</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#10b981' }}>
            {formatNumber(data?.summary?.total_rows)}
          </div>
        </div>

        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
          borderRadius: '16px',
          padding: '20px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <HardDrive size={24} color="#8b5cf6" />
            <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>Total Size</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#8b5cf6' }}>
            {(data?.summary?.total_size_mb / 1024).toFixed(2)} GB
          </div>
        </div>

        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#ffffff',
          borderRadius: '16px',
          padding: '20px',
          border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <Calendar size={24} color="#f59e0b" />
            <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>Last Refresh</span>
          </div>
          <div style={{ fontSize: '16px', fontWeight: '600', color: isDark ? '#f1f5f9' : '#1e293b' }}>
            {lastRefresh ? formatDate(lastRefresh.toISOString()) : 'N/A'}
          </div>
        </div>
      </div>

      {/* AI Insights Panel */}
      {showAiPanel && (
        <div style={{
          background: isDark ? 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%)' : 'linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%)',
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px',
          border: `1px solid ${isDark ? '#4c1d95' : '#a78bfa'}`,
          position: 'relative'
        }}>
          {/* Close button */}
          <button
            onClick={() => setShowAiPanel(false)}
            style={{
              position: 'absolute',
              top: '16px',
              right: '16px',
              background: 'transparent',
              border: 'none',
              color: isDark ? '#a78bfa' : '#7c3aed',
              cursor: 'pointer',
              padding: '4px'
            }}
          >
            <X size={20} />
          </button>

          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div style={{
              background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
              borderRadius: '12px',
              padding: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Brain size={24} color="white" />
            </div>
            <div>
              <h3 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: 0, fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={18} color="#fbbf24" />
                AI-Powered Analysis
              </h3>
              <p style={{ color: isDark ? '#a78bfa' : '#7c3aed', margin: '4px 0 0 0', fontSize: '13px' }}>
                {aiInsights?.model ? `Powered by ${aiInsights.model}` : 'Analyzing your data infrastructure...'}
              </p>
            </div>
          </div>

          {/* Analysis Type Buttons */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
            {[
              { type: 'overview', label: 'Overview', icon: TrendingUp },
              { type: 'quality', label: 'Data Quality', icon: AlertTriangle },
              { type: 'recommendations', label: 'Recommendations', icon: Lightbulb }
            ].map(({ type, label, icon: Icon }) => (
              <button
                key={type}
                onClick={() => fetchAiAnalysis(type)}
                disabled={aiLoading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  background: analysisType === type
                    ? 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)'
                    : (isDark ? '#1e1b4b' : '#ede9fe'),
                  color: analysisType === type ? 'white' : (isDark ? '#c4b5fd' : '#6d28d9'),
                  border: `1px solid ${analysisType === type ? 'transparent' : (isDark ? '#4c1d95' : '#a78bfa')}`,
                  borderRadius: '8px',
                  cursor: aiLoading ? 'not-allowed' : 'pointer',
                  fontSize: '13px',
                  fontWeight: '500',
                  opacity: aiLoading ? 0.7 : 1
                }}
              >
                <Icon size={14} />
                {label}
              </button>
            ))}
          </div>

          {/* AI Content */}
          <div style={{
            background: isDark ? 'rgba(0, 0, 0, 0.3)' : 'rgba(255, 255, 255, 0.8)',
            borderRadius: '12px',
            padding: '20px',
            minHeight: '150px'
          }}>
            {aiLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px', gap: '12px' }}>
                <Brain size={24} color="#8b5cf6" style={{ animation: 'spin 1s linear infinite' }} />
                <span style={{ color: isDark ? '#c4b5fd' : '#6d28d9', fontSize: '15px' }}>
                  Analyzing {data?.summary?.total_tables} tables with {formatNumber(data?.summary?.total_rows)} rows...
                </span>
              </div>
            ) : aiError && !aiInsights ? (
              <div style={{ color: '#ef4444', textAlign: 'center', padding: '20px' }}>
                <AlertTriangle size={32} style={{ marginBottom: '12px' }} />
                <div>Error: {aiError}</div>
              </div>
            ) : aiInsights?.fallback ? (
              <div>
                <p style={{ color: isDark ? '#fbbf24' : '#d97706', marginBottom: '16px', fontSize: '14px' }}>
                  {aiInsights.message}
                </p>
                <ul style={{ color: isDark ? '#e2e8f0' : '#1e293b', margin: 0, paddingLeft: '20px' }}>
                  {aiInsights.tips.map((tip, idx) => (
                    <li key={idx} style={{ marginBottom: '8px', fontSize: '14px' }}>{tip}</li>
                  ))}
                </ul>
              </div>
            ) : aiInsights?.text ? (
              <div style={{
                color: isDark ? '#e2e8f0' : '#1e293b',
                fontSize: '14px',
                lineHeight: '1.7',
                whiteSpace: 'pre-wrap'
              }}>
                {aiInsights.text}
              </div>
            ) : (
              <div style={{ color: isDark ? '#94a3b8' : '#64748b', textAlign: 'center', padding: '20px' }}>
                Click an analysis type above to get AI-powered insights
              </div>
            )}
          </div>

          {/* Timestamp */}
          {aiInsights?.timestamp && (
            <div style={{
              marginTop: '12px',
              fontSize: '11px',
              color: isDark ? '#6b7280' : '#9ca3af',
              textAlign: 'right'
            }}>
              Generated: {formatDate(aiInsights.timestamp)}
            </div>
          )}
        </div>
      )}

      {/* Category Breakdown */}
      <div style={{
        background: isDark ? '#1e293b' : '#ffffff',
        borderRadius: '16px',
        padding: '24px',
        border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
      }}>
        <h3 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: '0 0 20px 0', fontSize: '18px' }}>
          Tables by Category
        </h3>

        {data?.categories && Object.entries(data.categories).map(([category, catData]) => (
          <div key={category} style={{ marginBottom: '12px' }}>
            {/* Category Header */}
            <div
              onClick={() => toggleCategory(category)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px',
                background: isDark ? '#0f172a' : '#f8fafc',
                borderRadius: expandedCategories[category] ? '12px 12px 0 0' : '12px',
                cursor: 'pointer',
                border: `1px solid ${CATEGORY_COLORS[category]}44`,
                borderBottom: expandedCategories[category] ? 'none' : `1px solid ${CATEGORY_COLORS[category]}44`
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {expandedCategories[category] ? <ChevronDown size={20} color={CATEGORY_COLORS[category]} /> : <ChevronRight size={20} color={CATEGORY_COLORS[category]} />}
                <span style={{ fontSize: '20px' }}>{CATEGORY_ICONS[category]}</span>
                <span style={{ color: isDark ? '#f1f5f9' : '#1e293b', fontWeight: '600', textTransform: 'capitalize' }}>
                  {category}
                </span>
                <span style={{
                  background: CATEGORY_COLORS[category],
                  color: 'white',
                  padding: '2px 10px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {catData.count} tables
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                <span style={{ color: isDark ? '#94a3b8' : '#64748b', fontSize: '14px' }}>
                  {formatNumber(catData.total_rows)} rows
                </span>
              </div>
            </div>

            {/* Expanded Table List */}
            {expandedCategories[category] && (
              <div style={{
                background: isDark ? '#0f172a88' : '#f8fafc',
                borderRadius: '0 0 12px 12px',
                border: `1px solid ${CATEGORY_COLORS[category]}44`,
                borderTop: 'none',
                overflow: 'hidden'
              }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}` }}>
                      <th style={{ padding: '12px 16px', textAlign: 'left', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>TABLE NAME</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>ROWS</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>SIZE (MB)</th>
                      <th style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>LAST MODIFIED</th>
                      <th style={{ padding: '12px 16px', textAlign: 'center', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>STRUCTURE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {catData.tables.map((table, idx) => (
                      <tr
                        key={table.table_name}
                        style={{
                          borderBottom: idx < catData.tables.length - 1 ? `1px solid ${isDark ? '#334155' : '#e2e8f0'}` : 'none',
                          background: idx % 2 === 0 ? 'transparent' : (isDark ? '#1e293b22' : '#f1f5f922')
                        }}
                      >
                        <td style={{ padding: '12px 16px', color: isDark ? '#f1f5f9' : '#1e293b', fontSize: '13px', fontWeight: '500' }}>
                          {table.table_name}
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: '#10b981', fontSize: '13px', fontWeight: '600' }}>
                          {table.row_count.toLocaleString()}
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#94a3b8' : '#64748b', fontSize: '13px' }}>
                          {table.size_mb.toFixed(2)}
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'right', color: isDark ? '#64748b' : '#94a3b8', fontSize: '12px' }}>
                          {formatDate(table.last_modified)}
                        </td>
                        <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                          <button
                            onClick={() => fetchTableSchema(table.table_name)}
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '6px 12px',
                              background: '#3b82f6',
                              color: 'white',
                              border: 'none',
                              borderRadius: '6px',
                              fontSize: '12px',
                              cursor: 'pointer',
                              fontWeight: '500'
                            }}
                          >
                            <Columns size={14} />
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Schema Modal */}
      {selectedTable && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div style={{
            background: isDark ? '#1e293b' : '#ffffff',
            borderRadius: '16px',
            width: '90%',
            maxWidth: '1000px',
            maxHeight: '90vh',
            overflow: 'hidden',
            border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`
          }}>
            {/* Modal Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '20px 24px',
              borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
              background: isDark ? '#0f172a' : '#f8fafc'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Table size={24} color="#3b82f6" />
                <div>
                  <h3 style={{ margin: 0, color: isDark ? '#f1f5f9' : '#1e293b', fontSize: '18px' }}>
                    {selectedTable}
                  </h3>
                  {schemaData && !schemaData.error && (
                    <p style={{ margin: '4px 0 0 0', color: isDark ? '#64748b' : '#94a3b8', fontSize: '13px' }}>
                      {schemaData.num_fields} fields • {schemaData.num_rows?.toLocaleString()} rows • {schemaData.size_mb} MB
                    </p>
                  )}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                {/* Download Buttons */}
                <button
                  onClick={() => downloadCSVStream(selectedTable)}
                  title="Stream download - best for large tables (up to 100k rows)"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '8px 16px',
                    background: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: '600'
                  }}
                >
                  <Download size={16} />
                  CSV (100k)
                </button>
                <button
                  onClick={() => downloadXLSX(selectedTable)}
                  disabled={downloadLoading}
                  title="Excel with Structure + Data tabs (up to 50k rows)"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '8px 16px',
                    background: downloadLoading ? '#6b7280' : '#8b5cf6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: downloadLoading ? 'not-allowed' : 'pointer',
                    fontSize: '13px',
                    fontWeight: '600'
                  }}
                >
                  <FileSpreadsheet size={16} />
                  {downloadLoading ? 'Loading...' : 'Excel (50k)'}
                </button>
                <button
                  onClick={closeSchemaModal}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: isDark ? '#94a3b8' : '#64748b',
                    cursor: 'pointer',
                    padding: '8px'
                  }}
                >
                  <X size={24} />
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '24px', overflowY: 'auto', maxHeight: 'calc(90vh - 80px)' }}>
              {schemaLoading ? (
                <div style={{ textAlign: 'center', padding: '40px', color: isDark ? '#94a3b8' : '#64748b' }}>
                  <RefreshCw size={32} style={{ animation: 'spin 1s linear infinite', marginBottom: '12px' }} />
                  <div>Loading table structure...</div>
                </div>
              ) : schemaData?.error ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#ef4444' }}>
                  Error: {schemaData.error}
                </div>
              ) : schemaData ? (
                <>
                  {/* Schema Table */}
                  <h4 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: '0 0 16px 0' }}>
                    Table Structure ({schemaData.num_fields} fields)
                  </h4>
                  <div style={{
                    background: isDark ? '#0f172a' : '#f8fafc',
                    borderRadius: '8px',
                    overflow: 'hidden',
                    marginBottom: '24px'
                  }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}` }}>
                          <th style={{ padding: '12px 16px', textAlign: 'left', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>#</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>FIELD NAME</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>TYPE</th>
                          <th style={{ padding: '12px 16px', textAlign: 'left', color: isDark ? '#94a3b8' : '#64748b', fontSize: '12px', fontWeight: '600' }}>MODE</th>
                        </tr>
                      </thead>
                      <tbody>
                        {schemaData.schema.map((field, idx) => (
                          <tr key={field.name} style={{
                            borderBottom: idx < schemaData.schema.length - 1 ? `1px solid ${isDark ? '#334155' : '#e2e8f0'}` : 'none',
                            background: idx % 2 === 0 ? 'transparent' : (isDark ? '#1e293b22' : '#f1f5f922')
                          }}>
                            <td style={{ padding: '10px 16px', color: isDark ? '#64748b' : '#94a3b8', fontSize: '12px' }}>{idx + 1}</td>
                            <td style={{ padding: '10px 16px', color: isDark ? '#f1f5f9' : '#1e293b', fontSize: '13px', fontWeight: '500' }}>{field.name}</td>
                            <td style={{ padding: '10px 16px' }}>
                              <span style={{
                                background: field.type === 'STRING' ? '#3b82f6' :
                                           field.type === 'FLOAT' || field.type === 'FLOAT64' ? '#10b981' :
                                           field.type === 'INTEGER' || field.type === 'INT64' ? '#8b5cf6' :
                                           field.type === 'BOOLEAN' ? '#f59e0b' :
                                           field.type === 'TIMESTAMP' || field.type === 'DATETIME' || field.type === 'DATE' ? '#ec4899' : '#6b7280',
                                color: 'white',
                                padding: '2px 8px',
                                borderRadius: '4px',
                                fontSize: '11px',
                                fontWeight: '600'
                              }}>
                                {field.type}
                              </span>
                            </td>
                            <td style={{ padding: '10px 16px', color: isDark ? '#64748b' : '#94a3b8', fontSize: '12px' }}>{field.mode}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Sample Data */}
                  {schemaData.sample_data && schemaData.sample_data.length > 0 && (
                    <>
                      <h4 style={{ color: isDark ? '#f1f5f9' : '#1e293b', margin: '0 0 16px 0' }}>
                        Sample Data (First 5 rows)
                      </h4>
                      <div style={{
                        background: isDark ? '#0f172a' : '#f8fafc',
                        borderRadius: '8px',
                        overflow: 'auto',
                        maxHeight: '300px'
                      }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                          <thead>
                            <tr style={{ borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}` }}>
                              {Object.keys(schemaData.sample_data[0]).map(key => (
                                <th key={key} style={{
                                  padding: '10px 12px',
                                  textAlign: 'left',
                                  color: isDark ? '#94a3b8' : '#64748b',
                                  fontSize: '11px',
                                  fontWeight: '600',
                                  whiteSpace: 'nowrap',
                                  position: 'sticky',
                                  top: 0,
                                  background: isDark ? '#0f172a' : '#f8fafc'
                                }}>
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {schemaData.sample_data.map((row, rowIdx) => (
                              <tr key={rowIdx} style={{
                                borderBottom: rowIdx < schemaData.sample_data.length - 1 ? `1px solid ${isDark ? '#334155' : '#e2e8f0'}` : 'none'
                              }}>
                                {Object.values(row).map((value, colIdx) => (
                                  <td key={colIdx} style={{
                                    padding: '8px 12px',
                                    color: isDark ? '#f1f5f9' : '#1e293b',
                                    whiteSpace: 'nowrap',
                                    maxWidth: '200px',
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis'
                                  }}>
                                    {value === null ? <span style={{ color: '#6b7280' }}>null</span> : String(value)}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
