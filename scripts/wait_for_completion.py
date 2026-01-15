"""
Wait for all Cloud Functions to complete and verify data population
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import time
from datetime import datetime

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

TABLES = {
    'crypto_analysis': {
        'name': 'Daily Crypto Data',
        'expected_min': 400,  # Minimum expected (accounting for insufficient data pairs)
        'expected_max': 675
    },
    'crypto_hourly_data': {
        'name': 'Hourly Crypto Data',
        'expected_min': 400,
        'expected_max': 675
    },
    'crypto_5min_top10_gainers': {
        'name': '5-Minute Top 10 Gainers',
        'expected_min': 100,
        'expected_max': 120
    }
}

def get_table_count(client, table_id):
    """Get count of records in a table"""
    try:
        query = f"SELECT COUNT(*) as count FROM `{PROJECT_ID}.{DATASET_ID}.{table_id}`"
        result = client.query(query).result()
        row = next(result)
        return row.count
    except Exception as e:
        return 0

def get_detailed_stats(client, table_id):
    """Get detailed statistics for a table"""
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
            'total': row.total_records,
            'pairs': row.unique_pairs,
            'latest': row.latest_datetime,
            'earliest': row.earliest_datetime
        }
    except Exception as e:
        return {'total': 0, 'pairs': 0, 'latest': None, 'earliest': None}

def print_progress(iteration, counts):
    """Print current progress"""
    print(f"\n{'='*70}")
    print(f"Check #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}")

    for table_id, info in TABLES.items():
        count = counts.get(table_id, 0)
        expected_min = info['expected_min']
        status = "✓" if count >= expected_min else "⏳"
        print(f"{status} {info['name']}: {count:,} records")

    total = sum(counts.values())
    print(f"\nTotal Records: {total:,}")
    print(f"{'='*70}")

def main():
    client = bigquery.Client(project=PROJECT_ID)

    print("="*70)
    print("WAITING FOR DATA COLLECTION TO COMPLETE")
    print("="*70)
    print("\nMonitoring BigQuery tables every 2 minutes...")
    print("This will automatically stop when all tables have data.\n")

    iteration = 0
    start_time = time.time()

    while True:
        iteration += 1

        # Get current counts
        counts = {}
        for table_id in TABLES.keys():
            counts[table_id] = get_table_count(client, table_id)

        # Print progress
        print_progress(iteration, counts)

        # Check if all tables have minimum data
        all_complete = all(
            counts[tid] >= TABLES[tid]['expected_min']
            for tid in TABLES.keys()
        )

        if all_complete:
            print("\n✓ All tables have data! Getting detailed statistics...\n")
            break

        # Wait 2 minutes before next check
        elapsed = time.time() - start_time
        print(f"\nElapsed time: {elapsed/60:.1f} minutes")
        print("Next check in 2 minutes... (Press Ctrl+C to stop)")

        try:
            time.sleep(120)  # Wait 2 minutes
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")
            return

    # Get detailed statistics
    print("="*70)
    print("FINAL DATA COLLECTION REPORT")
    print("="*70)

    for table_id, info in TABLES.items():
        stats = get_detailed_stats(client, table_id)

        print(f"\n{info['name']} ({table_id})")
        print("-"*70)
        print(f"Total Records: {stats['total']:,}")
        print(f"Unique Pairs: {stats['pairs']}")

        if stats['latest']:
            print(f"Latest Data: {stats['latest']}")
        if stats['earliest']:
            print(f"Earliest Data: {stats['earliest']}")

        # Status check
        if stats['total'] >= info['expected_min']:
            print(f"Status: ✓ COMPLETE")
        else:
            print(f"Status: ⚠ Incomplete (expected min: {info['expected_min']})")

    # Overall summary
    total_records = sum(get_table_count(client, tid) for tid in TABLES.keys())

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total Records Across All Tables: {total_records:,}")
    print(f"Total Time: {(time.time() - start_time)/60:.1f} minutes")
    print("\n✓ DATA COLLECTION COMPLETE!")
    print("\nYour crypto trading data pipeline is now operational!")
    print("Automated schedulers will continue collecting data 24/7.")
    print("="*70)

if __name__ == "__main__":
    main()
