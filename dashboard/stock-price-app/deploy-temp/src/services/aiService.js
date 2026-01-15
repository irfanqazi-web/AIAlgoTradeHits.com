/**
 * AI Trading Intelligence Service
 * Communicates with AI Cloud Function for predictions, patterns, and signals
 */

const AI_FUNCTION_URL = import.meta.env.VITE_AI_FUNCTION_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-1075463475276.us-central1.run.app'
);

class AIService {
  /**
   * Convert symbol format from BTCUSD to BTC/USD for API compatibility
   * @param {string} symbol - Input symbol (e.g., 'BTCUSD')
   * @returns {string} Formatted symbol (e.g., 'BTC/USD')
   */
  formatSymbol(symbol) {
    // If already has a slash, return as is
    if (symbol.includes('/')) return symbol;

    // Common crypto pairs - convert BTCUSD to BTC/USD
    const cryptoPatterns = [
      { pattern: /^(BTC|ETH|XRP|SOL|DOGE|ADA|DOT|LINK|AVAX|MATIC|UNI|ATOM|LTC|BCH|XLM|TRX|NEAR|APT|FIL|ICP|ARB|OP|MKR|AAVE|CRV|SNX|COMP|YFI|SUSHI|1INCH)(USD|USDT|USDC|EUR|GBP)$/i, base: 1, quote: 2 }
    ];

    for (const { pattern, base, quote } of cryptoPatterns) {
      const match = symbol.match(pattern);
      if (match) {
        return `${match[base].toUpperCase()}/${match[quote].toUpperCase()}`;
      }
    }

    // For stocks, return as is
    return symbol;
  }

  /**
   * Get AI price predictions for a trading pair
   * @param {string} pair - Trading pair (e.g., 'BTCUSD')
   * @param {string} timeframe - Timeframe ('daily', 'hourly', '5min')
   * @param {string} aiProvider - AI provider ('claude', 'vertex', 'both')
   * @returns {Promise<Object>} Prediction results
   */
  async getPricePrediction(pair, timeframe = 'daily', aiProvider = 'both') {
    try {
      const formattedPair = this.formatSymbol(pair);
      const url = `${AI_FUNCTION_URL}?pair=${encodeURIComponent(formattedPair)}&timeframe=${timeframe}&type=prediction&ai_provider=${aiProvider}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`AI API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: this.normalizePrediction(data)
      };
    } catch (error) {
      console.error('Price prediction error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get AI pattern recognition analysis
   * @param {string} symbol - Trading symbol (stock or crypto)
   * @param {string} timeframe - Timeframe
   * @param {string} aiProvider - AI provider
   * @returns {Promise<Object>} Pattern analysis results
   */
  async getPatternAnalysis(symbol, timeframe = 'daily', aiProvider = 'both') {
    try {
      // First fetch historical price data for the symbol
      const assetType = symbol.includes('/') || symbol.match(/^(BTC|ETH|XRP|SOL|DOGE)/i) ? 'crypto' : 'stocks';
      const historyUrl = `${AI_FUNCTION_URL}/api/twelvedata/${assetType}/${timeframe}/history?symbol=${encodeURIComponent(symbol)}&limit=100`;

      const historyResponse = await fetch(historyUrl);
      const historyData = await historyResponse.json();

      if (!historyData.success || !historyData.data || historyData.data.length === 0) {
        throw new Error(`No price data available for ${symbol}`);
      }

      // Convert price data to the format expected by pattern recognition API
      const priceData = historyData.data.map(d => ({
        datetime: d.datetime,
        open: parseFloat(d.open),
        high: parseFloat(d.high),
        low: parseFloat(d.low),
        close: parseFloat(d.close),
        volume: parseInt(d.volume) || 0
      }));

      // Now call pattern recognition with the price data
      const response = await fetch(`${AI_FUNCTION_URL}/api/ai/pattern-recognition`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol,
          price_data: priceData,
          timeframe: timeframe,
          ai_provider: aiProvider
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `AI API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: this.normalizePatterns(data)
      };
    } catch (error) {
      console.error('Pattern analysis error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get AI trading signals
   * @param {string} pair - Trading pair
   * @param {string} timeframe - Timeframe
   * @param {string} aiProvider - AI provider
   * @returns {Promise<Object>} Trading signal results
   */
  async getTradingSignals(pair, timeframe = 'daily', aiProvider = 'both') {
    try {
      const formattedPair = this.formatSymbol(pair);
      const url = `${AI_FUNCTION_URL}?pair=${encodeURIComponent(formattedPair)}&timeframe=${timeframe}&type=signal&ai_provider=${aiProvider}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`AI API error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: this.normalizeSignals(data)
      };
    } catch (error) {
      console.error('Trading signals error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get comprehensive AI analysis (predictions + patterns + signals)
   * @param {string} pair - Trading pair
   * @param {string} timeframe - Timeframe
   * @returns {Promise<Object>} Complete AI analysis
   */
  async getComprehensiveAnalysis(pair, timeframe = 'daily') {
    try {
      const [predictions, patterns, signals] = await Promise.all([
        this.getPricePrediction(pair, timeframe, 'both'),
        this.getPatternAnalysis(pair, timeframe, 'both'),
        this.getTradingSignals(pair, timeframe, 'both')
      ]);

      return {
        success: true,
        data: {
          pair,
          timeframe,
          timestamp: new Date().toISOString(),
          predictions: predictions.success ? predictions.data : null,
          patterns: patterns.success ? patterns.data : null,
          signals: signals.success ? signals.data : null
        }
      };
    } catch (error) {
      console.error('Comprehensive analysis error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Normalize prediction data from different AI providers
   */
  normalizePrediction(data) {
    const normalized = {
      pair: data.pair,
      currentPrice: data.current_price,
      timestamp: data.timestamp,
      predictions: {}
    };

    // Process Claude analysis
    if (data.claude_analysis && !data.claude_analysis.error) {
      normalized.predictions.claude = {
        prediction_1h: data.claude_analysis.prediction_1h,
        prediction_24h: data.claude_analysis.prediction_24h,
        prediction_7d: data.claude_analysis.prediction_7d,
        confidence: data.claude_analysis.confidence,
        trend: data.claude_analysis.trend,
        keyFactors: data.claude_analysis.key_factors || [],
        riskLevel: data.claude_analysis.risk_level,
        recommendation: data.claude_analysis.recommendation
      };
    }

    // Process Vertex AI analysis
    if (data.vertex_analysis && !data.vertex_analysis.error) {
      normalized.predictions.vertex = data.vertex_analysis;
    }

    // Process consensus
    if (data.consensus) {
      normalized.consensus = data.consensus;
    }

    return normalized;
  }

  /**
   * Normalize pattern data from different AI providers
   */
  normalizePatterns(data) {
    const normalized = {
      pair: data.pair,
      currentPrice: data.current_price,
      timestamp: data.timestamp,
      patterns: {}
    };

    // Process Claude analysis
    if (data.claude_analysis && !data.claude_analysis.error) {
      normalized.patterns.claude = {
        detected: data.claude_analysis.patterns_detected || [],
        supportLevels: data.claude_analysis.support_levels || [],
        resistanceLevels: data.claude_analysis.resistance_levels || [],
        reliability: data.claude_analysis.pattern_reliability,
        breakoutProbability: data.claude_analysis.breakout_probability,
        recommendedAction: data.claude_analysis.recommended_action
      };
    }

    // Process Vertex AI analysis
    if (data.vertex_analysis && !data.vertex_analysis.error) {
      normalized.patterns.vertex = data.vertex_analysis;
    }

    return normalized;
  }

  /**
   * Normalize signal data from different AI providers
   */
  normalizeSignals(data) {
    const normalized = {
      pair: data.pair,
      currentPrice: data.current_price,
      timestamp: data.timestamp,
      signals: {}
    };

    // Process Claude analysis
    if (data.claude_analysis && !data.claude_analysis.error) {
      normalized.signals.claude = {
        signal: data.claude_analysis.signal,
        entryPrice: data.claude_analysis.entry_price,
        targetPrices: data.claude_analysis.target_prices || [],
        stopLoss: data.claude_analysis.stop_loss,
        riskRewardRatio: data.claude_analysis.risk_reward_ratio,
        timeframe: data.claude_analysis.timeframe,
        reasoning: data.claude_analysis.reasoning
      };
    }

    // Process Vertex AI analysis
    if (data.vertex_analysis && !data.vertex_analysis.error) {
      normalized.signals.vertex = data.vertex_analysis;
    }

    // Process consensus
    if (data.consensus) {
      normalized.consensus = data.consensus;
    }

    return normalized;
  }

  /**
   * Get signal strength indicator
   * @param {string} signal - Signal type (strong_buy, buy, hold, sell, strong_sell)
   * @returns {Object} Color and strength info
   */
  getSignalStrength(signal) {
    const signalMap = {
      'strong_buy': { strength: 100, color: '#10b981', label: 'Strong Buy', emoji: '🚀' },
      'buy': { strength: 75, color: '#22c55e', label: 'Buy', emoji: '📈' },
      'hold': { strength: 50, color: '#f59e0b', label: 'Hold', emoji: '⏸️' },
      'sell': { strength: 25, color: '#ef4444', label: 'Sell', emoji: '📉' },
      'strong_sell': { strength: 0, color: '#dc2626', label: 'Strong Sell', emoji: '⚠️' }
    };

    return signalMap[signal] || signalMap['hold'];
  }

  /**
   * Get trend indicator
   * @param {string} trend - Trend type (bullish, bearish, neutral)
   * @returns {Object} Color and trend info
   */
  getTrendIndicator(trend) {
    const trendMap = {
      'bullish': { color: '#10b981', label: 'Bullish', emoji: '🐂', direction: '↗️' },
      'bearish': { color: '#ef4444', label: 'Bearish', emoji: '🐻', direction: '↘️' },
      'neutral': { color: '#f59e0b', label: 'Neutral', emoji: '➡️', direction: '→' }
    };

    return trendMap[trend] || trendMap['neutral'];
  }
}

export default new AIService();
