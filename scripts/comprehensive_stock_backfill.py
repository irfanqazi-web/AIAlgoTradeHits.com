#!/usr/bin/env python3
"""
Comprehensive Stock Data Backfill Script
Fixes all data coverage issues for stocks_daily_clean table
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TABLE_NAME = 'stocks_daily_clean'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# ============================================================
# TECHNICAL INDICATORS CALCULATIONS
# ============================================================

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
    rsi = 100 - (100 / (1 + rs))
    return rsi.replace([np.inf, -np.inf], np.nan)

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
    width = ((upper - lower) / middle * 100).replace([np.inf, -np.inf], np.nan)
    return upper, middle, lower, width

def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    """Stochastic Oscillator"""
    lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
    highest_high = high.rolling(window=k_period, min_periods=k_period).max()
    denom = highest_high - lowest_low
    stoch_k = (100 * (close - lowest_low) / denom).replace([np.inf, -np.inf], np.nan)
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
    plus_di = (100 * (plus_dm.rolling(window=period, min_periods=period).mean() / atr)).replace([np.inf, -np.inf], np.nan)
    minus_di = (100 * (minus_dm.rolling(window=period, min_periods=period).mean() / atr)).replace([np.inf, -np.inf], np.nan)

    dx = (100 * abs(plus_di - minus_di) / (plus_di + minus_di)).replace([np.inf, -np.inf], np.nan)
    adx = dx.rolling(window=period, min_periods=period).mean()

    return adx, plus_di, minus_di

def calculate_cci(high, low, close, period=20):
    """Commodity Channel Index"""
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=period, min_periods=period).mean()
    mad = tp.rolling(window=period, min_periods=period).apply(lambda x: np.abs(x - x.mean()).mean())
    return ((tp - sma_tp) / (0.015 * mad)).replace([np.inf, -np.inf], np.nan)

def calculate_williams_r(high, low, close, period=14):
    """Williams %R"""
    highest_high = high.rolling(window=period, min_periods=period).max()
    lowest_low = low.rolling(window=period, min_periods=period).min()
    return (-100 * (highest_high - close) / (highest_high - lowest_low)).replace([np.inf, -np.inf], np.nan)

def calculate_obv(close, volume):
    """On-Balance Volume"""
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0] if len(close) > 0 else 0

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
    return (100 - (100 / (1 + mfr))).replace([np.inf, -np.inf], np.nan)

def calculate_cmf(high, low, close, volume, period=20):
    """Chaikin Money Flow"""
    denom = high - low
    mfm = ((close - low) - (high - close)) / denom
    mfm = mfm.replace([np.inf, -np.inf], 0).fillna(0)
    mfv = mfm * volume

    vol_sum = volume.rolling(window=period, min_periods=period).sum()
    return (mfv.rolling(window=period, min_periods=period).sum() / vol_sum).replace([np.inf, -np.inf], np.nan)

def calculate_ichimoku(high, low, close):
    """Ichimoku Cloud indicators"""
    tenkan = (high.rolling(window=9, min_periods=9).max() + low.rolling(window=9, min_periods=9).min()) / 2
    kijun = (high.rolling(window=26, min_periods=26).max() + low.rolling(window=26, min_periods=26).min()) / 2
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = ((high.rolling(window=52, min_periods=52).max() + low.rolling(window=52, min_periods=52).min()) / 2).shift(26)
    chikou = close.shift(-26)
    return tenkan, kijun, senkou_a, senkou_b, chikou

def calculate_vwap(high, low, close, volume):
    """Volume Weighted Average Price"""
    tp = (high + low + close) / 3
    vol_cum = volume.cumsum()
    return ((tp * volume).cumsum() / vol_cum).replace([np.inf, -np.inf], np.nan)

def calculate_kama(close, period=10, fast=2, slow=30):
    """Kaufman Adaptive Moving Average"""
    change = abs(close - close.shift(period))
    volatility = abs(close.diff()).rolling(window=period, min_periods=period).sum()

    er = (change / volatility).replace([np.inf, -np.inf], 0).fillna(0)
    fast_sc = 2 / (fast + 1)
    slow_sc = 2 / (slow + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2

    kama = pd.Series(index=close.index, dtype=float)
    if len(close) > period:
        kama.iloc[period-1] = close.iloc[period-1]
        for i in range(period, len(close)):
            kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (close.iloc[i] - kama.iloc[i-1])

    return kama

def calculate_trix(close, period=15):
    """Triple Exponential Average"""
    ema1 = calculate_ema(close, period)
    ema2 = calculate_ema(ema1, period)
    ema3 = calculate_ema(ema2, period)
    return (100 * (ema3 - ema3.shift(1)) / ema3.shift(1)).replace([np.inf, -np.inf], np.nan)

def calculate_roc(close, period=12):
    """Rate of Change"""
    return (100 * (close - close.shift(period)) / close.shift(period)).replace([np.inf, -np.inf], np.nan)

def calculate_pvo(volume, fast=12, slow=26):
    """Percentage Volume Oscillator"""
    ema_fast = calculate_ema(volume.astype(float), fast)
    ema_slow = calculate_ema(volume.astype(float), slow)
    return (100 * (ema_fast - ema_slow) / ema_slow).replace([np.inf, -np.inf], np.nan)

def calculate_ppo(close, fast=12, slow=26):
    """Percentage Price Oscillator"""
    ema_fast = calculate_ema(close, fast)
    ema_slow = calculate_ema(close, slow)
    return (100 * (ema_fast - ema_slow) / ema_slow).replace([np.inf, -np.inf], np.nan)

def calculate_ultimate_oscillator(high, low, close, period1=7, period2=14, period3=28):
    """Ultimate Oscillator"""
    prev_close = close.shift(1)
    bp = close - pd.concat([low, prev_close], axis=1).min(axis=1)
    tr = pd.concat([high, prev_close], axis=1).max(axis=1) - pd.concat([low, prev_close], axis=1).min(axis=1)

    tr_sum1 = tr.rolling(window=period1, min_periods=period1).sum()
    tr_sum2 = tr.rolling(window=period2, min_periods=period2).sum()
    tr_sum3 = tr.rolling(window=period3, min_periods=period3).sum()

    avg1 = bp.rolling(window=period1, min_periods=period1).sum() / tr_sum1
    avg2 = bp.rolling(window=period2, min_periods=period2).sum() / tr_sum2
    avg3 = bp.rolling(window=period3, min_periods=period3).sum() / tr_sum3

    return (100 * (4 * avg1 + 2 * avg2 + avg3) / 7).replace([np.inf, -np.inf], np.nan)

def calculate_awesome_oscillator(high, low):
    """Awesome Oscillator"""
    midpoint = (high + low) / 2
    return calculate_sma(midpoint, 5) - calculate_sma(midpoint, 34)


def calculate_all_indicators(df):
    """Calculate all technical indicators for a dataframe"""

    # Basic price data
    df['previous_close'] = df['close'].shift(1)
    df['change'] = df['close'] - df['previous_close']
    df['percent_change'] = (100 * df['change'] / df['previous_close']).replace([np.inf, -np.inf], np.nan)
    df['high_low'] = df['high'] - df['low']
    df['pct_high_low'] = (100 * df['high_low'] / df['low']).replace([np.inf, -np.inf], np.nan)
    df['week_52_high'] = df['high'].rolling(window=252, min_periods=50).max()
    df['week_52_low'] = df['low'].rolling(window=252, min_periods=50).min()
    df['average_volume'] = df['volume'].rolling(window=20, min_periods=5).mean()

    # RSI
    df['rsi'] = calculate_rsi(df['close'], 14)

    # MACD
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['close'])

    # Stochastic
    df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])

    # CCI
    df['cci'] = calculate_cci(df['high'], df['low'], df['close'])

    # Williams %R
    df['williams_r'] = calculate_williams_r(df['high'], df['low'], df['close'])

    # Momentum
    df['momentum'] = df['close'] - df['close'].shift(10)

    # SMAs
    df['sma_20'] = calculate_sma(df['close'], 20)
    df['sma_50'] = calculate_sma(df['close'], 50)
    df['sma_200'] = calculate_sma(df['close'], 200)

    # EMAs
    df['ema_12'] = calculate_ema(df['close'], 12)
    df['ema_20'] = calculate_ema(df['close'], 20)
    df['ema_26'] = calculate_ema(df['close'], 26)
    df['ema_50'] = calculate_ema(df['close'], 50)
    df['ema_200'] = calculate_ema(df['close'], 200)

    # KAMA
    df['kama'] = calculate_kama(df['close'])

    # Bollinger Bands
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'], df['bb_width'] = calculate_bollinger_bands(df['close'])

    # ADX
    df['adx'], df['plus_di'], df['minus_di'] = calculate_adx(df['high'], df['low'], df['close'])

    # ATR
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'])

    # TRIX
    df['trix'] = calculate_trix(df['close'])

    # ROC
    df['roc'] = calculate_roc(df['close'])

    # OBV
    df['obv'] = calculate_obv(df['close'], df['volume'])

    # PVO
    df['pvo'] = calculate_pvo(df['volume'])

    # PPO
    df['ppo'] = calculate_ppo(df['close'])

    # Ultimate Oscillator
    df['ultimate_osc'] = calculate_ultimate_oscillator(df['high'], df['low'], df['close'])

    # Awesome Oscillator
    df['awesome_osc'] = calculate_awesome_oscillator(df['high'], df['low'])

    # Log Return
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['log_return'] = df['log_return'].replace([np.inf, -np.inf], np.nan)

    # Returns
    df['return_2w'] = (100 * (df['close'] - df['close'].shift(10)) / df['close'].shift(10)).replace([np.inf, -np.inf], np.nan)
    df['return_4w'] = (100 * (df['close'] - df['close'].shift(20)) / df['close'].shift(20)).replace([np.inf, -np.inf], np.nan)

    # Close vs SMA percentages
    df['close_vs_sma20_pct'] = (100 * (df['close'] - df['sma_20']) / df['sma_20']).replace([np.inf, -np.inf], np.nan)
    df['close_vs_sma50_pct'] = (100 * (df['close'] - df['sma_50']) / df['sma_50']).replace([np.inf, -np.inf], np.nan)
    df['close_vs_sma200_pct'] = (100 * (df['close'] - df['sma_200']) / df['sma_200']).replace([np.inf, -np.inf], np.nan)

    # RSI derived
    df['rsi_slope'] = df['rsi'] - df['rsi'].shift(5)
    rsi_mean = df['rsi'].rolling(window=20, min_periods=10).mean()
    rsi_std = df['rsi'].rolling(window=20, min_periods=10).std()
    df['rsi_zscore'] = ((df['rsi'] - rsi_mean) / rsi_std).replace([np.inf, -np.inf], np.nan)
    df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi'] < 30).astype(int)

    # MACD cross
    df['macd_cross'] = ((df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int) - \
                       ((df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))).astype(int)

    # EMA slopes
    df['ema20_slope'] = df['ema_20'] - df['ema_20'].shift(5)
    df['ema50_slope'] = df['ema_50'] - df['ema_50'].shift(5)

    # ATR derived
    atr_mean = df['atr'].rolling(window=20, min_periods=10).mean()
    atr_std = df['atr'].rolling(window=20, min_periods=10).std()
    df['atr_zscore'] = ((df['atr'] - atr_mean) / atr_std).replace([np.inf, -np.inf], np.nan)
    df['atr_slope'] = df['atr'] - df['atr'].shift(5)

    # Volume derived
    vol_mean = df['volume'].rolling(window=20, min_periods=10).mean()
    vol_std = df['volume'].rolling(window=20, min_periods=10).std()
    df['volume_zscore'] = ((df['volume'] - vol_mean) / vol_std).replace([np.inf, -np.inf], np.nan)
    df['volume_ratio'] = (df['volume'] / vol_mean).replace([np.inf, -np.inf], np.nan)

    # Pivot flags
    df['pivot_high_flag'] = ((df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1).fillna(0))).astype(int)
    df['pivot_low_flag'] = ((df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1).fillna(float('inf')))).astype(int)

    # Distance to pivots
    recent_pivot_high = df['high'].where(df['pivot_high_flag'] == 1).ffill()
    recent_pivot_low = df['low'].where(df['pivot_low_flag'] == 1).ffill()
    df['dist_to_pivot_high'] = (100 * (df['close'] - recent_pivot_high) / recent_pivot_high).replace([np.inf, -np.inf], np.nan)
    df['dist_to_pivot_low'] = (100 * (df['close'] - recent_pivot_low) / recent_pivot_low).replace([np.inf, -np.inf], np.nan)

    # Trend regime
    df['trend_regime'] = 0
    df.loc[(df['close'] > df['sma_50']) & (df['sma_50'] > df['sma_200']), 'trend_regime'] = 1
    df.loc[(df['close'] < df['sma_50']) & (df['sma_50'] < df['sma_200']), 'trend_regime'] = -1

    df['vol_regime'] = 0
    df.loc[df['volume_zscore'] > 1, 'vol_regime'] = 1
    df.loc[df['volume_zscore'] < -1, 'vol_regime'] = -1

    # Regime confidence
    df['regime_confidence'] = (df['adx'] / 100).clip(0, 1)

    # MFI
    df['mfi'] = calculate_mfi(df['high'], df['low'], df['close'], df['volume'])

    # CMF
    df['cmf'] = calculate_cmf(df['high'], df['low'], df['close'], df['volume'])

    # Ichimoku
    df['ichimoku_tenkan'], df['ichimoku_kijun'], df['ichimoku_senkou_a'], df['ichimoku_senkou_b'], df['ichimoku_chikou'] = \
        calculate_ichimoku(df['high'], df['low'], df['close'])

    # VWAP
    df['vwap_daily'] = calculate_vwap(df['high'], df['low'], df['close'], df['volume'])

    # Weekly VWAP (5-day rolling)
    df['week_num'] = (df.index // 5)
    grouped = df.groupby('week_num')
    df['vwap_weekly'] = grouped.apply(
        lambda x: calculate_vwap(x['high'], x['low'], x['close'], x['volume'])
    ).reset_index(level=0, drop=True)
    df = df.drop('week_num', axis=1)

    # Volume Profile (simplified)
    df['volume_profile_poc'] = df['close'].rolling(window=20, min_periods=10).median()
    df['volume_profile_vah'] = df['high'].rolling(window=20, min_periods=10).quantile(0.7)
    df['volume_profile_val'] = df['low'].rolling(window=20, min_periods=10).quantile(0.3)

    return df


# ============================================================
# API FUNCTIONS
# ============================================================

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

            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df
        else:
            print(f"    API Error: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"    Error: {e}")
        return None


def fetch_fundamental_data(symbol):
    """Fetch fundamental data from TwelveData"""
    url = f"{BASE_URL}/stocks"
    params = {'symbol': symbol, 'apikey': TWELVEDATA_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'data' in data and len(data['data']) > 0:
            info = data['data'][0]
            return {
                'name': info.get('name', ''),
                'exchange': info.get('exchange', ''),
                'mic_code': info.get('mic_code', ''),
                'country': info.get('country', ''),
                'currency': info.get('currency', 'USD'),
                'type': info.get('type', 'stock')
            }
        return {}
    except Exception as e:
        return {}


def fetch_profile_data(symbol):
    """Fetch company profile from TwelveData"""
    url = f"{BASE_URL}/profile"
    params = {'symbol': symbol, 'apikey': TWELVEDATA_API_KEY}

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
        return {}


# ============================================================
# DATA MANAGEMENT
# ============================================================

def get_stock_coverage():
    """Get current data coverage for all symbols"""
    query = f"""
    SELECT
        symbol,
        COUNT(*) as record_count,
        MIN(DATE(datetime)) as start_date,
        MAX(DATE(datetime)) as end_date
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}`
    GROUP BY symbol
    ORDER BY symbol
    """
    results = client.query(query).result()
    return {row.symbol: {'count': row.record_count, 'start': row.start_date, 'end': row.end_date} for row in results}


def update_bigquery_table(symbol, df, fundamental_data, profile_data, mode='replace'):
    """Update BigQuery table for a symbol"""

    # Add metadata
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
    df['timestamp'] = df['datetime'].astype(np.int64) // 10**9
    df['created_at'] = datetime.utcnow()
    df['updated_at'] = datetime.utcnow()

    # Replace inf/-inf with NaN
    df = df.replace([np.inf, -np.inf], np.nan)

    if mode == 'replace':
        # Delete existing data for this symbol
        delete_query = f"DELETE FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}` WHERE symbol = '{symbol}'"
        client.query(delete_query).result()

    # Upload to BigQuery
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}"
    job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()

    return len(df)


def process_critical_symbol(symbol, index, total):
    """Process a CRITICAL symbol (only 1 record) - needs full backfill"""
    print(f"\n[{index}/{total}] CRITICAL: {symbol} - Fetching full 500-day history")

    # Fetch 500 days of historical data
    print(f"    Fetching historical data...")
    df = fetch_historical_data(symbol, outputsize=500)

    if df is None or len(df) < 10:
        print(f"    ERROR: Could not fetch data for {symbol}")
        return False

    print(f"    Got {len(df)} days of data")

    # Fetch fundamentals
    print(f"    Fetching fundamentals...")
    fundamental_data = fetch_fundamental_data(symbol)
    time.sleep(0.3)

    profile_data = fetch_profile_data(symbol)
    time.sleep(0.3)

    sector = profile_data.get('sector', 'N/A')
    industry = profile_data.get('industry', 'N/A')
    print(f"    Sector: {sector}, Industry: {industry}")

    # Calculate indicators
    print(f"    Calculating indicators...")
    df = calculate_all_indicators(df)

    # Update BigQuery
    print(f"    Updating BigQuery...")
    rows = update_bigquery_table(symbol, df, fundamental_data, profile_data, mode='replace')

    print(f"    SUCCESS: {rows} rows uploaded for {symbol}")
    return True


def process_outdated_symbol(symbol, current_end_date, index, total):
    """Process an OUTDATED symbol - needs recent data added"""
    print(f"\n[{index}/{total}] OUTDATED: {symbol} - ends {current_end_date}, fetching recent data")

    # Fetch enough data to get recent days plus calculate indicators
    # Need at least 200+ days for SMA_200
    print(f"    Fetching recent historical data...")
    df = fetch_historical_data(symbol, outputsize=500)

    if df is None or len(df) < 10:
        print(f"    ERROR: Could not fetch data for {symbol}")
        return False

    print(f"    Got {len(df)} days of data (from {df['datetime'].min().date()} to {df['datetime'].max().date()})")

    # Fetch fundamentals
    print(f"    Fetching fundamentals...")
    fundamental_data = fetch_fundamental_data(symbol)
    time.sleep(0.3)

    profile_data = fetch_profile_data(symbol)
    time.sleep(0.3)

    # Calculate indicators
    print(f"    Calculating indicators...")
    df = calculate_all_indicators(df)

    # Replace all data for this symbol
    print(f"    Updating BigQuery...")
    rows = update_bigquery_table(symbol, df, fundamental_data, profile_data, mode='replace')

    print(f"    SUCCESS: {rows} rows uploaded for {symbol}")
    return True


def main():
    print("=" * 70)
    print("COMPREHENSIVE STOCK DATA BACKFILL SCRIPT")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Get current coverage
    print("Analyzing current data coverage...")
    coverage = get_stock_coverage()
    print(f"Found {len(coverage)} symbols in database")

    # Categorize symbols
    critical_symbols = []  # Only 1 record
    outdated_symbols = []  # End date < 2025-12-01

    for symbol, info in coverage.items():
        if info['count'] == 1:
            critical_symbols.append(symbol)
        elif info['end'].isoformat() < '2025-12-01':
            outdated_symbols.append((symbol, info['end']))

    print(f"\nCRITICAL symbols (1 record only): {len(critical_symbols)}")
    for s in critical_symbols:
        print(f"  - {s}")

    print(f"\nOUTDATED symbols (end < Dec 1, 2025): {len(outdated_symbols)}")

    # Process CRITICAL symbols first
    print("\n" + "=" * 70)
    print("PHASE 1: Processing CRITICAL symbols (need full backfill)")
    print("=" * 70)

    critical_success = 0
    critical_failed = 0

    for i, symbol in enumerate(critical_symbols, 1):
        try:
            if process_critical_symbol(symbol, i, len(critical_symbols)):
                critical_success += 1
            else:
                critical_failed += 1
        except Exception as e:
            print(f"    EXCEPTION: {e}")
            critical_failed += 1

        time.sleep(1)  # Rate limiting between symbols

    print(f"\nCRITICAL Phase Complete: {critical_success} success, {critical_failed} failed")

    # Process OUTDATED symbols
    print("\n" + "=" * 70)
    print("PHASE 2: Processing OUTDATED symbols (need recent data)")
    print("=" * 70)

    outdated_success = 0
    outdated_failed = 0

    for i, (symbol, end_date) in enumerate(outdated_symbols, 1):
        try:
            if process_outdated_symbol(symbol, end_date, i, len(outdated_symbols)):
                outdated_success += 1
            else:
                outdated_failed += 1
        except Exception as e:
            print(f"    EXCEPTION: {e}")
            outdated_failed += 1

        time.sleep(1)  # Rate limiting between symbols

    print(f"\nOUTDATED Phase Complete: {outdated_success} success, {outdated_failed} failed")

    # Final Summary
    print("\n" + "=" * 70)
    print("BACKFILL COMPLETE")
    print("=" * 70)
    print(f"CRITICAL symbols: {critical_success}/{len(critical_symbols)} success")
    print(f"OUTDATED symbols: {outdated_success}/{len(outdated_symbols)} success")
    print(f"Total: {critical_success + outdated_success}/{len(critical_symbols) + len(outdated_symbols)} success")


if __name__ == "__main__":
    main()
