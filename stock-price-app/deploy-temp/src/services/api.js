/**
 * API Service for connecting to Trading Data API (BigQuery)
 * All market data from TwelveData API
 */

// Use environment variable if available, fallback to defaults
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-252370699783.us-central1.run.app'
);

export { API_BASE_URL };

// TwelveData Asset Types
const ASSET_TYPES = ['stocks', 'crypto', 'forex', 'etfs', 'indices', 'commodities'];
const TIMEFRAMES = ['weekly', 'daily', 'hourly', '5min'];

class ApiService {
  /**
   * Fetch TwelveData data for any asset type and timeframe
   * @param {string} assetType - stocks, crypto, forex, etfs, indices, commodities
   * @param {string} timeframe - weekly, daily, hourly, 5min
   * @param {number} limit - Number of records to fetch
   */
  async getTwelveData(assetType = 'stocks', timeframe = 'daily', limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/twelvedata/${assetType}/${timeframe}?limit=${limit}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Error fetching ${assetType} ${timeframe} data:`, error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * Fetch historical data for a specific symbol from TwelveData
   * @param {string} symbol - Asset symbol (e.g., 'AAPL', 'BTC/USD')
   * @param {string} assetType - stocks, crypto, forex, etfs, indices, commodities
   * @param {string} timeframe - weekly, daily, hourly, 5min
   * @param {number} limit - Number of historical records
   */
  async getTwelveDataHistory(symbol, assetType = 'stocks', timeframe = 'daily', limit = 100) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/twelvedata/${assetType}/${timeframe}/history?symbol=${encodeURIComponent(symbol)}&limit=${limit}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Error fetching ${symbol} history:`, error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * Smart NLP search across all TwelveData assets
   * @param {string} query - Natural language query
   * @param {string} assetType - Target asset type or 'all'
   * @param {string} timeframe - Target timeframe
   */
  async smartSearch(query, assetType = 'all', timeframe = 'daily') {
    try {
      // Use the correct endpoint /api/analysis/nlp-search
      const response = await fetch(`${API_BASE_URL}/api/analysis/nlp-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          asset_type: assetType,
          timeframe
        })
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Smart search error:', error);
      return { success: false, results: [], error: error.message };
    }
  }

  /**
   * Get market summary for TwelveData assets
   * @param {string} assetType - Asset type to summarize
   * @param {string} timeframe - Timeframe for summary
   */
  async getTwelveDataSummary(assetType = 'stocks', timeframe = 'daily') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/twelvedata/${assetType}/${timeframe}/summary`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Error fetching ${assetType} summary:`, error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Fetch crypto data for specified timeframe
   * @param {string} timeframe - 'daily', 'hourly', or '5min'
   * @param {number} limit - Number of records to fetch
   */
  async getCryptoData(timeframe = 'daily', limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/crypto/${timeframe}?limit=${limit}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching crypto data:', error);
      throw error;
    }
  }

  /**
   * Fetch stock data (daily)
   * @param {number} limit - Number of records to fetch
   */
  async getStockData(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stocks?limit=${limit}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching stock data:', error);
      throw error;
    }
  }

  /**
   * Fetch stock hourly data
   * @param {number} limit - Number of records to fetch
   */
  async getStockHourlyData(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stocks/hourly?limit=${limit}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching stock hourly data:', error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * Fetch stock 5-minute data
   * @param {number} limit - Number of records to fetch
   */
  async getStock5MinData(limit = 100) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stocks/5min?limit=${limit}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching stock 5-min data:', error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * Get market summary statistics
   * @param {string} marketType - 'crypto' or 'stock'
   */
  async getMarketSummary(marketType = 'crypto') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/summary/${marketType}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching market summary:', error);
      throw error;
    }
  }

  /**
   * Get all users (admin only)
   */
  async getUsers() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  }

  /**
   * Create a new user (admin only)
   * @param {object} userData - { email, name, role }
   */
  async createUser(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  }

  /**
   * Update user (admin only)
   * @param {string} userId - User ID
   * @param {object} updates - Fields to update
   */
  async updateUser(userId, updates) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error updating user:', error);
      throw error;
    }
  }

  /**
   * Delete user (admin only)
   * @param {string} userId - User ID
   */
  async deleteUser(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error deleting user:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * User authentication - Login
   * @param {string} email - User email
   * @param {string} password - User password
   */
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Store token in localStorage
        localStorage.setItem('auth_token', data.user.token);
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Change password
   * @param {string} oldPassword - Current password
   * @param {string} newPassword - New password
   */
  async changePassword(oldPassword, newPassword) {
    try {
      const token = localStorage.getItem('auth_token');

      const response = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Password change error:', error);
      throw error;
    }
  }

  /**
   * Verify authentication token
   */
  async verifyToken() {
    try {
      const token = localStorage.getItem('auth_token');

      if (!token) {
        return { success: false, error: 'No token found' };
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Token verification error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  /**
   * Get current user from localStorage
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!localStorage.getItem('auth_token');
  }

  /**
   * Send invitation email to user
   * @param {string} userId - User ID to send invite to
   */
  async sendInvitation(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/${userId}/send-invite`, {
        method: 'POST',
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Send invitation error:', error);
      throw error;
    }
  }

  /**
   * Get historical data for a specific crypto pair
   * @param {string} pair - Crypto pair (e.g., 'BTC/USD')
   * @param {string} timeframe - 'daily', 'hourly', or '5min'
   * @param {number} limit - Number of historical records (default 30 days)
   */
  async getCryptoHistory(pair, timeframe = 'daily', limit = 30) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/crypto/${timeframe}/history?pair=${encodeURIComponent(pair)}&limit=${limit}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching crypto history:', error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * Get historical data for a specific stock
   * @param {string} symbol - Stock symbol (e.g., 'AAPL')
   * @param {string} timeframe - 'daily', 'hourly', or '5min'
   * @param {number} limit - Number of historical records (default 30 days)
   */
  async getStockHistory(symbol, timeframe = 'daily', limit = 30) {
    try {
      const endpoint = timeframe === 'daily'
        ? 'stocks'
        : timeframe === 'hourly'
        ? 'stocks/hourly'
        : 'stocks/5min';

      const response = await fetch(`${API_BASE_URL}/api/${endpoint}/history?symbol=${encodeURIComponent(symbol)}&limit=${limit}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching stock history:', error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * Get scheduler status and execution logs (admin only)
   */
  async getSchedulerStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/scheduler-status`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching scheduler status:', error);
      return { success: false, schedulers: [], recent_executions: [], error: error.message };
    }
  }

  /**
   * Manually trigger a scheduler (admin only)
   * @param {string} schedulerName - Name of the scheduler to trigger
   */
  async triggerScheduler(schedulerName) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/trigger-scheduler`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ scheduler_name: schedulerName }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error triggering scheduler:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get weekly stock analysis data
   * @param {object} filters - Filters like sector, volatility_category, etc.
   * @param {number} limit - Number of records
   */
  async getWeeklyStocks(filters = {}, limit = 100) {
    try {
      const params = new URLSearchParams({ limit, ...filters });
      const response = await fetch(`${API_BASE_URL}/api/analysis/stocks/weekly?${params}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching weekly stocks:', error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * Get weekly crypto analysis data
   * @param {object} filters - Filters like category, volatility_category, etc.
   * @param {number} limit - Number of records
   */
  async getWeeklyCryptos(filters = {}, limit = 100) {
    try {
      const params = new URLSearchParams({ limit, ...filters });
      const response = await fetch(`${API_BASE_URL}/api/analysis/cryptos/weekly?${params}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching weekly cryptos:', error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * Get active trading list (top picks for day trading)
   */
  async getActiveTradingList() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analysis/active-list`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching active trading list:', error);
      return { success: false, data: [], error: error.message };
    }
  }

  /**
   * NLP Search - Natural language query for stocks/cryptos
   * @param {string} query - Natural language query (e.g., "high volatility tech stocks")
   * @param {string} assetType - 'stocks', 'cryptos', or 'all'
   */
  async nlpSearch(query, assetType = 'all') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analysis/nlp-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, asset_type: assetType }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error in NLP search:', error);
      return { success: false, results: [], error: error.message };
    }
  }
}

export default new ApiService();
