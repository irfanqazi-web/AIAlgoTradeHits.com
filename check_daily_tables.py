"""Check Daily Crypto and Stock Tables"""
from google.cloud import bigquery
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

# Check Daily Crypto
crypto_query = f"""
SELECT
    COUNT(*) as total_records,
    MAX(DATE(datetime)) as latest_date,
    COUNT(DISTINCT pair) as unique_pairs
FROM `{PROJECT_ID}.{DATASET_ID}.crypto_analysis`
"""

print("=" * 60)
print("DAILY CRYPTO TABLE (crypto_analysis)")
print("=" * 60)
result = client.query(crypto_query).result()
for row in result:
    print(f"Total Records: {row.total_records:,}")
    print(f"Latest Date: {row.latest_date}")
    print(f"Unique Pairs: {row.unique_pairs}")

# Check Daily Stock
stock_query = f"""
SELECT
    COUNT(*) as total_records,
    MAX(DATE(datetime)) as latest_date,
    COUNT(DISTINCT symbol) as unique_symbols
FROM `{PROJECT_ID}.{DATASET_ID}.stock_analysis`
"""

print("\n" + "=" * 60)
print("DAILY STOCK TABLE (stock_analysis)")
print("=" * 60)
result = client.query(stock_query).result()
for row in result:
    print(f"Total Records: {row.total_records:,}")
    print(f"Latest Date: {row.latest_date}")
    print(f"Unique Symbols: {row.unique_symbols}")

print("\n" + "=" * 60)
print("✓ VERIFICATION COMPLETE")
print("=" * 60)
