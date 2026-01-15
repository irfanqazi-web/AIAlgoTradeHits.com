/**
 * System Monitoring Service
 * Fetches BigQuery stats, billing data, and system health metrics
 */

const MONITORING_URL = import.meta.env.VITE_MONITORING_URL || 'https://system-monitoring-cnyn5l4u2a-uc.a.run.app';

class MonitoringService {
  /**
   * Get all table statistics
   */
  async getTableStats() {
    try {
      const response = await fetch(`${MONITORING_URL}?endpoint=tables`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Monitoring API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data.tables || []
      };
    } catch (error) {
      console.error('Table stats error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get billing information
   */
  async getBillingData() {
    try {
      const response = await fetch(`${MONITORING_URL}?endpoint=billing`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Monitoring API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data.billing || {}
      };
    } catch (error) {
      console.error('Billing data error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get system health status
   */
  async getSystemHealth() {
    try {
      const response = await fetch(`${MONITORING_URL}?endpoint=health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Monitoring API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: {
          functions: data.functions || [],
          schedulers: data.schedulers || []
        }
      };
    } catch (error) {
      console.error('System health error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get data growth metrics
   */
  async getDataGrowth() {
    try {
      const response = await fetch(`${MONITORING_URL}?endpoint=growth`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Monitoring API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data.growth || []
      };
    } catch (error) {
      console.error('Data growth error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get data quality metrics
   */
  async getDataQuality() {
    try {
      const response = await fetch(`${MONITORING_URL}?endpoint=quality`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Monitoring API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data.quality || []
      };
    } catch (error) {
      console.error('Data quality error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get top trading pairs by volume
   */
  async getTopPairs() {
    try {
      const response = await fetch(`${MONITORING_URL}?endpoint=top-pairs`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Monitoring API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data.top_pairs || []
      };
    } catch (error) {
      console.error('Top pairs error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get complete monitoring report
   */
  async getFullReport() {
    try {
      const response = await fetch(`${MONITORING_URL}?endpoint=full`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Monitoring API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data
      };
    } catch (error) {
      console.error('Full report error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Format bytes to human readable format
   */
  formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  /**
   * Format large numbers
   */
  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  }

  /**
   * Get status color
   */
  getStatusColor(status) {
    const colors = {
      'healthy': '#10b981',
      'good': '#10b981',
      'active': '#10b981',
      'enabled': '#10b981',
      'warning': '#f59e0b',
      'needs_attention': '#f59e0b',
      'error': '#ef4444',
      'disabled': '#ef4444'
    };
    return colors[status] || '#9ca3af';
  }

  /**
   * Calculate percentage change
   */
  calculateChange(current, previous) {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous * 100).toFixed(2);
  }
}

export default new MonitoringService();
