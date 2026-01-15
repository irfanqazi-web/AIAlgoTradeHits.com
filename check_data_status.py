"""
Check data status in BigQuery tables
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

print("=" * 70)
print("BIGQUERY DATA STATUS CHECK")
print("=" * 70)

tables = [
    'stocks_daily', 'crypto_daily', 'forex_daily',
    'etfs_daily', 'indices_daily', 'commodities_daily'
]

total_rows = 0

for table in tables:
    try:
        query = f"""
        SELECT
            COUNT(*) as row_count,
            COUNT(DISTINCT symbol) as unique_symbols,
            MIN(datetime) as earliest,
            MAX(datetime) as latest
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        """
        result = list(client.query(query).result())[0]

        print(f"\n{table}:")
        print(f"  Rows: {result.row_count:,}")
        print(f"  Unique symbols: {result.unique_symbols}")
        print(f"  Date range: {result.earliest} to {result.latest}")

        total_rows += result.row_count

        # Show symbols
        symbols_query = f"""
        SELECT DISTINCT symbol FROM `{PROJECT_ID}.{DATASET_ID}.{table}` LIMIT 20
        """
        symbols = [row.symbol for row in client.query(symbols_query).result()]
        print(f"  Symbols: {', '.join(symbols)}")

    except Exception as e:
        print(f"\n{table}: Error - {e}")

print("\n" + "=" * 70)
print(f"TOTAL ROWS ACROSS ALL TABLES: {total_rows:,}")
print("=" * 70)
