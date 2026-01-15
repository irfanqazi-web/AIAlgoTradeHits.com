"""Check BigQuery table schema"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

# Check stocks_daily schema (if exists)
try:
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.stocks_daily"
    table = client.get_table(table_ref)
    print("stocks_daily schema:")
    print("=" * 70)
    for field in table.schema:
        print(f"  {field.name}: {field.field_type}")
except Exception as e:
    print(f"stocks_daily: {e}")
