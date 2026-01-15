"""
BTC and NVDA Historical Data Fetcher for AI Model Training
============================================================
Purpose: Fetch comprehensive historical daily data for Bitcoin (BTC/USD) and
NVIDIA (NVDA) to build Fintech AI models using GCP Vertex AI and Gemini 3.

This script:
1. Fetches maximum available historical data from Twelve Data API
2. Calculates 29+ technical indicators for ML feature engineering
3. Stores data in BigQuery for Vertex AI training pipelines
4. Creates CSV exports for local model development
5. Supports incremental daily updates

Target Use Cases:
- Price prediction models (LSTM, Transformer)
- Pattern recognition (CNN-based)
- Sentiment correlation analysis
- Trading signal generation
- Risk assessment models

Author: AI Trading System
Date: November 2024
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
import csv

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'

# Target symbols for AI model development
AI_TRAINING_SYMBOLS = {
    'BTC/USD': {
        'table': 'btc_ai_training_daily',
        'asset_type': 'Crypto',
        'description': 'Bitcoin - Most traded cryptocurrency',
        'csv_file': 'btc_training_data.csv'
    },
    'NVDA': {
        'table': 'nvda_ai_training_daily',
        'asset_type': 'Stock',
        'description': 'NVIDIA - AI/GPU leader stock',
        'csv_file': 'nvda_training_data.csv'
    }
}


def create_ai_training_table(client, table_name):
    """Create BigQuery table optimized for AI/ML training with comprehensive schema"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    schema = [
        # Core OHLCV Data
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("open", "FLOAT64"),
        bigquery.SchemaField("high", "FLOAT64"),
        bigquery.SchemaField("low", "FLOAT64"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "FLOAT64"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP"),

        # Trend Indicators - Moving Averages
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
        bigquery.SchemaField("obv_ema", "FLOAT64"),
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
        bigquery.SchemaField("daily_return", "FLOAT64"),
        bigquery.SchemaField("daily_return_pct", "FLOAT64"),
        bigquery.SchemaField("log_return", "FLOAT64"),
        bigquery.SchemaField("high_low_range", "FLOAT64"),
        bigquery.SchemaField("high_low_pct", "FLOAT64"),
        bigquery.SchemaField("open_close_range", "FLOAT64"),
        bigquery.SchemaField("body_size", "FLOAT64"),
        bigquery.SchemaField("upper_shadow", "FLOAT64"),
        bigquery.SchemaField("lower_shadow", "FLOAT64"),

        # Lagged Features (for time series)
        bigquery.SchemaField("close_lag_1", "FLOAT64"),
        bigquery.SchemaField("close_lag_2", "FLOAT64"),
        bigquery.SchemaField("close_lag_3", "FLOAT64"),
        bigquery.SchemaField("close_lag_5", "FLOAT64"),
        bigquery.SchemaField("close_lag_10", "FLOAT64"),
        bigquery.SchemaField("return_lag_1", "FLOAT64"),
        bigquery.SchemaField("return_lag_2", "FLOAT64"),
        bigquery.SchemaField("return_lag_3", "FLOAT64"),

        # Future Target Variables (for supervised learning)
        bigquery.SchemaField("target_return_1d", "FLOAT64"),
        bigquery.SchemaField("target_return_5d", "FLOAT64"),
        bigquery.SchemaField("target_return_10d", "FLOAT64"),
        bigquery.SchemaField("target_direction_1d", "INT64"),  # 1=up, 0=down
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
        bigquery.SchemaField("is_month_start", "BOOL"),
        bigquery.SchemaField("is_month_end", "BOOL"),
    ]

    try:
        client.get_table(table_id)
        print(f"Table {table_name} already exists")
    except:
        table = bigquery.Table(table_id, schema=schema)
        table = client.create_table(table)
        print(f"Created table {table_name} with AI/ML optimized schema")


def fetch_historical_data(symbol, output_size=5000):
    """Fetch maximum historical daily data from Twelve Data API"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': output_size,  # Maximum available
        'apikey': TWELVE_DATA_API_KEY
    }

    print(f"  Requesting up to {output_size} days of data...")

    try:
        response = requests.get(url, params=params, timeout=60)
        data = response.json()

        if 'values' in data:
            print(f"  Received {len(data['values'])} data points")
            return data['values']
        elif 'code' in data:
            print(f"  API Error: {data.get('message', 'Unknown error')}")
            return None
        else:
            print(f"  Unexpected response format")
            return None
    except Exception as e:
        print(f"  Request error: {e}")
        return None


def calculate_ema(prices, period, prev_ema=None):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    multiplier = 2 / (period + 1)
    if prev_ema is None:
        return sum(prices[:period]) / period
    return (prices[0] - prev_ema) * multiplier + prev_ema


def calculate_rsi(closes, period, start_idx):
    """Calculate RSI for a given period"""
    if start_idx < period:
        return None

    gains = []
    losses = []
    for j in range(start_idx - period + 1, start_idx + 1):
        change = closes[j] - closes[j - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_all_ai_features(values):
    """Calculate comprehensive features for AI/ML training"""
    if not values or len(values) < 50:
        print("  Insufficient data for indicator calculation")
        return values

    # Reverse to chronological order (oldest first)
    values = list(reversed(values))
    n = len(values)

    print(f"  Calculating {n} days of indicators...")

    # Extract price arrays
    closes = [float(v['close']) for v in values]
    highs = [float(v['high']) for v in values]
    lows = [float(v['low']) for v in values]
    opens = [float(v['open']) for v in values]
    volumes = [float(v.get('volume', 0) or 0) for v in values]

    # Initialize tracking variables
    ema_trackers = {}
    prev_obv = 0

    for i in range(n):
        v = values[i]
        close = closes[i]
        high = highs[i]
        low = lows[i]
        open_price = opens[i]
        volume = volumes[i]

        # Parse date for time features
        try:
            date_str = v['datetime'].split(' ')[0]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            v['day_of_week'] = date_obj.weekday()
            v['month'] = date_obj.month
            v['quarter'] = (date_obj.month - 1) // 3 + 1
            v['is_month_start'] = date_obj.day <= 3
            v['is_month_end'] = date_obj.day >= 28
        except:
            pass

        # ===== SIMPLE MOVING AVERAGES =====
        for period in [5, 10, 20, 50, 100, 200]:
            if i >= period - 1:
                v[f'sma_{period}'] = sum(closes[i - period + 1:i + 1]) / period

        # ===== EXPONENTIAL MOVING AVERAGES =====
        for period in [5, 10, 12, 20, 26, 50]:
            key = f'ema_{period}'
            if i >= period - 1:
                if key not in ema_trackers:
                    ema_trackers[key] = sum(closes[i - period + 1:i + 1]) / period
                else:
                    multiplier = 2 / (period + 1)
                    ema_trackers[key] = (close - ema_trackers[key]) * multiplier + ema_trackers[key]
                v[key] = ema_trackers[key]

        # ===== MACD =====
        if v.get('ema_12') and v.get('ema_26'):
            macd = v['ema_12'] - v['ema_26']
            v['macd'] = macd

            # MACD Signal (9-period EMA of MACD)
            if i >= 33:
                macd_vals = [values[j].get('macd') for j in range(max(0, i - 8), i + 1)
                             if values[j].get('macd') is not None]
                if len(macd_vals) >= 9:
                    if 'macd_signal_ema' not in ema_trackers:
                        ema_trackers['macd_signal_ema'] = sum(macd_vals[:9]) / 9
                    else:
                        mult = 2 / 10
                        ema_trackers['macd_signal_ema'] = (macd - ema_trackers['macd_signal_ema']) * mult + ema_trackers['macd_signal_ema']
                    v['macd_signal'] = ema_trackers['macd_signal_ema']
                    v['macd_hist'] = macd - v['macd_signal']

        # ===== RSI (Multiple Periods) =====
        for period in [7, 14, 21]:
            if i >= period:
                v[f'rsi_{period}'] = calculate_rsi(closes, period, i)

        # ===== STOCHASTIC OSCILLATOR =====
        if i >= 13:
            period_highs = highs[i - 13:i + 1]
            period_lows = lows[i - 13:i + 1]
            highest = max(period_highs)
            lowest = min(period_lows)

            if highest != lowest:
                stoch_k = ((close - lowest) / (highest - lowest)) * 100
                v['stoch_k'] = stoch_k

                if i >= 15:
                    stoch_k_vals = [values[j].get('stoch_k') for j in range(i - 2, i + 1)
                                   if values[j].get('stoch_k') is not None]
                    if len(stoch_k_vals) == 3:
                        v['stoch_d'] = sum(stoch_k_vals) / 3

        # ===== STOCHASTIC RSI =====
        if v.get('rsi_14') and i >= 27:
            rsi_vals = [values[j].get('rsi_14') for j in range(i - 13, i + 1)
                       if values[j].get('rsi_14') is not None]
            if len(rsi_vals) >= 14:
                rsi_high = max(rsi_vals)
                rsi_low = min(rsi_vals)
                if rsi_high != rsi_low:
                    v['stoch_rsi'] = ((v['rsi_14'] - rsi_low) / (rsi_high - rsi_low)) * 100

        # ===== BOLLINGER BANDS =====
        if i >= 19:
            period_closes = closes[i - 19:i + 1]
            sma_20 = sum(period_closes) / 20
            std_dev = math.sqrt(sum((x - sma_20) ** 2 for x in period_closes) / 20)

            v['bb_middle'] = sma_20
            v['bb_upper'] = sma_20 + (2 * std_dev)
            v['bb_lower'] = sma_20 - (2 * std_dev)
            v['bb_width'] = ((v['bb_upper'] - v['bb_lower']) / v['bb_middle']) * 100 if sma_20 != 0 else 0
            v['bb_percent'] = ((close - v['bb_lower']) / (v['bb_upper'] - v['bb_lower'])) * 100 if v['bb_upper'] != v['bb_lower'] else 50

        # ===== ATR (Average True Range) =====
        for period in [7, 14]:
            if i >= period:
                true_ranges = []
                for j in range(i - period + 1, i + 1):
                    if j > 0:
                        tr = max(
                            highs[j] - lows[j],
                            abs(highs[j] - closes[j - 1]),
                            abs(lows[j] - closes[j - 1])
                        )
                        true_ranges.append(tr)
                if len(true_ranges) >= period:
                    v[f'atr_{period}'] = sum(true_ranges) / period
                    if period == 14 and close != 0:
                        v['atr_percent'] = (v['atr_14'] / close) * 100

        # ===== VOLATILITY =====
        for period in [10, 20]:
            if i >= period:
                returns = [(closes[j] - closes[j - 1]) / closes[j - 1] for j in range(i - period + 1, i + 1) if closes[j - 1] != 0]
                if len(returns) >= period:
                    mean_ret = sum(returns) / len(returns)
                    variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
                    v[f'volatility_{period}'] = math.sqrt(variance) * math.sqrt(252) * 100

        # ===== RATE OF CHANGE (ROC) =====
        for period in [5, 10, 20]:
            if i >= period and closes[i - period] != 0:
                v[f'roc_{period}'] = ((close - closes[i - period]) / closes[i - period]) * 100

        # ===== MOMENTUM =====
        if i >= 10:
            v['momentum_10'] = close - closes[i - 10]

        # ===== WILLIAMS %R =====
        if i >= 13:
            period_highs = highs[i - 13:i + 1]
            period_lows = lows[i - 13:i + 1]
            highest = max(period_highs)
            lowest = min(period_lows)
            if highest != lowest:
                v['williams_r'] = ((highest - close) / (highest - lowest)) * -100

        # ===== ON BALANCE VOLUME (OBV) =====
        if volume > 0:
            if i == 0:
                prev_obv = volume
            else:
                if close > closes[i - 1]:
                    prev_obv += volume
                elif close < closes[i - 1]:
                    prev_obv -= volume
            v['obv'] = prev_obv

            if i >= 19:
                obv_vals = [values[j].get('obv') for j in range(i - 19, i + 1) if values[j].get('obv') is not None]
                if len(obv_vals) >= 20:
                    v['obv_ema'] = sum(obv_vals) / 20

        # ===== VOLUME FEATURES =====
        if i >= 19 and volume > 0:
            vol_sma = sum(volumes[i - 19:i + 1]) / 20
            v['volume_sma_20'] = vol_sma
            if vol_sma > 0:
                v['volume_ratio'] = volume / vol_sma

        # ===== CCI (Commodity Channel Index) =====
        if i >= 19:
            typical_prices = [(highs[j] + lows[j] + closes[j]) / 3 for j in range(i - 19, i + 1)]
            tp_sma = sum(typical_prices) / 20
            mean_dev = sum(abs(tp - tp_sma) for tp in typical_prices) / 20
            if mean_dev != 0:
                v['cci'] = (typical_prices[-1] - tp_sma) / (0.015 * mean_dev)

        # ===== PPO (Percentage Price Oscillator) =====
        if v.get('ema_12') and v.get('ema_26') and v['ema_26'] != 0:
            v['ppo'] = ((v['ema_12'] - v['ema_26']) / v['ema_26']) * 100

        # ===== ULTIMATE OSCILLATOR =====
        if i >= 27:
            bp_7 = tr_7 = bp_14 = tr_14 = bp_28 = tr_28 = 0
            for j in range(i - 27, i + 1):
                if j > 0:
                    bp = closes[j] - min(lows[j], closes[j - 1])
                    tr = max(highs[j], closes[j - 1]) - min(lows[j], closes[j - 1])
                    if j >= i - 6:
                        bp_7 += bp
                        tr_7 += tr
                    if j >= i - 13:
                        bp_14 += bp
                        tr_14 += tr
                    bp_28 += bp
                    tr_28 += tr

            if tr_7 > 0 and tr_14 > 0 and tr_28 > 0:
                avg_7 = bp_7 / tr_7
                avg_14 = bp_14 / tr_14
                avg_28 = bp_28 / tr_28
                v['ultimate_osc'] = 100 * ((4 * avg_7) + (2 * avg_14) + avg_28) / 7

        # ===== AWESOME OSCILLATOR =====
        if i >= 33:
            midpoints = [(highs[j] + lows[j]) / 2 for j in range(i - 33, i + 1)]
            sma_5 = sum(midpoints[-5:]) / 5
            sma_34 = sum(midpoints) / 34
            v['awesome_osc'] = sma_5 - sma_34

        # ===== ADX (Average Directional Index) =====
        if i >= 14:
            plus_dm_sum = minus_dm_sum = tr_sum = 0
            for j in range(i - 13, i + 1):
                if j > 0:
                    plus_dm = highs[j] - highs[j - 1] if highs[j] - highs[j - 1] > 0 else 0
                    minus_dm = lows[j - 1] - lows[j] if lows[j - 1] - lows[j] > 0 else 0
                    if plus_dm > minus_dm:
                        minus_dm = 0
                    else:
                        plus_dm = 0
                    tr = max(highs[j] - lows[j], abs(highs[j] - closes[j - 1]), abs(lows[j] - closes[j - 1]))
                    plus_dm_sum += plus_dm
                    minus_dm_sum += minus_dm
                    tr_sum += tr

            if tr_sum > 0:
                plus_di = (plus_dm_sum / tr_sum) * 100
                minus_di = (minus_dm_sum / tr_sum) * 100
                v['di_plus'] = plus_di
                v['di_minus'] = minus_di
                if plus_di + minus_di > 0:
                    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
                    if i >= 27:
                        dx_vals = []
                        v['adx'] = dx  # Simplified ADX

        # ===== PRICE ACTION FEATURES =====
        if i > 0:
            v['daily_return'] = close - closes[i - 1]
            v['daily_return_pct'] = ((close - closes[i - 1]) / closes[i - 1]) * 100 if closes[i - 1] != 0 else 0
            v['log_return'] = math.log(close / closes[i - 1]) if closes[i - 1] > 0 and close > 0 else 0

        v['high_low_range'] = high - low
        v['high_low_pct'] = ((high - low) / close) * 100 if close != 0 else 0
        v['open_close_range'] = close - open_price
        v['body_size'] = abs(close - open_price)
        v['upper_shadow'] = high - max(open_price, close)
        v['lower_shadow'] = min(open_price, close) - low

        # ===== LAGGED FEATURES =====
        for lag in [1, 2, 3, 5, 10]:
            if i >= lag:
                v[f'close_lag_{lag}'] = closes[i - lag]
                if lag <= 3 and i >= lag + 1:
                    v[f'return_lag_{lag}'] = ((closes[i - lag] - closes[i - lag - 1]) / closes[i - lag - 1]) * 100 if closes[i - lag - 1] != 0 else 0

        # ===== SIGNAL CATEGORIES =====
        if v.get('sma_20') and v.get('sma_50'):
            if close > v['sma_20'] > v['sma_50']:
                v['trend_signal'] = 'strong_bullish'
            elif close > v['sma_20']:
                v['trend_signal'] = 'bullish'
            elif close < v['sma_20'] < v['sma_50']:
                v['trend_signal'] = 'strong_bearish'
            elif close < v['sma_20']:
                v['trend_signal'] = 'bearish'
            else:
                v['trend_signal'] = 'neutral'

        if v.get('rsi_14'):
            if v['rsi_14'] > 70:
                v['momentum_signal'] = 'overbought'
            elif v['rsi_14'] < 30:
                v['momentum_signal'] = 'oversold'
            elif v['rsi_14'] > 50:
                v['momentum_signal'] = 'bullish'
            else:
                v['momentum_signal'] = 'bearish'

        if v.get('bb_width'):
            if v['bb_width'] > 15:
                v['volatility_signal'] = 'high'
            elif v['bb_width'] < 5:
                v['volatility_signal'] = 'low'
            else:
                v['volatility_signal'] = 'normal'

        if v.get('volume_ratio'):
            if v['volume_ratio'] > 2:
                v['volume_signal'] = 'high'
            elif v['volume_ratio'] < 0.5:
                v['volume_signal'] = 'low'
            else:
                v['volume_signal'] = 'normal'

    # Calculate target variables (future returns) - need to iterate again
    print("  Calculating target variables for supervised learning...")
    for i in range(n):
        v = values[i]
        # 1-day future return
        if i < n - 1:
            v['target_return_1d'] = ((closes[i + 1] - closes[i]) / closes[i]) * 100 if closes[i] != 0 else 0
            v['target_direction_1d'] = 1 if closes[i + 1] > closes[i] else 0

        # 5-day future return
        if i < n - 5:
            v['target_return_5d'] = ((closes[i + 5] - closes[i]) / closes[i]) * 100 if closes[i] != 0 else 0
            v['target_direction_5d'] = 1 if closes[i + 5] > closes[i] else 0

        # 10-day future return
        if i < n - 10:
            v['target_return_10d'] = ((closes[i + 10] - closes[i]) / closes[i]) * 100 if closes[i] != 0 else 0

    print("  All indicators calculated successfully")
    # Reverse back to most recent first
    return list(reversed(values))


def export_to_csv(values, symbol, filename):
    """Export data to CSV for local AI model development"""
    if not values:
        return

    # Define CSV columns
    columns = [
        'date', 'open', 'high', 'low', 'close', 'volume',
        'sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_100', 'sma_200',
        'ema_5', 'ema_10', 'ema_12', 'ema_20', 'ema_26', 'ema_50',
        'macd', 'macd_signal', 'macd_hist',
        'rsi_7', 'rsi_14', 'rsi_21',
        'stoch_k', 'stoch_d', 'stoch_rsi',
        'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_percent',
        'atr_7', 'atr_14', 'atr_percent', 'volatility_10', 'volatility_20',
        'roc_5', 'roc_10', 'roc_20', 'momentum_10', 'williams_r',
        'obv', 'volume_sma_20', 'volume_ratio',
        'cci', 'ppo', 'ultimate_osc', 'awesome_osc', 'adx', 'di_plus', 'di_minus',
        'daily_return_pct', 'log_return', 'high_low_pct',
        'close_lag_1', 'close_lag_2', 'close_lag_3', 'close_lag_5', 'close_lag_10',
        'target_return_1d', 'target_return_5d', 'target_return_10d',
        'target_direction_1d', 'target_direction_5d',
        'trend_signal', 'momentum_signal', 'volatility_signal', 'volume_signal',
        'day_of_week', 'month', 'quarter'
    ]

    filepath = os.path.join(os.path.dirname(__file__), filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['symbol'] + columns)

        for v in reversed(values):  # Chronological order
            row = [symbol]
            for col in columns:
                if col == 'date':
                    row.append(v.get('datetime', '').split(' ')[0])
                else:
                    val = v.get(col)
                    if val is not None:
                        if isinstance(val, float):
                            row.append(round(val, 6))
                        else:
                            row.append(val)
                    else:
                        row.append('')
            writer.writerow(row)

    print(f"  Exported {len(values)} records to {filename}")


def upload_to_bigquery(client, table_name, values, symbol, asset_type):
    """Upload data to BigQuery"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    now = datetime.now(timezone.utc)

    records = []
    for v in values:
        try:
            date_str = v['datetime'].split(' ')[0]

            record = {
                'symbol': symbol,
                'date': date_str,
                'open': float(v.get('open', 0)),
                'high': float(v.get('high', 0)),
                'low': float(v.get('low', 0)),
                'close': float(v.get('close', 0)),
                'volume': float(v.get('volume', 0)) if v.get('volume') else None,
                'asset_type': asset_type,
                'fetch_timestamp': now.isoformat(),
            }

            # Add all calculated indicators
            indicator_fields = [
                'sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_100', 'sma_200',
                'ema_5', 'ema_10', 'ema_12', 'ema_20', 'ema_26', 'ema_50',
                'macd', 'macd_signal', 'macd_hist',
                'rsi_7', 'rsi_14', 'rsi_21',
                'stoch_k', 'stoch_d', 'stoch_rsi',
                'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_percent',
                'atr_7', 'atr_14', 'atr_percent', 'volatility_10', 'volatility_20',
                'roc_5', 'roc_10', 'roc_20', 'momentum_10', 'williams_r',
                'obv', 'obv_ema', 'volume_sma_20', 'volume_ratio',
                'cci', 'ppo', 'ultimate_osc', 'awesome_osc', 'adx', 'di_plus', 'di_minus',
                'daily_return', 'daily_return_pct', 'log_return',
                'high_low_range', 'high_low_pct', 'open_close_range',
                'body_size', 'upper_shadow', 'lower_shadow',
                'close_lag_1', 'close_lag_2', 'close_lag_3', 'close_lag_5', 'close_lag_10',
                'return_lag_1', 'return_lag_2', 'return_lag_3',
                'target_return_1d', 'target_return_5d', 'target_return_10d',
                'target_direction_1d', 'target_direction_5d',
                'trend_signal', 'momentum_signal', 'volatility_signal', 'volume_signal',
                'day_of_week', 'month', 'quarter', 'is_month_start', 'is_month_end'
            ]

            for field in indicator_fields:
                record[field] = v.get(field)

            records.append(record)
        except Exception as e:
            print(f"  Error processing record: {e}")

    # Upload in batches
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            errors = client.insert_rows_json(table_ref, batch)
            if errors:
                print(f"  Insert errors: {errors[:2]}")
            else:
                print(f"  Uploaded batch {i // batch_size + 1}: {len(batch)} records")
        except Exception as e:
            print(f"  Upload error: {e}")

    return len(records)


def main():
    """Main entry point - Fetch BTC and NVDA data for AI training"""
    print("=" * 70)
    print("BTC & NVDA HISTORICAL DATA FETCHER FOR AI MODEL TRAINING")
    print("Target: Vertex AI and Gemini 3 Model Development")
    print("=" * 70)
    print(f"Started at: {datetime.now()}")
    print()

    client = bigquery.Client(project=PROJECT_ID)

    for symbol, config in AI_TRAINING_SYMBOLS.items():
        print(f"\n{'=' * 60}")
        print(f"Processing {symbol} - {config['description']}")
        print(f"{'=' * 60}")

        # Create table
        create_ai_training_table(client, config['table'])

        # Fetch historical data
        print(f"\nFetching historical data for {symbol}...")
        values = fetch_historical_data(symbol, output_size=5000)

        if not values:
            print(f"  Failed to fetch data for {symbol}")
            continue

        print(f"  Retrieved {len(values)} days of historical data")

        # Calculate all AI/ML features
        print(f"\nCalculating AI/ML features...")
        values = calculate_all_ai_features(values)

        # Export to CSV for local development
        print(f"\nExporting to CSV...")
        export_to_csv(values, symbol, config['csv_file'])

        # Upload to BigQuery
        print(f"\nUploading to BigQuery table: {config['table']}...")
        records_uploaded = upload_to_bigquery(
            client, config['table'], values, symbol, config['asset_type']
        )
        print(f"  Total records uploaded: {records_uploaded}")

        # Rate limit between symbols
        print("\nWaiting for rate limit...")
        time.sleep(10)

    print("\n" + "=" * 70)
    print("FETCH COMPLETE")
    print("=" * 70)
    print(f"Completed at: {datetime.now()}")
    print()
    print("Data is now ready for:")
    print("  1. Vertex AI AutoML training")
    print("  2. Custom TensorFlow/PyTorch models")
    print("  3. Gemini 3 fine-tuning experiments")
    print("  4. Local Jupyter notebook analysis")
    print()
    print("CSV files created:")
    for symbol, config in AI_TRAINING_SYMBOLS.items():
        print(f"  - {config['csv_file']}")
    print()
    print("BigQuery tables populated:")
    for symbol, config in AI_TRAINING_SYMBOLS.items():
        print(f"  - {PROJECT_ID}.{DATASET_ID}.{config['table']}")


if __name__ == "__main__":
    main()
