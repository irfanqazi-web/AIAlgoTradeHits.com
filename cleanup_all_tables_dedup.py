"""
Comprehensive Data Cleanup and Deduplication Script
Cleans all BigQuery tables to ensure unique, high-quality data
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime
import time

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Tables to clean with their unique key columns
TABLES_CONFIG = {
    'stocks_daily_clean': {
        'unique_key': ['symbol', 'datetime'],
        'order_by': 'fetch_timestamp DESC',  # Keep most recent
        'description': 'Stocks Daily Data'
    },
    'crypto_daily_clean': {
        'unique_key': ['symbol', 'datetime'],
        'order_by': 'fetch_timestamp DESC',
        'description': 'Crypto Daily Data'
    },
    'etfs_daily_clean': {
        'unique_key': ['symbol', 'datetime'],
        'order_by': 'fetch_timestamp DESC',
        'description': 'ETFs Daily Data'
    },
    'stocks_hourly_clean': {
        'unique_key': ['symbol', 'datetime'],
        'order_by': 'fetch_timestamp DESC',
        'description': 'Stocks Hourly Data'
    },
    'crypto_hourly_clean': {
        'unique_key': ['symbol', 'datetime'],
        'order_by': 'fetch_timestamp DESC',
        'description': 'Crypto Hourly Data'
    },
    'forex_daily_clean': {
        'unique_key': ['symbol', 'datetime'],
        'order_by': 'fetch_timestamp DESC',
        'description': 'Forex Daily Data'
    },
    'indices_daily_clean': {
        'unique_key': ['symbol', 'datetime'],
        'order_by': 'fetch_timestamp DESC',
        'description': 'Indices Daily Data'
    },
    'fred_economic_data': {
        'unique_key': ['series_id', 'datetime'],
        'order_by': 'fetched_at DESC',
        'description': 'FRED Economic Data'
    },
    'finnhub_recommendations': {
        'unique_key': ['symbol', 'period'],
        'order_by': 'fetch_timestamp DESC',
        'description': 'Finnhub Analyst Recommendations'
    },
    'cmc_crypto_rankings': {
        'unique_key': ['symbol', 'datetime'],
        'order_by': 'datetime DESC',
        'description': 'CoinMarketCap Rankings'
    }
}


def get_table_stats(client, table_name):
    """Get current table statistics"""
    try:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        config = TABLES_CONFIG.get(table_name, {'unique_key': ['symbol', 'datetime']})
        unique_key = config['unique_key']

        # Build unique key expression
        if len(unique_key) == 1:
            key_expr = unique_key[0]
        else:
            key_expr = f"CONCAT({', '.join([f'CAST({k} AS STRING)' for k in unique_key])})"

        query = f"""
        SELECT
            COUNT(*) as total_rows,
            COUNT(DISTINCT {key_expr}) as unique_rows
        FROM `{table_id}`
        """

        result = list(client.query(query).result())
        if result:
            row = result[0]
            return {
                'total': row.total_rows,
                'unique': row.unique_rows,
                'duplicates': row.total_rows - row.unique_rows
            }
    except Exception as e:
        if 'Not found' in str(e):
            return {'total': 0, 'unique': 0, 'duplicates': 0, 'not_found': True}
        print(f"Error checking {table_name}: {e}")
        return None

    return {'total': 0, 'unique': 0, 'duplicates': 0}


def deduplicate_table(client, table_name):
    """Deduplicate a table by keeping the most recent record for each unique key"""
    try:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        config = TABLES_CONFIG.get(table_name, {'unique_key': ['symbol', 'datetime'], 'order_by': 'datetime DESC'})
        unique_key = config['unique_key']
        order_by = config['order_by']

        print(f"\n{'='*60}")
        print(f"DEDUPLICATING: {table_name}")
        print(f"{'='*60}")

        # Get before stats
        before_stats = get_table_stats(client, table_name)
        if before_stats is None or before_stats.get('not_found'):
            print(f"  Table not found or empty, skipping...")
            return False

        print(f"  Before: {before_stats['total']:,} total, {before_stats['unique']:,} unique, {before_stats['duplicates']:,} duplicates")

        if before_stats['duplicates'] == 0:
            print(f"  No duplicates found, skipping...")
            return True

        # Create temp table with deduplicated data
        temp_table = f"{table_name}_dedup_temp"
        temp_table_id = f"{PROJECT_ID}.{DATASET_ID}.{temp_table}"

        # Build partition expression
        partition_cols = ', '.join(unique_key)

        # First, get the schema to check if fetch_timestamp exists
        try:
            table = client.get_table(table_id)
            field_names = [field.name for field in table.schema]

            if 'fetch_timestamp' not in field_names and order_by == 'fetch_timestamp DESC':
                order_by = 'datetime DESC'
        except:
            order_by = 'datetime DESC'

        dedup_query = f"""
        CREATE OR REPLACE TABLE `{temp_table_id}` AS
        SELECT * EXCEPT(row_num) FROM (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY {partition_cols} ORDER BY {order_by}) as row_num
            FROM `{table_id}`
        )
        WHERE row_num = 1
        """

        print(f"  Creating deduplicated temp table...")
        job = client.query(dedup_query)
        job.result()

        # Get temp table stats
        temp_stats = get_table_stats(client, temp_table)
        print(f"  Temp table: {temp_stats['unique']:,} unique records")

        # Drop original and rename temp
        print(f"  Replacing original table...")

        # Copy temp to original (overwrite)
        copy_query = f"""
        CREATE OR REPLACE TABLE `{table_id}` AS
        SELECT * FROM `{temp_table_id}`
        """
        job = client.query(copy_query)
        job.result()

        # Drop temp table
        drop_query = f"DROP TABLE IF EXISTS `{temp_table_id}`"
        client.query(drop_query).result()

        # Get after stats
        after_stats = get_table_stats(client, table_name)
        print(f"  After: {after_stats['total']:,} total, {after_stats['unique']:,} unique")
        print(f"  Removed: {before_stats['total'] - after_stats['total']:,} duplicate records")

        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def create_dedup_views(client):
    """Create views that automatically deduplicate when queried"""
    print(f"\n{'='*60}")
    print("CREATING DEDUPLICATION VIEWS")
    print(f"{'='*60}")

    views = [
        ('v_stocks_daily_latest', 'stocks_daily_clean', ['symbol', 'datetime']),
        ('v_crypto_daily_latest', 'crypto_daily_clean', ['symbol', 'datetime']),
        ('v_etfs_daily_latest', 'etfs_daily_clean', ['symbol', 'datetime']),
    ]

    for view_name, source_table, unique_keys in views:
        try:
            partition_cols = ', '.join(unique_keys)
            view_id = f"{PROJECT_ID}.{DATASET_ID}.{view_name}"
            source_id = f"{PROJECT_ID}.{DATASET_ID}.{source_table}"

            view_query = f"""
            CREATE OR REPLACE VIEW `{view_id}` AS
            SELECT * EXCEPT(row_num) FROM (
                SELECT *,
                    ROW_NUMBER() OVER (PARTITION BY {partition_cols} ORDER BY datetime DESC) as row_num
                FROM `{source_id}`
            )
            WHERE row_num = 1
            """

            client.query(view_query).result()
            print(f"  Created view: {view_name}")

        except Exception as e:
            print(f"  Error creating {view_name}: {e}")


def add_unique_constraints_info(client):
    """Document the unique key constraints for each table"""
    print(f"\n{'='*60}")
    print("TABLE UNIQUE KEY DOCUMENTATION")
    print(f"{'='*60}")

    for table_name, config in TABLES_CONFIG.items():
        print(f"  {table_name}: UNIQUE({', '.join(config['unique_key'])})")


def main():
    print("=" * 70)
    print("COMPREHENSIVE DATA CLEANUP AND DEDUPLICATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    client = bigquery.Client(project=PROJECT_ID)

    # Step 1: Check all tables
    print("\n" + "=" * 60)
    print("STEP 1: ANALYZING ALL TABLES")
    print("=" * 60)

    table_stats = {}
    total_duplicates = 0

    for table_name in TABLES_CONFIG.keys():
        stats = get_table_stats(client, table_name)
        if stats and not stats.get('not_found'):
            table_stats[table_name] = stats
            total_duplicates += stats['duplicates']
            status = "NEEDS CLEANUP" if stats['duplicates'] > 0 else "OK"
            print(f"  {table_name}: {stats['total']:,} rows, {stats['duplicates']:,} duplicates [{status}]")
        else:
            print(f"  {table_name}: Not found or empty")

    print(f"\n  TOTAL DUPLICATES TO REMOVE: {total_duplicates:,}")

    if total_duplicates == 0:
        print("\nNo duplicates found! All tables are clean.")
        return

    # Step 2: Deduplicate each table
    print("\n" + "=" * 60)
    print("STEP 2: DEDUPLICATING TABLES")
    print("=" * 60)

    success_count = 0
    for table_name in table_stats.keys():
        if table_stats[table_name]['duplicates'] > 0:
            if deduplicate_table(client, table_name):
                success_count += 1
            time.sleep(1)  # Small delay between operations

    # Step 3: Create dedup views
    create_dedup_views(client)

    # Step 4: Final verification
    print("\n" + "=" * 60)
    print("STEP 3: FINAL VERIFICATION")
    print("=" * 60)

    final_duplicates = 0
    for table_name in table_stats.keys():
        stats = get_table_stats(client, table_name)
        if stats:
            final_duplicates += stats['duplicates']
            status = "CLEAN" if stats['duplicates'] == 0 else f"{stats['duplicates']} DUPLICATES REMAIN"
            print(f"  {table_name}: {stats['total']:,} rows [{status}]")

    # Summary
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    print(f"  Tables processed: {len(table_stats)}")
    print(f"  Duplicates removed: {total_duplicates - final_duplicates:,}")
    print(f"  Remaining duplicates: {final_duplicates:,}")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if final_duplicates == 0:
        print("\n  STATUS: ALL TABLES CLEAN - HIGH DATA QUALITY ACHIEVED")
    else:
        print("\n  STATUS: SOME DUPLICATES REMAIN - MANUAL REVIEW NEEDED")

    # Document unique keys
    add_unique_constraints_info(client)


if __name__ == '__main__':
    main()
