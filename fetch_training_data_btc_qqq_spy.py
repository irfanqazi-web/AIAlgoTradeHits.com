"""
Fetch Historical Training Data for Gemini 2.5
Symbols: BTC/USD, QQQ, SPY
Timeframes:
- Daily: 10 years (3,650 days)
- Hourly: 1 month (720 hours)
- 5-minute: 1 week (2,016 bars for crypto, 390 for stocks)
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
import json

# Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# TwelveData API base URL
API_BASE = "https://api.twelvedata.com"

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

def calculate_technical_indicators(df):
    """Calculate 29 technical indicators for each record"""
    if len(df) < 2:
        return df

    # Ensure volume column exists
    if 'volume' not in df.columns:
        df['volume'] = 0

    # Ensure numeric types
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0

    # RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # SMAs
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()

    # EMAs
    df['ema_12'] = ema12
    df['ema_26'] = ema26
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # Bollinger Bands
    df['bollinger_middle'] = df['sma_20']
    std20 = df['close'].rolling(window=20).std()
    df['bollinger_upper'] = df['bollinger_middle'] + (std20 * 2)
    df['bollinger_lower'] = df['bollinger_middle'] - (std20 * 2)

    # ATR (14)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = tr.rolling(window=14).mean()

    # ADX (14)
    plus_dm = df['high'].diff()
    minus_dm = df['low'].diff().abs() * -1
    plus_dm = plus_dm.where((plus_dm > minus_dm.abs()) & (plus_dm > 0), 0)
    minus_dm = minus_dm.abs().where((minus_dm.abs() > plus_dm) & (minus_dm < 0), 0)
    atr14 = tr.rolling(window=14).mean()
    plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr14)
    minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr14)
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=14).mean()

    # Stochastic (14, 3)
    low14 = df['low'].rolling(window=14).min()
    high14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low14) / (high14 - low14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()

    # CCI (20)
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    sma_tp = typical_price.rolling(window=20).mean()
    mad = typical_price.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
    df['cci'] = (typical_price - sma_tp) / (0.015 * mad)

    # Williams %R (14)
    df['williams_r'] = -100 * ((high14 - df['close']) / (high14 - low14))

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

    # Momentum (10)
    df['momentum'] = df['close'] - df['close'].shift(10)

    # ROC (10)
    df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

    # Percent change
    df['percent_change'] = df['close'].pct_change() * 100

    return df

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

    url = f"{API_BASE}/time_series"

    print(f"  Fetching {symbol} {interval}...")
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"  Error: HTTP {response.status_code}")
        return None

    data = response.json()

    if "code" in data and data["code"] != 200:
        print(f"  API Error: {data.get('message', 'Unknown error')}")
        return None

    if "values" not in data:
        print(f"  No values in response")
        return None

    print(f"  Got {len(data['values'])} records")
    return data["values"]

def upload_to_bigquery(df, table_name, symbol):
    """Upload dataframe to BigQuery"""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Delete existing data for this symbol
    delete_query = f"""
    DELETE FROM `{table_id}`
    WHERE symbol = '{symbol}'
    """
    try:
        client.query(delete_query).result()
        print(f"  Cleared existing {symbol} data from {table_name}")
    except Exception as e:
        print(f"  Note: Could not clear existing data - {str(e)[:50]}")

    # Upload new data
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    print(f"  Uploaded {len(df)} records to {table_name}")

def fetch_and_store_daily(symbol, asset_type, years=10):
    """Fetch 10 years of daily data"""
    print(f"\n{'='*60}")
    print(f"Fetching {years} years DAILY data for {symbol}")
    print('='*60)

    # TwelveData symbol format
    td_symbol = symbol.replace('USD', '/USD') if 'USD' in symbol and asset_type == 'crypto' else symbol

    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=years*365)).strftime("%Y-%m-%d")

    print(f"  Date range: {start_date} to {end_date}")

    # Fetch data
    values = fetch_twelvedata(td_symbol, "1day", outputsize=5000, start_date=start_date, end_date=end_date)

    if not values:
        print(f"  Failed to fetch data for {symbol}")
        return

    # Convert to DataFrame
    df = pd.DataFrame(values)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['symbol'] = symbol

    # Calculate indicators
    df = calculate_technical_indicators(df)

    # Determine table name
    table_map = {
        'crypto': 'v2_crypto_daily',
        'etf': 'v2_etfs_daily',
        'stock': 'v2_stocks_daily'
    }
    table_name = table_map.get(asset_type, 'v2_stocks_daily')

    # Upload to BigQuery
    upload_to_bigquery(df, table_name, symbol)

    return len(df)

def fetch_and_store_hourly(symbol, asset_type, days=30):
    """Fetch 1 month of hourly data"""
    print(f"\n{'='*60}")
    print(f"Fetching {days} days HOURLY data for {symbol}")
    print('='*60)

    td_symbol = symbol.replace('USD', '/USD') if 'USD' in symbol and asset_type == 'crypto' else symbol

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    print(f"  Date range: {start_date} to {end_date}")

    values = fetch_twelvedata(td_symbol, "1h", outputsize=5000, start_date=start_date, end_date=end_date)

    if not values:
        print(f"  Failed to fetch hourly data for {symbol}")
        return

    df = pd.DataFrame(values)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['symbol'] = symbol

    df = calculate_technical_indicators(df)

    table_map = {
        'crypto': 'v2_crypto_hourly',
        'etf': 'v2_etfs_hourly',
        'stock': 'v2_stocks_hourly'
    }
    table_name = table_map.get(asset_type, 'v2_stocks_hourly')

    upload_to_bigquery(df, table_name, symbol)

    return len(df)

def fetch_and_store_5min(symbol, asset_type, days=7):
    """Fetch 1 week of 5-minute data"""
    print(f"\n{'='*60}")
    print(f"Fetching {days} days 5-MINUTE data for {symbol}")
    print('='*60)

    td_symbol = symbol.replace('USD', '/USD') if 'USD' in symbol and asset_type == 'crypto' else symbol

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    print(f"  Date range: {start_date} to {end_date}")

    values = fetch_twelvedata(td_symbol, "5min", outputsize=5000, start_date=start_date, end_date=end_date)

    if not values:
        print(f"  Failed to fetch 5min data for {symbol}")
        return

    df = pd.DataFrame(values)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['symbol'] = symbol

    df = calculate_technical_indicators(df)

    table_map = {
        'crypto': 'v2_crypto_5min',
        'etf': 'v2_etfs_5min',
        'stock': 'v2_stocks_5min'
    }
    table_name = table_map.get(asset_type, 'v2_stocks_5min')

    upload_to_bigquery(df, table_name, symbol)

    return len(df)

def main():
    """Main function to fetch all training data"""
    print("="*80)
    print("GEMINI 2.5 TRAINING DATA FETCHER")
    print("Symbols: BTC/USD, QQQ, SPY")
    print("="*80)

    # Define symbols with their asset types
    symbols = [
        ("BTCUSD", "crypto"),
        ("QQQ", "etf"),
        ("SPY", "etf")
    ]

    results = {}

    for symbol, asset_type in symbols:
        results[symbol] = {
            'daily': 0,
            'hourly': 0,
            '5min': 0
        }

        # Fetch daily (10 years)
        count = fetch_and_store_daily(symbol, asset_type, years=10)
        if count:
            results[symbol]['daily'] = count
        time.sleep(2)  # Rate limiting

        # Fetch hourly (1 month)
        count = fetch_and_store_hourly(symbol, asset_type, days=30)
        if count:
            results[symbol]['hourly'] = count
        time.sleep(2)

        # Fetch 5-minute (1 week)
        count = fetch_and_store_5min(symbol, asset_type, days=7)
        if count:
            results[symbol]['5min'] = count
        time.sleep(2)

    # Print summary
    print("\n" + "="*80)
    print("FETCH COMPLETE - SUMMARY")
    print("="*80)

    for symbol, counts in results.items():
        print(f"\n{symbol}:")
        print(f"  Daily:  {counts['daily']:,} records (10 years)")
        print(f"  Hourly: {counts['hourly']:,} records (1 month)")
        print(f"  5-min:  {counts['5min']:,} records (1 week)")

    print("\n" + "="*80)
    print("Data ready for Gemini 2.5 training!")
    print("="*80)

if __name__ == "__main__":
    main()
