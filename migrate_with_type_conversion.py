"""
Migrate BigQuery tables with proper type conversion (DATETIME -> TIMESTAMP)
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import time

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

# Tables that need migration with type conversion
TABLE_MAPPINGS = {
    'stocks_daily': 'v2_stocks_daily',
    'stocks_hourly': 'v2_stocks_hourly',
    'crypto_hourly': 'v2_crypto_hourly',
    'forex_daily': 'v2_forex_daily',
    'forex_hourly': 'v2_forex_hourly',
    'forex_5min': 'v2_forex_5min',
    'etfs_daily': 'v2_etfs_daily',
    'etfs_hourly': 'v2_etfs_hourly',
    'etfs_5min': 'v2_etfs_5min',
    'indices_daily': 'v2_indices_daily',
    'indices_hourly': 'v2_indices_hourly',
    'indices_5min': 'v2_indices_5min',
    'commodities_daily': 'v2_commodities_daily',
    'commodities_hourly': 'v2_commodities_hourly',
    'commodities_5min': 'v2_commodities_5min',
}


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def get_table_info(client, table_name):
    """Get table schema with field types"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    try:
        table = client.get_table(table_ref)
        return {f.name: f.field_type for f in table.schema}
    except Exception as e:
        print(f"  Error getting {table_name}: {e}")
        return {}


def determine_asset_type(table_name):
    table_lower = table_name.lower()
    if 'stock' in table_lower: return 'stock'
    elif 'crypto' in table_lower: return 'crypto'
    elif 'forex' in table_lower: return 'forex'
    elif 'etf' in table_lower: return 'etf'
    elif 'indic' in table_lower: return 'index'
    elif 'commodit' in table_lower: return 'commodity'
    return 'other'


def migrate_with_conversion(client, source_table, dest_table):
    """Migrate with proper type conversion"""

    source_fields = get_table_info(client, source_table)
    dest_fields = get_table_info(client, dest_table)

    if not source_fields or not dest_fields:
        return False

    # Check if already migrated
    count_query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.{dest_table}`"
    count = list(client.query(count_query).result())[0].cnt
    if count > 0:
        print(f"  {dest_table} already has {count} rows, skipping...")
        return True

    asset_type = determine_asset_type(source_table)

    # Build SELECT with proper type conversions
    select_parts = []
    for dest_field, dest_type in dest_fields.items():
        if dest_field in source_fields:
            src_type = source_fields[dest_field]

            # Handle type conversions
            if src_type == 'DATETIME' and dest_type == 'TIMESTAMP':
                select_parts.append(f"CAST(`{dest_field}` AS TIMESTAMP) as `{dest_field}`")
            elif src_type == 'TIMESTAMP' and dest_type == 'DATETIME':
                select_parts.append(f"CAST(`{dest_field}` AS DATETIME) as `{dest_field}`")
            elif src_type != dest_type and dest_type == 'FLOAT64':
                select_parts.append(f"CAST(`{dest_field}` AS FLOAT64) as `{dest_field}`")
            elif src_type != dest_type and dest_type == 'INT64':
                select_parts.append(f"CAST(`{dest_field}` AS INT64) as `{dest_field}`")
            elif src_type != dest_type and dest_type == 'STRING':
                select_parts.append(f"CAST(`{dest_field}` AS STRING) as `{dest_field}`")
            else:
                select_parts.append(f"`{dest_field}`")

        # Special field mappings
        elif dest_field == 'asset_type':
            select_parts.append(f"'{asset_type}' as asset_type")
        elif dest_field == 'symbol' and 'pair' in source_fields:
            select_parts.append("`pair` as symbol")
        elif dest_field == 'macd_histogram' and 'macd_hist' in source_fields:
            select_parts.append("`macd_hist` as macd_histogram")
        elif dest_field == 'created_at':
            select_parts.append("CURRENT_TIMESTAMP() as created_at")
        else:
            # NULL for missing fields with proper type
            if dest_type == 'STRING':
                select_parts.append(f"CAST(NULL AS STRING) as `{dest_field}`")
            elif dest_type in ('FLOAT64', 'FLOAT'):
                select_parts.append(f"CAST(NULL AS FLOAT64) as `{dest_field}`")
            elif dest_type in ('INT64', 'INTEGER'):
                select_parts.append(f"CAST(NULL AS INT64) as `{dest_field}`")
            elif dest_type == 'TIMESTAMP':
                select_parts.append(f"CAST(NULL AS TIMESTAMP) as `{dest_field}`")
            elif dest_type == 'DATETIME':
                select_parts.append(f"CAST(NULL AS DATETIME) as `{dest_field}`")
            elif dest_type == 'DATE':
                select_parts.append(f"CAST(NULL AS DATE) as `{dest_field}`")
            else:
                select_parts.append(f"NULL as `{dest_field}`")

    select_clause = ",\n        ".join(select_parts)

    query = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{dest_table}`
    SELECT
        {select_clause}
    FROM `{PROJECT_ID}.{DATASET_ID}.{source_table}`
    """

    try:
        job = client.query(query)
        job.result()
        print(f"  SUCCESS: {source_table} -> {dest_table}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    print("=" * 80)
    print("MIGRATING TABLES WITH TYPE CONVERSION")
    print("=" * 80)

    client = get_client()
    migrated = []
    failed = []

    for source, dest in TABLE_MAPPINGS.items():
        print(f"\n[{source}] -> [{dest}]")
        if migrate_with_conversion(client, source, dest):
            migrated.append((source, dest))
        else:
            failed.append((source, dest))
        time.sleep(0.5)

    # Summary
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)

    print(f"\n{'Source':<25} {'Dest':<25} {'Source Rows':<12} {'Dest Rows':<12}")
    print("-" * 80)

    for source, dest in migrated:
        try:
            src = list(client.query(f"SELECT COUNT(*) as c FROM `{PROJECT_ID}.{DATASET_ID}.{source}`").result())[0].c
            dst = list(client.query(f"SELECT COUNT(*) as c FROM `{PROJECT_ID}.{DATASET_ID}.{dest}`").result())[0].c
            print(f"{source:<25} {dest:<25} {src:<12,} {dst:<12,}")
        except:
            pass

    print(f"\nSuccess: {len(migrated)}, Failed: {len(failed)}")

    if failed:
        print("\nFailed tables:")
        for s, d in failed:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
