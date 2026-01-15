"""
Fast sector population using Yahoo Finance (yfinance)
Populates sector data for stocks in weekly_stocks_all table
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import time
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

def get_weekly_symbols():
    """Get unique symbols from weekly_stocks_all that need sector data"""
    query = f"""
    WITH weekly_symbols AS (
        SELECT DISTINCT symbol
        FROM `{PROJECT_ID}.{DATASET_ID}.weekly_stocks_all`
    )
    SELECT w.symbol
    FROM weekly_symbols w
    LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master` m
        ON w.symbol = m.symbol AND m.sector IS NOT NULL AND m.sector != ''
    WHERE m.symbol IS NULL
    """
    result = client.query(query).result()
    return [row.symbol for row in result]

def fetch_sector_yfinance(symbol):
    """Fetch sector and industry from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'symbol': symbol,
            'sector': info.get('sector', ''),
            'industry': info.get('industry', ''),
            'name': info.get('shortName', ''),
            'exchange': info.get('exchange', '')
        }
    except Exception as e:
        return {'symbol': symbol, 'sector': '', 'industry': '', 'error': str(e)}

def upsert_stock_master(symbol, sector, industry, name='', exchange=''):
    """Insert or update stock in master table"""
    if not sector:
        return False

    # Try update first
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

    if result.num_dml_affected_rows == 0:
        # Insert new record
        insert_query = f"""
        INSERT INTO `{PROJECT_ID}.{DATASET_ID}.v2_stocks_master`
        (symbol, name, sector, industry, exchange)
        VALUES (@symbol, @name, @sector, @industry, @exchange)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
                bigquery.ScalarQueryParameter("name", "STRING", name),
                bigquery.ScalarQueryParameter("sector", "STRING", sector),
                bigquery.ScalarQueryParameter("industry", "STRING", industry),
                bigquery.ScalarQueryParameter("exchange", "STRING", exchange),
            ]
        )
        client.query(insert_query, job_config=job_config).result()

    return True

def main():
    print("=" * 60)
    print("SECTOR POPULATION WITH YFINANCE")
    print("=" * 60)

    # Get symbols
    print("\nFetching symbols from weekly_stocks_all without sector data...")
    symbols = get_weekly_symbols()
    print(f"Found {len(symbols)} symbols to process")

    if not symbols:
        print("All weekly stocks already have sector data!")
        return

    # Process with thread pool for parallel fetching
    total_updated = 0
    total_failed = 0
    batch_size = 50

    print(f"\nProcessing {len(symbols)} symbols in parallel batches...")
    print("-" * 60)

    for batch_start in range(0, len(symbols), batch_size):
        batch = symbols[batch_start:batch_start + batch_size]
        batch_num = batch_start // batch_size + 1
        total_batches = (len(symbols) + batch_size - 1) // batch_size

        print(f"\nBatch {batch_num}/{total_batches} ({len(batch)} symbols)")

        # Parallel fetch with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_sector_yfinance, sym): sym for sym in batch}

            for future in as_completed(futures):
                result = future.result()
                symbol = result['symbol']
                sector = result.get('sector', '')
                industry = result.get('industry', '')
                name = result.get('name', '')
                exchange = result.get('exchange', '')

                if sector:
                    try:
                        upsert_stock_master(symbol, sector, industry, name, exchange)
                        print(f"  + {symbol}: {sector}")
                        total_updated += 1
                    except Exception as e:
                        print(f"  x {symbol}: DB error - {str(e)[:50]}")
                        total_failed += 1
                else:
                    total_failed += 1

        # Small delay between batches to be nice to Yahoo
        if batch_start + batch_size < len(symbols):
            time.sleep(2)

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
