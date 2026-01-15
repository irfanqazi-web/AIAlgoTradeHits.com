"""
Fetch Historical Training Data for Gemini 2.5
Symbols: BTC/USD, QQQ, SPY
Uses TwelveData API with proper schema matching
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery

# Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"
API_BASE = "https://api.twelvedata.com"

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# Define table schemas (columns that exist in each table type)
DAILY_COLUMNS = [
    'datetime', 'open', 'high', 'low', 'close', 'volume', 'symbol', 'name',
    'exchange', 'currency', 'percent_change', 'rsi', 'macd', 'macd_signal',
    'macd_histogram', 'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
    'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'atr', 'adx', 'stoch_k',
    'stoch_d', 'cci', 'williams_r', 'obv', 'momentum', 'roc'
]

HOURLY_5MIN_COLUMNS = [
    'datetime', 'open', 'high', 'low', 'close', 'volume', 'symbol', 'name',
    'exchange', 'currency', 'percent_change', 'rsi', 'macd', 'macd_signal',
    'macd_histogram', 'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
    'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26', 'atr', 'adx'
]

def fetch_twelvedata(symbol, interval, outputsize=5000, start_date=None, end_date=None):
    """Fetch data from TwelveData API"""
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": TWELVEDATA_API_KEY,
        "outputsize": outputsize,
        "format": "JSON"
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    print(f"  Fetching {symbol} {interval}...")
    response = requests.get(f"{API_BASE}/time_series", params=params, timeout=60)

    if response.status_code != 200:
        print(f"  HTTP Error: {response.status_code}")
        return None, {}

    data = response.json()

    if "code" in data and data["code"] != 200:
        print(f"  API Error: {data.get('message', 'Unknown')}")
        return None, {}

    if "values" not in data:
        print(f"  No values in response")
        return None, {}

    meta = data.get('meta', {})
    print(f"  Got {len(data['values'])} records")
    return data["values"], meta

def fetch_indicators(symbol, interval, outputsize=5000):
    """Fetch technical indicators from TwelveData API"""
    indicators = {}
    indicator_specs = [
        ('rsi', {'time_period': 14}),
        ('macd', {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}),
        ('bbands', {'time_period': 20, 'sd': 2}),
        ('sma', {'time_period': 20}),
        ('sma', {'time_period': 50}),
        ('sma', {'time_period': 200}),
        ('ema', {'time_period': 12}),
        ('ema', {'time_period': 26}),
        ('atr', {'time_period': 14}),
        ('adx', {'time_period': 14}),
        ('stoch', {'fast_k_period': 14, 'slow_k_period': 3}),
        ('cci', {'time_period': 20}),
        ('willr', {'time_period': 14}),
    ]

    for indicator, params in indicator_specs:
        try:
            req_params = {
                "symbol": symbol,
                "interval": interval,
                "apikey": TWELVEDATA_API_KEY,
                "outputsize": min(outputsize, 5000),
                **params
            }

            response = requests.get(f"{API_BASE}/{indicator}", params=req_params, timeout=30)
            data = response.json()

            if "values" in data:
                key = f"{indicator}_{params.get('time_period', '')}" if 'time_period' in params else indicator
                indicators[key] = data["values"]

            time.sleep(0.15)  # Rate limit
        except Exception as e:
            print(f"  Warning: Could not fetch {indicator}: {e}")

    return indicators

def calculate_local_indicators(df):
    """Calculate indicators locally if API limits reached"""
    if len(df) < 20:
        return df

    # Ensure numeric
    for col in ['open', 'high', 'low', 'close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'volume' not in df.columns:
        df['volume'] = 0
    else:
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['sma_20'] = df['close'].rolling(window=20).mean()
    std20 = df['close'].rolling(window=20).std()
    df['bollinger_middle'] = df['sma_20']
    df['bollinger_upper'] = df['bollinger_middle'] + (std20 * 2)
    df['bollinger_lower'] = df['bollinger_middle'] - (std20 * 2)

    # SMAs
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()

    # EMAs
    df['ema_12'] = ema12
    df['ema_26'] = ema26

    # ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = tr.rolling(window=14).mean()

    # ADX
    plus_dm = df['high'].diff()
    minus_dm = df['low'].diff() * -1
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    tr_smooth = tr.rolling(window=14).sum()
    plus_di = 100 * (plus_dm.rolling(window=14).sum() / tr_smooth)
    minus_di = 100 * (minus_dm.rolling(window=14).sum() / tr_smooth)
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=14).mean()

    # Stochastic
    low14 = df['low'].rolling(window=14).min()
    high14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low14) / (high14 - low14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # CCI
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = typical_price.rolling(window=20).mean()
    mad = typical_price.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (typical_price - sma_tp) / (0.015 * mad)

    # Williams %R
    df['williams_r'] = -100 * ((high14 - df['close']) / (high14 - low14))

    # Percent change
    df['percent_change'] = df['close'].pct_change() * 100

    # OBV
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['obv'] = obv

    # Momentum and ROC
    df['momentum'] = df['close'] - df['close'].shift(10)
    df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

    return df

def filter_columns(df, table_type):
    """Filter dataframe to only include columns that exist in the table"""
    if table_type == 'daily':
        allowed = DAILY_COLUMNS
    else:
        allowed = HOURLY_5MIN_COLUMNS

    # Keep only columns that exist in the schema
    existing = [col for col in df.columns if col in allowed]

    # Add missing required columns with None
    for col in allowed:
        if col not in df.columns:
            df[col] = None

    return df[allowed]

def upload_to_bigquery(df, table_name, symbol):
    """Upload dataframe to BigQuery, replacing existing data for symbol"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Delete existing data for this symbol
    delete_query = f"DELETE FROM `{table_id}` WHERE symbol = '{symbol}'"
    try:
        client.query(delete_query).result()
        print(f"  Cleared existing {symbol} data")
    except Exception as e:
        print(f"  Note: {str(e)[:40]}")

    # Upload new data
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"  Uploaded {len(df)} records to {table_name}")

def fetch_daily_10years(symbol, asset_type):
    """Fetch 10 years of daily data"""
    print(f"\n{'='*60}")
    print(f"DAILY (10 years): {symbol}")
    print('='*60)

    td_symbol = symbol.replace('USD', '/USD') if 'USD' in symbol and asset_type == 'crypto' else symbol

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3650)).strftime("%Y-%m-%d")

    values, meta = fetch_twelvedata(td_symbol, "1day", 5000, start_date, end_date)
    if not values:
        return 0

    df = pd.DataFrame(values)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['symbol'] = symbol
    df['name'] = meta.get('name', symbol)
    df['exchange'] = meta.get('exchange', '')
    df['currency'] = meta.get('currency', 'USD')

    df = calculate_local_indicators(df)
    df = filter_columns(df, 'daily')

    table_map = {'crypto': 'v2_crypto_daily', 'etf': 'v2_etfs_daily'}
    upload_to_bigquery(df, table_map.get(asset_type, 'v2_stocks_daily'), symbol)

    return len(df)

def fetch_hourly_1month(symbol, asset_type):
    """Fetch 1 month of hourly data"""
    print(f"\n{'='*60}")
    print(f"HOURLY (1 month): {symbol}")
    print('='*60)

    td_symbol = symbol.replace('USD', '/USD') if 'USD' in symbol and asset_type == 'crypto' else symbol

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    values, meta = fetch_twelvedata(td_symbol, "1h", 720, start_date, end_date)
    if not values:
        return 0

    df = pd.DataFrame(values)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['symbol'] = symbol
    df['name'] = meta.get('name', symbol)
    df['exchange'] = meta.get('exchange', '')
    df['currency'] = meta.get('currency', 'USD')

    df = calculate_local_indicators(df)
    df = filter_columns(df, 'hourly')

    table_map = {'crypto': 'v2_crypto_hourly', 'etf': 'v2_etfs_hourly'}
    upload_to_bigquery(df, table_map.get(asset_type, 'v2_stocks_hourly'), symbol)

    return len(df)

def fetch_5min_1week(symbol, asset_type):
    """Fetch 1 week of 5-minute data"""
    print(f"\n{'='*60}")
    print(f"5-MINUTE (1 week): {symbol}")
    print('='*60)

    td_symbol = symbol.replace('USD', '/USD') if 'USD' in symbol and asset_type == 'crypto' else symbol

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    values, meta = fetch_twelvedata(td_symbol, "5min", 2016, start_date, end_date)
    if not values:
        return 0

    df = pd.DataFrame(values)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['symbol'] = symbol
    df['name'] = meta.get('name', symbol)
    df['exchange'] = meta.get('exchange', '')
    df['currency'] = meta.get('currency', 'USD')

    df = calculate_local_indicators(df)
    df = filter_columns(df, '5min')

    table_map = {'crypto': 'v2_crypto_5min', 'etf': 'v2_etfs_5min'}
    upload_to_bigquery(df, table_map.get(asset_type, 'v2_stocks_5min'), symbol)

    return len(df)

def main():
    print("="*80)
    print("GEMINI 2.5 TRAINING DATA FETCHER")
    print("Symbols: BTC/USD, QQQ, SPY")
    print("="*80)

    symbols = [
        ("BTCUSD", "crypto"),
        ("QQQ", "etf"),
        ("SPY", "etf")
    ]

    results = {}

    for symbol, asset_type in symbols:
        results[symbol] = {'daily': 0, 'hourly': 0, '5min': 0}

        # Daily - 10 years
        count = fetch_daily_10years(symbol, asset_type)
        results[symbol]['daily'] = count
        time.sleep(2)

        # Hourly - 1 month
        count = fetch_hourly_1month(symbol, asset_type)
        results[symbol]['hourly'] = count
        time.sleep(2)

        # 5-minute - 1 week
        count = fetch_5min_1week(symbol, asset_type)
        results[symbol]['5min'] = count
        time.sleep(2)

    # Print summary
    print("\n" + "="*80)
    print("TRAINING DATA FETCH COMPLETE")
    print("="*80)

    total_records = 0
    for symbol, counts in results.items():
        print(f"\n{symbol}:")
        print(f"  Daily:  {counts['daily']:,} records (10 years)")
        print(f"  Hourly: {counts['hourly']:,} records (1 month)")
        print(f"  5-min:  {counts['5min']:,} records (1 week)")
        total_records += sum(counts.values())

    print(f"\n{'='*80}")
    print(f"TOTAL RECORDS: {total_records:,}")
    print(f"Data ready for Gemini 2.5 training!")
    print("="*80)

if __name__ == "__main__":
    main()
