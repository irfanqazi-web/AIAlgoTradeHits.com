"""
Monitor BigQuery table data collection progress
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import time

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

TABLES = {
    'crypto_analysis': {
        'name': 'Daily Crypto Data',
        'expected_records': 675,
        'description': 'Daily OHLCV data with technical indicators'
    },
    'crypto_hourly_data': {
        'name': 'Hourly Crypto Data',
        'expected_records': 675,
        'description': 'Hourly OHLCV data with technical indicators'
    },
    'crypto_5min_top10_gainers': {
        'name': '5-Minute Top 10 Gainers',
        'expected_records': 120,
        'description': '5-minute data for top 10 gainers'
    }
}

def check_table_status(client, table_id, table_info):
    """Check the status of a BigQuery table"""
    try:
        query = f"""
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT pair) as unique_pairs,
            MAX(datetime) as latest_datetime,
            MIN(datetime) as earliest_datetime
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_id}`
        """

        result = client.query(query).result()
        row = next(result)

        return {
            'total_records': row.total_records,
            'unique_pairs': row.unique_pairs,
            'latest_datetime': row.latest_datetime,
            'earliest_datetime': row.earliest_datetime,
            'expected': table_info['expected_records']
        }

    except Exception as e:
        return {
            'error': str(e),
            'total_records': 0,
            'unique_pairs': 0
        }


def print_status(status_data):
    """Print formatted status"""
    print("\n" + "="*70)
    print("BIGQUERY DATA COLLECTION STATUS")
    print("="*70)

    for table_id, table_info in TABLES.items():
        print(f"\n{table_info['name']} ({table_id})")
        print(f"Description: {table_info['description']}")
        print("-" * 70)

        if table_id in status_data:
            data = status_data[table_id]

            if 'error' in data:
                print(f"✗ Error: {data['error']}")
            else:
                total = data['total_records']
                expected = data['expected']
                pairs = data['unique_pairs']
                latest = data['latest_datetime']
                earliest = data['earliest_datetime']

                percentage = (total / expected * 100) if expected > 0 else 0

                if total == 0:
                    status = "⚠ EMPTY - Waiting for data"
                elif total < expected:
                    status = f"⏳ IN PROGRESS - {percentage:.1f}% complete"
                else:
                    status = "✓ COMPLETE"

                print(f"Status: {status}")
                print(f"Total Records: {total:,} / {expected:,}")
                print(f"Unique Pairs: {pairs}")
                if latest:
                    print(f"Latest Data: {latest}")
                if earliest:
                    print(f"Earliest Data: {earliest}")

    print("\n" + "="*70)


def main(monitor=False, interval=60):
    """Monitor table status"""
    client = bigquery.Client(project=PROJECT_ID)

    if monitor:
        print("="*70)
        print("CONTINUOUS MONITORING MODE")
        print(f"Checking every {interval} seconds. Press Ctrl+C to stop.")
        print("="*70)

        try:
            while True:
                status_data = {}
                for table_id, table_info in TABLES.items():
                    status_data[table_id] = check_table_status(client, table_id, table_info)

                print_status(status_data)

                # Check if all tables have data
                all_have_data = all(
                    status_data[tid]['total_records'] > 0
                    for tid in TABLES.keys()
                )

                if all_have_data:
                    print("\n✓ All tables have data! Data collection is working.")
                    break

                print(f"\nNext check in {interval} seconds...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")

    else:
        # Single check
        status_data = {}
        for table_id, table_info in TABLES.items():
            status_data[table_id] = check_table_status(client, table_id, table_info)

        print_status(status_data)

        # Summary
        total_records = sum(s['total_records'] for s in status_data.values())
        if total_records == 0:
            print("⚠ No data found in any tables yet.")
            print("\nThis is normal if you just triggered the functions.")
            print("They may take 15-30 minutes to complete.\n")
            print("Run with --monitor to continuously check for data:")
            print("  python monitor_data_collection.py --monitor")
        else:
            print(f"\n✓ Found {total_records:,} total records across all tables!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Monitor BigQuery data collection')
    parser.add_argument('--monitor', action='store_true', help='Continuous monitoring mode')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds (default: 60)')

    args = parser.parse_args()

    main(monitor=args.monitor, interval=args.interval)
