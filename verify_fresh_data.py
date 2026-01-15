"""Verify fresh data loaded"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

print("="*70)
print("FRESH DATA VERIFICATION")
print("="*70)
print()

tables = {
    'stocks_daily': 'NVDA Daily',
    'stocks_hourly': 'NVDA Hourly',
    'stocks_5min': 'NVDA 5-minute',
    'crypto_analysis': 'BTC/USD Daily',
    'crypto_hourly_data': 'BTC/USD Hourly',
    'crypto_5min_top10_gainers': 'BTC/USD 5-minute'
}

for table_name, description in tables.items():
    query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`"
    try:
        result = client.query(query).result()
        count = list(result)[0]['cnt']
        print(f"{description:25} {count:>5} records")
    except Exception as e:
        print(f"{description:25} ERROR: {e}")

print()
print("="*70)
