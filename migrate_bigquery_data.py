"""
Migrate BigQuery data from cryptobot-462709 to aialgotradehits
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

SOURCE_PROJECT = 'cryptobot-462709'
SOURCE_DATASET = 'crypto_trading_data'
DEST_PROJECT = 'aialgotradehits'
DEST_DATASET = 'crypto_trading_data'

# Tables to migrate with their priority
TABLES_TO_MIGRATE = [
    'stocks_daily',
    'crypto_daily',
    'stocks_hourly',
    'crypto_hourly',
    'stocks_5min',
    'crypto_5min',
    'forex_daily',
    'forex_hourly',
    'etfs_daily',
    'indices_daily',
    'commodities_daily',
    'users',
    'search_history',
    'interest_rates',
]

def migrate_table(client, table_name):
    """Copy data from source to destination table"""
    print(f"\nMigrating {table_name}...")

    source_table = f"{SOURCE_PROJECT}.{SOURCE_DATASET}.{table_name}"
    dest_table = f"{DEST_PROJECT}.{DEST_DATASET}.{table_name}"

    # Check if source table exists and has data
    try:
        query = f"SELECT COUNT(*) as cnt FROM `{source_table}`"
        result = list(client.query(query).result())
        source_count = result[0].cnt
        print(f"  Source has {source_count:,} rows")

        if source_count == 0:
            print(f"  Skipping - no data in source")
            return True
    except Exception as e:
        print(f"  Error checking source: {e}")
        return False

    # Check destination count
    try:
        query = f"SELECT COUNT(*) as cnt FROM `{dest_table}`"
        result = list(client.query(query).result())
        dest_count = result[0].cnt
        print(f"  Destination has {dest_count:,} rows")

        if dest_count >= source_count:
            print(f"  Skipping - destination already has data")
            return True
    except Exception as e:
        print(f"  Destination table may not exist or is empty: {e}")
        dest_count = 0

    # Copy data using INSERT SELECT
    try:
        print(f"  Copying data...")
        query = f"""
        INSERT INTO `{dest_table}`
        SELECT * FROM `{source_table}`
        """
        job = client.query(query)
        job.result()  # Wait for completion

        # Verify
        query = f"SELECT COUNT(*) as cnt FROM `{dest_table}`"
        result = list(client.query(query).result())
        new_count = result[0].cnt
        print(f"  OK - Destination now has {new_count:,} rows")
        return True

    except Exception as e:
        print(f"  Error copying: {e}")
        # Try WRITE_TRUNCATE instead
        try:
            print(f"  Trying copy job instead...")
            job_config = bigquery.CopyJobConfig(write_disposition="WRITE_TRUNCATE")
            copy_job = client.copy_table(source_table, dest_table, job_config=job_config)
            copy_job.result()
            print(f"  OK - Copy completed")
            return True
        except Exception as e2:
            print(f"  Copy job also failed: {e2}")
            return False


def main():
    print("="*60)
    print("BIGQUERY DATA MIGRATION")
    print(f"From: {SOURCE_PROJECT}.{SOURCE_DATASET}")
    print(f"To: {DEST_PROJECT}.{DEST_DATASET}")
    print("="*60)

    client = bigquery.Client(project=SOURCE_PROJECT)

    results = {}
    for table in TABLES_TO_MIGRATE:
        results[table] = migrate_table(client, table)

    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)

    success = 0
    failed = 0
    for table, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"  {status}: {table}")
        if ok:
            success += 1
        else:
            failed += 1

    print(f"\nTotal: {success} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
