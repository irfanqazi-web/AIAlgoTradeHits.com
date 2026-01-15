"""
Migrate remaining BigQuery tables to standardized v2 schema
Uses actual table names from BigQuery
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import time

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

# Corrected table mappings based on actual BigQuery table names
TABLE_MAPPINGS = {
    # Stocks
    'stocks_daily': 'v2_stocks_daily',
    'stocks_hourly': 'v2_stocks_hourly',
    'stocks_5min': 'v2_stocks_5min',

    # Crypto
    'crypto_daily': 'v2_crypto_daily',
    'crypto_hourly': 'v2_crypto_hourly',
    'crypto_5min': 'v2_crypto_5min',

    # Forex
    'forex_daily': 'v2_forex_daily',
    'forex_hourly': 'v2_forex_hourly',
    'forex_5min': 'v2_forex_5min',

    # ETFs
    'etfs_daily': 'v2_etfs_daily',
    'etfs_hourly': 'v2_etfs_hourly',
    'etfs_5min': 'v2_etfs_5min',

    # Indices
    'indices_daily': 'v2_indices_daily',
    'indices_hourly': 'v2_indices_hourly',
    'indices_5min': 'v2_indices_5min',

    # Commodities
    'commodities_daily': 'v2_commodities_daily',
    'commodities_hourly': 'v2_commodities_hourly',
    'commodities_5min': 'v2_commodities_5min',
}


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def get_source_fields(client, source_table):
    """Get list of fields in source table"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{source_table}"
    try:
        table = client.get_table(table_ref)
        return {f.name: f.field_type for f in table.schema}
    except Exception as e:
        print(f"  Error getting schema for {source_table}: {e}")
        return {}


def get_dest_fields(client, dest_table):
    """Get list of fields in destination table"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{dest_table}"
    try:
        table = client.get_table(table_ref)
        return [f.name for f in table.schema]
    except Exception as e:
        print(f"  Error getting schema for {dest_table}: {e}")
        return []


def determine_asset_type(table_name):
    """Determine asset type from table name"""
    table_lower = table_name.lower()
    if 'stock' in table_lower:
        return 'stock'
    elif 'crypto' in table_lower:
        return 'crypto'
    elif 'forex' in table_lower:
        return 'forex'
    elif 'etf' in table_lower:
        return 'etf'
    elif 'indic' in table_lower:
        return 'index'
    elif 'commodit' in table_lower:
        return 'commodity'
    return 'other'


def migrate_data(client, source_table, dest_table):
    """Migrate data with proper field mapping"""

    source_fields = get_source_fields(client, source_table)
    dest_fields = get_dest_fields(client, dest_table)

    if not source_fields or not dest_fields:
        return False

    asset_type = determine_asset_type(source_table)

    # Build SELECT clause
    select_parts = []
    for dest_field in dest_fields:
        # Direct field mapping
        if dest_field in source_fields:
            select_parts.append(f"`{dest_field}`")
        # Special mappings
        elif dest_field == 'asset_type':
            select_parts.append(f"'{asset_type}' as asset_type")
        elif dest_field == 'symbol' and 'pair' in source_fields:
            select_parts.append("`pair` as symbol")
        elif dest_field == 'macd_histogram' and 'macd_hist' in source_fields:
            select_parts.append("`macd_hist` as macd_histogram")
        elif dest_field == 'created_at':
            select_parts.append("CURRENT_TIMESTAMP() as created_at")
        # NULL for missing
        else:
            # Determine type from dest schema
            dest_table_ref = f"{PROJECT_ID}.{DATASET_ID}.{dest_table}"
            dest_table_obj = client.get_table(dest_table_ref)
            field_type = 'STRING'
            for f in dest_table_obj.schema:
                if f.name == dest_field:
                    field_type = f.field_type
                    break

            if field_type in ('STRING',):
                select_parts.append(f"CAST(NULL AS STRING) as `{dest_field}`")
            elif field_type in ('FLOAT64', 'FLOAT'):
                select_parts.append(f"CAST(NULL AS FLOAT64) as `{dest_field}`")
            elif field_type in ('INT64', 'INTEGER'):
                select_parts.append(f"CAST(NULL AS INT64) as `{dest_field}`")
            elif field_type in ('TIMESTAMP',):
                select_parts.append(f"CAST(NULL AS TIMESTAMP) as `{dest_field}`")
            elif field_type in ('DATE',):
                select_parts.append(f"CAST(NULL AS DATE) as `{dest_field}`")
            else:
                select_parts.append(f"NULL as `{dest_field}`")

    select_clause = ",\n        ".join(select_parts)

    # First check if dest table already has data
    count_query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.{dest_table}`"
    count_result = list(client.query(count_query).result())[0]
    if count_result.cnt > 0:
        print(f"  Destination {dest_table} already has {count_result.cnt} rows, skipping...")
        return True

    query = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{dest_table}`
    SELECT
        {select_clause}
    FROM `{PROJECT_ID}.{DATASET_ID}.{source_table}`
    """

    try:
        job = client.query(query)
        job.result()
        print(f"  Migrated {source_table} -> {dest_table}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 80)
    print("MIGRATING REMAINING TABLES TO V2 STANDARDIZED SCHEMA")
    print("=" * 80)

    client = get_client()

    migrated = []
    failed = []

    for source, dest in TABLE_MAPPINGS.items():
        print(f"\n[{source}] -> [{dest}]")
        if migrate_data(client, source, dest):
            migrated.append((source, dest))
        else:
            failed.append((source, dest))
        time.sleep(0.5)

    # Verify
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    print(f"\n{'Source':<25} {'Dest':<25} {'Source Rows':<12} {'Dest Rows':<12}")
    print("-" * 80)

    for source, dest in migrated:
        try:
            src_count = list(client.query(f"SELECT COUNT(*) as c FROM `{PROJECT_ID}.{DATASET_ID}.{source}`").result())[0].c
            dst_count = list(client.query(f"SELECT COUNT(*) as c FROM `{PROJECT_ID}.{DATASET_ID}.{dest}`").result())[0].c
            status = "OK" if src_count == dst_count else "CHECK"
            print(f"{source:<25} {dest:<25} {src_count:<12,} {dst_count:<12,} {status}")
        except Exception as e:
            print(f"{source:<25} {dest:<25} Error: {e}")

    print(f"\n\nSuccessfully migrated: {len(migrated)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed:")
        for s, d in failed:
            print(f"  - {s} -> {d}")


if __name__ == "__main__":
    main()
