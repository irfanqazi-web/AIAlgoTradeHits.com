"""
Comprehensive Batch Weekly Data Fetcher from TwelveData
- 15,000+ stocks weekly data
- 300+ cryptocurrencies weekly data
- Maximum historical weeks available

Run: python batch_weekly_data_fetcher.py [stocks|crypto|all] [start_index]
"""
import sys
import io
import os
import json
import time
import requests
from datetime import datetime
from google.cloud import bigquery

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdout.reconfigure(line_buffering=True)

# Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"

# Rate limiting: TwelveData - 55 requests/minute for $229/month paid tier
# (600 API credits/minute plan - using conservative estimate of 55 req/min for time_series)
REQUESTS_PER_MINUTE = 55
REQUEST_DELAY = 60 / REQUESTS_PER_MINUTE + 0.1  # ~1.2 seconds between requests

# Progress tracking files
PROGRESS_FILE = "C:/1AITrading/Trading/batch_progress.json"
STOCKS_LIST_FILE = "C:/1AITrading/Trading/twelvedata_stocks_list.json"
CRYPTO_LIST_FILE = "C:/1AITrading/Trading/twelvedata_crypto_list.json"

# BigQuery client
client = None

def get_bigquery_client():
    global client
    if client is None:
        client = bigquery.Client(project=PROJECT_ID)
    return client

def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'stocks': 0, 'crypto': 0, 'stocks_done': [], 'crypto_done': []}

def save_progress(progress):
    """Save progress to file"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def load_stock_symbols():
    """Load ALL stock symbols from TwelveData list"""
    if os.path.exists(STOCKS_LIST_FILE):
        with open(STOCKS_LIST_FILE, 'r') as f:
            data = json.load(f)
            # Get ALL US stocks from major exchanges
            filtered = [
                s['symbol'] for s in data
                if s.get('exchange') in ['NYSE', 'NASDAQ', 'AMEX', 'OTC']
            ]
            print(f"Loaded {len(filtered)} US stocks")
            return filtered  # ALL stocks - no limit

    # Fetch fresh if file doesn't exist
    print("Fetching stock list from TwelveData API...")
    url = f"https://api.twelvedata.com/stocks?country=United States&apikey={TWELVEDATA_API_KEY}"
    r = requests.get(url, timeout=30)
    data = r.json()
    if 'data' in data:
        with open(STOCKS_LIST_FILE, 'w') as f:
            json.dump(data['data'], f)
        filtered = [
            s['symbol'] for s in data['data']
            if s.get('exchange') in ['NYSE', 'NASDAQ', 'AMEX', 'OTC']
        ]
        return filtered[:15000]
    return []

def load_crypto_symbols():
    """Load crypto symbols from TwelveData list"""
    if os.path.exists(CRYPTO_LIST_FILE):
        with open(CRYPTO_LIST_FILE, 'r') as f:
            data = json.load(f)
            # Filter USD pairs only
            usd_pairs = [
                c['symbol'] for c in data
                if c.get('currency_quote') == 'USD' or '/USD' in c.get('symbol', '')
            ]
            print(f"Loaded {len(usd_pairs)} USD crypto pairs")
            return usd_pairs  # ALL USD pairs - no limit

    # Fetch fresh if file doesn't exist
    print("Fetching crypto list from TwelveData API...")
    url = f"https://api.twelvedata.com/cryptocurrencies?apikey={TWELVEDATA_API_KEY}"
    r = requests.get(url, timeout=30)
    data = r.json()
    if 'data' in data:
        with open(CRYPTO_LIST_FILE, 'w') as f:
            json.dump(data['data'], f)
        usd_pairs = [
            c['symbol'] for c in data['data']
            if c.get('currency_quote') == 'USD' or '/USD' in c.get('symbol', '')
        ]
        print(f"Fetched {len(usd_pairs)} USD crypto pairs")
        return usd_pairs  # ALL USD pairs
    return []

def fetch_weekly_data(symbol, output_size=5000):
    """Fetch weekly time series data - max historical data available"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': '1week',
        'outputsize': output_size,  # Get maximum weeks
        'apikey': TWELVEDATA_API_KEY,
        'format': 'JSON'
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        data = response.json()

        if 'values' not in data:
            error_msg = data.get('message', data.get('status', 'Unknown error'))
            return None, error_msg

        return data, None
    except Exception as e:
        return None, str(e)

def create_table_if_not_exists(table_name, asset_type):
    """Create BigQuery table with appropriate schema"""
    bq = get_bigquery_client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    try:
        bq.get_table(table_ref)
        return True
    except Exception:
        print(f"  Creating table {table_name}...")
        schema = [
            bigquery.SchemaField("symbol", "STRING"),
            bigquery.SchemaField("datetime", "TIMESTAMP"),
            bigquery.SchemaField("week_open", "FLOAT"),
            bigquery.SchemaField("week_high", "FLOAT"),
            bigquery.SchemaField("week_low", "FLOAT"),
            bigquery.SchemaField("week_close", "FLOAT"),
            bigquery.SchemaField("volume", "INTEGER"),
            bigquery.SchemaField("week_range", "FLOAT"),
            bigquery.SchemaField("week_change", "FLOAT"),
            bigquery.SchemaField("week_change_pct", "FLOAT"),
            bigquery.SchemaField("asset_type", "STRING"),
            bigquery.SchemaField("fetched_at", "TIMESTAMP"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        bq.create_table(table)
        return True

def upload_to_bigquery(table_name, records):
    """Upload records to BigQuery"""
    if not records:
        return 0

    bq = get_bigquery_client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    try:
        errors = bq.insert_rows_json(table_ref, records)
        if errors:
            print(f"  BQ errors: {errors[:2]}")
            return 0
        return len(records)
    except Exception as e:
        print(f"  BQ error: {e}")
        return 0

def process_symbol(symbol, asset_type, table_name):
    """Process a single symbol - fetch data and upload"""
    data, error = fetch_weekly_data(symbol)

    if error:
        return 0, error

    if not data or 'values' not in data:
        return 0, "No values in response"

    values = data['values']
    records = []

    for v in values:
        try:
            open_price = float(v.get('open', 0))
            high_price = float(v.get('high', 0))
            low_price = float(v.get('low', 0))
            close_price = float(v.get('close', 0))
            volume = int(float(v.get('volume', 0))) if v.get('volume') else 0

            week_range = high_price - low_price
            week_change = close_price - open_price
            week_change_pct = (week_change / open_price * 100) if open_price > 0 else 0

            # Convert date to full timestamp format for BigQuery
            dt_str = v['datetime']
            if len(dt_str) == 10:  # Just date YYYY-MM-DD
                dt_str = f"{dt_str} 00:00:00"

            record = {
                'symbol': symbol,
                'datetime': dt_str,
                'week_open': open_price,
                'week_high': high_price,
                'week_low': low_price,
                'week_close': close_price,
                'volume': volume,
                'week_range': round(week_range, 4),
                'week_change': round(week_change, 4),
                'week_change_pct': round(week_change_pct, 4),
                'asset_type': asset_type,
                'fetched_at': datetime.now().isoformat()
            }
            records.append(record)
        except Exception as e:
            continue

    uploaded = upload_to_bigquery(table_name, records)
    return uploaded, None

def fetch_stocks(start_index=0, batch_size=100):
    """Fetch weekly data for stocks"""
    print("\n" + "="*70)
    print("FETCHING STOCKS WEEKLY DATA")
    print("="*70)

    symbols = load_stock_symbols()
    total = len(symbols)
    print(f"Total stocks to fetch: {total}")
    print(f"Starting from index: {start_index}")

    table_name = "stocks_weekly_batch"
    create_table_if_not_exists(table_name, "stocks")

    progress = load_progress()
    total_records = 0
    success_count = 0
    error_count = 0

    for i, symbol in enumerate(symbols[start_index:], start=start_index):
        print(f"\n[{i+1}/{total}] {symbol}...", end=" ", flush=True)

        records, error = process_symbol(symbol, "stocks", table_name)

        if error:
            print(f"ERROR: {error[:50]}")
            error_count += 1
        else:
            print(f"OK: {records} weeks")
            total_records += records
            success_count += 1
            progress['stocks_done'].append(symbol)

        progress['stocks'] = i + 1

        # Save progress every 10 symbols
        if (i + 1) % 10 == 0:
            save_progress(progress)
            print(f"\n  Progress saved. Total records: {total_records:,}")

        # Rate limiting
        if i < total - 1:
            time.sleep(REQUEST_DELAY)

        # Batch checkpoint
        if (i + 1 - start_index) >= batch_size:
            print(f"\n\nBatch of {batch_size} complete!")
            print(f"Run again with start_index={i+1} to continue")
            break

    save_progress(progress)
    print(f"\n\nSTOCKS SUMMARY:")
    print(f"  Processed: {success_count + error_count}")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total records: {total_records:,}")

    return total_records

def fetch_crypto(start_index=0, batch_size=50):
    """Fetch weekly data for cryptocurrencies"""
    print("\n" + "="*70)
    print("FETCHING CRYPTO WEEKLY DATA")
    print("="*70)

    symbols = load_crypto_symbols()
    total = len(symbols)
    print(f"Total cryptos to fetch: {total}")
    print(f"Starting from index: {start_index}")

    table_name = "crypto_weekly_batch"
    create_table_if_not_exists(table_name, "crypto")

    progress = load_progress()
    total_records = 0
    success_count = 0
    error_count = 0

    for i, symbol in enumerate(symbols[start_index:], start=start_index):
        print(f"\n[{i+1}/{total}] {symbol}...", end=" ", flush=True)

        records, error = process_symbol(symbol, "crypto", table_name)

        if error:
            print(f"ERROR: {error[:50]}")
            error_count += 1
        else:
            print(f"OK: {records} weeks")
            total_records += records
            success_count += 1
            progress['crypto_done'].append(symbol)

        progress['crypto'] = i + 1

        # Save progress every 10 symbols
        if (i + 1) % 10 == 0:
            save_progress(progress)
            print(f"\n  Progress saved. Total records: {total_records:,}")

        # Rate limiting
        if i < total - 1:
            time.sleep(REQUEST_DELAY)

        # Batch checkpoint
        if (i + 1 - start_index) >= batch_size:
            print(f"\n\nBatch of {batch_size} complete!")
            print(f"Run again with start_index={i+1} to continue")
            break

    save_progress(progress)
    print(f"\n\nCRYPTO SUMMARY:")
    print(f"  Processed: {success_count + error_count}")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total records: {total_records:,}")

    return total_records

def main():
    print("="*70)
    print("BATCH WEEKLY DATA FETCHER - TWELVEDATA")
    print(f"Started: {datetime.now()}")
    print("="*70)

    # Parse command line args
    asset_type = sys.argv[1] if len(sys.argv) > 1 else 'all'
    start_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print(f"\nMode: {asset_type}")
    print(f"Start index: {start_index}")

    total = 0

    if asset_type in ['stocks', 'all']:
        total += fetch_stocks(start_index if asset_type == 'stocks' else 0, batch_size=100)

    if asset_type in ['crypto', 'all']:
        total += fetch_crypto(start_index if asset_type == 'crypto' else 0, batch_size=50)

    print("\n" + "="*70)
    print("BATCH COMPLETE")
    print(f"Total records uploaded: {total:,}")
    print(f"Finished: {datetime.now()}")
    print("="*70)

    print("\n\nTO CONTINUE FETCHING:")
    print("  Stocks: python batch_weekly_data_fetcher.py stocks [start_index]")
    print("  Crypto: python batch_weekly_data_fetcher.py crypto [start_index]")
    print("  All:    python batch_weekly_data_fetcher.py all")

if __name__ == "__main__":
    main()
