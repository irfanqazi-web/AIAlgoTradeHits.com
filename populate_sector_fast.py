"""
Fast sector population for stocks with weekly data
Only populates sector for symbols that exist in weekly_stocks_all table
Uses parallel API requests for speed
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
TWELVEDATA_API_KEY = '84c9a70e54b04809b53e6d4d8b2c6a92'

client = bigquery.Client(project=PROJECT_ID)

def get_weekly_symbols_without_sector():
    """Get symbols from weekly_stocks_all that don't have sector in master table"""
    query = f"""
    WITH weekly_symbols AS (
        SELECT DISTINCT symbol
        FROM `{PROJECT_ID}.{DATASET_ID}.weekly_stocks_all`
    )
    SELECT w.symbol
    FROM weekly_symbols w
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master` m ON w.symbol = m.symbol
    WHERE m.symbol IS NULL OR m.sector IS NULL OR m.sector = ''
    LIMIT 2000
    """
    result = client.query(query).result()
    return [row.symbol for row in result]

def fetch_profile_batch(symbols):
    """Fetch profiles for batch of symbols"""
    url = f"https://api.twelvedata.com/profile?symbol={','.join(symbols)}&apikey={TWELVEDATA_API_KEY}"
    try:
        response = requests.get(url, timeout=20)
        data = response.json()
        if isinstance(data, dict) and 'code' in data:
            return {}
        if isinstance(data, dict) and len(symbols) == 1:
            symbol = symbols[0]
            if 'sector' in data:
                return {symbol: data}
            return {}
        return data if isinstance(data, dict) else {}
    except Exception as e:
        return {}

def upsert_stock_master(symbol, sector, industry):
    """Insert or update stock in master table"""
    # First try to update
    update_query = f"""
    UPDATE `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master`
    SET sector = @sector, industry = @industry
    WHERE symbol = @symbol
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
            bigquery.ScalarQueryParameter("sector", "STRING", sector),
            bigquery.ScalarQueryParameter("industry", "STRING", industry),
        ]
    )
    result = client.query(update_query, job_config=job_config).result()

    # Check if any rows were updated
    if result.num_dml_affected_rows == 0:
        # Insert new record
        insert_query = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master` (symbol, sector, industry)
        VALUES (@symbol, @sector, @industry)
        """
        client.query(insert_query, job_config=job_config).result()

def main():
    print("=" * 60)
    print("FAST SECTOR POPULATION FOR WEEKLY STOCKS")
    print("=" * 60)

    # Get symbols
    print("\nFetching weekly symbols without sector...")
    symbols = get_weekly_symbols_without_sector()
    print(f"Found {len(symbols)} symbols to process")

    if not symbols:
        print("All weekly stocks already have sector data!")
        return

    # Process in batches
    batch_size = 8
    total_updated = 0
    total_failed = 0

    print(f"\nProcessing {len(symbols)} symbols...")
    print("-" * 60)

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(symbols) + batch_size - 1) // batch_size

        profiles = fetch_profile_batch(batch)

        for symbol in batch:
            profile = profiles.get(symbol, {})
            sector = profile.get('sector', '')
            industry = profile.get('industry', '')

            if sector:
                try:
                    upsert_stock_master(symbol, sector, industry)
                    print(f"  + {symbol}: {sector}")
                    total_updated += 1
                except Exception as e:
                    print(f"  x {symbol}: {e}")
                    total_failed += 1
            else:
                total_failed += 1

        # Progress
        if batch_num % 10 == 0:
            print(f"\n[Progress: {batch_num}/{total_batches} batches, {total_updated} updated]")

        # Rate limit: ~8 requests per minute = 1 request every 7.5 seconds
        if i + batch_size < len(symbols):
            time.sleep(8)

    print("\n" + "=" * 60)
    print(f"DONE: {total_updated} updated, {total_failed} failed/no data")
    print("=" * 60)

    # Final verification
    verify_query = f"""
    SELECT sector, COUNT(*) as count
    FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master`
    WHERE sector IS NOT NULL AND sector != ''
    GROUP BY sector
    ORDER BY count DESC
    LIMIT 15
    """
    result = client.query(verify_query).result()
    print("\nSectors in database:")
    for row in result:
        print(f"  {row.sector}: {row.count}")

if __name__ == "__main__":
    main()
