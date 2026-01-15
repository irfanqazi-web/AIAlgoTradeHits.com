"""
Local TwelveData Data Fetcher
Runs locally with user credentials to populate BigQuery tables
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timezone
import time
import hashlib
import argparse

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Simplified symbol lists for initial data load
ASSET_CONFIG = {
    'stocks': {
        'symbols': [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'JNJ'
        ]
    },
    'crypto': {
        'symbols': [
            'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'SOL/USD', 'DOGE/USD', 'ADA/USD',
            'AVAX/USD', 'LINK/USD', 'DOT/USD'
        ]
    },
    'forex': {
        'symbols': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD']
    },
    'etfs': {
        'symbols': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI']
    },
    'indices': {
        'symbols': ['SPX', 'NDX', 'DJI', 'VIX']
    },
    'commodities': {
        'symbols': ['XAU/USD', 'XAG/USD', 'WTI', 'NATGAS']
    }
}

TIMEFRAME_CONFIG = {
    'weekly': {'interval': '1week', 'outputsize': 52},
    'daily': {'interval': '1day', 'outputsize': 365},
    'hourly': {'interval': '1h', 'outputsize': 200},
    '5min': {'interval': '5min', 'outputsize': 100}
}


def fetch_time_series(symbol, interval, outputsize=100):
    """Fetch OHLCV data from TwelveData"""
    try:
        url = f"{BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': TWELVEDATA_API_KEY,
            'format': 'JSON'
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            print(f"  [!] No data for {symbol}: {data.get('message', 'Unknown error')}")
            return None

        df = pd.DataFrame(data['values'])
        df['symbol'] = symbol.replace('/', '')
        df['name'] = data.get('meta', {}).get('name', symbol)
        df['exchange'] = data.get('meta', {}).get('exchange', '')
        df['currency'] = data.get('meta', {}).get('currency', 'USD')

        # Convert types
        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    except Exception as e:
        print(f"  [!] Error fetching {symbol}: {e}")
        return None


def fetch_basic_indicators(symbol, interval):
    """Fetch a small set of key indicators"""
    indicators = {}

    indicator_list = [
        ('rsi', {'time_period': 14}, 'rsi_14'),
        ('macd', {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}, 'macd'),
        ('sma', {'time_period': 20}, 'sma_20'),
        ('sma', {'time_period': 50}, 'sma_50'),
        ('bbands', {'time_period': 20}, 'bbands'),
    ]

    for item in indicator_list:
        indicator_name = item[0]
        params = item[1]

        try:
            url = f"{BASE_URL}/{indicator_name}"
            request_params = {
                'symbol': symbol,
                'interval': interval,
                'apikey': TWELVEDATA_API_KEY,
                'outputsize': 1,
                **params
            }

            response = requests.get(url, params=request_params, timeout=10)
            data = response.json()

            if 'values' in data and len(data['values']) > 0:
                value = data['values'][0]

                if indicator_name == 'macd':
                    indicators['macd_line'] = float(value.get('macd', 0) or 0)
                    indicators['macd_signal'] = float(value.get('macd_signal', 0) or 0)
                    indicators['macd_histogram'] = float(value.get('macd_hist', 0) or 0)
                elif indicator_name == 'bbands':
                    indicators['bbands_upper'] = float(value.get('upper_band', 0) or 0)
                    indicators['bbands_middle'] = float(value.get('middle_band', 0) or 0)
                    indicators['bbands_lower'] = float(value.get('lower_band', 0) or 0)
                elif indicator_name == 'sma':
                    period = params.get('time_period', 20)
                    indicators[f'sma_{period}'] = float(value.get('sma', 0) or 0)
                elif indicator_name == 'rsi':
                    indicators['rsi_14'] = float(value.get('rsi', 0) or 0)

            time.sleep(0.15)  # Rate limiting

        except Exception as e:
            pass  # Skip failed indicators silently

    return indicators


def generate_record_id(symbol, datetime_val):
    """Generate unique record ID"""
    key = f"{symbol}_{datetime_val}"
    return hashlib.md5(key.encode()).hexdigest()[:16]


def upload_to_bigquery(df, asset_type, timeframe):
    """Upload dataframe to BigQuery"""
    if df is None or df.empty:
        return 0

    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{asset_type}_{timeframe}"

        # Generate unique IDs
        df['id'] = df.apply(lambda row: generate_record_id(row['symbol'], row['datetime']), axis=1)

        # Add date column
        df['date'] = pd.to_datetime(df['datetime']).dt.date

        # Add metadata
        df['data_source'] = 'twelvedata'
        df['created_at'] = datetime.now(timezone.utc)
        df['updated_at'] = datetime.now(timezone.utc)

        # Upload with schema flexibility
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        return len(df)

    except Exception as e:
        print(f"  [!] Upload error: {e}")
        return 0


def fetch_and_upload(asset_type, timeframe, with_indicators=False):
    """Fetch data for an asset type and upload"""
    config = ASSET_CONFIG.get(asset_type, {})
    symbols = config.get('symbols', [])
    tf_config = TIMEFRAME_CONFIG.get(timeframe, {})
    interval = tf_config.get('interval', '1day')
    outputsize = tf_config.get('outputsize', 100)

    print(f"\n{'='*60}")
    print(f"Fetching {asset_type} - {timeframe}")
    print(f"{'='*60}")

    all_data = []

    for i, symbol in enumerate(symbols):
        print(f"  [{i+1}/{len(symbols)}] {symbol}...", end=" ")

        df = fetch_time_series(symbol, interval, outputsize)
        if df is None or df.empty:
            time.sleep(0.5)
            continue

        if with_indicators:
            indicators = fetch_basic_indicators(symbol, interval)
            for key, value in indicators.items():
                df[key] = value

        all_data.append(df)
        print(f"OK ({len(df)} rows)")
        time.sleep(0.5)  # Rate limiting

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        rows = upload_to_bigquery(combined_df, asset_type, timeframe)
        print(f"\n  Uploaded: {rows} rows to {asset_type}_{timeframe}")
        return rows

    return 0


def main():
    parser = argparse.ArgumentParser(description='Local TwelveData Fetcher')
    parser.add_argument('--asset', type=str, default='all',
                        help='Asset type: stocks, crypto, forex, etfs, indices, commodities, or all')
    parser.add_argument('--timeframe', type=str, default='daily',
                        help='Timeframe: weekly, daily, hourly, 5min')
    parser.add_argument('--indicators', action='store_true',
                        help='Include technical indicators')
    args = parser.parse_args()

    print("="*60)
    print("LOCAL TWELVEDATA FETCHER")
    print("="*60)
    print(f"Asset Type: {args.asset}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Indicators: {args.indicators}")

    total_rows = 0

    if args.asset == 'all':
        for asset_type in ASSET_CONFIG.keys():
            rows = fetch_and_upload(asset_type, args.timeframe, args.indicators)
            total_rows += rows
    else:
        rows = fetch_and_upload(args.asset, args.timeframe, args.indicators)
        total_rows = rows

    print("\n" + "="*60)
    print(f"COMPLETE: {total_rows} total rows uploaded")
    print("="*60)


if __name__ == "__main__":
    main()
