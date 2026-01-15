"""
Hourly Stock Data Fetcher - Restore Historical Data
Fetches hourly OHLC data for major US stocks using Yahoo Finance API
Populates v2_stocks_hourly table with 60 days of hourly data
"""

import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
from google.cloud import bigquery
import sys
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Initialize BigQuery client
client = bigquery.Client(project='aialgotradehits')

# Stock symbols - same 60 from the system
STOCK_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'V', 'MA',
    'UNH', 'JNJ', 'WMT', 'PG', 'HD', 'CVX', 'MRK', 'ABBV', 'KO', 'PEP',
    'COST', 'AVGO', 'LLY', 'NKE', 'MCD', 'CSCO', 'ABT', 'ACN', 'TMO', 'DHR',
    'TXN', 'NEE', 'RTX', 'PM', 'BMY', 'HON', 'UNP', 'AMD', 'QCOM', 'ORCL',
    'BA', 'INTC', 'GE', 'LIN', 'CMCSA', 'COP', 'SPGI', 'INTU', 'SBUX', 'GILD',
    'T', 'CAT', 'AMGN', 'CVS', 'AXP', 'BLK', 'BKNG', 'DE', 'DUK', 'LRCX'
]

print("=" * 80)
print("HOURLY STOCK DATA FETCHER - RESTORE HISTORICAL DATA")
print("=" * 80)
print(f"\nTotal symbols to fetch: {len(STOCK_SYMBOLS)}")
print(f"Fetching: 60 days of hourly data")
print(f"Target table: v2_stocks_hourly")
print("\n" + "=" * 80)

# Calculate date range - 60 days of hourly data
end_date = datetime.now()
start_date = end_date - timedelta(days=60)

all_stock_data = []
failed_symbols = []
successful_symbols = 0

for idx, symbol in enumerate(STOCK_SYMBOLS, 1):
    try:
        print(f"\n[{idx}/{len(STOCK_SYMBOLS)}] Fetching {symbol}...", end=' ')

        # Create ticker object
        ticker = yf.Ticker(symbol)

        # Fetch hourly historical data
        hist = ticker.history(start=start_date, end=end_date, interval='1h')

        if hist.empty:
            print(f"NO DATA")
            failed_symbols.append({'symbol': symbol, 'error': 'No data returned'})
            continue

        # Get stock info
        try:
            info = ticker.info
            company_name = info.get('longName', symbol)
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            exchange = info.get('exchange', 'Unknown')
        except:
            company_name = symbol
            sector = 'Unknown'
            industry = 'Unknown'
            exchange = 'Unknown'

        # Reset index to get datetime as column
        hist = hist.reset_index()

        # Add metadata columns
        hist['symbol'] = symbol
        hist['name'] = company_name
        hist['exchange'] = exchange
        hist['currency'] = 'USD'

        # Calculate percent change
        if len(hist) > 0:
            hist['percent_change'] = ((hist['Close'] - hist['Open']) / hist['Open'] * 100).round(2)
        else:
            hist['percent_change'] = 0.0

        # Rename columns to match BigQuery schema
        hist = hist.rename(columns={
            'Datetime': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        # Select only needed columns
        hist = hist[['datetime', 'open', 'high', 'low', 'close', 'volume',
                     'symbol', 'name', 'exchange', 'currency', 'percent_change']]

        # Convert datetime to timezone-naive (BigQuery TIMESTAMP doesn't support tz)
        hist['datetime'] = pd.to_datetime(hist['datetime']).dt.tz_localize(None)

        # Add to collection
        all_stock_data.append(hist)
        successful_symbols += 1

        print(f"OK ({len(hist)} rows)")
        time.sleep(0.1)  # Rate limiting

    except Exception as e:
        print(f"ERROR: {str(e)}")
        failed_symbols.append({'symbol': symbol, 'error': str(e)})
        continue

print("\n" + "=" * 80)
print(f"Fetch complete! Successful: {successful_symbols}/{len(STOCK_SYMBOLS)}")
print("=" * 80)

if all_stock_data:
    # Combine all dataframes
    print("\nCombining all data...")
    combined_df = pd.concat(all_stock_data, ignore_index=True)
    print(f"Total rows to upload: {len(combined_df):,}")

    # Upload to BigQuery
    print(f"\nUploading to BigQuery table: v2_stocks_hourly...")
    table_id = 'aialgotradehits.crypto_trading_data.v2_stocks_hourly'

    try:
        # Append to existing table
        job = client.load_table_from_dataframe(
            combined_df,
            table_id,
            job_config=bigquery.LoadJobConfig(
                write_disposition='WRITE_APPEND',
                schema_update_options=[
                    bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
                ]
            )
        )
        job.result()  # Wait for completion

        print(f"✓ Successfully uploaded {len(combined_df):,} rows to v2_stocks_hourly")

        # Verify
        verify_query = f"""
        SELECT COUNT(*) as total,
               COUNT(DISTINCT symbol) as symbols,
               MIN(datetime) as min_date,
               MAX(datetime) as max_date
        FROM `{table_id}`
        """
        result = client.query(verify_query).to_dataframe()
        print(f"\nVerification:")
        print(f"  Total rows: {result['total'].values[0]:,}")
        print(f"  Unique symbols: {result['symbols'].values[0]}")
        print(f"  Date range: {result['min_date'].values[0]} to {result['max_date'].values[0]}")

    except Exception as e:
        print(f"✗ Error uploading to BigQuery: {str(e)}")
        sys.exit(1)

else:
    print("\n⚠ No data fetched!")
    sys.exit(1)

if failed_symbols:
    print(f"\n⚠ Failed symbols ({len(failed_symbols)}):")
    for fail in failed_symbols:
        print(f"  - {fail['symbol']}: {fail['error']}")

print("\n" + "=" * 80)
print("✓ HOURLY DATA RESTORATION COMPLETE!")
print("=" * 80)
print("\nNext step: Run calculate_hourly_indicators.py to populate stocks_hourly_clean")
