"""
Full BigQuery Migration Script
Migrates all data from cryptobot-462709 to aialgotradehits (unified project)
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime
import time

# Configuration
SOURCE_PROJECT = 'cryptobot-462709'
SOURCE_DATASET = 'crypto_trading_data'
TARGET_PROJECT = 'aialgotradehits'
TARGET_DATASET = 'crypto_trading_data'

# Priority tables to migrate (v2_ standardized schema tables have the best data)
PRIORITY_TABLES = [
    # Historical data (largest and most important)
    'v2_stocks_historical_daily',
    'v2_etfs_historical_daily',
    'v2_forex_historical_daily',
    'v2_indices_historical_daily',
    'v2_commodities_historical_daily',
    'v2_cryptos_historical_daily',

    # Daily data
    'v2_stocks_daily',
    'v2_crypto_daily',
    'v2_etfs_daily',
    'v2_forex_daily',
    'v2_indices_daily',
    'v2_commodities_daily',

    # Hourly data
    'v2_stocks_hourly',
    'v2_crypto_hourly',
    'v2_etfs_hourly',
    'v2_forex_hourly',
    'v2_indices_hourly',
    'v2_commodities_hourly',

    # 5min data
    'v2_stocks_5min',
    'v2_crypto_5min',
    'v2_etfs_5min',
    'v2_forex_5min',
    'v2_indices_5min',
    'v2_commodities_5min',

    # Weekly summaries
    'v2_stocks_weekly_summary',
    'v2_cryptos_weekly_summary',
    'v2_etfs_weekly_summary',
    'v2_forex_weekly_summary',
    'v2_indices_weekly_summary',
    'v2_commodities_weekly_summary',

    # Master lists
    'v2_stocks_master',
    'stocks_master_list',

    # AI Training data
    'btc_ai_training_daily',
    'nvda_ai_training_daily',

    # User/config data
    'users',
    'trading_strategies',
    'search_history',
    'interest_rates',
]


def migrate_table(source_client, target_client, table_name):
    """Migrate a single table from source to target"""
    source_table = f"{SOURCE_PROJECT}.{SOURCE_DATASET}.{table_name}"
    target_table = f"{TARGET_PROJECT}.{TARGET_DATASET}.{table_name}"

    try:
        # Check if source table has data
        source_ref = source_client.get_table(source_table)
        row_count = source_ref.num_rows

        if row_count == 0:
            print(f"  [SKIP] {table_name}: No data in source")
            return 0

        # Check if target table exists
        try:
            target_ref = target_client.get_table(target_table)
            existing_rows = target_ref.num_rows

            if existing_rows >= row_count:
                print(f"  [SKIP] {table_name}: Target already has {existing_rows:,} rows (source: {row_count:,})")
                return 0
        except Exception:
            # Table doesn't exist, will be created
            existing_rows = 0

        print(f"  [MIGRATE] {table_name}: {row_count:,} rows...")

        # Use BigQuery copy job for efficiency
        job_config = bigquery.QueryJobConfig(
            destination=target_table,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        query = f"SELECT * FROM `{source_table}`"

        job = target_client.query(query, job_config=job_config)
        job.result()  # Wait for completion

        # Verify
        target_ref = target_client.get_table(target_table)
        print(f"  [OK] {table_name}: Migrated {target_ref.num_rows:,} rows")

        return target_ref.num_rows

    except Exception as e:
        print(f"  [ERROR] {table_name}: {e}")
        return 0


def main():
    print("="*70)
    print("BIGQUERY MIGRATION: cryptobot-462709 -> aialgotradehits")
    print("="*70)
    print(f"Started: {datetime.now()}")
    print()

    # Initialize clients
    source_client = bigquery.Client(project=SOURCE_PROJECT)
    target_client = bigquery.Client(project=TARGET_PROJECT)

    # Ensure target dataset exists
    try:
        target_client.get_dataset(f"{TARGET_PROJECT}.{TARGET_DATASET}")
        print(f"Target dataset exists: {TARGET_PROJECT}.{TARGET_DATASET}")
    except Exception:
        dataset = bigquery.Dataset(f"{TARGET_PROJECT}.{TARGET_DATASET}")
        dataset.location = "US"
        target_client.create_dataset(dataset)
        print(f"Created target dataset: {TARGET_PROJECT}.{TARGET_DATASET}")

    print()

    total_rows = 0
    migrated_tables = 0

    for i, table in enumerate(PRIORITY_TABLES):
        print(f"\n[{i+1}/{len(PRIORITY_TABLES)}] {table}")
        rows = migrate_table(source_client, target_client, table)
        total_rows += rows
        if rows > 0:
            migrated_tables += 1

        # Brief pause between tables
        time.sleep(0.5)

    print()
    print("="*70)
    print("MIGRATION COMPLETE")
    print("="*70)
    print(f"Tables migrated: {migrated_tables}")
    print(f"Total rows: {total_rows:,}")
    print(f"Completed: {datetime.now()}")


if __name__ == "__main__":
    main()
