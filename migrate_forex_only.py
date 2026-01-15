"""
Migrate Forex Data to Clean Schema with NO VOLUME support
Since forex pairs don't have volume data in TwelveData

Author: Claude Code
Date: December 2025
"""

import os
import sys
import time
import math
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
TWELVEDATA_BASE_URL = 'https://api.twelvedata.com'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# Forex symbols
FOREX_SYMBOLS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'NZD/USD',
    'USD/CAD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/CHF', 'EUR/AUD',
    'AUD/JPY', 'GBP/CHF', 'EUR/CAD', 'CAD/JPY', 'AUD/NZD', 'GBP/AUD',
    'USD/MXN', 'USD/ZAR', 'USD/TRY', 'USD/SGD'
]


def safe_float(val):
    """Convert to safe float for JSON/BigQuery"""
    if val is None or pd.isna(val):
        return None
    try:
        f = float(val)
        if math.isinf(f) or math.isnan(f):
            return None
        return f
    except:
        return None


def fetch_forex_data(symbol):
    """Fetch forex data from TwelveData - forex has no volume!"""
    try:
        url = f"{TWELVEDATA_BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': '1day',
            'outputsize': 5000,
            'apikey': TWELVEDATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'code' in data and data['code'] != 200:
            return None, data.get('message', 'Unknown error')

        if 'values' not in data:
            return None, 'No values in response'

        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Convert OHLC columns
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Forex has NO VOLUME - set to 0
        df['volume'] = 0.0

        df = df.sort_values('datetime').reset_index(drop=True)

        return df, None

    except Exception as e:
        return None, str(e)


def calculate_forex_indicators(df):
    """Calculate indicators for forex (NO volume-based indicators)"""
    if len(df) < 50:
        return df

    close = df['close']
    high = df['high']
    low = df['low']
    open_price = df['open']

    # RSI (14) - Wilder's RMA
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Slow Stochastic (14, 3, 3)
    lowest_low = low.rolling(14).min()
    highest_high = high.rolling(14).max()
    raw_k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
    df['stoch_k'] = raw_k.rolling(3).mean()
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()

    # CCI (20)
    typical_price = (high + low + close) / 3
    sma_tp = typical_price.rolling(20).mean()
    mad = typical_price.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    df['cci'] = (typical_price - sma_tp) / (0.015 * mad).replace(0, np.nan)

    # Williams %R
    df['williams_r'] = -100 * (highest_high - close) / (highest_high - lowest_low).replace(0, np.nan)

    # Momentum and ROC (10 period)
    df['momentum'] = close - close.shift(10)
    df['roc'] = ((close - close.shift(10)) / close.shift(10).replace(0, np.nan)) * 100

    # Moving Averages
    df['sma_20'] = close.rolling(20).mean()
    df['sma_50'] = close.rolling(50).mean()
    df['sma_200'] = close.rolling(200).mean()
    df['ema_12'] = ema_12
    df['ema_20'] = close.ewm(span=20, adjust=False).mean()
    df['ema_26'] = ema_26
    df['ema_50'] = close.ewm(span=50, adjust=False).mean()
    df['ema_200'] = close.ewm(span=200, adjust=False).mean()

    # KAMA
    change = (close - close.shift(10)).abs()
    volatility = close.diff().abs().rolling(10).sum()
    er = change / volatility.replace(0, np.nan)
    sc = (er * (2/3 - 2/31) + 2/31) ** 2
    kama = [close.iloc[0]]
    for i in range(1, len(close)):
        kama.append(kama[-1] + sc.iloc[i] * (close.iloc[i] - kama[-1]) if pd.notna(sc.iloc[i]) else kama[-1])
    df['kama'] = kama

    # TRIX
    ema1 = close.ewm(span=15, adjust=False).mean()
    ema2 = ema1.ewm(span=15, adjust=False).mean()
    ema3 = ema2.ewm(span=15, adjust=False).mean()
    df['trix'] = ((ema3 - ema3.shift(1)) / ema3.shift(1).replace(0, np.nan)) * 100

    # Bollinger Bands (ddof=0)
    bb_middle = close.rolling(20).mean()
    bb_std = close.rolling(20).std(ddof=0)
    df['bollinger_middle'] = bb_middle
    df['bollinger_upper'] = bb_middle + 2 * bb_std
    df['bollinger_lower'] = bb_middle - 2 * bb_std
    df['bb_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / bb_middle.replace(0, np.nan)

    # ATR (14) - Wilder's RMA
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['true_range'] = tr
    df['atr'] = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    df['natr'] = (df['atr'] / close) * 100

    # ADX (14) - Wilder's RMA
    plus_dm = high.diff()
    minus_dm = (-low.diff())
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    atr_14 = tr.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr_14.replace(0, np.nan))
    minus_di = 100 * (minus_dm.ewm(alpha=1/14, adjust=False, min_periods=14).mean() / atr_14.replace(0, np.nan))

    df['plus_di'] = plus_di
    df['minus_di'] = minus_di
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    df['adx'] = dx.ewm(alpha=1/14, adjust=False, min_periods=14).mean()

    # No volume indicators for forex - set to NULL
    df['obv'] = None
    df['pvo'] = None
    df['mfi'] = None
    df['cmf'] = None
    df['ad_line'] = None
    df['vwap'] = None

    # PPO (price-based, works for forex)
    df['ppo'] = ((ema_12 - ema_26) / ema_26.replace(0, np.nan)) * 100

    # Ichimoku Cloud (with forward shift)
    high_9 = high.rolling(9).max()
    low_9 = low.rolling(9).min()
    df['ichimoku_tenkan'] = (high_9 + low_9) / 2

    high_26 = high.rolling(26).max()
    low_26 = low.rolling(26).min()
    df['ichimoku_kijun'] = (high_26 + low_26) / 2

    senkou_a_raw = (df['ichimoku_tenkan'] + df['ichimoku_kijun']) / 2
    df['ichimoku_senkou_a'] = senkou_a_raw.shift(26)

    high_52 = high.rolling(52).max()
    low_52 = low.rolling(52).min()
    senkou_b_raw = (high_52 + low_52) / 2
    df['ichimoku_senkou_b'] = senkou_b_raw.shift(26)

    df['ichimoku_chikou'] = close.shift(-26)

    # Price changes
    df['price_change'] = close - close.shift(1)
    df['price_change_pct'] = df['price_change'] / close.shift(1).replace(0, np.nan) * 100
    df['high_low_range'] = high - low
    df['gap'] = open_price - close.shift(1)
    df['gap_pct'] = df['gap'] / close.shift(1).replace(0, np.nan) * 100

    # Pivot Points
    df['pivot_point'] = (high.shift(1) + low.shift(1) + close.shift(1)) / 3
    df['r1'] = 2 * df['pivot_point'] - low.shift(1)
    df['r2'] = df['pivot_point'] + (high.shift(1) - low.shift(1))
    df['r3'] = high.shift(1) + 2 * (df['pivot_point'] - low.shift(1))
    df['s1'] = 2 * df['pivot_point'] - high.shift(1)
    df['s2'] = df['pivot_point'] - (high.shift(1) - low.shift(1))
    df['s3'] = low.shift(1) - 2 * (high.shift(1) - df['pivot_point'])

    # Fibonacci
    high_50 = high.rolling(50).max()
    low_50 = low.rolling(50).min()
    fib_range = high_50 - low_50
    df['fib_0'] = low_50
    df['fib_236'] = low_50 + 0.236 * fib_range
    df['fib_382'] = low_50 + 0.382 * fib_range
    df['fib_500'] = low_50 + 0.500 * fib_range
    df['fib_618'] = low_50 + 0.618 * fib_range
    df['fib_786'] = low_50 + 0.786 * fib_range
    df['fib_1000'] = high_50

    # Candlestick patterns
    body = (close - open_price).abs()
    df['doji'] = body < (0.1 * (high - low))
    df['hammer'] = False
    df['engulfing_bullish'] = False
    df['engulfing_bearish'] = False
    df['morning_star'] = False
    df['evening_star'] = False

    # Trend
    df['trend_sma_20'] = np.where(close > df['sma_20'], 'Bullish', np.where(close < df['sma_20'], 'Bearish', 'Neutral'))
    df['trend_sma_50'] = np.where(close > df['sma_50'], 'Bullish', np.where(close < df['sma_50'], 'Bearish', 'Neutral'))
    df['trend_sma_200'] = np.where(close > df['sma_200'], 'Bullish', np.where(close < df['sma_200'], 'Bearish', 'Neutral'))
    df['golden_cross'] = (df['sma_50'] > df['sma_200']) & (df['sma_50'].shift(1) <= df['sma_200'].shift(1))
    df['death_cross'] = (df['sma_50'] < df['sma_200']) & (df['sma_50'].shift(1) >= df['sma_200'].shift(1))

    # Price averages
    df['typical_price'] = (high + low + close) / 3
    df['median_price'] = (high + low) / 2
    df['weighted_close'] = (high + low + close + close) / 4
    df['avg_price'] = (open_price + high + low + close) / 4

    # Statistics
    df['std_20'] = close.rolling(20).std(ddof=0)
    df['variance_20'] = close.rolling(20).var(ddof=0)
    mean_20 = close.rolling(20).mean()
    df['zscore'] = (close - mean_20) / df['std_20'].replace(0, np.nan)

    # Ultimate Oscillator
    bp = close - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    tr_uo = pd.concat([high, close.shift(1)], axis=1).max(axis=1) - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    avg7 = bp.rolling(7).sum() / tr_uo.rolling(7).sum().replace(0, np.nan)
    avg14 = bp.rolling(14).sum() / tr_uo.rolling(14).sum().replace(0, np.nan)
    avg28 = bp.rolling(28).sum() / tr_uo.rolling(28).sum().replace(0, np.nan)
    df['ultimate_oscillator'] = 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7

    # Awesome Oscillator
    mid = (high + low) / 2
    df['awesome_oscillator'] = mid.rolling(5).mean() - mid.rolling(34).mean()

    return df


def get_table_columns(table_id):
    """Get existing column names from a BigQuery table"""
    try:
        table = client.get_table(table_id)
        return [field.name for field in table.schema]
    except:
        return None


def upload_to_bigquery(df, table_id):
    """Upload DataFrame to BigQuery, matching existing schema"""
    if df is None or len(df) == 0:
        return 0

    # Get existing columns in table
    existing_cols = get_table_columns(table_id)
    if existing_cols:
        # Only keep columns that exist in the table
        cols_to_keep = [c for c in df.columns if c in existing_cols]
        df = df[cols_to_keep]

    # Sanitize float columns
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32']:
            df[col] = df[col].apply(safe_float)

    job_config = bigquery.LoadJobConfig(
        write_disposition='WRITE_APPEND',
        autodetect=False,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    return len(df)


def main():
    """Main migration function for Forex"""
    print("="*60)
    print("FOREX MIGRATION - No Volume Version")
    print("="*60)
    print(f"Start time: {datetime.now()}\n")

    table_id = f"{PROJECT_ID}.{DATASET_ID}.forex_daily_clean"

    total_rows = 0
    success_count = 0

    for i, symbol in enumerate(FOREX_SYMBOLS, 1):
        print(f"[{i}/{len(FOREX_SYMBOLS)}] Processing {symbol}...")

        # Rate limiting - 2.5 seconds between calls
        time.sleep(2.5)

        df, error = fetch_forex_data(symbol)

        if error:
            print(f"  Error: {error}")
            continue

        if df is None or len(df) < 50:
            print(f"  Insufficient data: {len(df) if df is not None else 0} rows")
            continue

        # Add metadata
        df['symbol'] = symbol
        df['asset_type'] = 'Forex'
        df['exchange'] = 'Forex'
        df['currency'] = 'USD'

        # Calculate indicators
        df = calculate_forex_indicators(df)

        # Add metadata fields
        df['fetch_timestamp'] = datetime.now(timezone.utc)
        df['data_source'] = 'TwelveData'
        df['timeframe'] = '1D'

        try:
            uploaded = upload_to_bigquery(df, table_id)
            total_rows += uploaded
            success_count += 1
            print(f"  Success: {uploaded} rows uploaded")
        except Exception as e:
            print(f"  Upload error: {e}")

    print(f"\n{'='*60}")
    print(f"FOREX Migration Complete: {success_count}/{len(FOREX_SYMBOLS)} symbols")
    print(f"Total rows: {total_rows:,}")
    print(f"End time: {datetime.now()}")


if __name__ == '__main__':
    main()
