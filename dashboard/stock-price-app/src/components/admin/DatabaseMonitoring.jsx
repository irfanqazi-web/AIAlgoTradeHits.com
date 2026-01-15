/**
 * DatabaseMonitoring Component
 * @version 5.2.0 - Migrated to SSOT architecture
 */
import { useState, useEffect } from 'react'
import { Database, Activity, AlertCircle, CheckCircle, Clock, TrendingUp, HardDrive, Loader, FileDown } from 'lucide-react'
import { api } from '@/api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import jsPDF from 'jspdf'
import 'jspdf-autotable'

function DatabaseMonitoring() {
  const [loading, setLoading] = useState(true)
  const [monitoringData, setMonitoringData] = useState(null)
  const [error, setError] = useState(null)
  const [selectedView, setSelectedView] = useState('overview')
  const [lastRefresh, setLastRefresh] = useState(new Date())

  useEffect(() => {
    fetchMonitoringData()
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchMonitoringData, 300000)
    return () => clearInterval(interval)
  }, [])

  const fetchMonitoringData = async () => {
    setLoading(true)
    setError(null)

    const result = await api.admin.getFullReport()

    if (result.success) {
      setMonitoringData(result.data)
      setLastRefresh(new Date())
    } else {
      setError(result.error)
    }

    setLoading(false)
  }

  const downloadPDF = () => {
    if (!monitoringData) return

    const doc = new jsPDF()
    const summary = monitoringData.summary || {}
    const tables = monitoringData.tables || []
    const topPairs = monitoringData.top_pairs || []

    // Title
    doc.setFontSize(20)
    doc.setTextColor(16, 185, 129) // green
    doc.text('Database Monitoring Report', 14, 20)

    // Date
    doc.setFontSize(10)
    doc.setTextColor(100, 100, 100)
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28)

    // Summary Section
    doc.setFontSize(14)
    doc.setTextColor(0, 0, 0)
    doc.text('Summary', 14, 40)

    doc.setFontSize(10)
    let yPos = 48
    doc.text(`Total Tables: ${summary.total_tables || 0}`, 14, yPos)
    yPos += 6
    doc.text(`Healthy Tables: ${summary.healthy_tables || 0}`, 14, yPos)
    yPos += 6
    doc.text(`Total Records: ${api.admin.formatNumber(summary.total_records || 0)}`, 14, yPos)
    yPos += 6
    doc.text(`Total Size: ${(summary.total_size_gb || 0).toFixed(2)} GB`, 14, yPos)
    yPos += 10

    // Tables Section
    doc.setFontSize(14)
    doc.text('BigQuery Tables', 14, yPos)
    yPos += 8

    const tableData = tables.map(table => [
      table.table_name,
      api.admin.formatNumber(table.row_count || 0),
      `${(table.size_gb || 0).toFixed(2)} GB`,
      table.unique_pairs || 0,
      table.records_24h || 0,
      table.latest_data || 'N/A',
      table.status || 'Unknown'
    ])

    doc.autoTable({
      head: [['Table Name', 'Rows', 'Size', 'Pairs', '24h Records', 'Latest Data', 'Status']],
      body: tableData,
      startY: yPos,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [16, 185, 129] },
      columnStyles: {
        0: { cellWidth: 40 },
        1: { cellWidth: 20 },
        2: { cellWidth: 18 },
        3: { cellWidth: 15 },
        4: { cellWidth: 20 },
        5: { cellWidth: 35 },
        6: { cellWidth: 20 }
      }
    })

    // Top Pairs Section
    if (topPairs.length > 0) {
      doc.addPage()
      doc.setFontSize(14)
      doc.setTextColor(0, 0, 0)
      doc.text('Top 20 Trading Pairs by Volume (24h)', 14, 20)

      const pairsData = topPairs.map((pair, idx) => [
        `#${idx + 1}`,
        pair.pair,
        `$${pair.latest_price.toFixed(2)}`,
        api.admin.formatNumber(pair.avg_volume_24h),
        pair.data_points
      ])

      doc.autoTable({
        head: [['Rank', 'Pair', 'Latest Price', 'Avg Volume (24h)', 'Data Points']],
        body: pairsData,
        startY: 28,
        styles: { fontSize: 9 },
        headStyles: { fillColor: [16, 185, 129] },
        columnStyles: {
          0: { cellWidth: 15 },
          1: { cellWidth: 45 },
          2: { cellWidth: 30 },
          3: { cellWidth: 40 },
          4: { cellWidth: 30 }
        }
      })
    }

    // Save PDF
    doc.save(`Database_Monitoring_Report_${new Date().toISOString().split('T')[0]}.pdf`)
  }

  const renderOverview = () => {
    if (!monitoringData?.tables) return null

    const summary = monitoringData.summary || {}
    const tables = monitoringData.tables || []

    return (
      <div>
        {/* Summary Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '30px' }}>
          <SummaryCard
            title="Total Tables"
            value={summary.total_tables || 0}
            icon={Database}
            color="#3b82f6"
          />
          <SummaryCard
            title="Healthy Tables"
            value={summary.healthy_tables || 0}
            icon={CheckCircle}
            color="#10b981"
          />
          <SummaryCard
            title="Total Records"
            value={api.admin.formatNumber(summary.total_records || 0)}
            icon={Activity}
            color="#8b5cf6"
          />
          <SummaryCard
            title="Total Size"
            value={`${(summary.total_size_gb || 0).toFixed(2)} GB`}
            icon={HardDrive}
            color="#f59e0b"
          />
        </div>

        {/* Tables Grid */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155',
          marginBottom: '20px'
        }}>
          <h3 style={{ color: 'white', marginBottom: '20px' }}>BigQuery Tables</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', color: 'white', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #334155' }}>
                  <th style={{ padding: '12px', textAlign: 'left', color: '#10b981' }}>Table Name</th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>Rows</th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>Size (GB)</th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>Pairs</th>
                  <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>24h Records</th>
                  <th style={{ padding: '12px', textAlign: 'center', color: '#10b981' }}>Latest Data</th>
                  <th style={{ padding: '12px', textAlign: 'center', color: '#10b981' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {tables.map((table, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #334155' }}>
                    <td style={{ padding: '12px', fontWeight: '600' }}>{table.table_name}</td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      {api.admin.formatNumber(table.row_count || 0)}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      {(table.size_gb || 0).toFixed(4)}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      {table.unique_pairs || 'N/A'}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>
                      {api.admin.formatNumber(table.recent_24h_count || 0)}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', fontSize: '12px', color: '#9ca3af' }}>
                      {table.latest_timestamp ? new Date(table.latest_timestamp).toLocaleString() : 'N/A'}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <StatusBadge status={table.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Data Quality */}
        {monitoringData.quality && monitoringData.quality.length > 0 && (
          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #334155'
          }}>
            <h3 style={{ color: 'white', marginBottom: '20px' }}>Data Quality (Last 7 Days)</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
              {monitoringData.quality.map((quality, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(15, 23, 42, 0.5)',
                    borderRadius: '12px',
                    padding: '16px',
                    border: `1px solid ${api.admin.getStatusColor(quality.status)}`
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h4 style={{ color: 'white', margin: 0 }}>{quality.table_name}</h4>
                    <StatusBadge status={quality.status} />
                  </div>
                  <div style={{ color: '#10b981', fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
                    {quality.completeness}
                  </div>
                  {quality.missing_dates && quality.missing_dates.length > 0 && (
                    <div style={{ color: '#ef4444', fontSize: '12px' }}>
                      Missing dates: {quality.missing_dates.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  const renderGrowth = () => {
    if (!monitoringData?.growth) return null

    return (
      <div>
        {monitoringData.growth.map((tableGrowth, idx) => (
          <div
            key={idx}
            style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              borderRadius: '16px',
              padding: '24px',
              border: '1px solid #334155',
              marginBottom: '20px'
            }}
          >
            <h3 style={{ color: 'white', marginBottom: '20px' }}>
              {tableGrowth.table_name} - Daily Growth (Last 30 Days)
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tableGrowth.daily_records}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: 'white'
                  }}
                />
                <Bar dataKey="records" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ))}
      </div>
    )
  }

  const renderTopPairs = () => {
    if (!monitoringData?.top_pairs) return null

    return (
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155'
      }}>
        <h3 style={{ color: 'white', marginBottom: '20px' }}>
          Top 20 Trading Pairs by Volume (24h)
        </h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', color: 'white', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #334155' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: '#10b981' }}>Rank</th>
                <th style={{ padding: '12px', textAlign: 'left', color: '#10b981' }}>Pair</th>
                <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>Latest Price</th>
                <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>Avg Volume (24h)</th>
                <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>Data Points</th>
              </tr>
            </thead>
            <tbody>
              {monitoringData.top_pairs.map((pair, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #334155' }}>
                  <td style={{ padding: '12px', fontWeight: 'bold', color: '#10b981' }}>
                    #{idx + 1}
                  </td>
                  <td style={{ padding: '12px', fontWeight: '600' }}>{pair.pair}</td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    ${pair.latest_price.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    {api.admin.formatNumber(pair.avg_volume_24h)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>{pair.data_points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  if (loading && !monitoringData) {
    return (
      <div style={{
        minHeight: '400px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white'
      }}>
        <Loader size={48} className="spin" style={{ color: '#10b981', marginBottom: '16px' }} />
        <div>Loading monitoring data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '32px',
        border: '1px solid #334155',
        textAlign: 'center'
      }}>
        <AlertCircle size={48} style={{ color: '#ef4444', marginBottom: '16px' }} />
        <h3 style={{ color: 'white', marginBottom: '8px' }}>Error Loading Monitoring Data</h3>
        <p style={{ color: '#9ca3af', marginBottom: '20px' }}>{error}</p>
        <button
          onClick={fetchMonitoringData}
          style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ color: 'white', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Database size={32} style={{ color: '#10b981' }} />
            Database Monitoring
          </h2>
          <p style={{ color: '#9ca3af', margin: 0 }}>
            Real-time BigQuery statistics and system health metrics
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ color: '#9ca3af', fontSize: '14px' }}>
            <Clock size={16} style={{ display: 'inline', marginRight: '6px' }} />
            Last refresh: {lastRefresh.toLocaleTimeString()}
          </div>
          <button
            onClick={downloadPDF}
            disabled={!monitoringData}
            style={{
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 20px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: !monitoringData ? 'not-allowed' : 'pointer',
              opacity: !monitoringData ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <FileDown size={16} />
            Download PDF
          </button>
          <button
            onClick={fetchMonitoringData}
            disabled={loading}
            style={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 20px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1
            }}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* View Selector */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '24px',
        padding: '8px',
        background: '#1e293b',
        borderRadius: '12px',
        width: 'fit-content'
      }}>
        {['overview', 'growth', 'top-pairs'].map(view => (
          <button
            key={view}
            onClick={() => setSelectedView(view)}
            style={{
              padding: '8px 20px',
              borderRadius: '8px',
              border: 'none',
              background: selectedView === view
                ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                : 'transparent',
              color: 'white',
              cursor: 'pointer',
              fontWeight: selectedView === view ? '600' : '400',
              transition: 'all 0.3s'
            }}
          >
            {view === 'overview' ? 'Overview' : view === 'growth' ? 'Data Growth' : 'Top Pairs'}
          </button>
        ))}
      </div>

      {/* Content */}
      {selectedView === 'overview' && renderOverview()}
      {selectedView === 'growth' && renderGrowth()}
      {selectedView === 'top-pairs' && renderTopPairs()}
    </div>
  )
}

function SummaryCard({ title, value, icon: Icon, color }) {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid #334155'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
        <Icon size={24} style={{ color: color, marginRight: '12px' }} />
        <span style={{ color: '#9ca3af', fontSize: '14px' }}>{title}</span>
      </div>
      <div style={{ color: 'white', fontSize: '28px', fontWeight: 'bold' }}>
        {value}
      </div>
    </div>
  )
}

function StatusBadge({ status }) {
  const color = api.admin.getStatusColor(status)
  return (
    <span style={{
      display: 'inline-block',
      padding: '4px 12px',
      borderRadius: '12px',
      background: color + '20',
      border: `1px solid ${color}`,
      color: color,
      fontSize: '12px',
      fontWeight: '600',
      textTransform: 'uppercase'
    }}>
      {status}
    </span>
  )
}

export default DatabaseMonitoring
