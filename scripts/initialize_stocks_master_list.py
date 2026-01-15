"""
ONE-TIME INITIALIZATION: Master Stock List for Weekly Analysis
==============================================================
Fetches ALL US Stocks from TwelveData (20,000+ stocks)
This creates the base reference table that weekly analysis builds upon.

Table: stocks_master_list (linked to stocks_weekly)
Run once to populate, then weekly updates use stocks_weekly

Usage: python initialize_stocks_master_list.py
"""

import requests
import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime, timezone
import time
import sys
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
TWELVE_DATA_API_KEY = '16ee060fd4d34a628a14bcb6f0167565'  # Your $229 plan key
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'stocks_master_list'  # Master reference table for all stocks

# Batch size (TwelveData allows up to 120 symbols per request)
BATCH_SIZE = 100  # Using 100 to be safe


def get_all_us_stocks():
    """Get list of all US stocks from TwelveData /stocks endpoint"""
    print("Step 1: Fetching US stock list from TwelveData /stocks endpoint...")
    url = "https://api.twelvedata.com/stocks"
    params = {
        'country': 'United States',
        'apikey': TWELVE_DATA_API_KEY
    }

    response = requests.get(url, params=params, timeout=60)
    data = response.json()

    if 'data' not in data:
        print(f"Error: {data}")
        return []

    stocks = []
    for item in data['data']:
        # Include Common Stock and ETF only
        if item.get('type') in ['Common Stock', 'ETF']:
            stocks.append({
                'symbol': item['symbol'],
                'name': item['name'],
                'currency': item.get('currency', 'USD'),
                'exchange': item['exchange'],
                'mic_code': item.get('mic_code', ''),
                'country': item.get('country', 'United States'),
                'type': item['type']
            })

    print(f"   Found {len(stocks)} US stocks (Common Stock + ETF)")
    return stocks


def fetch_batch_quotes(symbols):
    """Fetch quotes for multiple symbols in one API call"""
    symbols_str = ','.join(symbols)
    url = "https://api.twelvedata.com/quote"
    params = {
        'symbol': symbols_str,
        'apikey': TWELVE_DATA_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=60)
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching batch: {e}")
        return {}


def process_quote(symbol, quote_data, stock_info):
    """Process a single quote response into a record"""
    try:
        # Handle error responses
        if 'code' in quote_data or 'status' in quote_data:
            if quote_data.get('code') == 400 or quote_data.get('status') == 'error':
                return None

        record = {
            # Identity fields (from /stocks)
            'symbol': symbol,
            'name': stock_info.get('name', quote_data.get('name', '')),
            'currency': stock_info.get('currency', quote_data.get('currency', 'USD')),
            'exchange': stock_info.get('exchange', quote_data.get('exchange', '')),
            'mic_code': stock_info.get('mic_code', quote_data.get('mic_code', '')),
            'country': stock_info.get('country', 'United States'),
            'type': stock_info.get('type', 'Common Stock'),

            # Price fields (from /quote)
            'open': float(quote_data.get('open', 0)) if quote_data.get('open') else None,
            'high': float(quote_data.get('high', 0)) if quote_data.get('high') else None,
            'low': float(quote_data.get('low', 0)) if quote_data.get('low') else None,
            'close': float(quote_data.get('close', 0)) if quote_data.get('close') else None,
            'volume': int(float(quote_data.get('volume', 0))) if quote_data.get('volume') else None,
            'previous_close': float(quote_data.get('previous_close', 0)) if quote_data.get('previous_close') else None,
            'change': float(quote_data.get('change', 0)) if quote_data.get('change') else None,
            'percent_change': float(quote_data.get('percent_change', 0)) if quote_data.get('percent_change') else None,
            'average_volume': int(float(quote_data.get('average_volume', 0))) if quote_data.get('average_volume') else None,

            # 52-week range
            'week_52_high': None,
            'week_52_low': None,

            # Classification (from /quote)
            'sector': quote_data.get('sector', ''),
            'industry': quote_data.get('industry', ''),

            # Metadata
            'quote_datetime': quote_data.get('datetime', ''),
            'is_market_open': quote_data.get('is_market_open', False),
            'fetch_timestamp': datetime.now(timezone.utc).isoformat(),
            'data_source': 'twelvedata',

            # Status flags for weekly analysis
            'is_active': True,
            'last_weekly_update': None
        }

        # Extract 52-week data
        fifty_two = quote_data.get('fifty_two_week', {})
        if fifty_two:
            record['week_52_high'] = float(fifty_two.get('high', 0)) if fifty_two.get('high') else None
            record['week_52_low'] = float(fifty_two.get('low', 0)) if fifty_two.get('low') else None

        return record
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return None


def create_bigquery_table(client):
    """Create the stocks_master_list table"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    schema = [
        # Identity
        bigquery.SchemaField("symbol", "STRING", description="Stock ticker symbol"),
        bigquery.SchemaField("name", "STRING", description="Company name"),
        bigquery.SchemaField("currency", "STRING", description="Trading currency"),
        bigquery.SchemaField("exchange", "STRING", description="Stock exchange"),
        bigquery.SchemaField("mic_code", "STRING", description="Market Identifier Code"),
        bigquery.SchemaField("country", "STRING", description="Country"),
        bigquery.SchemaField("type", "STRING", description="Security type (Common Stock/ETF)"),

        # Price data
        bigquery.SchemaField("open", "FLOAT", description="Opening price"),
        bigquery.SchemaField("high", "FLOAT", description="High price"),
        bigquery.SchemaField("low", "FLOAT", description="Low price"),
        bigquery.SchemaField("close", "FLOAT", description="Closing price"),
        bigquery.SchemaField("volume", "INTEGER", description="Trading volume"),
        bigquery.SchemaField("previous_close", "FLOAT", description="Previous close"),
        bigquery.SchemaField("change", "FLOAT", description="Price change"),
        bigquery.SchemaField("percent_change", "FLOAT", description="Percent change"),
        bigquery.SchemaField("average_volume", "INTEGER", description="Average volume"),

        # 52-week range
        bigquery.SchemaField("week_52_high", "FLOAT", description="52-week high"),
        bigquery.SchemaField("week_52_low", "FLOAT", description="52-week low"),

        # Classification
        bigquery.SchemaField("sector", "STRING", description="Sector"),
        bigquery.SchemaField("industry", "STRING", description="Industry"),

        # Metadata
        bigquery.SchemaField("quote_datetime", "STRING", description="Quote datetime from API"),
        bigquery.SchemaField("is_market_open", "BOOLEAN", description="Is market open"),
        bigquery.SchemaField("fetch_timestamp", "TIMESTAMP", description="When data was fetched"),
        bigquery.SchemaField("data_source", "STRING", description="Data source (twelvedata)"),

        # Status for weekly analysis
        bigquery.SchemaField("is_active", "BOOLEAN", description="Is stock active for tracking"),
        bigquery.SchemaField("last_weekly_update", "TIMESTAMP", description="Last weekly analysis update"),
    ]

    table = bigquery.Table(table_ref, schema=schema)

    try:
        client.create_table(table)
        print(f"   Created table: {table_ref}")
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"   Table exists: {table_ref} (will be replaced)")
        else:
            print(f"   Note: {e}")


def upload_to_bigquery(records, client):
    """Upload records to BigQuery (replaces all data)"""
    if not records:
        return 0

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    df = pd.DataFrame(records)

    # Convert timestamp
    df['fetch_timestamp'] = pd.to_datetime(df['fetch_timestamp'])

    # Replace inf/nan
    df = df.replace([np.inf, -np.inf], np.nan)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Replace all
    )

    try:
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        return len(records)
    except Exception as e:
        print(f"Upload error: {e}")
        return 0


def main():
    """Main initialization function"""
    start_time = time.time()

    print("=" * 70)
    print("   STOCKS MASTER LIST INITIALIZATION")
    print("   One-time setup for Weekly Stock Analysis")
    print("=" * 70)
    print()

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Create table
    print("Step 0: Setting up BigQuery table...")
    create_bigquery_table(client)
    print()

    # Get all stocks
    stocks = get_all_us_stocks()
    if not stocks:
        print("FAILED: Could not get stock list")
        return
    print()

    # Create lookup dict
    stock_lookup = {s['symbol']: s for s in stocks}
    symbols = [s['symbol'] for s in stocks]

    # Fetch quotes in batches
    print(f"Step 2: Fetching quotes for {len(symbols)} stocks...")
    print(f"   Using batch size: {BATCH_SIZE} symbols per API call")
    print(f"   Estimated time: ~{len(symbols) / BATCH_SIZE * 1 / 60:.1f} minutes")
    print()

    all_records = []
    total_batches = (len(symbols) + BATCH_SIZE - 1) // BATCH_SIZE
    successful = 0
    failed = 0

    for i in range(0, len(symbols), BATCH_SIZE):
        batch_num = i // BATCH_SIZE + 1
        batch_symbols = symbols[i:i + BATCH_SIZE]

        # Progress bar style output
        progress = batch_num / total_batches * 100
        print(f"\r   Progress: [{('=' * int(progress/5)):<20}] {progress:.0f}% - Batch {batch_num}/{total_batches}", end="")

        quotes = fetch_batch_quotes(batch_symbols)

        if not quotes:
            failed += len(batch_symbols)
            continue

        batch_success = 0
        if isinstance(quotes, dict):
            if len(batch_symbols) == 1:
                symbol = batch_symbols[0]
                record = process_quote(symbol, quotes, stock_lookup.get(symbol, {}))
                if record:
                    all_records.append(record)
                    batch_success += 1
                else:
                    failed += 1
            else:
                for symbol in batch_symbols:
                    quote_data = quotes.get(symbol, {})
                    if quote_data and 'close' in quote_data:
                        record = process_quote(symbol, quote_data, stock_lookup.get(symbol, {}))
                        if record:
                            all_records.append(record)
                            batch_success += 1
                        else:
                            failed += 1
                    else:
                        failed += 1

        successful += batch_success

        # Rate limiting
        time.sleep(0.9)

    print()  # New line after progress bar
    print()

    # Upload to BigQuery
    print(f"Step 3: Uploading {len(all_records)} records to BigQuery...")
    uploaded = upload_to_bigquery(all_records, client)

    # Summary
    elapsed = time.time() - start_time

    print()
    print("=" * 70)
    print("   INITIALIZATION COMPLETE")
    print("=" * 70)
    print(f"   Total US stocks available:  {len(symbols)}")
    print(f"   Successfully fetched:       {successful}")
    print(f"   Failed:                     {failed}")
    print(f"   Records in master list:    {uploaded}")
    print(f"   Time elapsed:               {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print()
    print(f"   Table: {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
    print()
    print("   NEXT STEP: Run weekly analysis on this master list")
    print("   The stocks_weekly table will reference stocks_master_list")
    print("=" * 70)


if __name__ == "__main__":
    main()
