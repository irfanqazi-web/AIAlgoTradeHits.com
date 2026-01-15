"""
Migrate ALL asset data tables to v2 standardized schema with AI-recommended field ordering.

AI-Recommended Field Order (7 Tiers):
1. Identity: symbol, name, asset_type
2. Classification: exchange, country, sector, industry, currency
3. Price Data: open, high, low, close, previous_close
4. Volume/Change: volume, average_volume, change, percent_change
5. Range: week_52_high, week_52_low
6. Technical Indicators: rsi, macd, sma_*, ema_*, bollinger_*, atr, adx, etc.
7. Timestamps: datetime, timestamp, data_source, created_at
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import time

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

# Standard v2 schema with AI-recommended field order
STANDARD_SCHEMA = [
    # Tier 1: Identity
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("asset_type", "STRING"),

    # Tier 2: Classification
    bigquery.SchemaField("exchange", "STRING"),
    bigquery.SchemaField("country", "STRING"),
    bigquery.SchemaField("sector", "STRING"),
    bigquery.SchemaField("industry", "STRING"),
    bigquery.SchemaField("currency", "STRING"),

    # Tier 3: Price Data
    bigquery.SchemaField("open", "FLOAT64"),
    bigquery.SchemaField("high", "FLOAT64"),
    bigquery.SchemaField("low", "FLOAT64"),
    bigquery.SchemaField("close", "FLOAT64"),
    bigquery.SchemaField("previous_close", "FLOAT64"),

    # Tier 4: Volume/Change
    bigquery.SchemaField("volume", "FLOAT64"),
    bigquery.SchemaField("average_volume", "FLOAT64"),
    bigquery.SchemaField("change", "FLOAT64"),
    bigquery.SchemaField("percent_change", "FLOAT64"),
    bigquery.SchemaField("hi_lo", "FLOAT64"),
    bigquery.SchemaField("pct_hi_lo", "FLOAT64"),

    # Tier 5: Range
    bigquery.SchemaField("week_52_high", "FLOAT64"),
    bigquery.SchemaField("week_52_low", "FLOAT64"),

    # Tier 6: Technical Indicators
    bigquery.SchemaField("rsi", "FLOAT64"),
    bigquery.SchemaField("stoch_k", "FLOAT64"),
    bigquery.SchemaField("stoch_d", "FLOAT64"),
    bigquery.SchemaField("momentum", "FLOAT64"),
    bigquery.SchemaField("roc", "FLOAT64"),
    bigquery.SchemaField("williams_r", "FLOAT64"),
    bigquery.SchemaField("sma_20", "FLOAT64"),
    bigquery.SchemaField("sma_50", "FLOAT64"),
    bigquery.SchemaField("sma_200", "FLOAT64"),
    bigquery.SchemaField("ema_12", "FLOAT64"),
    bigquery.SchemaField("ema_26", "FLOAT64"),
    bigquery.SchemaField("ema_50", "FLOAT64"),
    bigquery.SchemaField("macd", "FLOAT64"),
    bigquery.SchemaField("macd_signal", "FLOAT64"),
    bigquery.SchemaField("macd_histogram", "FLOAT64"),
    bigquery.SchemaField("bollinger_upper", "FLOAT64"),
    bigquery.SchemaField("bollinger_middle", "FLOAT64"),
    bigquery.SchemaField("bollinger_lower", "FLOAT64"),
    bigquery.SchemaField("atr", "FLOAT64"),
    bigquery.SchemaField("adx", "FLOAT64"),
    bigquery.SchemaField("plus_di", "FLOAT64"),
    bigquery.SchemaField("minus_di", "FLOAT64"),
    bigquery.SchemaField("cci", "FLOAT64"),
    bigquery.SchemaField("obv", "FLOAT64"),
    bigquery.SchemaField("pvo", "FLOAT64"),
    bigquery.SchemaField("ppo", "FLOAT64"),
    bigquery.SchemaField("kama", "FLOAT64"),
    bigquery.SchemaField("trix", "FLOAT64"),
    bigquery.SchemaField("ultimate_osc", "FLOAT64"),
    bigquery.SchemaField("awesome_osc", "FLOAT64"),

    # Tier 7: Timestamps
    bigquery.SchemaField("datetime", "TIMESTAMP"),
    bigquery.SchemaField("timestamp", "INTEGER"),
    bigquery.SchemaField("data_source", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]

# Weekly schema adds week fields
WEEKLY_SCHEMA = STANDARD_SCHEMA.copy()
# Insert week fields before datetime
week_fields = [
    bigquery.SchemaField("week_start", "DATE"),
    bigquery.SchemaField("week_end", "DATE"),
    bigquery.SchemaField("weekly_high", "FLOAT64"),
    bigquery.SchemaField("weekly_low", "FLOAT64"),
    bigquery.SchemaField("weekly_open", "FLOAT64"),
    bigquery.SchemaField("weekly_close", "FLOAT64"),
    bigquery.SchemaField("weekly_volume", "FLOAT64"),
]

# Historical schema (simpler, for large historical tables)
HISTORICAL_SCHEMA = [
    bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("asset_type", "STRING"),
    bigquery.SchemaField("exchange", "STRING"),
    bigquery.SchemaField("country", "STRING"),
    bigquery.SchemaField("currency", "STRING"),
    bigquery.SchemaField("open", "FLOAT64"),
    bigquery.SchemaField("high", "FLOAT64"),
    bigquery.SchemaField("low", "FLOAT64"),
    bigquery.SchemaField("close", "FLOAT64"),
    bigquery.SchemaField("volume", "FLOAT64"),
    bigquery.SchemaField("change", "FLOAT64"),
    bigquery.SchemaField("percent_change", "FLOAT64"),
    bigquery.SchemaField("datetime", "TIMESTAMP"),
    bigquery.SchemaField("data_source", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP"),
]

# Tables to migrate with their target v2 names
TABLES_TO_MIGRATE = {
    # Historical tables (large)
    'stocks_historical_daily': 'v2_stocks_historical_daily',
    'etfs_historical_daily': 'v2_etfs_historical_daily',
    'forex_historical_daily': 'v2_forex_historical_daily',
    'indices_historical_daily': 'v2_indices_historical_daily',
    'commodities_historical_daily': 'v2_commodities_historical_daily',
    'cryptos_historical_daily': 'v2_cryptos_historical_daily',

    # Weekly summary tables
    'stocks_weekly_summary': 'v2_stocks_weekly_summary',
    'cryptos_weekly_summary': 'v2_cryptos_weekly_summary',
    'etfs_weekly_summary': 'v2_etfs_weekly_summary',
    'forex_weekly_summary': 'v2_forex_weekly_summary',
    'indices_weekly_summary': 'v2_indices_weekly_summary',
    'commodities_weekly_summary': 'v2_commodities_weekly_summary',

    # Other asset tables
    'stocks_master_list': 'v2_stocks_master',  # Already exists, skip
    'daily_crypto': 'v2_daily_crypto',
    'daily_stock': 'v2_daily_stock',
    'hourly_crypto': 'v2_hourly_crypto',
    'crypto_weekly': 'v2_crypto_weekly_data',
    'crypto_analysis': 'v2_crypto_analysis',
    'stock_analysis': 'v2_stock_analysis',
    '5min_crypto': 'v2_5min_crypto',
    'crypto_5min_top10_gainers': 'v2_crypto_5min_top10_gainers',
    'crypto_hourly_data': 'v2_crypto_hourly_data',
    'crypto_15min': 'v2_crypto_15min',
    'stocks_15min': 'v2_stocks_15min',
}


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def determine_asset_type(table_name):
    """Determine asset type from table name"""
    name = table_name.lower()
    if 'stock' in name:
        return 'stock'
    elif 'crypto' in name:
        return 'crypto'
    elif 'forex' in name:
        return 'forex'
    elif 'etf' in name:
        return 'etf'
    elif 'indic' in name:
        return 'index'
    elif 'commodit' in name:
        return 'commodity'
    return 'other'


def get_source_schema(client, table_name):
    """Get schema of source table"""
    try:
        table = client.get_table(f"{PROJECT_ID}.{DATASET_ID}.{table_name}")
        return {f.name: f.field_type for f in table.schema}
    except Exception as e:
        print(f"  Error getting schema: {e}")
        return {}


def table_exists(client, table_name):
    """Check if table exists"""
    try:
        client.get_table(f"{PROJECT_ID}.{DATASET_ID}.{table_name}")
        return True
    except:
        return False


def get_row_count(client, table_name):
    """Get row count of a table"""
    try:
        result = list(client.query(f"SELECT COUNT(*) as c FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`").result())
        return result[0].c
    except:
        return 0


def create_v2_table(client, table_name, schema_type='standard'):
    """Create a v2 table with AI-recommended schema"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    if schema_type == 'historical':
        schema = HISTORICAL_SCHEMA
    elif schema_type == 'weekly':
        schema = STANDARD_SCHEMA  # Use standard for now
    else:
        schema = STANDARD_SCHEMA

    table = bigquery.Table(table_ref, schema=schema)

    try:
        client.create_table(table)
        print(f"  Created table: {table_name}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  Table exists: {table_name}")
            return True
        print(f"  Error creating table: {e}")
        return False


def build_field_mapping(source_fields, dest_schema, asset_type):
    """Build field mapping from source to destination with proper conversions"""
    dest_fields = {f.name: f.field_type for f in dest_schema}
    select_parts = []

    # Common field mappings (source -> dest)
    field_aliases = {
        'pair': 'symbol',
        'ticker': 'symbol',
        'rsi_14': 'rsi',
        'rsi_7': 'rsi',
        'macd_line': 'macd',
        'macd_hist': 'macd_histogram',
        'macd_histogram_12_26_9': 'macd_histogram',
        'bbands_upper': 'bollinger_upper',
        'bbands_middle': 'bollinger_middle',
        'bbands_lower': 'bollinger_lower',
        'bb_upper': 'bollinger_upper',
        'bb_middle': 'bollinger_middle',
        'bb_lower': 'bollinger_lower',
        'sma20': 'sma_20',
        'sma50': 'sma_50',
        'sma200': 'sma_200',
        'ema12': 'ema_12',
        'ema26': 'ema_26',
        'ema50': 'ema_50',
        'stoch_slowk': 'stoch_k',
        'stoch_slowd': 'stoch_d',
        'willr': 'williams_r',
    }

    for dest_field, dest_type in dest_fields.items():
        # Check direct match
        if dest_field in source_fields:
            src_type = source_fields[dest_field]
            # Handle type conversions
            if src_type == 'DATETIME' and dest_type == 'TIMESTAMP':
                select_parts.append(f"CAST(`{dest_field}` AS TIMESTAMP) as `{dest_field}`")
            elif src_type == 'INTEGER' and dest_type == 'FLOAT64':
                select_parts.append(f"CAST(`{dest_field}` AS FLOAT64) as `{dest_field}`")
            elif src_type != dest_type and dest_type == 'FLOAT64':
                select_parts.append(f"CAST(`{dest_field}` AS FLOAT64) as `{dest_field}`")
            else:
                select_parts.append(f"`{dest_field}`")

        # Check alias mapping
        elif dest_field in field_aliases.values():
            # Find source field that maps to this dest
            source_alias = None
            for src, dst in field_aliases.items():
                if dst == dest_field and src in source_fields:
                    source_alias = src
                    break

            if source_alias:
                src_type = source_fields[source_alias]
                if src_type == 'DATETIME' and dest_type == 'TIMESTAMP':
                    select_parts.append(f"CAST(`{source_alias}` AS TIMESTAMP) as `{dest_field}`")
                else:
                    select_parts.append(f"`{source_alias}` as `{dest_field}`")
            else:
                select_parts.append(f"CAST(NULL AS {dest_type}) as `{dest_field}`")

        # Special fields
        elif dest_field == 'asset_type':
            select_parts.append(f"'{asset_type}' as asset_type")
        elif dest_field == 'created_at':
            select_parts.append("CURRENT_TIMESTAMP() as created_at")
        elif dest_field == 'data_source':
            if 'data_source' in source_fields:
                select_parts.append("`data_source`")
            else:
                select_parts.append("'migrated' as data_source")

        # NULL for missing fields
        else:
            select_parts.append(f"CAST(NULL AS {dest_type}) as `{dest_field}`")

    return select_parts


def migrate_table(client, source_table, dest_table, schema_type='standard'):
    """Migrate data from source to destination table"""

    # Check if source exists and has data
    if not table_exists(client, source_table):
        print(f"  Source table not found: {source_table}")
        return False

    source_count = get_row_count(client, source_table)
    if source_count == 0:
        print(f"  Source table empty: {source_table}")
        return True

    # Check if dest already has data
    if table_exists(client, dest_table):
        dest_count = get_row_count(client, dest_table)
        if dest_count >= source_count * 0.9:  # Allow 10% variance
            print(f"  Destination already migrated: {dest_table} ({dest_count:,} rows)")
            return True

    # Create dest table if needed
    if not table_exists(client, dest_table):
        if not create_v2_table(client, dest_table, schema_type):
            return False

    # Get schemas
    source_fields = get_source_schema(client, source_table)
    if not source_fields:
        return False

    if schema_type == 'historical':
        dest_schema = HISTORICAL_SCHEMA
    else:
        dest_schema = STANDARD_SCHEMA

    asset_type = determine_asset_type(source_table)

    # Build SELECT clause
    select_parts = build_field_mapping(source_fields, dest_schema, asset_type)
    select_clause = ",\n        ".join(select_parts)

    # Execute migration
    query = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{dest_table}`
    SELECT
        {select_clause}
    FROM `{PROJECT_ID}.{DATASET_ID}.{source_table}`
    """

    try:
        print(f"  Migrating {source_count:,} rows...")
        job = client.query(query)
        job.result()

        # Verify
        new_count = get_row_count(client, dest_table)
        print(f"  SUCCESS: {source_table} -> {dest_table} ({new_count:,} rows)")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    print("=" * 80)
    print("MIGRATING ALL ASSET TABLES TO V2 (AI-RECOMMENDED STRUCTURE)")
    print("=" * 80)

    client = get_client()

    migrated = []
    failed = []
    skipped = []

    for source, dest in TABLES_TO_MIGRATE.items():
        print(f"\n[{source}] -> [{dest}]")

        # Skip if v2_stocks_master (already exists)
        if dest == 'v2_stocks_master':
            print("  Skipping (already exists)")
            skipped.append((source, dest))
            continue

        # Determine schema type
        schema_type = 'standard'
        if 'historical' in source.lower():
            schema_type = 'historical'
        elif 'weekly' in source.lower():
            schema_type = 'weekly'

        if migrate_table(client, source, dest, schema_type):
            migrated.append((source, dest))
        else:
            failed.append((source, dest))

        time.sleep(0.5)

    # Summary
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)

    print(f"\nMigrated: {len(migrated)}")
    print(f"Failed: {len(failed)}")
    print(f"Skipped: {len(skipped)}")

    if failed:
        print("\nFailed tables:")
        for s, d in failed:
            print(f"  - {s}")

    # Show final row counts
    print(f"\n{'Source':<35} {'Dest':<35} {'Rows':>12}")
    print("-" * 85)

    for source, dest in migrated:
        try:
            cnt = get_row_count(client, dest)
            print(f"{source:<35} {dest:<35} {cnt:>12,}")
        except:
            pass


if __name__ == "__main__":
    main()
