"""
Recreate crypto tables with new Twelve Data schema (71 indicators)
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

print("="*70)
print("RECREATING CRYPTO TABLES WITH NEW SCHEMA")
print("="*70)
print()

# Delete old crypto tables
tables_to_recreate = ['crypto_analysis', 'crypto_hourly_data', 'crypto_5min_top10_gainers']

for table_name in tables_to_recreate:
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    try:
        client.delete_table(table_ref)
        print(f"✓ Deleted old {table_name}")
    except Exception as e:
        print(f"  Note: {table_name} - {e}")

print("\nNow run fetch_fresh_twelvedata.py to reload data with new schema")
print("="*70)
