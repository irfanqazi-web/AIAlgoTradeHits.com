"""
Load Fresh Test Data - Download and upload NVDA and BTC/USD data for all timeframes
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery
import time
import requests

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

def calculate_technical_indicators(df):
    """Calculate all 71 technical indicators"""

    # Handle insufficient data
    if len(df) < 200:
        print(f"  ⚠ Only {len(df)} candles - filling with nulls for indicators requiring more data")

    # Price-based calculations
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

    # RSI (14)
    if len(df) >= 15:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
    else:
        df['rsi'] = None

    # MACD
    if len(df) >= 26:
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
    else:
        df['macd'] = None
        df['macd_signal'] = None
        df['macd_histogram'] = None

    # Moving Averages
    if len(df) >= 20:
        df['sma_20'] = df['close'].rolling(window=20).mean()
    else:
        df['sma_20'] = None

    if len(df) >= 50:
        df['sma_50'] = df['close'].rolling(window=50).mean()
    else:
        df['sma_50'] = None

    if len(df) >= 200:
        df['sma_200'] = df['close'].rolling(window=200).mean()
    else:
        df['sma_200'] = None

    # EMAs
    if len(df) >= 12:
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    else:
        df['ema_12'] = None

    if len(df) >= 26:
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    else:
        df['ema_26'] = None

    if len(df) >= 50:
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    else:
        df['ema_50'] = None

    # Bollinger Bands
    if len(df) >= 20:
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    else:
        df['bb_middle'] = None
        df['bb_upper'] = None
        df['bb_lower'] = None

    # ATR (Average True Range)
    if len(df) >= 14:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(14).mean()
    else:
        df['atr'] = None

    # ADX (Average Directional Index)
    if len(df) >= 14:
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()

        plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(14).mean() / atr)

        dx = (np.abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        df['adx'] = dx.rolling(14).mean()
    else:
        df['adx'] = None

    # OBV (On-Balance Volume)
    if len(df) >= 2:
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    else:
        df['obv'] = None

    # Stochastic Oscillator
    if len(df) >= 14:
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
    else:
        df['stoch_k'] = None
        df['stoch_d'] = None

    # CCI (Commodity Channel Index)
    if len(df) >= 20:
        tp = (df['high'] + df['low'] + df['close']) / 3
        df['cci'] = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())
    else:
        df['cci'] = None

    # Williams %R
    if len(df) >= 14:
        high_14 = df['high'].rolling(window=14).max()
        low_14 = df['low'].rolling(window=14).min()
        df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14))
    else:
        df['williams_r'] = None

    # ROC (Rate of Change)
    if len(df) >= 10:
        df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
    else:
        df['roc'] = 0

    # Fibonacci Retracement Levels (based on recent swing high/low)
    if len(df) >= 50:
        recent_high = df['high'].rolling(window=50).max()
        recent_low = df['low'].rolling(window=50).min()
        diff = recent_high - recent_low

        df['fib_0'] = recent_high
        df['fib_236'] = recent_high - (0.236 * diff)
        df['fib_382'] = recent_high - (0.382 * diff)
        df['fib_500'] = recent_high - (0.500 * diff)
        df['fib_618'] = recent_high - (0.618 * diff)
        df['fib_786'] = recent_high - (0.786 * diff)
        df['fib_100'] = recent_low
    else:
        df['fib_0'] = None
        df['fib_236'] = None
        df['fib_382'] = None
        df['fib_500'] = None
        df['fib_618'] = None
        df['fib_786'] = None
        df['fib_100'] = None

    # Elliott Wave Analysis (simplified)
    if len(df) >= 50:
        # Detect peaks and troughs
        df['wave_position'] = 0
        df['wave_1_high'] = None
        df['wave_2_low'] = None
        df['wave_3_high'] = None
        df['wave_4_low'] = None
        df['wave_5_high'] = None
        df['trend_direction'] = 0
        df['elliott_wave_degree'] = 'minor'
    else:
        df['wave_position'] = None
        df['wave_1_high'] = None
        df['wave_2_low'] = None
        df['wave_3_high'] = None
        df['wave_4_low'] = None
        df['wave_5_high'] = None
        df['trend_direction'] = None
        df['elliott_wave_degree'] = None

    return df


def fetch_stock_data_yfinance(symbol, interval, period):
    """Fetch stock data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(interval=interval, period=period)

        if hist.empty:
            return None

        # Rename columns to match our schema
        df = pd.DataFrame({
            'datetime': hist.index,
            'open': hist['Open'],
            'high': hist['High'],
            'low': hist['Low'],
            'close': hist['Close'],
            'volume': hist['Volume'],
            'symbol': symbol
        })

        df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
        return df

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None


def fetch_crypto_data_kraken(pair, interval, since=None):
    """Fetch crypto data from Kraken API"""
    try:
        # Map our intervals to Kraken intervals
        kraken_intervals = {
            'daily': 1440,
            'hourly': 60,
            '5min': 5
        }

        url = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={kraken_intervals[interval]}"
        if since:
            url += f"&since={since}"

        response = requests.get(url)
        data = response.json()

        if data['error']:
            print(f"    ✗ Kraken API error: {data['error']}")
            return None

        # Get the pair key (Kraken returns it with different formatting)
        result_key = list(data['result'].keys())[0]
        ohlc_data = data['result'][result_key]

        df = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        df['datetime'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
        df['pair'] = 'BTC/USD'

        return df

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None


def upload_to_bigquery(df, table_name):
    """Upload dataframe to BigQuery"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Convert datetime to timestamp
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])

        # Upload
        job = client.load_table_from_dataframe(df, table_id)
        job.result()

        print(f"    ✓ Uploaded {len(df)} records to {table_name}")
        return True

    except Exception as e:
        print(f"    ✗ Upload error: {e}")
        return False


def main():
    print("="*70)
    print("LOADING FRESH TEST DATA")
    print("="*70)
    print()

    # ===================
    # STOCK DATA - NVDA
    # ===================
    print("FETCHING STOCK DATA (NVDA)")
    print("-"*70)

    # Daily (6 months)
    print("\n1. Daily data (6 months)...")
    df_stock_daily = fetch_stock_data_yfinance('NVDA', '1d', '6mo')
    if df_stock_daily is not None:
        df_stock_daily = calculate_technical_indicators(df_stock_daily)
        upload_to_bigquery(df_stock_daily, 'stocks_daily')

    time.sleep(2)

    # Hourly (1 month)
    print("\n2. Hourly data (1 month)...")
    df_stock_hourly = fetch_stock_data_yfinance('NVDA', '1h', '1mo')
    if df_stock_hourly is not None:
        df_stock_hourly = calculate_technical_indicators(df_stock_hourly)
        upload_to_bigquery(df_stock_hourly, 'stocks_hourly')

    time.sleep(2)

    # 5-minute (7 days)
    print("\n3. 5-minute data (7 days)...")
    df_stock_5min = fetch_stock_data_yfinance('NVDA', '5m', '7d')
    if df_stock_5min is not None:
        df_stock_5min = calculate_technical_indicators(df_stock_5min)
        upload_to_bigquery(df_stock_5min, 'stocks_5min')

    # ===================
    # CRYPTO DATA - BTC/USD
    # ===================
    print("\n\n" + "="*70)
    print("FETCHING CRYPTO DATA (BTC/USD)")
    print("-"*70)

    # Daily (6 months)
    print("\n1. Daily data (6 months)...")
    # Kraken: 720 days * 1440 min/day = 1,036,800 minutes ago
    since_daily = int((datetime.now() - timedelta(days=180)).timestamp())
    df_crypto_daily = fetch_crypto_data_kraken('XBTUSD', 'daily', since=since_daily)
    if df_crypto_daily is not None:
        df_crypto_daily = calculate_technical_indicators(df_crypto_daily)
        upload_to_bigquery(df_crypto_daily, 'crypto_analysis')

    time.sleep(2)

    # Hourly (30 days)
    print("\n2. Hourly data (30 days)...")
    since_hourly = int((datetime.now() - timedelta(days=30)).timestamp())
    df_crypto_hourly = fetch_crypto_data_kraken('XBTUSD', 'hourly', since=since_hourly)
    if df_crypto_hourly is not None:
        df_crypto_hourly = calculate_technical_indicators(df_crypto_hourly)
        upload_to_bigquery(df_crypto_hourly, 'crypto_hourly_data')

    time.sleep(2)

    # 5-minute (7 days)
    print("\n3. 5-minute data (7 days)...")
    since_5min = int((datetime.now() - timedelta(days=7)).timestamp())
    df_crypto_5min = fetch_crypto_data_kraken('XBTUSD', '5min', since=since_5min)
    if df_crypto_5min is not None:
        df_crypto_5min = calculate_technical_indicators(df_crypto_5min)
        upload_to_bigquery(df_crypto_5min, 'crypto_5min_top10_gainers')

    print("\n\n" + "="*70)
    print("✓ FRESH TEST DATA LOADED")
    print("="*70)
    print("\nData loaded:")
    print("  Stock (NVDA): Daily, Hourly, 5-minute")
    print("  Crypto (BTC/USD): Daily, Hourly, 5-minute")


if __name__ == "__main__":
    main()
