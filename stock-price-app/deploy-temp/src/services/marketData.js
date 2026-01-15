// Market Data Service
// Fetches real-time crypto and stock data from Trading API (BigQuery backend)

// Use environment variable if available, fallback to defaults
const BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-252370699783.us-central1.run.app'
);
const API_BASE_URL = `${BASE_URL}/api`;

class MarketDataService {
  /**
   * Fetch crypto OHLC data with different timeframes
   * @param {string} symbol - Trading pair (e.g., 'BTCUSD')
   * @param {string} timeframe - 'daily', 'hourly', or '5min'
   * @param {number} limit - Number of candles to fetch
   * @returns {Promise<Array>} Array of OHLC data with indicators
   */
  async getCryptoData(symbol, timeframe = 'hourly', limit = 100) {
    try {
      // Map timeframe to correct endpoint
      let endpoint;
      if (timeframe === 'daily') {
        endpoint = 'crypto/daily/history';
      } else if (timeframe === 'hourly' || timeframe === '15min') {
        endpoint = 'crypto/15min/history'; // Use 15min for hourly requests
      } else {
        endpoint = 'crypto/5min/history';
      }

      const params = new URLSearchParams({
        pair: symbol,  // API expects 'pair' parameter
        limit: limit
      });

      const response = await fetch(`${API_BASE_URL}/${endpoint}?${params}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      console.log(`✓ Crypto ${timeframe} response:`, {
        success: data.success,
        count: data.count,
        dataLength: data.data?.length,
        endpoint
      });

      // Transform data to chart format
      const transformed = this.transformToChartData(data.data || []);
      console.log(`✓ Transformed ${transformed.length} crypto ${timeframe} candles for ${symbol}`);
      return transformed;
    } catch (error) {
      console.error(`Error fetching ${timeframe} crypto data:`, error);
      return [];
    }
  }

  /**
   * Fetch stock OHLC data
   * @param {string} symbol - Stock symbol (e.g., 'AAPL')
   * @param {string} timeframe - 'daily', 'hourly', or '5min'
   * @param {number} limit - Number of candles to fetch
   * @returns {Promise<Array>} Array of OHLC data with indicators
   */
  async getStockData(symbol, timeframe = 'hourly', limit = 100) {
    try {
      // Map timeframe to correct endpoint
      let endpoint;
      if (timeframe === 'daily') {
        endpoint = 'stocks/history';
      } else if (timeframe === 'hourly' || timeframe === '15min') {
        endpoint = 'stocks/15min/history'; // Use 15min for hourly requests
      } else {
        endpoint = 'stocks/5min/history';
      }

      const params = new URLSearchParams({
        symbol: symbol,
        limit: limit
      });

      const response = await fetch(`${API_BASE_URL}/${endpoint}?${params}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      console.log(`✓ Stock ${timeframe} response:`, {
        success: data.success,
        count: data.count,
        dataLength: data.data?.length,
        endpoint
      });

      // Transform data to chart format
      const transformed = this.transformToChartData(data.data || []);
      console.log(`✓ Transformed ${transformed.length} stock ${timeframe} candles for ${symbol}`);
      return transformed;
    } catch (error) {
      console.error(`Error fetching ${timeframe} stock data:`, error);
      return [];
    }
  }

  /**
   * Fetch market summary (top gainers, losers, volume)
   * @param {string} marketType - 'crypto' or 'stock'
   * @returns {Promise<Object>} Market summary statistics
   */
  async getMarketSummary(marketType = 'crypto') {
    try {
      const response = await fetch(`${API_BASE_URL}/summary/${marketType}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // API returns {success: true, summary: {...}}, extract the summary object
      return data.summary || {
        top_gainers: [],
        top_losers: [],
        highest_volume: [],
        total_pairs: 0
      };
    } catch (error) {
      console.error(`Error fetching ${marketType} summary:`, error);
      return {
        top_gainers: [],
        top_losers: [],
        highest_volume: [],
        total_pairs: 0
      };
    }
  }

  /**
   * Get latest price for a symbol
   * @param {string} symbol - Trading symbol
   * @param {string} marketType - 'crypto' or 'stock'
   * @returns {Promise<Object>} Latest price data
   */
  async getLatestPrice(symbol, marketType = 'crypto') {
    try {
      const data = await (marketType === 'crypto' ?
        this.getCryptoData(symbol, 'hourly', 1) :
        this.getStockData(symbol, 'hourly', 1)
      );

      return data[0] || null;
    } catch (error) {
      console.error(`Error fetching latest price for ${symbol}:`, error);
      return null;
    }
  }

  /**
   * Transform BigQuery data to chart-compatible format
   * @param {Array} data - Raw data from BigQuery
   * @returns {Array} Transformed data for charts
   */
  transformToChartData(data) {
    if (!Array.isArray(data)) return [];

    const transformed = data.map((candle, index) => {
      // Use timestamp field if available (already in Unix seconds), otherwise parse datetime
      const time = candle.timestamp || this.parseTimestamp(candle.datetime);

      // Log first few candles for debugging
      if (index < 3) {
        console.log(`Candle ${index}:`, {
          datetime: candle.datetime,
          timestamp: candle.timestamp,
          parsedTime: time,
          close: candle.close
        });
      }

      return {
        time,
        open: parseFloat(candle.open || 0),
        high: parseFloat(candle.high || 0),
        low: parseFloat(candle.low || 0),
        close: parseFloat(candle.close || 0),
        volume: parseFloat(candle.volume || 0),
      // Technical indicators - use null for missing data
      rsi: candle.rsi != null ? parseFloat(candle.rsi) : null,
      macd: candle.macd != null ? parseFloat(candle.macd) : null,
      macd_signal: candle.macd_signal != null ? parseFloat(candle.macd_signal) : null,
      macd_histogram: candle.macd_histogram != null ? parseFloat(candle.macd_histogram) : null,
      sma_20: candle.sma_20 != null ? parseFloat(candle.sma_20) : null,
      sma_50: candle.sma_50 != null ? parseFloat(candle.sma_50) : null,
      sma_200: candle.sma_200 != null ? parseFloat(candle.sma_200) : null,
      ema_12: candle.ema_12 != null ? parseFloat(candle.ema_12) : null,
      ema_26: candle.ema_26 != null ? parseFloat(candle.ema_26) : null,
      ema_50: candle.ema_50 != null ? parseFloat(candle.ema_50) : null,
      // Support both old (bb_*) and new (bollinger_*) field names for v2 tables
      bb_upper: candle.bollinger_upper != null ? parseFloat(candle.bollinger_upper) : (candle.bb_upper != null ? parseFloat(candle.bb_upper) : null),
      bb_middle: candle.bollinger_middle != null ? parseFloat(candle.bollinger_middle) : (candle.bb_middle != null ? parseFloat(candle.bb_middle) : null),
      bb_lower: candle.bollinger_lower != null ? parseFloat(candle.bollinger_lower) : (candle.bb_lower != null ? parseFloat(candle.bb_lower) : null),
      atr: candle.atr != null ? parseFloat(candle.atr) : null,
      adx: candle.adx != null ? parseFloat(candle.adx) : null,
      obv: candle.obv != null ? parseFloat(candle.obv) : null,
      stoch_k: candle.stoch_k != null ? parseFloat(candle.stoch_k) : null,
      stoch_d: candle.stoch_d != null ? parseFloat(candle.stoch_d) : null,
      cci: candle.cci != null ? parseFloat(candle.cci) : null,
      williams_r: candle.williams_r != null ? parseFloat(candle.williams_r) : null,
      roc: candle.roc != null ? parseFloat(candle.roc) : 0, // Keep 0 for ROC as it's used in table
      // Fibonacci levels
      fib_0: candle.fib_0 != null ? parseFloat(candle.fib_0) : null,
      fib_236: candle.fib_236 != null ? parseFloat(candle.fib_236) : null,
      fib_382: candle.fib_382 != null ? parseFloat(candle.fib_382) : null,
      fib_500: candle.fib_500 != null ? parseFloat(candle.fib_500) : null,
      fib_618: candle.fib_618 != null ? parseFloat(candle.fib_618) : null,
      fib_786: candle.fib_786 != null ? parseFloat(candle.fib_786) : null,
      fib_100: candle.fib_100 != null ? parseFloat(candle.fib_100) : null,
      // Elliott Wave
      wave_position: candle.wave_position != null ? parseFloat(candle.wave_position) : null,
      wave_1_high: candle.wave_1_high != null ? parseFloat(candle.wave_1_high) : null,
      wave_2_low: candle.wave_2_low != null ? parseFloat(candle.wave_2_low) : null,
      wave_3_high: candle.wave_3_high != null ? parseFloat(candle.wave_3_high) : null,
      wave_4_low: candle.wave_4_low != null ? parseFloat(candle.wave_4_low) : null,
      wave_5_high: candle.wave_5_high != null ? parseFloat(candle.wave_5_high) : null,
      trend_direction: candle.trend_direction != null ? parseFloat(candle.trend_direction) : null,
      elliott_wave_degree: candle.elliott_wave_degree || null,
      // Metadata
      symbol: candle.pair || candle.symbol || '',
      pair: candle.pair || candle.symbol || ''
      };
    });

    const sorted = transformed.sort((a, b) => a.time - b.time); // Ensure chronological order

    // Remove duplicate timestamps (keep the last occurrence)
    const deduplicated = [];
    const seen = new Set();
    for (let i = sorted.length - 1; i >= 0; i--) {
      const candle = sorted[i];
      if (!seen.has(candle.time)) {
        seen.add(candle.time);
        deduplicated.unshift(candle); // Add to beginning to maintain order
      } else {
        console.warn(`Removing duplicate timestamp: ${candle.time} (${new Date(candle.time * 1000).toISOString()})`);
      }
    }

    console.log(`Transformed data: ${sorted.length} candles → ${deduplicated.length} after dedup, time range: ${deduplicated[0]?.time} to ${deduplicated[deduplicated.length-1]?.time}`);
    return deduplicated;
  }

  /**
   * Parse various timestamp formats to Unix timestamp
   * @param {string|number} timestamp - Timestamp in various formats
   * @returns {number} Unix timestamp in seconds
   */
  parseTimestamp(timestamp) {
    if (!timestamp) return 0;

    // If already a number, return it
    if (typeof timestamp === 'number') {
      // If it's in milliseconds, convert to seconds
      return timestamp > 10000000000 ? Math.floor(timestamp / 1000) : timestamp;
    }

    // Parse ISO string or other date formats
    const date = new Date(timestamp);
    return Math.floor(date.getTime() / 1000);
  }

  /**
   * Get all available trading pairs (legacy method using summary)
   * @param {string} marketType - 'crypto' or 'stock'
   * @returns {Promise<Array>} List of trading pairs
   */
  async getAllPairs(marketType = 'crypto') {
    try {
      const summary = await this.getMarketSummary(marketType);

      // Extract unique pairs from top gainers/losers
      const pairs = new Set();

      if (summary.top_gainers) {
        summary.top_gainers.forEach(item => pairs.add(item.pair || item.symbol));
      }
      if (summary.top_losers) {
        summary.top_losers.forEach(item => pairs.add(item.pair || item.symbol));
      }
      if (summary.highest_volume) {
        summary.highest_volume.forEach(item => pairs.add(item.pair || item.symbol));
      }

      return Array.from(pairs).sort();
    } catch (error) {
      console.error('Error fetching pairs:', error);
      return [];
    }
  }

  /**
   * Get ALL crypto pairs from the database with latest data
   * @returns {Promise<Array>} List of all crypto pairs with price data
   */
  async getAllCryptoPairs() {
    try {
      const response = await fetch(`${API_BASE_URL}/crypto/pairs`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        console.log(`✓ Fetched ${data.count} crypto pairs from database`);
        return data.data || [];
      }
      return [];
    } catch (error) {
      console.error('Error fetching all crypto pairs:', error);
      return [];
    }
  }

  /**
   * Get ALL stock symbols from the database with latest data
   * @returns {Promise<Array>} List of all stock symbols with price data
   */
  async getAllStockSymbols() {
    try {
      const response = await fetch(`${API_BASE_URL}/stocks/symbols`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        console.log(`✓ Fetched ${data.count} stock symbols from database`);
        return data.data || [];
      }
      return [];
    } catch (error) {
      console.error('Error fetching all stock symbols:', error);
      return [];
    }
  }

  /**
   * Generic method to fetch data for any asset type
   * @param {string} symbol - Asset symbol
   * @param {string} assetType - 'forex', 'etfs', 'indices', 'commodities', 'interest_rates'
   * @param {string} timeframe - 'daily', 'hourly', '5min'
   * @param {number} limit - Number of candles
   * @returns {Promise<Array>} Array of OHLC data
   */
  async getAssetData(symbol, assetType, timeframe = 'daily', limit = 100) {
    try {
      // Map asset types to API endpoints
      const endpointMap = {
        'forex': 'forex',
        'etfs': 'etfs',
        'indices': 'indices',
        'commodities': 'commodities',
        'interest_rates': 'interest-rates'
      };

      const baseEndpoint = endpointMap[assetType] || assetType;

      // Build endpoint based on timeframe
      let endpoint;
      if (timeframe === 'daily') {
        endpoint = `${baseEndpoint}/history`;
      } else if (timeframe === 'hourly') {
        endpoint = `${baseEndpoint}/hourly/history`;
      } else {
        endpoint = `${baseEndpoint}/5min/history`;
      }

      const params = new URLSearchParams({
        symbol: symbol,
        limit: limit
      });

      const response = await fetch(`${API_BASE_URL}/${endpoint}?${params}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      console.log(`✓ ${assetType} ${timeframe} response:`, {
        success: data.success,
        count: data.count,
        dataLength: data.data?.length,
        endpoint
      });

      // Transform data to chart format
      const transformed = this.transformToChartData(data.data || []);
      console.log(`✓ Transformed ${transformed.length} ${assetType} ${timeframe} candles for ${symbol}`);
      return transformed;
    } catch (error) {
      console.error(`Error fetching ${timeframe} ${assetType} data:`, error);
      return [];
    }
  }

  /**
   * Fetch Forex data
   */
  async getForexData(symbol, timeframe = 'daily', limit = 100) {
    return this.getAssetData(symbol, 'forex', timeframe, limit);
  }

  /**
   * Fetch ETF data
   */
  async getETFData(symbol, timeframe = 'daily', limit = 100) {
    return this.getAssetData(symbol, 'etfs', timeframe, limit);
  }

  /**
   * Fetch Index data
   */
  async getIndexData(symbol, timeframe = 'daily', limit = 100) {
    return this.getAssetData(symbol, 'indices', timeframe, limit);
  }

  /**
   * Fetch Commodities data
   */
  async getCommoditiesData(symbol, timeframe = 'daily', limit = 100) {
    return this.getAssetData(symbol, 'commodities', timeframe, limit);
  }

  /**
   * Fetch Interest Rates data
   */
  async getInterestRatesData(symbol, timeframe = 'daily', limit = 100) {
    return this.getAssetData(symbol, 'interest_rates', timeframe, limit);
  }

  /**
   * Universal method to get data for any asset type
   * @param {string} symbol - Asset symbol
   * @param {string} assetType - Asset type
   * @param {string} timeframe - Timeframe
   * @param {number} limit - Limit
   */
  async getData(symbol, assetType, timeframe = 'daily', limit = 100) {
    switch (assetType) {
      case 'crypto':
        return this.getCryptoData(symbol, timeframe, limit);
      case 'stocks':
        return this.getStockData(symbol, timeframe, limit);
      case 'forex':
        return this.getForexData(symbol, timeframe, limit);
      case 'etfs':
        return this.getETFData(symbol, timeframe, limit);
      case 'indices':
        return this.getIndexData(symbol, timeframe, limit);
      case 'commodities':
        return this.getCommoditiesData(symbol, timeframe, limit);
      case 'interest_rates':
        return this.getInterestRatesData(symbol, timeframe, limit);
      default:
        console.warn(`Unknown asset type: ${assetType}, falling back to stocks`);
        return this.getStockData(symbol, timeframe, limit);
    }
  }

  /**
   * Search for symbols/pairs
   * @param {string} query - Search query
   * @param {string} marketType - 'crypto' or 'stock'
   * @returns {Promise<Array>} Matching symbols
   */
  async searchSymbols(query, marketType = 'crypto') {
    const allPairs = await this.getAllPairs(marketType);
    const lowerQuery = query.toLowerCase();

    return allPairs.filter(pair =>
      pair.toLowerCase().includes(lowerQuery)
    );
  }
}

// Export singleton instance
const marketDataService = new MarketDataService();
export default marketDataService;
