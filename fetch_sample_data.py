"""
Quick script to fetch sample data from TwelveData and upload to BigQuery
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timezone
import time

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'
BASE_URL = 'https://api.twelvedata.com'

# Sample symbols for each asset type
SAMPLES = {
    'stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
    'crypto': ['BTC/USD', 'ETH/USD', 'SOL/USD'],
    'forex': ['EUR/USD', 'GBP/USD', 'USD/JPY'],
    'etfs': ['SPY', 'QQQ', 'IWM'],
    'indices': ['SPX', 'NDX', 'DJI'],
    'commodities': ['XAU/USD', 'XAG/USD']
}

def fetch_and_upload(symbol, asset_type, timeframe='daily'):
    """Fetch data for one symbol and upload"""
    try:
        # Map timeframe to interval
        intervals = {'weekly': '1week', 'daily': '1day', 'hourly': '1h', '5min': '5min'}
        interval = intervals.get(timeframe, '1day')

        # Fetch OHLCV
        url = f"{BASE_URL}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': 100,
            'apikey': TWELVEDATA_API_KEY
        }

        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            print(f"  No data for {symbol}")
            return 0

        df = pd.DataFrame(data['values'])

        # Process data
        df['symbol'] = symbol.replace('/', '')
        df['name'] = data.get('meta', {}).get('name', symbol)
        df['exchange'] = data.get('meta', {}).get('exchange', '')
        df['currency'] = data.get('meta', {}).get('currency', 'USD')
        df['asset_type'] = asset_type
        df['datetime'] = pd.to_datetime(df['datetime'])

        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Calculate basic indicators
        if len(df) > 0:
            df['change_percent'] = df['close'].pct_change() * 100
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3

        # Add metadata
        df['fetch_timestamp'] = datetime.now(timezone.utc)
        df['data_source'] = 'twelvedata'

        # Upload to BigQuery
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{asset_type}_{timeframe}"

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        print(f"  ✓ {symbol}: {len(df)} rows uploaded")
        return len(df)

    except Exception as e:
        print(f"  ✗ Error with {symbol}: {e}")
        return 0

def main():
    print("=" * 60)
    print("FETCHING SAMPLE DATA FROM TWELVEDATA")
    print("=" * 60)

    total_rows = 0

    for asset_type, symbols in SAMPLES.items():
        print(f"\n{asset_type.upper()}:")
        for symbol in symbols:
            rows = fetch_and_upload(symbol, asset_type, 'daily')
            total_rows += rows
            time.sleep(1)  # Rate limiting

    print("\n" + "=" * 60)
    print(f"COMPLETE! Total rows uploaded: {total_rows}")
    print("=" * 60)

if __name__ == "__main__":
    main()
