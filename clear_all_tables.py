"""
Clear all data from BigQuery tables to start fresh
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

def clear_all_tables():
    """Delete all records from all tables"""
    print("="*70)
    print("CLEARING ALL BIGQUERY TABLES")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print("="*70)
    print()

    client = bigquery.Client(project=PROJECT_ID)

    # All tables to clear
    tables = [
        # Crypto tables
        'crypto_analysis',
        'crypto_hourly_data',
        'crypto_5min_top10_gainers',
        # Stock tables
        'stocks_daily',
        'stocks_hourly',
        'stocks_5min'
    ]

    for table_id in tables:
        table_ref = f'{PROJECT_ID}.{DATASET_ID}.{table_id}'

        try:
            # Check if table exists and get count
            query_count = f"SELECT COUNT(*) as count FROM `{table_ref}`"
            result = client.query(query_count).result()
            count = list(result)[0]['count']

            print(f"\n{table_id}:")
            print(f"  Current records: {count:,}")

            if count > 0:
                # Delete all records
                query_delete = f"DELETE FROM `{table_ref}` WHERE TRUE"
                client.query(query_delete).result()
                print(f"  ✓ Cleared {count:,} records")
            else:
                print(f"  • Already empty")

        except Exception as e:
            if "Not found" in str(e):
                print(f"\n{table_id}:")
                print(f"  • Table doesn't exist yet")
            else:
                print(f"\n{table_id}:")
                print(f"  ✗ Error: {e}")

    print("\n" + "="*70)
    print("✓ ALL TABLES CLEARED")
    print("="*70)


if __name__ == "__main__":
    response = input("\n⚠ This will DELETE ALL DATA from all tables. Continue? (yes/no): ")
    if response.lower() == 'yes':
        clear_all_tables()
    else:
        print("Cancelled.")
