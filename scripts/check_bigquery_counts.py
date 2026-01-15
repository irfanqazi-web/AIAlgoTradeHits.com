"""
Check record counts in all BigQuery tables for cryptobot-462709
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

def check_table_counts():
    """Check counts in all three tables"""
    print("="*70)
    print("CHECKING BIGQUERY TABLE COUNTS")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print("="*70)
    print()

    client = bigquery.Client(project=PROJECT_ID)

    tables = {
        'Daily (crypto_analysis)': 'crypto_analysis',
        'Hourly (crypto_hourly_data)': 'crypto_hourly_data',
        '5-Minute (crypto_5min_top10_gainers)': 'crypto_5min_top10_gainers'
    }

    for table_name, table_id in tables.items():
        print(f"\n{'='*70}")
        print(f"Table: {table_name}")
        print('='*70)

        table_ref = f'{PROJECT_ID}.{DATASET_ID}.{table_id}'

        # Total count
        query_total = f"SELECT COUNT(*) as total FROM `{table_ref}`"
        try:
            result = client.query(query_total).result()
            total = list(result)[0]['total']
            print(f"Total Records: {total:,}")

            if total == 0:
                print("⚠ Table is empty - schedulers may not have run yet")
                continue

            # Recent data count
            if table_id == 'crypto_analysis':
                # Daily - check last 3 days
                query_recent = f"""
                SELECT DATE(datetime) as date, COUNT(*) as count
                FROM `{table_ref}`
                WHERE DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
                GROUP BY date
                ORDER BY date DESC
                """
            elif table_id == 'crypto_hourly_data':
                # Hourly - check last 6 hours
                query_recent = f"""
                SELECT
                    TIMESTAMP_TRUNC(datetime, HOUR) as hour,
                    COUNT(*) as count
                FROM `{table_ref}`
                WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 6 HOUR)
                GROUP BY hour
                ORDER BY hour DESC
                """
            else:
                # 5-minute - check last hour
                query_recent = f"""
                SELECT
                    TIMESTAMP_TRUNC(datetime, MINUTE) as minute,
                    COUNT(*) as count
                FROM `{table_ref}`
                WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
                GROUP BY minute
                ORDER BY minute DESC
                LIMIT 12
                """

            result = client.query(query_recent).result()
            recent_data = list(result)

            if recent_data:
                print("\nRecent Data:")
                for row in recent_data:
                    if table_id == 'crypto_analysis':
                        print(f"  {row['date']}: {row['count']:,} records")
                    elif table_id == 'crypto_hourly_data':
                        print(f"  {row['hour']}: {row['count']:,} records")
                    else:
                        print(f"  {row['minute']}: {row['count']:,} records")
            else:
                print("⚠ No recent data found")

            # Latest timestamp
            query_latest = f"SELECT MAX(datetime) as latest FROM `{table_ref}`"
            result = client.query(query_latest).result()
            latest = list(result)[0]['latest']
            if latest:
                print(f"\nLatest Data: {latest}")

            # Unique pairs
            query_pairs = f"SELECT COUNT(DISTINCT pair) as pairs FROM `{table_ref}`"
            result = client.query(query_pairs).result()
            pairs = list(result)[0]['pairs']
            print(f"Unique Pairs: {pairs:,}")

        except Exception as e:
            print(f"✗ Error querying table: {e}")

    print("\n" + "="*70)
    print("✓ BIGQUERY CHECK COMPLETE")
    print("="*70)


if __name__ == "__main__":
    check_table_counts()
