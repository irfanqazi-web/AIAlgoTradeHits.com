"""
Populate sector and industry data in v2_stocks_master table
Uses Twelvedata profile API to fetch stock profile information
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import time
import requests
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '84c9a70e54b04809b53e6d4d8b2c6a92'

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

def get_stocks_without_sector():
    """Get all stocks that don't have sector data"""
    query = f"""
    SELECT symbol
    FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master`
    WHERE sector IS NULL OR sector = ''
    """
    result = client.query(query).result()
    return [row.symbol for row in result]

def fetch_stock_profile(symbol):
    """Fetch stock profile from Twelvedata API"""
    url = f"https://api.twelvedata.com/profile?symbol={symbol}&apikey={TWELVEDATA_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'code' in data:  # Error response
            return None
        return data
    except Exception as e:
        print(f"  Error fetching {symbol}: {e}")
        return None

def batch_fetch_profiles(symbols, batch_size=8):
    """Fetch profiles for multiple symbols (Twelvedata allows 8 per request)"""
    url = f"https://api.twelvedata.com/profile?symbol={','.join(symbols)}&apikey={TWELVEDATA_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if isinstance(data, dict) and 'code' in data:  # Single error
            return {}
        if isinstance(data, dict) and len(symbols) == 1:  # Single result
            return {symbols[0]: data}
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"  Batch error: {e}")
        return {}

def update_stock_sector(symbol, sector, industry, description=None, ceo=None, employees=None, website=None):
    """Update sector and industry for a stock"""
    query = f"""
    UPDATE `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master`
    SET
        sector = @sector,
        industry = @industry
    WHERE symbol = @symbol
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
            bigquery.ScalarQueryParameter("sector", "STRING", sector),
            bigquery.ScalarQueryParameter("industry", "STRING", industry),
        ]
    )
    client.query(query, job_config=job_config).result()

def main():
    print("=" * 60)
    print("SECTOR DATA POPULATION SCRIPT")
    print("=" * 60)

    # Get stocks without sector
    print("\nFetching stocks without sector data...")
    symbols = get_stocks_without_sector()
    print(f"Found {len(symbols)} stocks without sector data")

    if not symbols:
        print("All stocks already have sector data!")
        return

    # Process in batches
    batch_size = 8  # Twelvedata allows 8 symbols per request
    total_updated = 0
    total_failed = 0

    print(f"\nProcessing {len(symbols)} symbols in batches of {batch_size}...")
    print("-" * 60)

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(symbols) + batch_size - 1) // batch_size

        print(f"\nBatch {batch_num}/{total_batches}: {', '.join(batch)}")

        # Fetch profiles
        profiles = batch_fetch_profiles(batch)

        # Update each stock
        for symbol in batch:
            profile = profiles.get(symbol, {})
            sector = profile.get('sector', '')
            industry = profile.get('industry', '')

            if sector:
                try:
                    update_stock_sector(symbol, sector, industry)
                    print(f"  + {symbol}: {sector} / {industry}")
                    total_updated += 1
                except Exception as e:
                    print(f"  x {symbol}: Update failed - {e}")
                    total_failed += 1
            else:
                print(f"  - {symbol}: No sector data available")
                total_failed += 1

        # Rate limiting - Twelvedata allows 8 requests per minute on free tier
        # We're doing batch requests, so 1 request per batch
        if i + batch_size < len(symbols):
            print("  Waiting 8 seconds for rate limit...")
            time.sleep(8)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total processed: {len(symbols)}")
    print(f"Successfully updated: {total_updated}")
    print(f"Failed/No data: {total_failed}")

    # Verify final counts
    print("\nVerifying sector distribution...")
    verify_query = f"""
    SELECT
        CASE WHEN sector IS NULL OR sector = '' THEN 'No Sector' ELSE sector END as sector,
        COUNT(*) as count
    FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master`
    GROUP BY 1
    ORDER BY count DESC
    LIMIT 20
    """
    result = client.query(verify_query).result()
    print("\nTop sectors in database:")
    for row in result:
        print(f"  {row.sector}: {row.count} stocks")

if __name__ == "__main__":
    main()
