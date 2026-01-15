"""
Data Deduplication Cloud Function
=================================
Removes duplicate rows from BigQuery tables, keeping only one row per symbol per date.
Runs after the 1 AM data fetching to ensure clean data for ML analysis.

Scheduled: 2:30 AM ET daily (after data fetch completes)
"""

import functions_framework
from google.cloud import bigquery
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Tables to deduplicate
TABLES_TO_DEDUP = [
    'stocks_daily_clean',
    'crypto_daily_clean',
    'etfs_daily_clean',
    'forex_daily_clean',
    'stocks_hourly_clean',
    'crypto_hourly_clean'
]


def deduplicate_table(client, table_name):
    """Remove duplicates from a table, keeping the most recent row per symbol/date"""

    full_table = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    # Check for duplicates first
    check_query = f"""
    SELECT COUNT(*) as total_rows,
           COUNT(DISTINCT CONCAT(symbol, '_', DATE(datetime))) as unique_combinations,
           COUNT(*) - COUNT(DISTINCT CONCAT(symbol, '_', DATE(datetime))) as duplicate_rows
    FROM `{full_table}`
    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    """

    try:
        result = client.query(check_query).result()
        row = list(result)[0]
        total = row.total_rows
        unique = row.unique_combinations
        dupes = row.duplicate_rows

        if dupes == 0:
            logger.info(f"  {table_name}: No duplicates found (last 30 days)")
            return {'table': table_name, 'duplicates_removed': 0, 'status': 'CLEAN'}

        logger.info(f"  {table_name}: Found {dupes} duplicates, cleaning...")

        # Create deduplicated version
        dedup_query = f"""
        CREATE OR REPLACE TABLE `{full_table}_deduped` AS
        WITH ranked AS (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY symbol, DATE(datetime)
                       ORDER BY datetime DESC, updated_at DESC NULLS LAST
                   ) as rn
            FROM `{full_table}`
        )
        SELECT * EXCEPT(rn)
        FROM ranked
        WHERE rn = 1
        """

        client.query(dedup_query).result()

        # Get new count
        new_count_query = f"SELECT COUNT(*) as cnt FROM `{full_table}_deduped`"
        new_result = client.query(new_count_query).result()
        new_count = list(new_result)[0].cnt

        # Replace original with deduplicated
        replace_query = f"""
        CREATE OR REPLACE TABLE `{full_table}` AS
        SELECT * FROM `{full_table}_deduped`
        """
        client.query(replace_query).result()

        # Drop temp table
        drop_query = f"DROP TABLE IF EXISTS `{full_table}_deduped`"
        client.query(drop_query).result()

        logger.info(f"  {table_name}: Removed {dupes} duplicates, now {new_count} rows")

        return {
            'table': table_name,
            'original_rows': total,
            'unique_rows': new_count,
            'duplicates_removed': dupes,
            'status': 'CLEANED'
        }

    except Exception as e:
        logger.error(f"  Error deduplicating {table_name}: {e}")
        return {
            'table': table_name,
            'duplicates_removed': 0,
            'status': 'ERROR',
            'error': str(e)
        }


@functions_framework.http
def deduplicate_all_tables(request):
    """
    Cloud Function entry point - deduplicates all trading tables

    Query params:
        tables: comma-separated list (default: all)
    """

    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting deduplication at {start_time}")

    # Parse parameters
    args = request.args
    tables_param = args.get('tables', 'all')

    if tables_param == 'all':
        tables = TABLES_TO_DEDUP
    else:
        tables = [t.strip() for t in tables_param.split(',')]

    client = bigquery.Client(project=PROJECT_ID)

    results = []
    total_removed = 0

    for table in tables:
        logger.info(f"Processing {table}...")
        result = deduplicate_table(client, table)
        results.append(result)
        total_removed += result.get('duplicates_removed', 0)

    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()

    response = {
        'status': 'success',
        'timestamp': start_time.isoformat(),
        'duration_seconds': round(duration, 1),
        'tables_processed': len(tables),
        'total_duplicates_removed': total_removed,
        'results': results
    }

    logger.info(f"Deduplication complete: {total_removed} duplicates removed in {duration:.1f}s")

    return response, 200


if __name__ == "__main__":
    class MockRequest:
        args = {'tables': 'stocks_daily_clean'}
    result, _ = deduplicate_all_tables(MockRequest())
    print(result)
