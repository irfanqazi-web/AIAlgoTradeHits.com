import { useState, useEffect } from 'react';
import { Database, Download, FileSpreadsheet, RefreshCw, ArrowUpDown } from 'lucide-react';
import * as XLSX from 'xlsx';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-1075463475276.us-central1.run.app'
);

export default function DatabaseSummary({ theme = 'dark' }) {
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: 'row_count', direction: 'desc' });

  const isDark = theme === 'dark';

  useEffect(() => {
    fetchTableCounts();
  }, []);

  const fetchTableCounts = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching from:', `${API_BASE_URL}/api/admin/table-counts`);
      const response = await fetch(`${API_BASE_URL}/api/admin/table-counts`);
      const data = await response.json();

      console.log('API Response:', data);

      if (data.success && data.tables) {
        setTables(data.tables);
        console.log(`✅ Loaded ${data.tables.length} tables`);
      } else {
        setError(data.error || 'Failed to fetch data');
        console.error('❌ API Error:', data);
      }
    } catch (err) {
      setError('Failed to connect to API: ' + err.message);
      console.error('❌ Fetch Error:', err);
    }
    setLoading(false);
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });

    const sorted = [...tables].sort((a, b) => {
      const aVal = a[key] || 0;
      const bVal = b[key] || 0;

      if (typeof aVal === 'string') {
        return direction === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      return direction === 'asc' ? aVal - bVal : bVal - aVal;
    });

    setTables(sorted);
  };

  const downloadAsXLSX = () => {
    if (tables.length === 0) {
      alert('No data to download');
      return;
    }

    setDownloading(true);

    try {
      console.log('📊 Creating Excel with', tables.length, 'rows');

      // Create simple data array for Excel
      const excelData = tables.map((table, index) => ({
        '#': index + 1,
        'Category': table.category || 'other',
        'Table Name': table.table_name,
        'Record Count': table.row_count || 0,
        'Table Size (MB)': table.size_mb ? table.size_mb.toFixed(2) : '0.00'
      }));

      console.log('First row:', excelData[0]);

      // Create worksheet from data
      const ws = XLSX.utils.json_to_sheet(excelData);

      // Set column widths
      ws['!cols'] = [
        { wch: 5 },   // #
        { wch: 18 },  // Category
        { wch: 35 },  // Table Name
        { wch: 15 },  // Record Count
        { wch: 18 }   // Table Size
      ];

      // Create workbook
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Database Summary');

      // Generate filename
      const filename = `database_summary_${new Date().toISOString().split('T')[0]}.xlsx`;

      // Download
      XLSX.writeFile(wb, filename);

      console.log(`✅ Downloaded ${filename}`);
      alert(`Successfully downloaded ${filename} with ${tables.length} tables`);
    } catch (error) {
      console.error('❌ Error generating Excel:', error);
      alert('Error generating Excel file: ' + error.message);
    } finally {
      setDownloading(false);
    }
  };

  const SortableHeader = ({ label, sortKey }) => (
    <th
      onClick={() => handleSort(sortKey)}
      style={{
        padding: '12px 16px',
        textAlign: 'left',
        color: isDark ? '#94a3b8' : '#64748b',
        fontSize: '13px',
        fontWeight: '600',
        cursor: 'pointer',
        userSelect: 'none',
        transition: 'color 0.2s'
      }}
      onMouseEnter={(e) => e.currentTarget.style.color = isDark ? '#fff' : '#000'}
      onMouseLeave={(e) => e.currentTarget.style.color = isDark ? '#94a3b8' : '#64748b'}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {label}
        <ArrowUpDown
          size={14}
          color={sortConfig.key === sortKey ? '#10b981' : (isDark ? '#64748b' : '#94a3b8')}
        />
      </div>
    </th>
  );

  const totalRows = tables.reduce((sum, t) => sum + (t.row_count || 0), 0);
  const totalSize = tables.reduce((sum, t) => sum + (t.size_mb || 0), 0);

  return (
    <div style={{
      padding: '24px',
      maxWidth: '1600px',
      margin: '0 auto',
      minHeight: '100vh',
      background: isDark ? '#0a0e27' : '#f8fafc'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: isDark ? 'white' : '#1e293b',
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <Database size={32} color="#10b981" />
            Database Summary
          </h1>
          <p style={{
            color: isDark ? '#64748b' : '#64748b',
            marginTop: '4px',
            fontSize: '14px'
          }}>
            Download complete overview of all BigQuery tables (Category, Table Name, Record Count, Size)
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={fetchTableCounts}
            disabled={loading}
            style={{
              padding: '12px 20px',
              background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#fff',
              color: isDark ? 'white' : '#1e293b',
              border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              opacity: loading ? 0.6 : 1
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
          <button
            onClick={downloadAsXLSX}
            disabled={downloading || loading || tables.length === 0}
            style={{
              padding: '12px 20px',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: (downloading || loading || tables.length === 0) ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              opacity: (downloading || loading || tables.length === 0) ? 0.6 : 1
            }}
          >
            <FileSpreadsheet size={16} />
            {downloading ? 'Generating...' : 'Download XLSX'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{
          padding: '16px',
          marginBottom: '24px',
          background: '#fee2e2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          color: '#991b1b'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Summary Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '20px',
        marginBottom: '32px'
      }}>
        <StatCard
          label="Total Tables"
          value={tables.length.toLocaleString()}
          color="#10b981"
          isDark={isDark}
        />
        <StatCard
          label="Total Rows"
          value={totalRows.toLocaleString()}
          color="#3b82f6"
          isDark={isDark}
        />
        <StatCard
          label="Total Size"
          value={`${totalSize.toFixed(2)} MB`}
          color="#f59e0b"
          isDark={isDark}
        />
      </div>

      {/* Tables List */}
      <div style={{
        background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#fff',
        borderRadius: '16px',
        padding: '24px',
        border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
        boxShadow: isDark ? 'none' : '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: isDark ? 'white' : '#1e293b',
          marginBottom: '16px'
        }}>
          All Tables ({tables.length})
        </h3>

        {loading ? (
          <div style={{
            textAlign: 'center',
            padding: '60px',
            color: isDark ? '#64748b' : '#94a3b8'
          }}>
            Loading table counts...
          </div>
        ) : tables.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px',
            color: isDark ? '#64748b' : '#94a3b8'
          }}>
            No tables found
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '14px'
            }}>
              <thead>
                <tr style={{
                  borderBottom: `2px solid ${isDark ? '#334155' : '#e2e8f0'}`
                }}>
                  <th style={{ padding: '12px 16px', textAlign: 'left', color: isDark ? '#94a3b8' : '#64748b', fontSize: '13px', fontWeight: '600' }}>#</th>
                  <SortableHeader label="Category" sortKey="category" />
                  <SortableHeader label="Table Name" sortKey="table_name" />
                  <SortableHeader label="Record Count" sortKey="row_count" />
                  <SortableHeader label="Size (MB)" sortKey="size_mb" />
                </tr>
              </thead>
              <tbody>
                {tables.map((table, index) => (
                  <tr
                    key={table.table_name}
                    style={{
                      borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = isDark ? '#1e293b' : '#f8fafc'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '12px 16px', color: isDark ? '#64748b' : '#94a3b8' }}>{index + 1}</td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '16px',
                        fontSize: '12px',
                        fontWeight: '600',
                        background: getCategoryColor(table.category),
                        color: 'white'
                      }}>
                        {table.category || 'other'}
                      </span>
                    </td>
                    <td style={{
                      padding: '12px 16px',
                      fontWeight: '600',
                      color: isDark ? 'white' : '#1e293b',
                      fontFamily: 'monospace'
                    }}>
                      {table.table_name}
                    </td>
                    <td style={{
                      padding: '12px 16px',
                      color: isDark ? '#10b981' : '#059669',
                      fontWeight: '600'
                    }}>
                      {(table.row_count || 0).toLocaleString()}
                    </td>
                    <td style={{
                      padding: '12px 16px',
                      color: isDark ? '#94a3b8' : '#64748b'
                    }}>
                      {table.size_mb ? table.size_mb.toFixed(2) : '0.00'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color, isDark }) {
  return (
    <div style={{
      background: isDark ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' : '#fff',
      borderRadius: '12px',
      padding: '20px',
      border: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
      boxShadow: isDark ? 'none' : '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <div style={{
        fontSize: '13px',
        color: isDark ? '#64748b' : '#64748b',
        fontWeight: '500',
        marginBottom: '12px'
      }}>
        {label}
      </div>
      <div style={{
        fontSize: '28px',
        fontWeight: '700',
        color: isDark ? 'white' : '#1e293b'
      }}>
        {value}
      </div>
    </div>
  );
}

function getCategoryColor(category) {
  const colors = {
    stocks: '#ef4444',
    crypto: '#f59e0b',
    forex: '#10b981',
    etfs: '#3b82f6',
    indices: '#8b5cf6',
    commodities: '#ec4899',
    fundamentals: '#06b6d4',
    analyst: '#14b8a6',
    corporate_actions: '#a855f7',
    other: '#6b7280'
  };
  return colors[category] || colors.other;
}
