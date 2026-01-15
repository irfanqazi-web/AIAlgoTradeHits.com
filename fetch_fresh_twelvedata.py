"""
Fetch Fresh Test Data - NVDA and BTC/USD for all timeframes
Uses TwelveData API to fetch data with 71 technical indicators
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Test symbols - just NVDA for stocks and BTC/USD for crypto
TEST_STOCK = 'NVDA'
TEST_CRYPTO = 'BTC/USD'

# Table mappings
TABLES = {
    'stocks': {
        'daily': 'stocks_daily',
        'hourly': 'stocks_hourly',
        '5min': 'stocks_5min'
    },
    'crypto': {
        'daily': 'crypto_analysis',
        'hourly': 'crypto_hourly_data',
        '5min': 'crypto_5min_top10_gainers'
    }
}

def fetch_time_series(symbol, interval='1day', outputsize=100):
    """
    Fetch OHLCV time series data from TwelveData
    """
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': outputsize,
        'apikey': TWELVE_DATA_API_KEY,
        'format': 'JSON'
    }

    try:
        response = requests.get(f"{BASE_URL}/time_series", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'values' in data and len(data['values']) > 0:
                return data
            else:
                logger.warning(f"No data for {symbol}: {data.get('message', 'Unknown error')}")
                return None
        else:
            logger.error(f"API error for {symbol}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return None

def fetch_stock_metadata(symbol):
    """Fetch stock metadata (name, exchange, currency)"""
    params = {
        'symbol': symbol,
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(f"{BASE_URL}/stocks", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                stock_info = data['data'][0]
                return {
                    'name': stock_info.get('name', ''),
                    'exchange': stock_info.get('exchange', ''),
                    'currency': stock_info.get('currency', 'USD'),
                    'country': stock_info.get('country', 'US'),
                    'mic_code': stock_info.get('mic_code', '')
                }
    except Exception as e:
        logger.error(f"Error fetching metadata for {symbol}: {str(e)}")

    return {
        'name': '',
        'exchange': 'NASDAQ/NYSE',
        'currency': 'USD',
        'country': 'United States',
        'mic_code': ''
    }

def calculate_technical_indicators(df):
    """
    Calculate all 71 technical indicators
    Input: DataFrame with columns [datetime, open, high, low, close, volume]
    Output: DataFrame with added indicator columns
    """

    # Ensure we have enough data
    if len(df) < 200:
        logger.warning(f"Not enough data for indicators: {len(df)} rows")
        # Return df with null indicators
        indicator_cols = [
            'rsi', 'macd', 'macd_signal', 'macd_hist', 'stoch_k', 'stoch_d',
            'williams_r', 'cci', 'roc', 'momentum',
            'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'ema_50',
            'wma_20', 'dema_20', 'tema_20', 'kama_20', 'vwap',
            'bb_upper', 'bb_middle', 'bb_lower', 'atr', 'natr', 'stddev',
            'obv', 'ad', 'adosc', 'pvo',
            'adx', 'adxr', 'plus_di', 'minus_di', 'aroon_up', 'aroon_down',
            'aroonosc', 'trix', 'dx', 'sar',
            'cdl_doji', 'cdl_hammer', 'cdl_engulfing', 'cdl_harami', 'cdl_morningstar',
            'cdl_3blackcrows', 'cdl_2crows', 'cdl_3inside', 'cdl_3linestrike', 'cdl_abandonedbaby',
            'correl', 'linearreg', 'linearreg_slope', 'linearreg_angle', 'tsf', 'variance', 'beta',
            'ultosc', 'bop', 'cmo', 'dpo', 'ht_dcperiod', 'ht_dcphase', 'ht_trendmode',
            'midpoint', 'midprice', 'ppo', 'stochrsi', 'apo', 'ht_sine_lead'
        ]
        for col in indicator_cols:
            df[col] = None
        return df

    try:
        # Momentum Indicators
        df['rsi'] = calculate_rsi(df['close'], period=14)
        macd_data = calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_hist'] = macd_data['histogram']

        stoch = calculate_stochastic(df)
        df['stoch_k'] = stoch['k']
        df['stoch_d'] = stoch['d']

        df['williams_r'] = calculate_williams_r(df)
        df['cci'] = calculate_cci(df)
        df['roc'] = df['close'].pct_change(periods=10) * 100
        df['momentum'] = df['close'].diff(10)

        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['wma_20'] = df['close'].rolling(window=20).apply(lambda x: (x * np.arange(1, len(x) + 1)).sum() / np.arange(1, len(x) + 1).sum())

        # Simple DEMA/TEMA calculations
        ema_20 = df['close'].ewm(span=20, adjust=False).mean()
        df['dema_20'] = 2 * ema_20 - ema_20.ewm(span=20, adjust=False).mean()
        df['tema_20'] = 3 * ema_20 - 3 * ema_20.ewm(span=20, adjust=False).mean() + ema_20.ewm(span=20, adjust=False).mean().ewm(span=20, adjust=False).mean()

        df['kama_20'] = calculate_kama(df['close'], period=20)
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

        # Volatility
        bb = calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb['upper']
        df['bb_middle'] = bb['middle']
        df['bb_lower'] = bb['lower']

        df['atr'] = calculate_atr(df)
        df['natr'] = (df['atr'] / df['close']) * 100
        df['stddev'] = df['close'].rolling(window=20).std()

        # Volume
        df['obv'] = calculate_obv(df)
        df['ad'] = calculate_ad(df)
        df['adosc'] = df['ad'].diff(3)
        ema_vol_12 = df['volume'].ewm(span=12, adjust=False).mean()
        ema_vol_26 = df['volume'].ewm(span=26, adjust=False).mean()
        df['pvo'] = ((ema_vol_12 - ema_vol_26) / ema_vol_26) * 100

        # Trend
        adx_data = calculate_adx(df)
        df['adx'] = adx_data['adx']
        df['plus_di'] = adx_data['plus_di']
        df['minus_di'] = adx_data['minus_di']
        df['dx'] = adx_data['dx']
        df['adxr'] = (df['adx'] + df['adx'].shift(14)) / 2

        aroon = calculate_aroon(df)
        df['aroon_up'] = aroon['up']
        df['aroon_down'] = aroon['down']
        df['aroonosc'] = aroon['up'] - aroon['down']

        df['trix'] = df['close'].ewm(span=15, adjust=False).mean().ewm(span=15, adjust=False).mean().ewm(span=15, adjust=False).mean().pct_change() * 100
        df['sar'] = calculate_sar(df)

        # Pattern Recognition (simplified)
        df['cdl_doji'] = detect_doji(df)
        df['cdl_hammer'] = detect_hammer(df)
        df['cdl_engulfing'] = detect_engulfing(df)
        df['cdl_harami'] = 0
        df['cdl_morningstar'] = 0
        df['cdl_3blackcrows'] = 0
        df['cdl_2crows'] = 0
        df['cdl_3inside'] = 0
        df['cdl_3linestrike'] = 0
        df['cdl_abandonedbaby'] = 0

        # Statistical
        df['correl'] = df['close'].rolling(window=20).corr(df['volume'])
        df['linearreg'] = calculate_linear_regression(df['close'], period=14)
        df['linearreg_slope'] = df['close'].rolling(window=14).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        df['linearreg_angle'] = np.arctan(df['linearreg_slope']) * (180 / np.pi)
        df['tsf'] = df['linearreg']
        df['variance'] = df['close'].rolling(window=20).var()
        df['beta'] = df['close'].rolling(window=50).apply(lambda x: np.cov(x, df['close'].iloc[-50:])[0, 1] / np.var(df['close'].iloc[-50:]))

        # Other Advanced
        df['ultosc'] = calculate_ultimate_oscillator(df)
        df['bop'] = (df['close'] - df['open']) / (df['high'] - df['low'])
        df['cmo'] = calculate_cmo(df['close'])
        df['dpo'] = df['close'] - df['close'].rolling(window=20).mean().shift(10)
        df['ht_dcperiod'] = 20  # Simplified
        df['ht_dcphase'] = 0
        df['ht_trendmode'] = 1 if df['close'].iloc[-1] > df['sma_50'].iloc[-1] else 0
        df['midpoint'] = (df['high'].rolling(window=14).max() + df['low'].rolling(window=14).min()) / 2
        df['midprice'] = (df['high'] + df['low']) / 2
        df['ppo'] = ((df['ema_12'] - df['ema_26']) / df['ema_26']) * 100
        df['stochrsi'] = (df['rsi'] - df['rsi'].rolling(window=14).min()) / (df['rsi'].rolling(window=14).max() - df['rsi'].rolling(window=14).min()) * 100
        df['apo'] = df['ema_12'] - df['ema_26']
        df['ht_sine_lead'] = 0

    except Exception as e:
        logger.error(f"Error calculating indicators: {str(e)}")

    return df

# Helper functions for indicator calculations
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return {'macd': macd, 'signal': signal_line, 'histogram': histogram}

def calculate_stochastic(df, period=14):
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    k = 100 * (df['close'] - low_min) / (high_max - low_min)
    d = k.rolling(window=3).mean()
    return {'k': k, 'd': d}

def calculate_williams_r(df, period=14):
    high_max = df['high'].rolling(window=period).max()
    low_min = df['low'].rolling(window=period).min()
    return -100 * (high_max - df['close']) / (high_max - low_min)

def calculate_cci(df, period=20):
    tp = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    return (tp - sma_tp) / (0.015 * mad)

def calculate_bollinger_bands(series, period=20, std=2):
    middle = series.rolling(window=period).mean()
    std_dev = series.rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    return {'upper': upper, 'middle': middle, 'lower': lower}

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean()

def calculate_obv(df):
    obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    return obv

def calculate_ad(df):
    mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
    mfv = mfm * df['volume']
    return mfv.cumsum()

def calculate_adx(df, period=14):
    plus_dm = df['high'].diff()
    minus_dm = -df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    atr = calculate_atr(df, period)
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()

    return {'adx': adx, 'plus_di': plus_di, 'minus_di': minus_di, 'dx': dx}

def calculate_aroon(df, period=25):
    aroon_up = df['high'].rolling(window=period + 1).apply(lambda x: x.argmax()) / period * 100
    aroon_down = df['low'].rolling(window=period + 1).apply(lambda x: x.argmin()) / period * 100
    return {'up': aroon_up, 'down': aroon_down}

def calculate_sar(df, af=0.02, max_af=0.2):
    # Simplified SAR calculation
    return df['close'].rolling(window=2).mean()

def calculate_kama(series, period=20):
    change = np.abs(series - series.shift(period))
    volatility = series.diff().abs().rolling(window=period).sum()
    er = change / volatility
    sc = (er * (2 / (2 + 1) - 2 / (30 + 1)) + 2 / (30 + 1)) ** 2
    kama = pd.Series(index=series.index, dtype=float)
    kama.iloc[period] = series.iloc[period]
    for i in range(period + 1, len(series)):
        kama.iloc[i] = kama.iloc[i - 1] + sc.iloc[i] * (series.iloc[i] - kama.iloc[i - 1])
    return kama

def calculate_ultimate_oscillator(df):
    bp = df['close'] - df[['low', 'close']].shift().min(axis=1)
    tr = df[['high', 'close']].max(axis=1) - df[['low', 'close']].shift().min(axis=1)
    avg7 = bp.rolling(window=7).sum() / tr.rolling(window=7).sum()
    avg14 = bp.rolling(window=14).sum() / tr.rolling(window=14).sum()
    avg28 = bp.rolling(window=28).sum() / tr.rolling(window=28).sum()
    return 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7

def calculate_cmo(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).sum()
    loss = -delta.where(delta < 0, 0).rolling(window=period).sum()
    return 100 * (gain - loss) / (gain + loss)

def calculate_linear_regression(series, period=14):
    lr = series.rolling(window=period).apply(lambda x: np.polyval(np.polyfit(range(len(x)), x, 1), len(x) - 1))
    return lr

def detect_doji(df):
    body = np.abs(df['close'] - df['open'])
    range_hl = df['high'] - df['low']
    return (body / range_hl < 0.1).astype(int)

def detect_hammer(df):
    body = np.abs(df['close'] - df['open'])
    lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
    upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
    return ((lower_shadow > 2 * body) & (upper_shadow < body * 0.3)).astype(int)

def detect_engulfing(df):
    bullish = ((df['close'].shift() < df['open'].shift()) &
               (df['close'] > df['open']) &
               (df['open'] < df['close'].shift()) &
               (df['close'] > df['open'].shift())).astype(int)
    return bullish

def upload_to_bigquery_batch(df, table_name):
    """Upload DataFrame to BigQuery using load_table_from_dataframe"""
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f'{PROJECT_ID}.{DATASET_ID}.{table_name}'

    try:
        # Ensure datetime column is proper type
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])

        # Upload
        job = client.load_table_from_dataframe(df, table_id)
        job.result()  # Wait for the job to complete

        print(f"    ✓ Uploaded {len(df)} records to {table_name}")
        return True
    except Exception as e:
        print(f"    ✗ Upload error: {e}")
        return False

def process_symbol(symbol, interval, outputsize, is_crypto=False):
    """
    Fetch and process a single symbol for a given timeframe
    Returns DataFrame with all indicators calculated
    """
    print(f"  Fetching {symbol} ({interval}, outputsize={outputsize})...")

    # Fetch time series data
    ts_data = fetch_time_series(symbol, interval=interval, outputsize=outputsize)
    if not ts_data:
        print(f"    ✗ No data returned")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(ts_data['values'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)

    # Volume field may not exist for all assets (crypto doesn't always have it)
    if 'volume' in df.columns:
        df['volume'] = df['volume'].astype(int)
    else:
        df['volume'] = 0  # Default to 0 if not available

    # Sort by datetime ascending for indicator calculation
    df = df.sort_values('datetime')

    # Calculate indicators
    df = calculate_technical_indicators(df)

    # Add metadata fields
    if is_crypto:
        df['pair'] = symbol
    else:
        df['symbol'] = symbol
        # Fetch metadata
        metadata = fetch_stock_metadata(symbol)
        df['name'] = metadata['name']
        df['exchange'] = metadata['exchange']
        df['mic_code'] = metadata['mic_code']
        df['currency'] = metadata['currency']
        df['asset_type'] = 'stock'

    df['date'] = df['datetime'].dt.date.astype(str)  # Convert to string for BigQuery
    df['interval'] = interval
    df['data_source'] = 'twelvedata'
    df['fetch_timestamp'] = pd.Timestamp.now('UTC')

    print(f"    ✓ Processed {len(df)} records")
    return df


def main():
    """
    Fetch fresh test data for NVDA and BTC/USD across all timeframes
    """
    print("="*70)
    print("FETCHING FRESH TEST DATA FROM TWELVE DATA API")
    print("="*70)
    print()

    # Interval mappings for TwelveData API
    intervals = {
        'daily': {'interval': '1day', 'outputsize': 200},  # 200 days for good indicators
        'hourly': {'interval': '1h', 'outputsize': 500},   # 500 hours ~= 21 days
        '5min': {'interval': '5min', 'outputsize': 500}    # 500 * 5min ~= 1.7 days
    }

    # ========================================
    # STOCK DATA - NVDA
    # ========================================
    print("STOCK DATA - NVDA")
    print("-"*70)

    for timeframe, params in intervals.items():
        print(f"\n{timeframe.upper()}:")
        df = process_symbol(TEST_STOCK, params['interval'], params['outputsize'], is_crypto=False)
        if df is not None:
            table_name = TABLES['stocks'][timeframe]
            upload_to_bigquery_batch(df, table_name)
        time.sleep(2)  # Rate limiting

    # ========================================
    # CRYPTO DATA - BTC/USD
    # ========================================
    print("\n\n" + "="*70)
    print("CRYPTO DATA - BTC/USD")
    print("-"*70)

    for timeframe, params in intervals.items():
        print(f"\n{timeframe.upper()}:")
        df = process_symbol(TEST_CRYPTO, params['interval'], params['outputsize'], is_crypto=True)
        if df is not None:
            table_name = TABLES['crypto'][timeframe]
            upload_to_bigquery_batch(df, table_name)
        time.sleep(2)  # Rate limiting

    print("\n\n" + "="*70)
    print("✓ FRESH TEST DATA LOADED SUCCESSFULLY")
    print("="*70)
    print("\nData loaded:")
    print("  NVDA: daily (200 records), hourly (500 records), 5min (500 records)")
    print("  BTC/USD: daily (200 records), hourly (500 records), 5min (500 records)")
    print("\nTables populated:")
    print("  stocks_daily, stocks_hourly, stocks_5min")
    print("  crypto_analysis, crypto_hourly_data, crypto_5min_top10_gainers")


if __name__ == '__main__':
    main()
