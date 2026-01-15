/**
 * BillingDashboard Component
 * @version 5.2.0 - Migrated to SSOT architecture
 */
import { useState, useEffect } from 'react'
import { DollarSign, TrendingUp, Activity, AlertCircle, Loader, PieChart } from 'lucide-react'
import { api } from '@/api'
import { PieChart as RechartsPie, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#ec4899']

function BillingDashboard() {
  const [loading, setLoading] = useState(true)
  const [billingData, setBillingData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchBillingData()
  }, [])

  const fetchBillingData = async () => {
    setLoading(true)
    setError(null)

    const result = await api.admin.getBillingData()

    if (result.success) {
      setBillingData(result.data)
    } else {
      setError(result.error)
    }

    setLoading(false)
  }

  const preparePieData = () => {
    if (!billingData?.breakdown_by_category) return []

    return Object.entries(billingData.breakdown_by_category).map(([name, value]) => ({
      name: name.replace(/_/g, ' ').toUpperCase(),
      value: value
    }))
  }

  const prepareBarData = () => {
    if (!billingData?.estimated_monthly_costs) return []

    const data = []

    // Cloud Functions
    Object.entries(billingData.estimated_monthly_costs.cloud_functions || {}).forEach(([name, cost]) => {
      data.push({
        name: name.replace(/_/g, ' '),
        cost: cost,
        category: 'Cloud Functions'
      })
    })

    // BigQuery
    Object.entries(billingData.estimated_monthly_costs.bigquery || {}).forEach(([name, cost]) => {
      data.push({
        name: name,
        cost: cost,
        category: 'BigQuery'
      })
    })

    // AI APIs
    Object.entries(billingData.estimated_monthly_costs.ai_apis || {}).forEach(([name, cost]) => {
      data.push({
        name: name,
        cost: cost,
        category: 'AI/ML'
      })
    })

    // Other services
    data.push({
      name: 'Cloud Scheduler',
      cost: billingData.estimated_monthly_costs.cloud_scheduler || 0,
      category: 'Other'
    })
    data.push({
      name: 'Cloud Run',
      cost: billingData.estimated_monthly_costs.cloud_run || 0,
      category: 'Other'
    })
    data.push({
      name: 'Networking',
      cost: billingData.estimated_monthly_costs.networking || 0,
      category: 'Other'
    })

    return data.sort((a, b) => b.cost - a.cost)
  }

  if (loading) {
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
        <div>Loading billing data...</div>
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
        <h3 style={{ color: 'white', marginBottom: '8px' }}>Error Loading Billing Data</h3>
        <p style={{ color: '#9ca3af', marginBottom: '20px' }}>{error}</p>
        <button
          onClick={fetchBillingData}
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

  const pieData = preparePieData()
  const barData = prepareBarData()

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ color: 'white', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <DollarSign size={32} style={{ color: '#10b981' }} />
          GCP Billing Dashboard
        </h2>
        <p style={{ color: '#9ca3af', margin: 0 }}>
          Estimated monthly costs and usage breakdown
        </p>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '30px' }}>
        <div style={{
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
            <DollarSign size={24} style={{ marginRight: '12px' }} />
            <span style={{ fontSize: '14px', opacity: 0.9 }}>Total Monthly Cost</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold' }}>
            ${billingData?.total_estimated?.toFixed(2)}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '8px' }}>
            Period: {billingData?.billing_period}
          </div>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
            <Activity size={24} style={{ marginRight: '12px' }} />
            <span style={{ fontSize: '14px', opacity: 0.9 }}>Compute & Functions</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold' }}>
            ${billingData?.breakdown_by_category?.compute?.toFixed(2)}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '8px' }}>
            {((billingData?.breakdown_by_category?.compute / billingData?.total_estimated) * 100).toFixed(1)}% of total
          </div>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
            <TrendingUp size={24} style={{ marginRight: '12px' }} />
            <span style={{ fontSize: '14px', opacity: 0.9 }}>AI & ML Services</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold' }}>
            ${billingData?.breakdown_by_category?.ai_ml?.toFixed(2)}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '8px' }}>
            {((billingData?.breakdown_by_category?.ai_ml / billingData?.total_estimated) * 100).toFixed(1)}% of total
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
        {/* Pie Chart */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155'
        }}>
          <h3 style={{ color: 'white', marginBottom: '20px' }}>Cost Breakdown by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsPie>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: 'white'
                }}
              />
            </RechartsPie>
          </ResponsiveContainer>
        </div>

        {/* Bar Chart */}
        <div style={{
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          borderRadius: '16px',
          padding: '24px',
          border: '1px solid #334155'
        }}>
          <h3 style={{ color: 'white', marginBottom: '20px' }}>Cost by Service</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="name"
                stroke="#9ca3af"
                angle={-45}
                textAnchor="end"
                height={100}
                fontSize={10}
              />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: 'white'
                }}
                formatter={(value) => `$${value.toFixed(2)}`}
              />
              <Bar dataKey="cost" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Breakdown */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155',
        marginBottom: '20px'
      }}>
        <h3 style={{ color: 'white', marginBottom: '20px' }}>Detailed Cost Breakdown</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', color: 'white', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #334155' }}>
                <th style={{ padding: '12px', textAlign: 'left', color: '#10b981' }}>Service</th>
                <th style={{ padding: '12px', textAlign: 'left', color: '#10b981' }}>Category</th>
                <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>Monthly Cost</th>
                <th style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>% of Total</th>
              </tr>
            </thead>
            <tbody>
              {barData.map((item, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #334155' }}>
                  <td style={{ padding: '12px' }}>{item.name}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      padding: '4px 12px',
                      borderRadius: '12px',
                      background: '#10b98120',
                      border: '1px solid #10b981',
                      color: '#10b981',
                      fontSize: '12px'
                    }}>
                      {item.category}
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', fontWeight: 'bold' }}>
                    ${item.cost.toFixed(2)}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>
                    {((item.cost / billingData.total_estimated) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
              <tr style={{ borderTop: '2px solid #334155', fontWeight: 'bold' }}>
                <td style={{ padding: '12px' }} colSpan="2">TOTAL</td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>
                  ${billingData.total_estimated.toFixed(2)}
                </td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>
                  100.0%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Cost Optimization Tips */}
      <div style={{
        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        borderRadius: '16px',
        padding: '24px',
        color: 'white'
      }}>
        <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center' }}>
          <AlertCircle size={24} style={{ marginRight: '12px' }} />
          Cost Optimization Tips
        </h3>
        <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.8' }}>
          <li>Implement caching for AI predictions to reduce API calls by 90%</li>
          <li>Consider using BigQuery partitioning to reduce query costs</li>
          <li>Review Cloud Function memory allocation (may be over-provisioned)</li>
          <li>Set up billing alerts at $50, $100, and $200 thresholds</li>
          <li>Monitor AI API usage and optimize prompt lengths</li>
          <li>Use committed use discounts for predictable workloads</li>
        </ul>
      </div>
    </div>
  )
}

export default BillingDashboard
