#!/usr/bin/env python3
"""
Complete Backfill Script for stocks_daily_clean
Populates all 97 fields for all 106 stocks using TwelveData API and calculated indicators
"""

import os
import sys
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_NAME = 'stocks_daily_clean'
TWELVEDATA_API_KEY = '78f25d759e8a4e78b2c859919822d966'  # From your existing code
BASE_URL = 'https://api.twelvedata.com'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

def get_stock_symbols():
    """Get list of all stock symbols from the table"""
    query = f"""
    SELECT DISTINCT symbol
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}`
    ORDER BY symbol
    """
    results = client.query(query).result()
    return [row.symbol for row in results]

def fetch_historical_data(symbol, outputsize=500):
    """Fetch historical daily data from TwelveData API"""
    url = f"{BASE_URL}/time_series"
    params = {
        'symbol': symbol,
        'interval': '1day',
        'outputsize': outputsize,
        'apikey': TWELVEDATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' in data:
            df = pd.DataFrame(data['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)

            # Convert numeric columns
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df
        else:
            print(f"  No data for {symbol}: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return None

def fetch_fundamental_data(symbol):
    """Fetch fundamental data (name, sector, industry) from TwelveData"""
    url = f"{BASE_URL}/stocks"
    params = {
        'symbol': symbol,
        'apikey': TWELVEDATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            stock_info = data['data'][0]
            return {
                'name': stock_info.get('name', ''),
                'exchange': stock_info.get('exchange', ''),
                'mic_code': stock_info.get('mic_code', ''),
                'country': stock_info.get('country', ''),
                'currency': stock_info.get('currency', 'USD'),
                'type': stock_info.get('type', 'stock')
            }
        return {}
    except Exception as e:
        print(f"  Error fetching fundamentals for {symbol}: {e}")
        return {}

def fetch_profile_data(symbol):
    """Fetch company profile (sector, industry) from TwelveData"""
    url = f"{BASE_URL}/profile"
    params = {
        'symbol': symbol,
        'apikey': TWELVEDATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'sector' in data or 'industry' in data:
            return {
                'sector': data.get('sector', ''),
                'industry': data.get('industry', ''),
                'name': data.get('name', ''),
                'asset_type': data.get('type', 'Common Stock')
            }
        return {}
    except Exception as e:
        print(f"  Error fetching profile for {symbol}: {e}")
        return {}

def calculate_sma(series, period):
    """Simple Moving Average"""
    return series.rolling(window=period, min_periods=period).mean()

def calculate_ema(series, period):
    """Exponential Moving Average"""
    return series.ewm(span=period, adjust=False, min_periods=period).mean()

def calculate_rsi(series, period=14):
    """Relative Strength Index"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series, fast=12, slow=26, signal=9):
    """MACD, Signal, and Histogram"""
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd = ema_fast - ema_slow
    macd_signal = calculate_ema(macd, signal)
    macd_histogram = macd - macd_signal
    return macd, macd_signal, macd_histogram

def calculate_bollinger_bands(series, period=20, std_dev=2):
    """Bollinger Bands"""
    middle = calculate_sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    width = (upper - lower) / middle * 100
    return upper, middle, lower, width

def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    """Stochastic Oscillator"""
    lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
    highest_high = high.rolling(window=k_period, min_periods=k_period).max()
    stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    stoch_d = stoch_k.rolling(window=d_period, min_periods=d_period).mean()
    return stoch_k, stoch_d

def calculate_atr(high, low, close, period=14):
    """Average True Range"""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=period).mean()

def calculate_adx(high, low, close, period=14):
    """Average Directional Index"""
    prev_high = high.shift(1)
    prev_low = low.shift(1)
    prev_close = close.shift(1)

    plus_dm = high - prev_high
    minus_dm = prev_low - low

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period, min_periods=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period, min_periods=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period, min_periods=period).mean() / atr)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period, min_periods=period).mean()

    return adx, plus_di, minus_di

def calculate_cci(high, low, close, period=20):
    """Commodity Channel Index"""
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=period, min_periods=period).mean()
    mad = tp.rolling(window=period, min_periods=period).apply(lambda x: np.abs(x - x.mean()).mean())
    return (tp - sma_tp) / (0.015 * mad)

def calculate_williams_r(high, low, close, period=14):
    """Williams %R"""
    highest_high = high.rolling(window=period, min_periods=period).max()
    lowest_low = low.rolling(window=period, min_periods=period).min()
    return -100 * (highest_high - close) / (highest_high - lowest_low)

def calculate_obv(close, volume):
    """On-Balance Volume"""
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]

    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]

    return obv

def calculate_mfi(high, low, close, volume, period=14):
    """Money Flow Index"""
    tp = (high + low + close) / 3
    mf = tp * volume

    positive_mf = mf.where(tp > tp.shift(1), 0).rolling(window=period, min_periods=period).sum()
    negative_mf = mf.where(tp < tp.shift(1), 0).rolling(window=period, min_periods=period).sum()

    mfr = positive_mf / negative_mf
    return 100 - (100 / (1 + mfr))

def calculate_cmf(high, low, close, volume, period=20):
    """Chaikin Money Flow"""
    mfm = ((close - low) - (high - close)) / (high - low)
    mfm = mfm.fillna(0)
    mfv = mfm * volume

    return mfv.rolling(window=period, min_periods=period).sum() / volume.rolling(window=period, min_periods=period).sum()

def calculate_ichimoku(high, low, close):
    """Ichimoku Cloud indicators"""
    # Tenkan-sen (Conversion Line) - 9 periods
    tenkan = (high.rolling(window=9, min_periods=9).max() + low.rolling(window=9, min_periods=9).min()) / 2

    # Kijun-sen (Base Line) - 26 periods
    kijun = (high.rolling(window=26, min_periods=26).max() + low.rolling(window=26, min_periods=26).min()) / 2

    # Senkou Span A (Leading Span A)
    senkou_a = ((tenkan + kijun) / 2).shift(26)

    # Senkou Span B (Leading Span B) - 52 periods
    senkou_b = ((high.rolling(window=52, min_periods=52).max() + low.rolling(window=52, min_periods=52).min()) / 2).shift(26)

    # Chikou Span (Lagging Span)
    chikou = close.shift(-26)

    return tenkan, kijun, senkou_a, senkou_b, chikou

def calculate_vwap(high, low, close, volume):
    """Volume Weighted Average Price (daily reset assumed)"""
    tp = (high + low + close) / 3
    return (tp * volume).cumsum() / volume.cumsum()

def calculate_kama(close, period=10, fast=2, slow=30):
    """Kaufman Adaptive Moving Average"""
    change = abs(close - close.shift(period))
    volatility = abs(close.diff()).rolling(window=period, min_periods=period).sum()

    er = change / volatility
    fast_sc = 2 / (fast + 1)
    slow_sc = 2 / (slow + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2

    kama = pd.Series(index=close.index, dtype=float)
    kama.iloc[period-1] = close.iloc[period-1]

    for i in range(period, len(close)):
        kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (close.iloc[i] - kama.iloc[i-1])

    return kama

def calculate_trix(close, period=15):
    """Triple Exponential Average"""
    ema1 = calculate_ema(close, period)
    ema2 = calculate_ema(ema1, period)
    ema3 = calculate_ema(ema2, period)
    return 100 * (ema3 - ema3.shift(1)) / ema3.shift(1)

def calculate_roc(close, period=12):
    """Rate of Change"""
    return 100 * (close - close.shift(period)) / close.shift(period)

def calculate_pvo(volume, fast=12, slow=26, signal=9):
    """Percentage Volume Oscillator"""
    ema_fast = calculate_ema(volume.astype(float), fast)
    ema_slow = calculate_ema(volume.astype(float), slow)
    return 100 * (ema_fast - ema_slow) / ema_slow

def calculate_ppo(close, fast=12, slow=26):
    """Percentage Price Oscillator"""
    ema_fast = calculate_ema(close, fast)
    ema_slow = calculate_ema(close, slow)
    return 100 * (ema_fast - ema_slow) / ema_slow

def calculate_ultimate_oscillator(high, low, close, period1=7, period2=14, period3=28):
    """Ultimate Oscillator"""
    prev_close = close.shift(1)
    bp = close - pd.concat([low, prev_close], axis=1).min(axis=1)
    tr = pd.concat([high, prev_close], axis=1).max(axis=1) - pd.concat([low, prev_close], axis=1).min(axis=1)

    avg1 = bp.rolling(window=period1, min_periods=period1).sum() / tr.rolling(window=period1, min_periods=period1).sum()
    avg2 = bp.rolling(window=period2, min_periods=period2).sum() / tr.rolling(window=period2, min_periods=period2).sum()
    avg3 = bp.rolling(window=period3, min_periods=period3).sum() / tr.rolling(window=period3, min_periods=period3).sum()

    return 100 * (4 * avg1 + 2 * avg2 + avg3) / 7

def calculate_awesome_oscillator(high, low):
    """Awesome Oscillator"""
    midpoint = (high + low) / 2
    return calculate_sma(midpoint, 5) - calculate_sma(midpoint, 34)

def calculate_all_indicators(df):
    """Calculate all 97 fields for a dataframe"""

    # Basic price data (fields 1-15)
    df['previous_close'] = df['close'].shift(1)
    df['change'] = df['close'] - df['previous_close']
    df['percent_change'] = 100 * df['change'] / df['previous_close']
    df['high_low'] = df['high'] - df['low']
    df['pct_high_low'] = 100 * df['high_low'] / df['low']
    df['week_52_high'] = df['high'].rolling(window=252, min_periods=50).max()
    df['week_52_low'] = df['low'].rolling(window=252, min_periods=50).min()
    df['average_volume'] = df['volume'].rolling(window=20, min_periods=10).mean().astype(int)

    # RSI (field 16)
    df['rsi'] = calculate_rsi(df['close'], 14)

    # MACD (fields 17-19)
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['close'])

    # Stochastic (fields 20-21)
    df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])

    # CCI (field 22)
    df['cci'] = calculate_cci(df['high'], df['low'], df['close'])

    # Williams %R (field 23)
    df['williams_r'] = calculate_williams_r(df['high'], df['low'], df['close'])

    # Momentum (field 24)
    df['momentum'] = df['close'] - df['close'].shift(10)

    # SMAs (fields 25-27)
    df['sma_20'] = calculate_sma(df['close'], 20)
    df['sma_50'] = calculate_sma(df['close'], 50)
    df['sma_200'] = calculate_sma(df['close'], 200)

    # EMAs (fields 28-32)
    df['ema_12'] = calculate_ema(df['close'], 12)
    df['ema_20'] = calculate_ema(df['close'], 20)
    df['ema_26'] = calculate_ema(df['close'], 26)
    df['ema_50'] = calculate_ema(df['close'], 50)
    df['ema_200'] = calculate_ema(df['close'], 200)

    # KAMA (field 33)
    df['kama'] = calculate_kama(df['close'])

    # Bollinger Bands (fields 34-37)
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'], df['bb_width'] = calculate_bollinger_bands(df['close'])

    # ADX (fields 38-40)
    df['adx'], df['plus_di'], df['minus_di'] = calculate_adx(df['high'], df['low'], df['close'])

    # ATR (field 41)
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'])

    # TRIX (field 42)
    df['trix'] = calculate_trix(df['close'])

    # ROC (field 43)
    df['roc'] = calculate_roc(df['close'])

    # OBV (field 44)
    df['obv'] = calculate_obv(df['close'], df['volume'])

    # PVO (field 45)
    df['pvo'] = calculate_pvo(df['volume'])

    # PPO (field 46)
    df['ppo'] = calculate_ppo(df['close'])

    # Ultimate Oscillator (field 47)
    df['ultimate_osc'] = calculate_ultimate_oscillator(df['high'], df['low'], df['close'])

    # Awesome Oscillator (field 48)
    df['awesome_osc'] = calculate_awesome_oscillator(df['high'], df['low'])

    # Log Return (field 49)
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))

    # Returns (fields 50-51)
    df['return_2w'] = 100 * (df['close'] - df['close'].shift(10)) / df['close'].shift(10)
    df['return_4w'] = 100 * (df['close'] - df['close'].shift(20)) / df['close'].shift(20)

    # Close vs SMA percentages (fields 52-54)
    df['close_vs_sma20_pct'] = 100 * (df['close'] - df['sma_20']) / df['sma_20']
    df['close_vs_sma50_pct'] = 100 * (df['close'] - df['sma_50']) / df['sma_50']
    df['close_vs_sma200_pct'] = 100 * (df['close'] - df['sma_200']) / df['sma_200']

    # RSI derived (fields 55-58)
    df['rsi_slope'] = df['rsi'] - df['rsi'].shift(5)
    df['rsi_zscore'] = (df['rsi'] - df['rsi'].rolling(window=20, min_periods=10).mean()) / df['rsi'].rolling(window=20, min_periods=10).std()
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)

    # MACD cross (field 59)
    df['macd_cross'] = ((df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int) - \
                       ((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))).astype(int)

    # EMA slopes (fields 60-61)
    df['ema20_slope'] = df['ema_20'] - df['ema_20'].shift(5)
    df['ema50_slope'] = df['ema_50'] - df['ema_50'].shift(5)

    # ATR derived (fields 62-63)
    df['atr_zscore'] = (df['atr'] - df['atr'].rolling(window=20, min_periods=10).mean()) / df['atr'].rolling(window=20, min_periods=10).std()
    df['atr_slope'] = df['atr'] - df['atr'].shift(5)

    # Volume derived (fields 64-65)
    df['volume_zscore'] = (df['volume'] - df['volume'].rolling(window=20, min_periods=10).mean()) / df['volume'].rolling(window=20, min_periods=10).std()
    avg_vol = df['volume'].rolling(window=20, min_periods=10).mean()
    df['volume_ratio'] = df['volume'] / avg_vol
    df['volume_ratio'] = df['volume_ratio'].replace([np.inf, -np.inf], np.nan)

    # Pivot points (fields 66-69)
    df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))).astype(int)
    df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))).astype(int)

    # Find recent pivot high/low
    recent_pivot_high = df['high'].where(df['pivot_high_flag'] == 1).ffill()
    recent_pivot_low = df['low'].where(df['pivot_low_flag'] == 1).ffill()
    df['dist_to_pivot_high'] = 100 * (df['close'] - recent_pivot_high) / recent_pivot_high
    df['dist_to_pivot_low'] = 100 * (df['close'] - recent_pivot_low) / recent_pivot_low

    # Trend regime (fields 70-72)
    df['trend_regime'] = 0
    df.loc[(df['close'] > df['sma_50']) & (df['sma_50'] > df['sma_200']), 'trend_regime'] = 1  # Uptrend
    df.loc[(df['close'] < df['sma_50']) & (df['sma_50'] < df['sma_200']), 'trend_regime'] = -1  # Downtrend

    df['vol_regime'] = 0
    df.loc[df['volume_zscore'] > 1, 'vol_regime'] = 1  # High volume
    df.loc[df['volume_zscore'] < -1, 'vol_regime'] = -1  # Low volume

    # Regime confidence based on ADX
    df['regime_confidence'] = df['adx'] / 100

    # MFI (field 86)
    df['mfi'] = calculate_mfi(df['high'], df['low'], df['close'], df['volume'])

    # CMF (field 87)
    df['cmf'] = calculate_cmf(df['high'], df['low'], df['close'], df['volume'])

    # Ichimoku (fields 88-92)
    df['ichimoku_tenkan'], df['ichimoku_kijun'], df['ichimoku_senkou_a'], df['ichimoku_senkou_b'], df['ichimoku_chikou'] = \
        calculate_ichimoku(df['high'], df['low'], df['close'])

    # VWAP (fields 93-94)
    df['vwap_daily'] = calculate_vwap(df['high'], df['low'], df['close'], df['volume'])
    # Weekly VWAP - reset every 5 days
    df['week_num'] = (df.index // 5)
    df['vwap_weekly'] = df.groupby('week_num').apply(
        lambda x: calculate_vwap(x['high'], x['low'], x['close'], x['volume'])
    ).reset_index(level=0, drop=True)
    df = df.drop('week_num', axis=1)

    # Volume Profile (fields 95-97) - simplified POC, VAH, VAL
    df['volume_profile_poc'] = df['close'].rolling(window=20, min_periods=10).apply(
        lambda x: x.mode()[0] if len(x.mode()) > 0 else x.median()
    )
    df['volume_profile_vah'] = df['high'].rolling(window=20, min_periods=10).quantile(0.7)
    df['volume_profile_val'] = df['low'].rolling(window=20, min_periods=10).quantile(0.3)

    return df

def update_bigquery_table(symbol, df, fundamental_data, profile_data):
    """Update BigQuery table with calculated data"""

    # Add fundamental data
    df['symbol'] = symbol
    df['name'] = profile_data.get('name', '') or fundamental_data.get('name', '')
    df['sector'] = profile_data.get('sector', '')
    df['industry'] = profile_data.get('industry', '')
    df['asset_type'] = profile_data.get('asset_type', 'Common Stock')
    df['exchange'] = fundamental_data.get('exchange', '')
    df['mic_code'] = fundamental_data.get('mic_code', '')
    df['country'] = fundamental_data.get('country', 'United States')
    df['currency'] = fundamental_data.get('currency', 'USD')
    df['type'] = fundamental_data.get('type', 'stock')
    df['data_source'] = 'twelvedata'
    df['timestamp'] = df['datetime'].astype(int) // 10**9
    df['created_at'] = datetime.utcnow()
    df['updated_at'] = datetime.utcnow()

    # Replace inf/-inf with None
    df = df.replace([np.inf, -np.inf], np.nan)

    # Delete existing data for this symbol
    delete_query = f"""
    DELETE FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}`
    WHERE symbol = '{symbol}'
    """
    client.query(delete_query).result()

    # Prepare data for BigQuery
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"

    # Upload to BigQuery
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()

    return len(df)

def process_symbol(symbol, index, total):
    """Process a single symbol"""
    print(f"\n[{index}/{total}] Processing {symbol}...")

    # Fetch historical data (500 days for SMA_200 and other long-period indicators)
    print(f"  Fetching historical data...")
    df = fetch_historical_data(symbol, outputsize=500)
    if df is None or len(df) < 50:
        print(f"  Skipping {symbol} - insufficient data")
        return False

    print(f"  Got {len(df)} days of data")

    # Fetch fundamental data
    print(f"  Fetching fundamental data...")
    fundamental_data = fetch_fundamental_data(symbol)
    time.sleep(0.5)  # Rate limiting

    # Fetch profile data (sector, industry)
    print(f"  Fetching profile data...")
    profile_data = fetch_profile_data(symbol)
    time.sleep(0.5)  # Rate limiting

    print(f"  Sector: {profile_data.get('sector', 'N/A')}, Industry: {profile_data.get('industry', 'N/A')}")

    # Calculate all indicators
    print(f"  Calculating indicators...")
    df = calculate_all_indicators(df)

    # Update BigQuery
    print(f"  Updating BigQuery...")
    rows = update_bigquery_table(symbol, df, fundamental_data, profile_data)

    print(f"  ✓ Updated {rows} rows for {symbol}")
    return True

def main():
    print("=" * 60)
    print("Complete Backfill Script for stocks_daily_clean")
    print("Populating all 97 fields for all 106 stocks")
    print("=" * 60)

    # Get all symbols
    symbols = get_stock_symbols()
    print(f"\nFound {len(symbols)} symbols to process")

    success_count = 0
    fail_count = 0

    for i, symbol in enumerate(symbols, 1):
        try:
            if process_symbol(symbol, i, len(symbols)):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  ERROR processing {symbol}: {e}")
            fail_count += 1

        # Rate limiting between symbols
        time.sleep(1)

    print("\n" + "=" * 60)
    print(f"Backfill Complete!")
    print(f"  Success: {success_count}")
    print(f"  Failed: {fail_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
