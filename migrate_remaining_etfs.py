"""
Migrate Remaining ETFs to Clean Schema
ETFs that failed due to API rate limiting in first run

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

# ETFs that failed in first run
ETF_SYMBOLS = [
    'IJH', 'IWM', 'VIG', 'VXUS', 'GLD', 'VNQ', 'VGT', 'LQD',
    'SCHD', 'XLF', 'XLK', 'XLV', 'XLE', 'XLI', 'XLY', 'XLP', 'XLU', 'XLRE'
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


def fetch_etf_data(symbol):
    """Fetch ETF data from TwelveData"""
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

        # Convert OHLCV columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                df[col] = 0.0

        df = df.sort_values('datetime').reset_index(drop=True)

        return df, None

    except Exception as e:
        return None, str(e)


def calculate_indicators(df):
    """Calculate indicators with Saleem's corrections"""
    if len(df) < 50:
        return df

    close = df['close']
    high = df['high']
    low = df['low']
    open_price = df['open']
    volume = df['volume']

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

    # Volume indicators
    if volume.sum() > 0:
        # OBV
        obv = [0]
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        df['obv'] = obv

        # PVO
        vol_ema_12 = volume.ewm(span=12, adjust=False).mean()
        vol_ema_26 = volume.ewm(span=26, adjust=False).mean()
        df['pvo'] = ((vol_ema_12 - vol_ema_26) / vol_ema_26.replace(0, np.nan)) * 100

        # MFI (14)
        raw_money_flow = typical_price * volume
        pos_flow = raw_money_flow.where(typical_price > typical_price.shift(1), 0)
        neg_flow = raw_money_flow.where(typical_price < typical_price.shift(1), 0)
        money_ratio = pos_flow.rolling(14).sum() / neg_flow.rolling(14).sum().replace(0, np.nan)
        df['mfi'] = 100 - (100 / (1 + money_ratio))

        # CMF (21)
        clv = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        df['cmf'] = (clv * volume).rolling(21).sum() / volume.rolling(21).sum().replace(0, np.nan)

        # A/D Line
        ad = [0]
        for i in range(1, len(close)):
            if high.iloc[i] != low.iloc[i]:
                clv_i = ((close.iloc[i] - low.iloc[i]) - (high.iloc[i] - close.iloc[i])) / (high.iloc[i] - low.iloc[i])
                ad.append(ad[-1] + clv_i * volume.iloc[i])
            else:
                ad.append(ad[-1])
        df['ad_line'] = ad
    else:
        df['obv'] = None
        df['pvo'] = None
        df['mfi'] = None
        df['cmf'] = None
        df['ad_line'] = None

    # PPO
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

    # Pivot Points
    df['pivot'] = (high.shift(1) + low.shift(1) + close.shift(1)) / 3
    df['r1'] = 2 * df['pivot'] - low.shift(1)
    df['r2'] = df['pivot'] + (high.shift(1) - low.shift(1))
    df['r3'] = high.shift(1) + 2 * (df['pivot'] - low.shift(1))
    df['s1'] = 2 * df['pivot'] - high.shift(1)
    df['s2'] = df['pivot'] - (high.shift(1) - low.shift(1))
    df['s3'] = low.shift(1) - 2 * (high.shift(1) - df['pivot'])

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
        df = df[cols_to_keep].copy()

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
    """Main migration function for remaining ETFs"""
    print("="*60)
    print("REMAINING ETF MIGRATION")
    print("="*60)
    print(f"Start time: {datetime.now()}\n")

    table_id = f"{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean"

    total_rows = 0
    success_count = 0

    for i, symbol in enumerate(ETF_SYMBOLS, 1):
        print(f"[{i}/{len(ETF_SYMBOLS)}] Processing {symbol}...")

        # Rate limiting - 2.5 seconds between calls
        time.sleep(2.5)

        df, error = fetch_etf_data(symbol)

        if error:
            print(f"  Error: {error}")
            continue

        if df is None or len(df) < 50:
            print(f"  Insufficient data: {len(df) if df is not None else 0} rows")
            continue

        # Add metadata
        df['symbol'] = symbol
        df['asset_type'] = 'ETF'
        df['exchange'] = 'NYSE'
        df['currency'] = 'USD'

        # Calculate indicators
        df = calculate_indicators(df)

        # Add metadata fields
        df['fetch_timestamp'] = datetime.now(timezone.utc)

        try:
            uploaded = upload_to_bigquery(df, table_id)
            total_rows += uploaded
            success_count += 1
            print(f"  Success: {uploaded} rows uploaded")
        except Exception as e:
            print(f"  Upload error: {e}")

    print(f"\n{'='*60}")
    print(f"ETF Migration Complete: {success_count}/{len(ETF_SYMBOLS)} symbols")
    print(f"Total rows: {total_rows:,}")
    print(f"End time: {datetime.now()}")


if __name__ == '__main__':
    main()
