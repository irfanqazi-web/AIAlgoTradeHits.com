"""
Week-by-Week Batch Data Fetcher for ALL Asset Types
- Fetches ONE WEEK at a time for ALL assets
- All 7 asset types: stocks, crypto, forex, etfs, indices, commodities, bonds
- Goes backwards through history week by week

Run: python weekly_batch_all_assets.py [weeks_back]
Example: python weekly_batch_all_assets.py 0  # Start from most recent week
"""
import sys
import io
import os
import json
import time
import requests
from datetime import datetime, timedelta
from google.cloud import bigquery

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdout.reconfigure(line_buffering=True)

# Configuration
TWELVEDATA_API_KEY = "16ee060fd4d34a628a14bcb6f0167565"
PROJECT_ID = "cryptobot-462709"
DATASET_ID = "crypto_trading_data"

# Rate limiting: TwelveData $229/month Growth plan = 800 requests/minute
# Using 700 to leave some buffer for other API calls
REQUESTS_PER_MINUTE = 700
REQUEST_DELAY = 60 / REQUESTS_PER_MINUTE  # ~0.086 seconds between requests

# Progress tracking
PROGRESS_FILE = "C:/1AITrading/Trading/weekly_progress.json"
SYMBOLS_CACHE_FILE = "C:/1AITrading/Trading/all_symbols_cache.json"

# BigQuery client
client = None

# Asset type configurations
ASSET_CONFIGS = {
    'stocks': {
        'table': 'weekly_stocks_all',
        'api_endpoint': 'stocks',
        'filter_key': 'country',
        'filter_value': 'United States',
        'symbol_key': 'symbol',
        'limit': 20000  # All US stocks
    },
    'crypto': {
        'table': 'weekly_crypto_all',
        'api_endpoint': 'cryptocurrencies',
        'filter_key': 'currency_quote',
        'filter_value': 'USD',
        'symbol_key': 'symbol',
        'limit': 1500  # All USD crypto pairs
    },
    'forex': {
        'table': 'weekly_forex_all',
        'api_endpoint': 'forex_pairs',
        'filter_key': 'currency_quote',
        'filter_value': 'USD',
        'symbol_key': 'symbol',
        'limit': 500
    },
    'etfs': {
        'table': 'weekly_etfs_all',
        'api_endpoint': 'etf',
        'filter_key': 'country',
        'filter_value': 'United States',
        'symbol_key': 'symbol',
        'limit': 5000
    },
    'indices': {
        'table': 'weekly_indices_all',
        'api_endpoint': 'indices',
        'filter_key': 'country',
        'filter_value': 'United States',
        'symbol_key': 'symbol',
        'limit': 500
    },
    'commodities': {
        'table': 'weekly_commodities_all',
        'api_endpoint': 'commodities',
        'filter_key': None,  # No filter needed
        'filter_value': None,
        'symbol_key': 'symbol',
        'limit': 100
    }
}

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
    return {
        'current_week': 0,
        'weeks_completed': [],
        'last_run': None,
        'total_records': 0
    }

def save_progress(progress):
    """Save progress to file"""
    progress['last_run'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def load_symbols_cache():
    """Load cached symbols"""
    if os.path.exists(SYMBOLS_CACHE_FILE):
        with open(SYMBOLS_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_symbols_cache(cache):
    """Save symbols cache"""
    with open(SYMBOLS_CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def fetch_symbols(asset_type):
    """Fetch symbols for an asset type from TwelveData"""
    config = ASSET_CONFIGS[asset_type]
    cache = load_symbols_cache()

    # Check cache first
    if asset_type in cache and len(cache[asset_type]) > 0:
        print(f"  Using cached {len(cache[asset_type])} {asset_type} symbols")
        return cache[asset_type][:config['limit']]

    print(f"  Fetching {asset_type} symbols from TwelveData API...")

    url = f"https://api.twelvedata.com/{config['api_endpoint']}?apikey={TWELVEDATA_API_KEY}"

    try:
        r = requests.get(url, timeout=60)
        data = r.json()

        if 'data' not in data:
            print(f"    Error: {data.get('message', 'No data returned')}")
            return []

        symbols = []
        for item in data['data']:
            # Apply filter if configured
            if config['filter_key']:
                if item.get(config['filter_key']) == config['filter_value']:
                    symbols.append(item[config['symbol_key']])
                elif config['filter_value'] in str(item.get(config['symbol_key'], '')):
                    # For crypto pairs like BTC/USD
                    symbols.append(item[config['symbol_key']])
            else:
                symbols.append(item[config['symbol_key']])

        # Save to cache
        cache[asset_type] = symbols
        save_symbols_cache(cache)

        print(f"    Found {len(symbols)} {asset_type} symbols")
        return symbols[:config['limit']]

    except Exception as e:
        print(f"    Error fetching symbols: {e}")
        return []

def get_week_dates(weeks_back):
    """Get start and end date for a specific week"""
    # Find the most recent Sunday (end of week)
    today = datetime.now()
    days_since_sunday = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(days=days_since_sunday)

    # Go back the specified number of weeks
    week_end = last_sunday - timedelta(weeks=weeks_back)
    week_start = week_end - timedelta(days=6)

    return week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')

def create_table_if_not_exists(table_name):
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
            bigquery.SchemaField("week_start", "DATE"),
            bigquery.SchemaField("week_end", "DATE"),
            bigquery.SchemaField("open", "FLOAT"),
            bigquery.SchemaField("high", "FLOAT"),
            bigquery.SchemaField("low", "FLOAT"),
            bigquery.SchemaField("close", "FLOAT"),
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

def fetch_week_data(symbol, start_date, end_date):
    """Fetch weekly data for a specific date range"""
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': '1week',
        'start_date': start_date,
        'end_date': end_date,
        'apikey': TWELVEDATA_API_KEY,
        'format': 'JSON'
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'values' not in data:
            error_msg = data.get('message', data.get('status', 'Unknown error'))
            return None, error_msg

        return data, None
    except Exception as e:
        return None, str(e)

def upload_to_bigquery(table_name, records):
    """Upload records to BigQuery"""
    if not records:
        return 0

    bq = get_bigquery_client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    try:
        errors = bq.insert_rows_json(table_ref, records)
        if errors:
            print(f"    BQ errors: {errors[:1]}")
            return 0
        return len(records)
    except Exception as e:
        print(f"    BQ error: {e}")
        return 0

def process_week_for_asset(asset_type, symbols, start_date, end_date, batch_size=25):
    """Process one week of data for all symbols of an asset type"""
    config = ASSET_CONFIGS[asset_type]
    table_name = config['table']

    create_table_if_not_exists(table_name)

    total_uploaded = 0
    success_count = 0
    error_count = 0
    request_count = 0

    # Process in batches to show progress
    for batch_start in range(0, len(symbols), batch_size):
        batch_symbols = symbols[batch_start:batch_start + batch_size]
        batch_records = []

        for symbol in batch_symbols:
            request_count += 1
            # Show per-symbol progress
            if request_count % 5 == 0:
                print(f"    [{request_count}/{len(symbols)}] Processing {symbol}...", flush=True)

            data, error = fetch_week_data(symbol, start_date, end_date)

            if error:
                if 'not found' not in error.lower() and 'no data' not in error.lower():
                    error_count += 1
                continue

            if not data or 'values' not in data:
                continue

            for v in data['values']:
                try:
                    open_price = float(v.get('open', 0))
                    high_price = float(v.get('high', 0))
                    low_price = float(v.get('low', 0))
                    close_price = float(v.get('close', 0))
                    volume = int(float(v.get('volume', 0))) if v.get('volume') else 0

                    week_range = high_price - low_price
                    week_change = close_price - open_price
                    week_change_pct = (week_change / open_price * 100) if open_price > 0 else 0

                    # Convert date to timestamp
                    dt_str = v['datetime']
                    if len(dt_str) == 10:
                        dt_str = f"{dt_str} 00:00:00"

                    record = {
                        'symbol': symbol,
                        'datetime': dt_str,
                        'week_start': start_date,
                        'week_end': end_date,
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'close': close_price,
                        'volume': volume,
                        'week_range': round(week_range, 4),
                        'week_change': round(week_change, 4),
                        'week_change_pct': round(week_change_pct, 4),
                        'asset_type': asset_type,
                        'fetched_at': datetime.now().isoformat()
                    }
                    batch_records.append(record)
                    success_count += 1
                except Exception:
                    continue

            # Rate limiting
            time.sleep(REQUEST_DELAY)

        # Upload batch
        if batch_records:
            uploaded = upload_to_bigquery(table_name, batch_records)
            total_uploaded += uploaded
            print(f"    Batch uploaded: {uploaded} records to {table_name}", flush=True)

        # Progress update
        processed = min(batch_start + batch_size, len(symbols))
        print(f"    {asset_type}: {processed}/{len(symbols)} symbols processed, {total_uploaded} records uploaded", flush=True)

    return total_uploaded, success_count, error_count

def fetch_week_all_assets(weeks_back):
    """Fetch one week of data for ALL asset types"""
    start_date, end_date = get_week_dates(weeks_back)

    print(f"\n{'='*70}")
    print(f"FETCHING WEEK {weeks_back}: {start_date} to {end_date}")
    print(f"{'='*70}")

    progress = load_progress()
    total_records = 0

    for asset_type in ASSET_CONFIGS.keys():
        print(f"\n--- {asset_type.upper()} ---")

        symbols = fetch_symbols(asset_type)
        if not symbols:
            print(f"  No symbols found for {asset_type}")
            continue

        uploaded, success, errors = process_week_for_asset(
            asset_type, symbols, start_date, end_date
        )

        total_records += uploaded
        print(f"  {asset_type}: {uploaded} records uploaded, {errors} errors")

    # Save progress
    if weeks_back not in progress['weeks_completed']:
        progress['weeks_completed'].append(weeks_back)
    progress['current_week'] = weeks_back
    progress['total_records'] += total_records
    save_progress(progress)

    print(f"\n{'='*70}")
    print(f"WEEK {weeks_back} COMPLETE: {total_records} total records")
    print(f"{'='*70}")

    return total_records

def main():
    print("="*70)
    print("WEEK-BY-WEEK ALL ASSETS DATA FETCHER")
    print(f"Started: {datetime.now()}")
    print("="*70)

    # Parse command line args
    start_week = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    max_weeks = int(sys.argv[2]) if len(sys.argv) > 2 else 52  # Default 1 year

    print(f"\nStarting from week {start_week}, fetching up to {max_weeks} weeks")

    progress = load_progress()
    total = 0

    for week in range(start_week, start_week + max_weeks):
        # Skip already completed weeks
        if week in progress.get('weeks_completed', []):
            print(f"\nWeek {week} already completed, skipping...")
            continue

        records = fetch_week_all_assets(week)
        total += records

        print(f"\nCumulative total: {total:,} records")
        print(f"To resume from here: python weekly_batch_all_assets.py {week + 1}")

    print("\n" + "="*70)
    print("ALL WEEKS COMPLETE")
    print(f"Total records: {total:,}")
    print(f"Finished: {datetime.now()}")
    print("="*70)

if __name__ == "__main__":
    main()
