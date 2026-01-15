"""
Generate Comprehensive Trading Table Documentation for Gemini 2.5 Learning
Creates detailed documentation of all BigQuery tables with trading terminology explanations
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime
import json

# Initialize BigQuery client
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
client = bigquery.Client(project=PROJECT_ID)

# Trading terminology explanations for each field type
FIELD_DESCRIPTIONS = {
    # Identification Fields
    'symbol': {
        'description': 'Unique ticker symbol identifying the trading asset',
        'trading_meaning': 'The standardized code used to identify a security on exchanges (e.g., AAPL for Apple, BTCUSD for Bitcoin)',
        'data_type': 'STRING',
        'example': 'AAPL, TSLA, BTCUSD, EUR/USD'
    },
    'name': {
        'description': 'Full name of the trading asset or company',
        'trading_meaning': 'Human-readable name of the asset for display purposes',
        'data_type': 'STRING',
        'example': 'Apple Inc., Bitcoin, Euro/US Dollar'
    },
    'asset_type': {
        'description': 'Classification of the asset type',
        'trading_meaning': 'Categorizes assets into: stocks, crypto, forex, etfs, indices, commodities, bonds',
        'data_type': 'STRING',
        'example': 'Common Stock, Digital Currency, Currency Pair'
    },
    'exchange': {
        'description': 'Stock exchange or trading venue where the asset is listed',
        'trading_meaning': 'Indicates market hours, liquidity, and regulatory jurisdiction',
        'data_type': 'STRING',
        'example': 'NASDAQ, NYSE, Binance, FOREX'
    },
    'country': {
        'description': 'Country where the asset is domiciled or primarily traded',
        'trading_meaning': 'Important for tax implications, currency exposure, and geopolitical risk assessment',
        'data_type': 'STRING',
        'example': 'United States, United Kingdom, Global'
    },
    'sector': {
        'description': 'Economic sector classification of the asset',
        'trading_meaning': 'Used for sector rotation strategies and portfolio diversification. Common sectors: Technology, Healthcare, Energy, Financial Services',
        'data_type': 'STRING',
        'example': 'Technology, Healthcare, Energy, Consumer Cyclical'
    },
    'industry': {
        'description': 'Specific industry within a sector',
        'trading_meaning': 'More granular classification for industry-specific analysis and peer comparison',
        'data_type': 'STRING',
        'example': 'Software - Infrastructure, Biotechnology, Oil & Gas'
    },
    'currency': {
        'description': 'Currency in which the asset is priced',
        'trading_meaning': 'Determines currency exposure and conversion requirements for international traders',
        'data_type': 'STRING',
        'example': 'USD, EUR, GBP, JPY'
    },

    # OHLCV Data (Core Price Data)
    'open': {
        'description': 'Opening price at the start of the trading period',
        'trading_meaning': 'First traded price of the period. Gap analysis uses open vs previous close. Opening range breakout strategies use this level.',
        'data_type': 'FLOAT',
        'trading_signals': 'Gap up (open > prev_close) = bullish; Gap down (open < prev_close) = bearish',
        'example': '150.25'
    },
    'high': {
        'description': 'Highest price reached during the trading period',
        'trading_meaning': 'Intraday resistance level. Upper shadow in candlestick patterns. Used in calculating ATR, Stochastic, and range analysis.',
        'data_type': 'FLOAT',
        'trading_signals': 'Rejection from highs = selling pressure; Breaking previous highs = bullish momentum',
        'example': '155.75'
    },
    'low': {
        'description': 'Lowest price reached during the trading period',
        'trading_meaning': 'Intraday support level. Lower shadow in candlestick patterns. Used in calculating ATR, Stochastic, and range analysis.',
        'data_type': 'FLOAT',
        'trading_signals': 'Bounce from lows = buying pressure; Breaking previous lows = bearish momentum',
        'example': '148.50'
    },
    'close': {
        'description': 'Closing/last traded price of the period',
        'trading_meaning': 'Most important price for technical analysis. Most indicators use close price. Settlement price for many derivatives.',
        'data_type': 'FLOAT',
        'trading_signals': 'Close near high = bullish; Close near low = bearish; Close near open = indecision (doji)',
        'example': '153.20'
    },
    'previous_close': {
        'description': 'Closing price from the previous trading period',
        'trading_meaning': 'Reference point for calculating daily change and identifying gaps. Used for after-hours movement analysis.',
        'data_type': 'FLOAT',
        'example': '151.00'
    },
    'volume': {
        'description': 'Number of shares/units traded during the period',
        'trading_meaning': 'Measures market participation and conviction. High volume confirms price moves; Low volume suggests weak moves.',
        'data_type': 'FLOAT',
        'trading_signals': 'Volume spike + price up = strong buying; Volume spike + price down = strong selling; Low volume move = likely reversal',
        'example': '75000000'
    },
    'average_volume': {
        'description': 'Average trading volume over a lookback period (typically 10-30 days)',
        'trading_meaning': 'Baseline for volume comparison. Current volume / average volume = relative volume ratio.',
        'data_type': 'FLOAT',
        'trading_signals': 'Volume > 2x average = significant activity; Volume < 0.5x average = low interest',
        'example': '50000000'
    },

    # Price Change Metrics
    'change': {
        'description': 'Absolute price change from previous close (close - previous_close)',
        'trading_meaning': 'Dollar/unit change in price. Important for position sizing and P&L calculations.',
        'data_type': 'FLOAT',
        'example': '2.20'
    },
    'percent_change': {
        'description': 'Percentage price change from previous close ((close - previous_close) / previous_close * 100)',
        'trading_meaning': 'Normalized change for comparing assets of different prices. Basis for screening gainers/losers.',
        'data_type': 'FLOAT',
        'trading_signals': '> 5% daily move = significant; > 10% = major move; > 20% = extreme volatility',
        'example': '1.46'
    },
    'hi_lo': {
        'description': 'Daily trading range (high - low)',
        'trading_meaning': 'Measures intraday volatility. Wide range = volatile trading; Narrow range = consolidation.',
        'data_type': 'FLOAT',
        'example': '7.25'
    },
    'pct_hi_lo': {
        'description': 'Daily range as percentage of price ((high - low) / low * 100)',
        'trading_meaning': 'Normalized volatility measure for comparing assets. Useful for day trading stock selection.',
        'data_type': 'FLOAT',
        'example': '4.88'
    },

    # 52-Week Metrics
    'week_52_high': {
        'description': 'Highest price in the last 52 weeks (1 year)',
        'trading_meaning': 'Major resistance level. Breaking 52-week high = strong bullish signal. Used for breakout strategies.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price near 52w high = potential breakout or resistance; Breaking 52w high on volume = very bullish',
        'example': '180.00'
    },
    'week_52_low': {
        'description': 'Lowest price in the last 52 weeks (1 year)',
        'trading_meaning': 'Major support level. Breaking 52-week low = strong bearish signal. Value investors look for bounces here.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price near 52w low = potential value or falling knife; Bounce from 52w low on volume = potentially bullish',
        'example': '120.00'
    },

    # Momentum Indicators
    'rsi': {
        'description': 'Relative Strength Index (14-period default)',
        'trading_meaning': 'Oscillator measuring speed and magnitude of price changes. Range 0-100. Most popular momentum indicator.',
        'data_type': 'FLOAT',
        'trading_signals': 'RSI < 30 = oversold (buy signal); RSI > 70 = overbought (sell signal); Divergence with price = reversal signal',
        'formula': 'RSI = 100 - (100 / (1 + RS)) where RS = avg gain / avg loss over 14 periods',
        'example': '45.5'
    },
    'stoch_k': {
        'description': 'Stochastic %K (Fast Stochastic)',
        'trading_meaning': 'Shows where close is relative to high-low range. Range 0-100. More sensitive than %D.',
        'data_type': 'FLOAT',
        'trading_signals': '%K crossing above %D = bullish; %K crossing below %D = bearish',
        'formula': '%K = ((Close - Lowest Low) / (Highest High - Lowest Low)) * 100',
        'example': '55.2'
    },
    'stoch_d': {
        'description': 'Stochastic %D (Slow Stochastic)',
        'trading_meaning': '3-period SMA of %K. Smoother signal line. Used for crossover signals.',
        'data_type': 'FLOAT',
        'trading_signals': '%K < 20 and crossing above %D = buy; %K > 80 and crossing below %D = sell',
        'example': '52.8'
    },
    'momentum': {
        'description': 'Price momentum (close - close[n periods ago])',
        'trading_meaning': 'Raw momentum calculation showing acceleration/deceleration of price.',
        'data_type': 'FLOAT',
        'trading_signals': 'Positive momentum = upward acceleration; Negative momentum = downward acceleration',
        'example': '5.50'
    },
    'roc': {
        'description': 'Rate of Change ((close - close[n]) / close[n] * 100)',
        'trading_meaning': 'Percentage-based momentum. Shows speed of price change. Used for momentum ranking.',
        'data_type': 'FLOAT',
        'trading_signals': 'ROC > 0 = bullish momentum; ROC < 0 = bearish momentum; Extreme values = potential reversal',
        'example': '3.75'
    },
    'williams_r': {
        'description': "Williams %R (Williams Percent Range)",
        'trading_meaning': 'Momentum indicator similar to Stochastic but inverted. Range -100 to 0.',
        'data_type': 'FLOAT',
        'trading_signals': '%R > -20 = overbought; %R < -80 = oversold',
        'formula': '%R = ((Highest High - Close) / (Highest High - Lowest Low)) * -100',
        'example': '-35.5'
    },

    # Moving Averages (Trend Indicators)
    'sma_20': {
        'description': '20-period Simple Moving Average',
        'trading_meaning': 'Short-term trend indicator. Used for short-term trading and Bollinger Bands middle line.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price > SMA20 = short-term uptrend; Price < SMA20 = short-term downtrend; SMA20 slope indicates trend strength',
        'example': '152.50'
    },
    'sma_50': {
        'description': '50-period Simple Moving Average',
        'trading_meaning': 'Medium-term trend indicator. Key level for swing traders. Often acts as dynamic support/resistance.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price crossing SMA50 = trend change; SMA50 > SMA200 = bullish market; Golden/Death cross reference',
        'example': '148.00'
    },
    'sma_200': {
        'description': '200-period Simple Moving Average',
        'trading_meaning': 'Long-term trend indicator. Institutional reference. Defines bull/bear market boundary.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price > SMA200 = bull market; Price < SMA200 = bear market; SMA50 crossing SMA200 = major signal',
        'example': '140.00'
    },
    'ema_12': {
        'description': '12-period Exponential Moving Average',
        'trading_meaning': 'Fast EMA for MACD calculation. More weight on recent prices than SMA.',
        'data_type': 'FLOAT',
        'trading_signals': 'EMA12 > EMA26 = bullish MACD; EMA12 < EMA26 = bearish MACD',
        'example': '153.00'
    },
    'ema_26': {
        'description': '26-period Exponential Moving Average',
        'trading_meaning': 'Slow EMA for MACD calculation. Signal line base.',
        'data_type': 'FLOAT',
        'trading_signals': 'Crossover with EMA12 generates MACD signals',
        'example': '151.50'
    },
    'ema_50': {
        'description': '50-period Exponential Moving Average',
        'trading_meaning': 'Medium-term EMA. Alternative to SMA50 with more responsiveness to recent price.',
        'data_type': 'FLOAT',
        'example': '149.00'
    },

    # MACD (Moving Average Convergence Divergence)
    'macd': {
        'description': 'MACD Line (EMA12 - EMA26)',
        'trading_meaning': 'Trend-following momentum indicator. Shows relationship between two EMAs.',
        'data_type': 'FLOAT',
        'trading_signals': 'MACD > 0 = bullish; MACD < 0 = bearish; Crossing signal line = trade signal',
        'formula': 'MACD = EMA(12) - EMA(26)',
        'example': '1.50'
    },
    'macd_signal': {
        'description': 'MACD Signal Line (9-period EMA of MACD)',
        'trading_meaning': 'Trigger line for MACD crossover signals.',
        'data_type': 'FLOAT',
        'trading_signals': 'MACD crossing above signal = buy; MACD crossing below signal = sell',
        'example': '1.20'
    },
    'macd_histogram': {
        'description': 'MACD Histogram (MACD - Signal)',
        'trading_meaning': 'Visual representation of MACD/Signal difference. Shows momentum acceleration.',
        'data_type': 'FLOAT',
        'trading_signals': 'Histogram increasing = momentum building; Histogram decreasing = momentum fading; Histogram crossing zero = trend change',
        'example': '0.30'
    },

    # Bollinger Bands (Volatility)
    'bollinger_upper': {
        'description': 'Upper Bollinger Band (SMA20 + 2*StdDev)',
        'trading_meaning': 'Dynamic resistance level based on volatility. Price touching = potentially overbought.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price at upper band = overbought/breakout; Walking the band = strong trend',
        'example': '158.00'
    },
    'bollinger_middle': {
        'description': 'Middle Bollinger Band (SMA20)',
        'trading_meaning': 'Center line and dynamic support/resistance. Same as SMA20.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price crossing middle = trend change; Price bouncing off = support/resistance',
        'example': '152.50'
    },
    'bollinger_lower': {
        'description': 'Lower Bollinger Band (SMA20 - 2*StdDev)',
        'trading_meaning': 'Dynamic support level based on volatility. Price touching = potentially oversold.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price at lower band = oversold/breakdown; Band squeeze = low volatility, breakout coming',
        'example': '147.00'
    },

    # Volatility Indicators
    'atr': {
        'description': 'Average True Range (14-period)',
        'trading_meaning': 'Volatility indicator showing average price range. Used for stop-loss placement and position sizing.',
        'data_type': 'FLOAT',
        'trading_signals': 'High ATR = high volatility, use wider stops; Low ATR = low volatility, potential breakout setup',
        'formula': 'ATR = EMA of TR; TR = max(high-low, |high-prev_close|, |low-prev_close|)',
        'example': '3.50'
    },

    # Trend Strength Indicators
    'adx': {
        'description': 'Average Directional Index (14-period)',
        'trading_meaning': 'Measures trend strength (not direction). Range 0-100. Core trend strength indicator.',
        'data_type': 'FLOAT',
        'trading_signals': 'ADX > 25 = strong trend; ADX < 20 = weak/no trend; ADX rising = trend strengthening',
        'example': '28.5'
    },
    'plus_di': {
        'description': 'Positive Directional Indicator (+DI)',
        'trading_meaning': 'Measures bullish trend strength. Part of ADX system.',
        'data_type': 'FLOAT',
        'trading_signals': '+DI > -DI = uptrend; +DI crossing above -DI = bullish signal',
        'example': '22.0'
    },
    'minus_di': {
        'description': 'Negative Directional Indicator (-DI)',
        'trading_meaning': 'Measures bearish trend strength. Part of ADX system.',
        'data_type': 'FLOAT',
        'trading_signals': '-DI > +DI = downtrend; -DI crossing above +DI = bearish signal',
        'example': '18.0'
    },

    # Oscillators
    'cci': {
        'description': 'Commodity Channel Index (20-period)',
        'trading_meaning': 'Oscillator measuring price relative to average. Range typically -300 to +300.',
        'data_type': 'FLOAT',
        'trading_signals': 'CCI > 100 = overbought; CCI < -100 = oversold; CCI crossing 0 = trend change',
        'formula': 'CCI = (Typical Price - SMA) / (0.015 * Mean Deviation)',
        'example': '75.5'
    },
    'ultimate_osc': {
        'description': 'Ultimate Oscillator',
        'trading_meaning': 'Combines short, medium, and long-term momentum. Range 0-100.',
        'data_type': 'FLOAT',
        'trading_signals': 'UO > 70 = overbought; UO < 30 = oversold; Divergence = reversal signal',
        'example': '55.0'
    },
    'awesome_osc': {
        'description': 'Awesome Oscillator (AO)',
        'trading_meaning': 'Momentum indicator comparing recent momentum to larger momentum. Histogram format.',
        'data_type': 'FLOAT',
        'trading_signals': 'AO > 0 = bullish momentum; AO < 0 = bearish momentum; Twin peaks = reversal signal',
        'formula': 'AO = SMA(5, Median Price) - SMA(34, Median Price)',
        'example': '2.50'
    },

    # Volume Indicators
    'obv': {
        'description': 'On-Balance Volume',
        'trading_meaning': 'Cumulative volume indicator. Shows if volume is flowing into or out of the asset.',
        'data_type': 'FLOAT',
        'trading_signals': 'OBV rising with price = confirmed uptrend; OBV falling with price rising = potential reversal',
        'formula': 'OBV adds volume on up days, subtracts on down days',
        'example': '150000000'
    },
    'pvo': {
        'description': 'Percentage Volume Oscillator',
        'trading_meaning': 'Shows relationship between two volume EMAs. Similar to MACD for volume.',
        'data_type': 'FLOAT',
        'trading_signals': 'PVO > 0 = above average volume activity; PVO crossing signal line = volume momentum change',
        'example': '5.5'
    },

    # Other Indicators
    'ppo': {
        'description': 'Percentage Price Oscillator',
        'trading_meaning': 'MACD expressed as percentage. Useful for comparing different priced assets.',
        'data_type': 'FLOAT',
        'trading_signals': 'Similar to MACD but normalized; PPO > 0 = bullish; PPO < 0 = bearish',
        'example': '1.2'
    },
    'kama': {
        'description': "Kaufman's Adaptive Moving Average",
        'trading_meaning': 'Adaptive moving average that adjusts to market volatility. Less whipsaws than traditional MAs.',
        'data_type': 'FLOAT',
        'trading_signals': 'Price > KAMA = uptrend; Price < KAMA = downtrend; KAMA slope shows trend direction',
        'example': '151.75'
    },
    'trix': {
        'description': 'Triple Exponential Average (TRIX)',
        'trading_meaning': 'Triple smoothed exponential moving average. Filters out market noise.',
        'data_type': 'FLOAT',
        'trading_signals': 'TRIX > 0 = bullish; TRIX < 0 = bearish; TRIX crossing zero = potential trend change',
        'example': '0.15'
    },

    # Timestamp Fields
    'datetime': {
        'description': 'Timestamp of the data point',
        'trading_meaning': 'When the candle/bar closed. Essential for time-series analysis and backtesting.',
        'data_type': 'TIMESTAMP',
        'example': '2024-12-07 16:00:00 UTC'
    },
    'timestamp': {
        'description': 'Unix timestamp (seconds since epoch)',
        'trading_meaning': 'Machine-readable time format. Useful for calculations and sorting.',
        'data_type': 'INTEGER',
        'example': '1733594400'
    },
    'created_at': {
        'description': 'When the record was inserted into the database',
        'trading_meaning': 'Data freshness indicator. Useful for debugging and audit trails.',
        'data_type': 'TIMESTAMP',
        'example': '2024-12-07 16:05:00 UTC'
    },
    'data_source': {
        'description': 'Origin of the data',
        'trading_meaning': 'Identifies API source (TwelveData, Kraken, etc.). Important for data quality assessment.',
        'data_type': 'STRING',
        'example': 'twelvedata, kraken, coinmarketcap'
    }
}

# Table type descriptions
TABLE_TYPES = {
    '5min': {
        'timeframe': '5-minute intervals',
        'use_case': 'Intraday scalping and day trading',
        'typical_lookback': 'Last 1-5 trading days',
        'strategies': 'Scalping, momentum plays, opening range breakouts'
    },
    'hourly': {
        'timeframe': 'Hourly intervals',
        'use_case': 'Day trading and short-term swing trading',
        'typical_lookback': 'Last 1-4 weeks',
        'strategies': 'Intraday trends, session trading, short swings'
    },
    'daily': {
        'timeframe': 'Daily intervals (end of day)',
        'use_case': 'Swing trading and position trading',
        'typical_lookback': '3-12 months',
        'strategies': 'Trend following, breakouts, mean reversion'
    },
    'weekly_summary': {
        'timeframe': 'Weekly aggregate data',
        'use_case': 'Position trading and long-term analysis',
        'typical_lookback': '1-5 years',
        'strategies': 'Long-term trends, sector rotation, value investing'
    },
    'historical_daily': {
        'timeframe': 'Daily data with extended history',
        'use_case': 'Backtesting and long-term analysis',
        'typical_lookback': '5-20+ years',
        'strategies': 'Strategy backtesting, statistical analysis, machine learning training'
    }
}

# Asset type descriptions
ASSET_TYPES = {
    'stocks': {
        'description': 'Equities - ownership shares in public companies',
        'typical_count': '15,000+ US stocks from TwelveData',
        'trading_hours': 'US markets: 9:30 AM - 4:00 PM ET (pre/post market available)',
        'key_metrics': ['sector', 'industry', 'market_cap', 'pe_ratio', 'dividend_yield']
    },
    'crypto': {
        'description': 'Cryptocurrencies - digital assets on blockchain',
        'typical_count': '200+ major cryptocurrencies',
        'trading_hours': '24/7/365',
        'key_metrics': ['market_cap', 'circulating_supply', 'total_supply', 'dominance']
    },
    'forex': {
        'description': 'Foreign Exchange - currency pairs',
        'typical_count': '50+ major and minor pairs',
        'trading_hours': '24/5 (Sunday 5 PM - Friday 5 PM ET)',
        'key_metrics': ['pip_value', 'spread', 'interest_rate_differential']
    },
    'etfs': {
        'description': 'Exchange-Traded Funds - baskets of securities',
        'typical_count': '3,000+ ETFs',
        'trading_hours': 'Same as underlying market',
        'key_metrics': ['expense_ratio', 'aum', 'holdings', 'tracking_error']
    },
    'indices': {
        'description': 'Market Indices - benchmarks representing market segments',
        'typical_count': '50+ major indices',
        'trading_hours': 'Varies by index',
        'key_metrics': ['composition', 'weighting_method', 'rebalancing_frequency']
    },
    'commodities': {
        'description': 'Raw materials and natural resources',
        'typical_count': '30+ major commodities',
        'trading_hours': 'Varies by commodity and exchange',
        'key_metrics': ['futures_curve', 'seasonality', 'inventory_levels']
    }
}

def get_all_tables():
    """Get all v2 tables from BigQuery"""
    tables = list(client.list_tables(f'{PROJECT_ID}.{DATASET_ID}'))
    return [t for t in tables if t.table_id.startswith('v2_')]

def get_table_schema(table_id):
    """Get schema for a specific table"""
    full_table_id = f'{PROJECT_ID}.{DATASET_ID}.{table_id}'
    table = client.get_table(full_table_id)
    return table.schema, table.num_rows, table.num_bytes

def generate_documentation():
    """Generate comprehensive documentation"""
    doc = []

    # Header
    doc.append("=" * 100)
    doc.append("AIALGOTRADEHITS TRADING DATA WAREHOUSE")
    doc.append("Comprehensive Table Documentation for AI/ML and Text-to-SQL")
    doc.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.append("=" * 100)
    doc.append("")

    # Executive Summary
    doc.append("## EXECUTIVE SUMMARY")
    doc.append("-" * 50)
    doc.append("""
This document provides complete documentation of the AIAlgoTradeHits trading data warehouse
stored in Google BigQuery. It is designed to be consumed by AI systems (particularly Gemini 2.5)
to enable accurate Text-to-SQL query generation for financial analysis.

PROJECT: aialgotradehits
DATASET: crypto_trading_data
DATA SOURCES: TwelveData API, Kraken Pro API, CoinMarketCap API

ASSET COVERAGE:
- Stocks: 15,000+ US equities with 18+ fundamental fields
- Crypto: 200+ cryptocurrencies with real-time pricing
- Forex: 50+ currency pairs
- ETFs: 3,000+ exchange-traded funds
- Indices: 50+ market indices
- Commodities: 30+ raw materials

TIMEFRAMES:
- 5-minute: Intraday scalping data
- Hourly: Day trading data
- Daily: Swing trading data
- Weekly Summary: Position trading data
- Historical: Backtesting data (10+ years)
""")
    doc.append("")

    # Asset Type Descriptions
    doc.append("## ASSET TYPES")
    doc.append("-" * 50)
    for asset_type, info in ASSET_TYPES.items():
        doc.append(f"\n### {asset_type.upper()}")
        doc.append(f"Description: {info['description']}")
        doc.append(f"Typical Count: {info['typical_count']}")
        doc.append(f"Trading Hours: {info['trading_hours']}")
        doc.append(f"Key Metrics: {', '.join(info['key_metrics'])}")
    doc.append("")

    # Table Timeframe Descriptions
    doc.append("## TABLE TIMEFRAMES")
    doc.append("-" * 50)
    for tf, info in TABLE_TYPES.items():
        doc.append(f"\n### {tf.upper()}")
        doc.append(f"Timeframe: {info['timeframe']}")
        doc.append(f"Use Case: {info['use_case']}")
        doc.append(f"Typical Lookback: {info['typical_lookback']}")
        doc.append(f"Trading Strategies: {info['strategies']}")
    doc.append("")

    # Field Reference
    doc.append("## FIELD REFERENCE DICTIONARY")
    doc.append("-" * 50)
    doc.append("""
This section provides detailed explanations of all fields found in the trading tables.
Each field includes its data type, trading meaning, and signal interpretations.
""")

    for field_name, field_info in FIELD_DESCRIPTIONS.items():
        doc.append(f"\n### {field_name.upper()}")
        doc.append(f"Data Type: {field_info.get('data_type', 'FLOAT')}")
        doc.append(f"Description: {field_info.get('description', '')}")
        doc.append(f"Trading Meaning: {field_info.get('trading_meaning', '')}")
        if 'trading_signals' in field_info:
            doc.append(f"Trading Signals: {field_info['trading_signals']}")
        if 'formula' in field_info:
            doc.append(f"Formula: {field_info['formula']}")
        if 'example' in field_info:
            doc.append(f"Example Value: {field_info['example']}")
    doc.append("")

    # Individual Table Documentation
    doc.append("## TABLE CATALOG")
    doc.append("-" * 50)

    tables = get_all_tables()
    for table in tables:
        try:
            schema, num_rows, num_bytes = get_table_schema(table.table_id)

            doc.append(f"\n### {table.table_id}")
            doc.append(f"Full Path: `{PROJECT_ID}.{DATASET_ID}.{table.table_id}`")
            doc.append(f"Row Count: {num_rows:,}")
            doc.append(f"Size: {num_bytes / (1024*1024):.2f} MB")

            # Determine table type and asset type
            parts = table.table_id.replace('v2_', '').split('_')
            asset_type = parts[0] if parts else 'unknown'
            table_type = '_'.join(parts[1:]) if len(parts) > 1 else 'unknown'

            if asset_type in ASSET_TYPES:
                doc.append(f"Asset Type: {asset_type} - {ASSET_TYPES[asset_type]['description']}")
            if table_type in TABLE_TYPES:
                doc.append(f"Timeframe: {TABLE_TYPES[table_type]['timeframe']}")
                doc.append(f"Use Case: {TABLE_TYPES[table_type]['use_case']}")

            doc.append("\nColumns:")
            doc.append("-" * 40)
            for field in schema:
                field_desc = FIELD_DESCRIPTIONS.get(field.name, {})
                trading_meaning = field_desc.get('trading_meaning', 'Standard field')
                doc.append(f"  - {field.name} ({field.field_type}): {trading_meaning[:100]}...")

        except Exception as e:
            doc.append(f"Error processing {table.table_id}: {str(e)}")

    # SQL Query Examples
    doc.append("\n## SQL QUERY EXAMPLES FOR TEXT-TO-SQL")
    doc.append("-" * 50)
    doc.append("""
### Finding Oversold Stocks (RSI < 30)
```sql
SELECT symbol, name, close, rsi, percent_change
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
WHERE rsi < 30 AND rsi IS NOT NULL
ORDER BY rsi ASC
LIMIT 20;
```

### Top Gainers Today
```sql
SELECT symbol, name, close, percent_change, volume
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
WHERE percent_change > 0
ORDER BY percent_change DESC
LIMIT 20;
```

### Stocks Breaking 52-Week High
```sql
SELECT symbol, name, close, week_52_high,
       (close / week_52_high * 100) as pct_of_high
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
WHERE close >= week_52_high * 0.98
ORDER BY close / week_52_high DESC
LIMIT 20;
```

### High Volume Cryptos with Bullish MACD
```sql
SELECT symbol, name, close, volume, macd, macd_signal
FROM `aialgotradehits.crypto_trading_data.v2_crypto_daily`
WHERE macd > macd_signal AND macd > 0
  AND volume > average_volume
ORDER BY volume DESC
LIMIT 20;
```

### Strong Trend Assets (ADX > 25)
```sql
SELECT symbol, name, close, adx, plus_di, minus_di,
       CASE WHEN plus_di > minus_di THEN 'Bullish' ELSE 'Bearish' END as trend_direction
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
WHERE adx > 25
ORDER BY adx DESC
LIMIT 30;
```

### Bollinger Band Squeeze (Low Volatility, Pending Breakout)
```sql
SELECT symbol, name, close,
       bollinger_upper - bollinger_lower as band_width,
       atr
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
WHERE (bollinger_upper - bollinger_lower) / bollinger_middle < 0.04
ORDER BY (bollinger_upper - bollinger_lower) / bollinger_middle ASC
LIMIT 20;
```

### Weekly Performance Analysis
```sql
SELECT symbol, name,
       close as current_price,
       percent_change as weekly_change,
       week_52_high, week_52_low,
       (close - week_52_low) / (week_52_high - week_52_low) * 100 as position_in_range
FROM `aialgotradehits.crypto_trading_data.v2_stocks_weekly_summary`
ORDER BY percent_change DESC
LIMIT 50;
```
""")

    # Join the document
    return "\n".join(doc)

def main():
    print("Generating comprehensive trading table documentation...")
    documentation = generate_documentation()

    # Save as text file
    output_file = 'TRADING_TABLE_DOCUMENTATION.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(documentation)

    print(f"Documentation saved to: {output_file}")
    print(f"Total length: {len(documentation):,} characters")

    # Also create a summary JSON for programmatic access
    tables = get_all_tables()
    summary = {
        'generated': datetime.now().isoformat(),
        'project': PROJECT_ID,
        'dataset': DATASET_ID,
        'field_descriptions': FIELD_DESCRIPTIONS,
        'asset_types': ASSET_TYPES,
        'table_types': TABLE_TYPES,
        'tables': {}
    }

    for table in tables:
        try:
            schema, num_rows, num_bytes = get_table_schema(table.table_id)
            summary['tables'][table.table_id] = {
                'full_path': f'{PROJECT_ID}.{DATASET_ID}.{table.table_id}',
                'num_rows': num_rows,
                'num_bytes': num_bytes,
                'columns': [{'name': f.name, 'type': f.field_type} for f in schema]
            }
        except Exception as e:
            summary['tables'][table.table_id] = {'error': str(e)}

    json_file = 'TRADING_TABLE_SCHEMA.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"Schema JSON saved to: {json_file}")

if __name__ == "__main__":
    main()
