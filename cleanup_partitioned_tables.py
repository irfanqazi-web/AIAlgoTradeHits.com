"""
Cleanup Partitioned Tables - Handles BigQuery partitioned tables
Uses DELETE to remove duplicates while preserving partitioning
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

# Tables to clean
TABLES_TO_CLEAN = [
    'stocks_daily_clean',
    'crypto_daily_clean',
    'etfs_daily_clean',
    'forex_daily_clean',
    'indices_daily_clean'
]


def get_table_stats(client, table_name):
    """Get current table statistics"""
    try:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        query = f"""
        SELECT
            COUNT(*) as total_rows,
            COUNT(DISTINCT CONCAT(symbol, '_', CAST(datetime AS STRING))) as unique_rows
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
        print(f"Error checking {table_name}: {e}")
        return None

    return {'total': 0, 'unique': 0, 'duplicates': 0}


def deduplicate_partitioned_table(client, table_name):
    """
    Deduplicate a partitioned table using MERGE statement
    This preserves partitioning and clustering
    """
    try:
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        backup_table = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_id = f"{PROJECT_ID}.{DATASET_ID}.{backup_table}"

        print(f"\n{'='*60}")
        print(f"DEDUPLICATING: {table_name}")
        print(f"{'='*60}")

        # Get before stats
        before_stats = get_table_stats(client, table_name)
        if before_stats is None:
            print(f"  Table not found, skipping...")
            return False

        print(f"  Before: {before_stats['total']:,} total, {before_stats['unique']:,} unique, {before_stats['duplicates']:,} duplicates")

        if before_stats['duplicates'] == 0:
            print(f"  No duplicates found, skipping...")
            return True

        # Step 1: Create backup of deduplicated data
        print(f"  Step 1: Creating deduplicated backup table...")
        backup_query = f"""
        CREATE TABLE `{backup_id}` AS
        SELECT * EXCEPT(row_num) FROM (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY symbol, datetime ORDER BY datetime DESC) as row_num
            FROM `{table_id}`
        )
        WHERE row_num = 1
        """
        job = client.query(backup_query)
        job.result()

        # Verify backup
        backup_stats = get_table_stats(client, backup_table)
        print(f"  Backup created: {backup_stats['unique']:,} unique records")

        # Step 2: Get the table schema to recreate with partitioning
        print(f"  Step 2: Getting original table schema...")
        original_table = client.get_table(table_id)
        schema = original_table.schema

        # Step 3: Delete all data from original table
        print(f"  Step 3: Truncating original table...")
        truncate_query = f"DELETE FROM `{table_id}` WHERE TRUE"
        job = client.query(truncate_query)
        job.result()

        # Step 4: Insert deduplicated data back
        print(f"  Step 4: Inserting deduplicated data...")
        insert_query = f"""
        INSERT INTO `{table_id}`
        SELECT * FROM `{backup_id}`
        """
        job = client.query(insert_query)
        job.result()

        # Step 5: Verify and cleanup
        after_stats = get_table_stats(client, table_name)
        print(f"  After: {after_stats['total']:,} total, {after_stats['unique']:,} unique")
        print(f"  Removed: {before_stats['total'] - after_stats['total']:,} duplicate records")

        # Drop backup table
        print(f"  Cleaning up backup table...")
        drop_query = f"DROP TABLE IF EXISTS `{backup_id}`"
        client.query(drop_query).result()

        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("PARTITIONED TABLE CLEANUP AND DEDUPLICATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    client = bigquery.Client(project=PROJECT_ID)

    # Step 1: Check all tables
    print("\n" + "=" * 60)
    print("STEP 1: ANALYZING TABLES")
    print("=" * 60)

    table_stats = {}
    total_duplicates = 0

    for table_name in TABLES_TO_CLEAN:
        stats = get_table_stats(client, table_name)
        if stats:
            table_stats[table_name] = stats
            total_duplicates += stats['duplicates']
            status = "NEEDS CLEANUP" if stats['duplicates'] > 0 else "OK"
            dup_pct = (stats['duplicates'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {table_name}: {stats['total']:,} rows, {stats['duplicates']:,} duplicates ({dup_pct:.1f}%) [{status}]")

    print(f"\n  TOTAL DUPLICATES TO REMOVE: {total_duplicates:,}")

    if total_duplicates == 0:
        print("\nNo duplicates found! All tables are clean.")
        return

    # Step 2: Deduplicate each table
    print("\n" + "=" * 60)
    print("STEP 2: DEDUPLICATING TABLES")
    print("=" * 60)

    success_count = 0
    for table_name in TABLES_TO_CLEAN:
        if table_name in table_stats and table_stats[table_name]['duplicates'] > 0:
            if deduplicate_partitioned_table(client, table_name):
                success_count += 1
            time.sleep(2)  # Delay between operations

    # Step 3: Final verification
    print("\n" + "=" * 60)
    print("STEP 3: FINAL VERIFICATION")
    print("=" * 60)

    final_duplicates = 0
    final_total = 0
    for table_name in TABLES_TO_CLEAN:
        stats = get_table_stats(client, table_name)
        if stats:
            final_duplicates += stats['duplicates']
            final_total += stats['total']
            status = "CLEAN" if stats['duplicates'] == 0 else f"{stats['duplicates']} DUPLICATES REMAIN"
            print(f"  {table_name}: {stats['total']:,} rows [{status}]")

    # Summary
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    print(f"  Tables processed: {len(TABLES_TO_CLEAN)}")
    print(f"  Tables cleaned successfully: {success_count}")
    print(f"  Total rows after cleanup: {final_total:,}")
    print(f"  Duplicates removed: {total_duplicates - final_duplicates:,}")
    print(f"  Remaining duplicates: {final_duplicates:,}")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if final_duplicates == 0:
        print("\n  STATUS: ALL TABLES CLEAN - HIGH DATA QUALITY ACHIEVED")
    else:
        print("\n  STATUS: SOME DUPLICATES REMAIN - CHECK ERRORS ABOVE")


if __name__ == '__main__':
    main()
