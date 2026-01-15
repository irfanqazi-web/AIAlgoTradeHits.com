"""
Historical Data Backfill Script with Comprehensive Technical Indicators
Builds a data warehouse with 6 months to 10 years of historical daily OHLC data
for all 6 asset types: ETFs, Forex, Indices, Commodities, Stocks, Cryptos

Features:
- 50+ Technical indicators for AI/ML feature engineering
- Target variables for supervised learning
- Designed for Vertex AI and Gemini 3 model development

Strategy:
- Phase 1: Build 6-month history (~180 days)
- Phase 2: Extend to 1 year (~365 days)
- Phase 3: Gradual 10-year build (monthly backfill)

API Considerations:
- Twelve Data free tier: 800 API calls/day
- Rate limit: 8 calls/minute
- This script is designed to run daily and gradually build history
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import requests
import time
from datetime import datetime, timedelta, timezone
import json
import os
import math
import numpy as np

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
API_CALLS_PER_MINUTE = 8
API_CALLS_PER_DAY = 800

# Asset configurations with expanded symbols
ASSET_CONFIGS = {
    'etfs': {
        'table': 'etfs_historical_daily',
        'symbols': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'GLD', 'SLV', 'USO', 'TLT',
                   'XLF', 'XLK', 'XLE', 'XLV', 'ARKK', 'VWO', 'EFA', 'HYG', 'LQD', 'SCHD'],
        'type': 'ETF'
    },
    'forex': {
        'table': 'forex_historical_daily',
        'symbols': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD',
                   'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY'],
        'type': 'Forex'
    },
    'indices': {
        'table': 'indices_historical_daily',
        'symbols': ['SPX', 'NDX', 'DJI', 'RUT', 'VIX', 'FTSE', 'DAX', 'N225', 'HSI', 'NIFTY'],
        'type': 'Index'
    },
    'commodities': {
        'table': 'commodities_historical_daily',
        'symbols': ['XAU/USD', 'XAG/USD', 'CL', 'NG', 'ZC', 'ZW', 'KC', 'SB', 'CT'],
        'type': 'Commodity'
    },
    'stocks': {
        'table': 'stocks_historical_daily',
        'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B',
                   'UNH', 'JNJ', 'V', 'XOM', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
                   'PFE', 'KO', 'PEP', 'COST', 'TMO', 'WMT', 'CSCO'],
        'type': 'Stock'
    },
    'cryptos': {
        'table': 'cryptos_historical_daily',
        'symbols': ['BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'ADA/USD', 'SOL/USD',
                   'DOGE/USD', 'DOT/USD', 'MATIC/USD', 'LTC/USD'],
        'type': 'Crypto'
    }
}


def get_comprehensive_schema():
    """Get BigQuery schema with all 50+ technical indicators"""
    return [
        # Core OHLCV fields
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("open", "FLOAT64"),
        bigquery.SchemaField("high", "FLOAT64"),
        bigquery.SchemaField("low", "FLOAT64"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "FLOAT64"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP"),

        # Simple Moving Averages
        bigquery.SchemaField("sma_5", "FLOAT64"),
        bigquery.SchemaField("sma_10", "FLOAT64"),
        bigquery.SchemaField("sma_20", "FLOAT64"),
        bigquery.SchemaField("sma_50", "FLOAT64"),
        bigquery.SchemaField("sma_100", "FLOAT64"),
        bigquery.SchemaField("sma_200", "FLOAT64"),

        # Exponential Moving Averages
        bigquery.SchemaField("ema_5", "FLOAT64"),
        bigquery.SchemaField("ema_10", "FLOAT64"),
        bigquery.SchemaField("ema_12", "FLOAT64"),
        bigquery.SchemaField("ema_20", "FLOAT64"),
        bigquery.SchemaField("ema_26", "FLOAT64"),
        bigquery.SchemaField("ema_50", "FLOAT64"),

        # MACD Family
        bigquery.SchemaField("macd", "FLOAT64"),
        bigquery.SchemaField("macd_signal", "FLOAT64"),
        bigquery.SchemaField("macd_hist", "FLOAT64"),

        # RSI Family
        bigquery.SchemaField("rsi_7", "FLOAT64"),
        bigquery.SchemaField("rsi_14", "FLOAT64"),
        bigquery.SchemaField("rsi_21", "FLOAT64"),

        # Stochastic Oscillator
        bigquery.SchemaField("stoch_k", "FLOAT64"),
        bigquery.SchemaField("stoch_d", "FLOAT64"),
        bigquery.SchemaField("stoch_rsi", "FLOAT64"),

        # Bollinger Bands
        bigquery.SchemaField("bb_upper", "FLOAT64"),
        bigquery.SchemaField("bb_middle", "FLOAT64"),
        bigquery.SchemaField("bb_lower", "FLOAT64"),
        bigquery.SchemaField("bb_width", "FLOAT64"),
        bigquery.SchemaField("bb_percent", "FLOAT64"),

        # Volatility Indicators
        bigquery.SchemaField("atr_7", "FLOAT64"),
        bigquery.SchemaField("atr_14", "FLOAT64"),
        bigquery.SchemaField("atr_percent", "FLOAT64"),
        bigquery.SchemaField("volatility_10", "FLOAT64"),
        bigquery.SchemaField("volatility_20", "FLOAT64"),

        # Momentum Indicators
        bigquery.SchemaField("roc_5", "FLOAT64"),
        bigquery.SchemaField("roc_10", "FLOAT64"),
        bigquery.SchemaField("roc_20", "FLOAT64"),
        bigquery.SchemaField("momentum_10", "FLOAT64"),
        bigquery.SchemaField("williams_r", "FLOAT64"),

        # Volume Indicators
        bigquery.SchemaField("obv", "FLOAT64"),
        bigquery.SchemaField("volume_sma_20", "FLOAT64"),
        bigquery.SchemaField("volume_ratio", "FLOAT64"),

        # Oscillators
        bigquery.SchemaField("cci", "FLOAT64"),
        bigquery.SchemaField("ppo", "FLOAT64"),
        bigquery.SchemaField("ultimate_osc", "FLOAT64"),
        bigquery.SchemaField("awesome_osc", "FLOAT64"),
        bigquery.SchemaField("adx", "FLOAT64"),
        bigquery.SchemaField("di_plus", "FLOAT64"),
        bigquery.SchemaField("di_minus", "FLOAT64"),

        # Price Action Features
        bigquery.SchemaField("daily_return_pct", "FLOAT64"),
        bigquery.SchemaField("log_return", "FLOAT64"),
        bigquery.SchemaField("high_low_pct", "FLOAT64"),
        bigquery.SchemaField("body_size", "FLOAT64"),
        bigquery.SchemaField("upper_shadow", "FLOAT64"),
        bigquery.SchemaField("lower_shadow", "FLOAT64"),

        # Lagged Features
        bigquery.SchemaField("close_lag_1", "FLOAT64"),
        bigquery.SchemaField("close_lag_2", "FLOAT64"),
        bigquery.SchemaField("close_lag_3", "FLOAT64"),
        bigquery.SchemaField("close_lag_5", "FLOAT64"),
        bigquery.SchemaField("close_lag_10", "FLOAT64"),
        bigquery.SchemaField("return_lag_1", "FLOAT64"),
        bigquery.SchemaField("return_lag_2", "FLOAT64"),
        bigquery.SchemaField("return_lag_3", "FLOAT64"),

        # Target Variables (for ML)
        bigquery.SchemaField("target_return_1d", "FLOAT64"),
        bigquery.SchemaField("target_return_5d", "FLOAT64"),
        bigquery.SchemaField("target_return_10d", "FLOAT64"),
        bigquery.SchemaField("target_direction_1d", "INT64"),
        bigquery.SchemaField("target_direction_5d", "INT64"),

        # Signal Categories
        bigquery.SchemaField("trend_signal", "STRING"),
        bigquery.SchemaField("momentum_signal", "STRING"),
        bigquery.SchemaField("volatility_signal", "STRING"),
        bigquery.SchemaField("volume_signal", "STRING"),

        # Time Features
        bigquery.SchemaField("day_of_week", "INT64"),
        bigquery.SchemaField("month", "INT64"),
        bigquery.SchemaField("quarter", "INT64"),
        bigquery.SchemaField("is_month_start", "BOOLEAN"),
        bigquery.SchemaField("is_month_end", "BOOLEAN"),

        # Cumulative metrics
        bigquery.SchemaField("cumulative_return", "FLOAT64"),
    ]


def create_historical_table(client, table_name):
    """Create historical data table if it doesn't exist with comprehensive schema"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    try:
        client.get_table(table_id)
        print(f"Table {table_name} already exists")
    except:
        table = bigquery.Table(table_id, schema=get_comprehensive_schema())
        table = client.create_table(table)
        print(f"Created table {table_name} with 80+ fields")


def get_existing_dates(client, table_name, symbol):
    """Get dates that already have data for this symbol"""
    query = f"""
    SELECT DISTINCT date
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    WHERE symbol = '{symbol}'
    ORDER BY date
    """
    try:
        results = client.query(query).result()
        return set(row.date for row in results)
    except:
        return set()


def fetch_historical_data(symbol, output_size=5000):
    """Fetch maximum historical daily data from Twelve Data API"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': output_size,
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        data = response.json()

        if 'values' in data:
            return data['values']
        elif 'code' in data:
            print(f"  API Error for {symbol}: {data.get('message', 'Unknown error')}")
            return None
        else:
            print(f"  Unexpected response for {symbol}")
            return None
    except Exception as e:
        print(f"  Request error for {symbol}: {e}")
        return None


def calculate_sma(prices, period):
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return [None] * len(prices)

    result = [None] * (period - 1)
    for i in range(period - 1, len(prices)):
        result.append(sum(prices[i - period + 1:i + 1]) / period)
    return result


def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return [None] * len(prices)

    multiplier = 2 / (period + 1)
    ema = [None] * (period - 1)
    ema.append(sum(prices[:period]) / period)

    for i in range(period, len(prices)):
        ema.append((prices[i] - ema[-1]) * multiplier + ema[-1])
    return ema


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return [None] * len(prices)

    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    result = [None] * period
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(deltas)):
        if avg_loss == 0:
            result.append(100)
        else:
            rs = avg_gain / avg_loss
            result.append(100 - (100 / (1 + rs)))

        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    return [None] + result


def calculate_atr(highs, lows, closes, period=14):
    """Calculate Average True Range"""
    if len(closes) < period + 1:
        return [None] * len(closes)

    true_ranges = [highs[0] - lows[0]]
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        true_ranges.append(tr)

    result = [None] * (period - 1)
    result.append(sum(true_ranges[:period]) / period)

    for i in range(period, len(true_ranges)):
        result.append((result[-1] * (period - 1) + true_ranges[i]) / period)

    return result


def calculate_all_indicators(values):
    """Calculate all 50+ technical indicators"""
    if not values or len(values) < 50:
        return values

    # Reverse to chronological order
    values = list(reversed(values))
    n = len(values)

    # Extract OHLCV arrays
    opens = [float(v.get('open', 0)) for v in values]
    highs = [float(v.get('high', 0)) for v in values]
    lows = [float(v.get('low', 0)) for v in values]
    closes = [float(v.get('close', 0)) for v in values]
    volumes = [float(v.get('volume', 0)) if v.get('volume') else 0 for v in values]

    # Calculate SMAs
    sma_5 = calculate_sma(closes, 5)
    sma_10 = calculate_sma(closes, 10)
    sma_20 = calculate_sma(closes, 20)
    sma_50 = calculate_sma(closes, 50)
    sma_100 = calculate_sma(closes, 100)
    sma_200 = calculate_sma(closes, 200)

    # Calculate EMAs
    ema_5 = calculate_ema(closes, 5)
    ema_10 = calculate_ema(closes, 10)
    ema_12 = calculate_ema(closes, 12)
    ema_20 = calculate_ema(closes, 20)
    ema_26 = calculate_ema(closes, 26)
    ema_50 = calculate_ema(closes, 50)

    # MACD
    macd = [e12 - e26 if e12 and e26 else None for e12, e26 in zip(ema_12, ema_26)]
    macd_valid = [m for m in macd if m is not None]
    macd_signal_raw = calculate_ema(macd_valid, 9) if len(macd_valid) >= 9 else [None] * len(macd_valid)

    # Pad macd_signal to match length
    macd_signal = [None] * (n - len(macd_signal_raw)) + macd_signal_raw
    macd_hist = [m - s if m and s else None for m, s in zip(macd, macd_signal)]

    # RSI
    rsi_7 = calculate_rsi(closes, 7)
    rsi_14 = calculate_rsi(closes, 14)
    rsi_21 = calculate_rsi(closes, 21)

    # ATR
    atr_7 = calculate_atr(highs, lows, closes, 7)
    atr_14 = calculate_atr(highs, lows, closes, 14)

    # Bollinger Bands
    bb_middle = sma_20
    bb_upper = []
    bb_lower = []
    bb_width = []
    bb_percent = []

    for i in range(n):
        if i >= 19 and bb_middle[i]:
            std = (sum((closes[j] - bb_middle[i])**2 for j in range(i-19, i+1)) / 20) ** 0.5
            bb_upper.append(bb_middle[i] + 2 * std)
            bb_lower.append(bb_middle[i] - 2 * std)
            bb_width.append((bb_upper[-1] - bb_lower[-1]) / bb_middle[i] * 100 if bb_middle[i] else None)
            bb_percent.append((closes[i] - bb_lower[-1]) / (bb_upper[-1] - bb_lower[-1]) * 100 if bb_upper[-1] != bb_lower[-1] else 50)
        else:
            bb_upper.append(None)
            bb_lower.append(None)
            bb_width.append(None)
            bb_percent.append(None)

    # Stochastic
    stoch_k = []
    stoch_d = []
    for i in range(n):
        if i >= 13:
            h14 = max(highs[i-13:i+1])
            l14 = min(lows[i-13:i+1])
            if h14 != l14:
                k = (closes[i] - l14) / (h14 - l14) * 100
            else:
                k = 50
            stoch_k.append(k)
        else:
            stoch_k.append(None)

    # Stochastic %D
    for i in range(n):
        if i >= 15 and stoch_k[i] and stoch_k[i-1] and stoch_k[i-2]:
            stoch_d.append((stoch_k[i] + stoch_k[i-1] + stoch_k[i-2]) / 3)
        else:
            stoch_d.append(None)

    # Stochastic RSI
    stoch_rsi = []
    for i in range(n):
        if rsi_14[i] and i >= 27:
            rsi_window = [r for r in rsi_14[i-13:i+1] if r is not None]
            if len(rsi_window) >= 14:
                rsi_max = max(rsi_window)
                rsi_min = min(rsi_window)
                if rsi_max != rsi_min:
                    stoch_rsi.append((rsi_14[i] - rsi_min) / (rsi_max - rsi_min) * 100)
                else:
                    stoch_rsi.append(50)
            else:
                stoch_rsi.append(None)
        else:
            stoch_rsi.append(None)

    # Williams %R
    williams_r = []
    for i in range(n):
        if i >= 13:
            h14 = max(highs[i-13:i+1])
            l14 = min(lows[i-13:i+1])
            if h14 != l14:
                williams_r.append((h14 - closes[i]) / (h14 - l14) * -100)
            else:
                williams_r.append(-50)
        else:
            williams_r.append(None)

    # ROC and Momentum
    roc_5 = [None] * 5 + [(closes[i] - closes[i-5]) / closes[i-5] * 100 if closes[i-5] else None for i in range(5, n)]
    roc_10 = [None] * 10 + [(closes[i] - closes[i-10]) / closes[i-10] * 100 if closes[i-10] else None for i in range(10, n)]
    roc_20 = [None] * 20 + [(closes[i] - closes[i-20]) / closes[i-20] * 100 if closes[i-20] else None for i in range(20, n)]
    momentum_10 = [None] * 10 + [closes[i] - closes[i-10] for i in range(10, n)]

    # Volatility
    volatility_10 = []
    volatility_20 = []
    for i in range(n):
        if i >= 9:
            returns = [(closes[j] - closes[j-1]) / closes[j-1] for j in range(i-8, i+1) if closes[j-1]]
            if returns:
                vol = (sum(r**2 for r in returns) / len(returns)) ** 0.5 * (252 ** 0.5) * 100
                volatility_10.append(vol)
            else:
                volatility_10.append(None)
        else:
            volatility_10.append(None)

        if i >= 19:
            returns = [(closes[j] - closes[j-1]) / closes[j-1] for j in range(i-18, i+1) if closes[j-1]]
            if returns:
                vol = (sum(r**2 for r in returns) / len(returns)) ** 0.5 * (252 ** 0.5) * 100
                volatility_20.append(vol)
            else:
                volatility_20.append(None)
        else:
            volatility_20.append(None)

    # OBV
    obv = [0]
    for i in range(1, n):
        if closes[i] > closes[i-1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i-1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])

    # Volume SMA and Ratio
    volume_sma_20 = calculate_sma(volumes, 20)
    volume_ratio = [v / vsma if vsma and vsma > 0 else None for v, vsma in zip(volumes, volume_sma_20)]

    # CCI
    cci = []
    for i in range(n):
        if i >= 19:
            tp_values = [(highs[j] + lows[j] + closes[j]) / 3 for j in range(i-19, i+1)]
            tp_mean = sum(tp_values) / 20
            mad = sum(abs(tp - tp_mean) for tp in tp_values) / 20
            tp_current = (highs[i] + lows[i] + closes[i]) / 3
            if mad != 0:
                cci.append((tp_current - tp_mean) / (0.015 * mad))
            else:
                cci.append(0)
        else:
            cci.append(None)

    # PPO
    ppo = [(e12 - e26) / e26 * 100 if e12 and e26 and e26 != 0 else None for e12, e26 in zip(ema_12, ema_26)]

    # Awesome Oscillator
    sma_5_hl = calculate_sma([(h + l) / 2 for h, l in zip(highs, lows)], 5)
    sma_34_hl = calculate_sma([(h + l) / 2 for h, l in zip(highs, lows)], 34)
    awesome_osc = [s5 - s34 if s5 and s34 else None for s5, s34 in zip(sma_5_hl, sma_34_hl)]

    # Daily returns and log returns
    daily_returns = [None] + [(closes[i] - closes[i-1]) / closes[i-1] * 100 if closes[i-1] else None for i in range(1, n)]
    log_returns = [None] + [math.log(closes[i] / closes[i-1]) if closes[i-1] and closes[i] > 0 else None for i in range(1, n)]

    # Price action features
    high_low_pct = [(h - l) / c * 100 if c else None for h, l, c in zip(highs, lows, closes)]
    body_size = [abs(c - o) / c * 100 if c else None for o, c in zip(opens, closes)]
    upper_shadow = [(h - max(o, c)) / c * 100 if c else None for o, h, l, c in zip(opens, highs, lows, closes)]
    lower_shadow = [(min(o, c) - l) / c * 100 if c else None for o, h, l, c in zip(opens, highs, lows, closes)]

    # Lagged features
    close_lag_1 = [None] + closes[:-1]
    close_lag_2 = [None, None] + closes[:-2]
    close_lag_3 = [None, None, None] + closes[:-3]
    close_lag_5 = [None] * 5 + closes[:-5]
    close_lag_10 = [None] * 10 + closes[:-10]
    return_lag_1 = [None] + daily_returns[:-1]
    return_lag_2 = [None, None] + daily_returns[:-2]
    return_lag_3 = [None, None, None] + daily_returns[:-3]

    # Target variables (shift future values back)
    target_return_1d = daily_returns[1:] + [None]
    target_return_5d = [None] * n
    target_return_10d = [None] * n
    for i in range(n - 5):
        target_return_5d[i] = (closes[i + 5] - closes[i]) / closes[i] * 100 if closes[i] else None
    for i in range(n - 10):
        target_return_10d[i] = (closes[i + 10] - closes[i]) / closes[i] * 100 if closes[i] else None

    target_direction_1d = [1 if r and r > 0 else 0 if r is not None else None for r in target_return_1d]
    target_direction_5d = [1 if r and r > 0 else 0 if r is not None else None for r in target_return_5d]

    # Cumulative return
    cumulative_return = [0]
    for i in range(1, n):
        if closes[0] and closes[0] > 0:
            cumulative_return.append((closes[i] - closes[0]) / closes[0] * 100)
        else:
            cumulative_return.append(None)

    # ATR Percent
    atr_percent = [a / c * 100 if a and c else None for a, c in zip(atr_14, closes)]

    # Assign all indicators to values
    for i in range(n):
        v = values[i]

        # SMAs
        v['sma_5'] = sma_5[i]
        v['sma_10'] = sma_10[i]
        v['sma_20'] = sma_20[i]
        v['sma_50'] = sma_50[i]
        v['sma_100'] = sma_100[i]
        v['sma_200'] = sma_200[i]

        # EMAs
        v['ema_5'] = ema_5[i]
        v['ema_10'] = ema_10[i]
        v['ema_12'] = ema_12[i]
        v['ema_20'] = ema_20[i]
        v['ema_26'] = ema_26[i]
        v['ema_50'] = ema_50[i]

        # MACD
        v['macd'] = macd[i]
        v['macd_signal'] = macd_signal[i]
        v['macd_hist'] = macd_hist[i]

        # RSI
        v['rsi_7'] = rsi_7[i]
        v['rsi_14'] = rsi_14[i]
        v['rsi_21'] = rsi_21[i]

        # Stochastic
        v['stoch_k'] = stoch_k[i]
        v['stoch_d'] = stoch_d[i]
        v['stoch_rsi'] = stoch_rsi[i]

        # Bollinger
        v['bb_upper'] = bb_upper[i]
        v['bb_middle'] = bb_middle[i]
        v['bb_lower'] = bb_lower[i]
        v['bb_width'] = bb_width[i]
        v['bb_percent'] = bb_percent[i]

        # ATR and Volatility
        v['atr_7'] = atr_7[i]
        v['atr_14'] = atr_14[i]
        v['atr_percent'] = atr_percent[i]
        v['volatility_10'] = volatility_10[i]
        v['volatility_20'] = volatility_20[i]

        # Momentum
        v['roc_5'] = roc_5[i]
        v['roc_10'] = roc_10[i]
        v['roc_20'] = roc_20[i]
        v['momentum_10'] = momentum_10[i]
        v['williams_r'] = williams_r[i]

        # Volume
        v['obv'] = obv[i]
        v['volume_sma_20'] = volume_sma_20[i]
        v['volume_ratio'] = volume_ratio[i]

        # Oscillators
        v['cci'] = cci[i]
        v['ppo'] = ppo[i]
        v['awesome_osc'] = awesome_osc[i]

        # Price Action
        v['daily_return_pct'] = daily_returns[i]
        v['log_return'] = log_returns[i]
        v['high_low_pct'] = high_low_pct[i]
        v['body_size'] = body_size[i]
        v['upper_shadow'] = upper_shadow[i]
        v['lower_shadow'] = lower_shadow[i]

        # Lagged
        v['close_lag_1'] = close_lag_1[i]
        v['close_lag_2'] = close_lag_2[i]
        v['close_lag_3'] = close_lag_3[i]
        v['close_lag_5'] = close_lag_5[i]
        v['close_lag_10'] = close_lag_10[i]
        v['return_lag_1'] = return_lag_1[i]
        v['return_lag_2'] = return_lag_2[i]
        v['return_lag_3'] = return_lag_3[i]

        # Targets
        v['target_return_1d'] = target_return_1d[i]
        v['target_return_5d'] = target_return_5d[i]
        v['target_return_10d'] = target_return_10d[i]
        v['target_direction_1d'] = target_direction_1d[i]
        v['target_direction_5d'] = target_direction_5d[i]

        # Cumulative
        v['cumulative_return'] = cumulative_return[i]

        # Signal categories
        close = closes[i]
        rsi = rsi_14[i]
        vol = volatility_20[i]
        vol_r = volume_ratio[i]

        # Trend signal
        if sma_50[i] and sma_200[i]:
            if close > sma_50[i] > sma_200[i]:
                v['trend_signal'] = 'strong_bullish'
            elif close > sma_50[i]:
                v['trend_signal'] = 'bullish'
            elif close < sma_50[i] < sma_200[i]:
                v['trend_signal'] = 'strong_bearish'
            elif close < sma_50[i]:
                v['trend_signal'] = 'bearish'
            else:
                v['trend_signal'] = 'neutral'
        else:
            v['trend_signal'] = None

        # Momentum signal
        if rsi:
            if rsi > 70:
                v['momentum_signal'] = 'overbought'
            elif rsi > 50:
                v['momentum_signal'] = 'bullish'
            elif rsi > 30:
                v['momentum_signal'] = 'bearish'
            else:
                v['momentum_signal'] = 'oversold'
        else:
            v['momentum_signal'] = None

        # Volatility signal
        if vol:
            if vol > 40:
                v['volatility_signal'] = 'high'
            elif vol > 20:
                v['volatility_signal'] = 'normal'
            else:
                v['volatility_signal'] = 'low'
        else:
            v['volatility_signal'] = None

        # Volume signal
        if vol_r:
            if vol_r > 2:
                v['volume_signal'] = 'high'
            elif vol_r > 0.5:
                v['volume_signal'] = 'normal'
            else:
                v['volume_signal'] = 'low'
        else:
            v['volume_signal'] = None

    # Reverse back to most recent first
    return list(reversed(values))


def backfill_asset_type(client, asset_type, config, max_calls=100):
    """Backfill historical data for one asset type with all indicators"""
    table_name = config['table']
    symbols = config['symbols']
    asset_type_name = config['type']

    print(f"\n{'='*60}")
    print(f"Backfilling {asset_type_name} data to {table_name}")
    print(f"{'='*60}")

    # Create table if needed
    create_historical_table(client, table_name)

    records = []
    calls_made = 0
    now = datetime.now(timezone.utc)

    for symbol in symbols:
        if calls_made >= max_calls:
            print(f"\nReached max API calls ({max_calls}). Stopping for today.")
            break

        print(f"\nFetching {symbol}...")

        # Get existing dates
        existing_dates = get_existing_dates(client, table_name, symbol)
        print(f"  Already have {len(existing_dates)} days of data")

        # Fetch new data (up to 5000 records)
        values = fetch_historical_data(symbol, output_size=5000)
        calls_made += 1

        if not values:
            continue

        print(f"  Received {len(values)} records from Twelve Data")

        # Calculate all indicators
        values = calculate_all_indicators(values)

        # Filter out existing dates and prepare records
        new_records = 0
        for v in values:
            try:
                date_str = v['datetime'].split(' ')[0]
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                if date_obj in existing_dates:
                    continue

                # Parse date for time features
                day_of_week = date_obj.weekday()
                month = date_obj.month
                quarter = (month - 1) // 3 + 1
                is_month_start = date_obj.day <= 3
                is_month_end = date_obj.day >= 28

                record = {
                    'symbol': symbol,
                    'date': date_str,
                    'open': float(v.get('open', 0)),
                    'high': float(v.get('high', 0)),
                    'low': float(v.get('low', 0)),
                    'close': float(v.get('close', 0)),
                    'volume': float(v.get('volume', 0)) if v.get('volume') else None,
                    'asset_type': asset_type_name,
                    'fetch_timestamp': now.isoformat(),

                    # All indicators
                    'sma_5': v.get('sma_5'),
                    'sma_10': v.get('sma_10'),
                    'sma_20': v.get('sma_20'),
                    'sma_50': v.get('sma_50'),
                    'sma_100': v.get('sma_100'),
                    'sma_200': v.get('sma_200'),
                    'ema_5': v.get('ema_5'),
                    'ema_10': v.get('ema_10'),
                    'ema_12': v.get('ema_12'),
                    'ema_20': v.get('ema_20'),
                    'ema_26': v.get('ema_26'),
                    'ema_50': v.get('ema_50'),
                    'macd': v.get('macd'),
                    'macd_signal': v.get('macd_signal'),
                    'macd_hist': v.get('macd_hist'),
                    'rsi_7': v.get('rsi_7'),
                    'rsi_14': v.get('rsi_14'),
                    'rsi_21': v.get('rsi_21'),
                    'stoch_k': v.get('stoch_k'),
                    'stoch_d': v.get('stoch_d'),
                    'stoch_rsi': v.get('stoch_rsi'),
                    'bb_upper': v.get('bb_upper'),
                    'bb_middle': v.get('bb_middle'),
                    'bb_lower': v.get('bb_lower'),
                    'bb_width': v.get('bb_width'),
                    'bb_percent': v.get('bb_percent'),
                    'atr_7': v.get('atr_7'),
                    'atr_14': v.get('atr_14'),
                    'atr_percent': v.get('atr_percent'),
                    'volatility_10': v.get('volatility_10'),
                    'volatility_20': v.get('volatility_20'),
                    'roc_5': v.get('roc_5'),
                    'roc_10': v.get('roc_10'),
                    'roc_20': v.get('roc_20'),
                    'momentum_10': v.get('momentum_10'),
                    'williams_r': v.get('williams_r'),
                    'obv': v.get('obv'),
                    'volume_sma_20': v.get('volume_sma_20'),
                    'volume_ratio': v.get('volume_ratio'),
                    'cci': v.get('cci'),
                    'ppo': v.get('ppo'),
                    'ultimate_osc': None,  # Complex calculation, skip for now
                    'awesome_osc': v.get('awesome_osc'),
                    'adx': None,  # Complex calculation
                    'di_plus': None,
                    'di_minus': None,
                    'daily_return_pct': v.get('daily_return_pct'),
                    'log_return': v.get('log_return'),
                    'high_low_pct': v.get('high_low_pct'),
                    'body_size': v.get('body_size'),
                    'upper_shadow': v.get('upper_shadow'),
                    'lower_shadow': v.get('lower_shadow'),
                    'close_lag_1': v.get('close_lag_1'),
                    'close_lag_2': v.get('close_lag_2'),
                    'close_lag_3': v.get('close_lag_3'),
                    'close_lag_5': v.get('close_lag_5'),
                    'close_lag_10': v.get('close_lag_10'),
                    'return_lag_1': v.get('return_lag_1'),
                    'return_lag_2': v.get('return_lag_2'),
                    'return_lag_3': v.get('return_lag_3'),
                    'target_return_1d': v.get('target_return_1d'),
                    'target_return_5d': v.get('target_return_5d'),
                    'target_return_10d': v.get('target_return_10d'),
                    'target_direction_1d': v.get('target_direction_1d'),
                    'target_direction_5d': v.get('target_direction_5d'),
                    'trend_signal': v.get('trend_signal'),
                    'momentum_signal': v.get('momentum_signal'),
                    'volatility_signal': v.get('volatility_signal'),
                    'volume_signal': v.get('volume_signal'),
                    'day_of_week': day_of_week,
                    'month': month,
                    'quarter': quarter,
                    'is_month_start': is_month_start,
                    'is_month_end': is_month_end,
                    'cumulative_return': v.get('cumulative_return'),
                }
                records.append(record)
                new_records += 1
            except Exception as e:
                print(f"  Error processing record: {e}")

        print(f"  Added {new_records} new records with 80+ fields")

        # Rate limiting
        time.sleep(60 / API_CALLS_PER_MINUTE)

        # Batch upload every 500 records
        if len(records) >= 500:
            upload_records(client, table_name, records)
            records = []

    # Upload remaining records
    if records:
        upload_records(client, table_name, records)

    return calls_made


def upload_records(client, table_name, records):
    """Upload records to BigQuery"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    try:
        errors = client.insert_rows_json(table_ref, records)
        if errors:
            print(f"Insert errors: {errors[:3]}")
        else:
            print(f"Uploaded {len(records)} records to {table_name}")
    except Exception as e:
        print(f"Upload error: {e}")


def get_backfill_status(client):
    """Get current backfill status for all asset types"""
    print("\n" + "="*60)
    print("HISTORICAL DATA BACKFILL STATUS (WITH 50+ INDICATORS)")
    print("="*60)

    for asset_type, config in ASSET_CONFIGS.items():
        table_name = config['table']
        try:
            query = f"""
            SELECT
                COUNT(*) as total_records,
                COUNT(DISTINCT symbol) as unique_symbols,
                MIN(date) as earliest_date,
                MAX(date) as latest_date,
                COUNT(DISTINCT date) as unique_dates
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            """
            result = list(client.query(query).result())[0]

            print(f"\n{asset_type.upper()}:")
            print(f"  Records: {result.total_records:,}")
            print(f"  Symbols: {result.unique_symbols}")
            print(f"  Date range: {result.earliest_date} to {result.latest_date}")
            print(f"  Unique dates: {result.unique_dates}")
        except Exception as e:
            print(f"\n{asset_type.upper()}: No data yet (table may not exist)")


def main():
    """Main entry point"""
    print("="*60)
    print("HISTORICAL DATA WAREHOUSE BUILDER")
    print("With 50+ Technical Indicators for AI/ML")
    print("="*60)
    print(f"Started at: {datetime.now()}")
    print(f"API calls available: {API_CALLS_PER_DAY}/day")

    client = bigquery.Client(project=PROJECT_ID)

    # Check current status
    get_backfill_status(client)

    # Calculate API calls per asset type
    calls_per_type = API_CALLS_PER_DAY // len(ASSET_CONFIGS)
    print(f"\nAllocating ~{calls_per_type} API calls per asset type")

    total_calls = 0
    for asset_type, config in ASSET_CONFIGS.items():
        calls_made = backfill_asset_type(client, asset_type, config, max_calls=calls_per_type)
        total_calls += calls_made

    print("\n" + "="*60)
    print("BACKFILL COMPLETE")
    print("="*60)
    print(f"Total API calls made: {total_calls}")
    print(f"Completed at: {datetime.now()}")

    # Show updated status
    get_backfill_status(client)


if __name__ == "__main__":
    main()
