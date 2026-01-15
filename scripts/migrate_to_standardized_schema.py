"""
Migrate BigQuery tables to standardized schema with proper field ordering
Strategy: Create new v2_ tables with standardized schema, migrate data

Field Order Tiers:
1. IDENTITY: symbol, name, asset_type
2. CLASSIFICATION: exchange, country, sector, industry, currency
3. PRICE: open, high, low, close, previous_close
4. VOLUME/CHANGE: volume, average_volume, change, percent_change, hi_lo, pct_hi_lo
5. RANGE: week_52_high, week_52_low
6. TECHNICAL INDICATORS: rsi, macd, sma_*, ema_*, etc.
7. TIMESTAMPS: datetime, timestamp, data_source, created_at, updated_at
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime
import time

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

# Standardized schema definitions for each table type
STANDARDIZED_SCHEMAS = {
    # Master List Schema (for stocks_master_list, etc.)
    'master_list': [
        ('symbol', 'STRING', 'Primary ticker symbol'),
        ('name', 'STRING', 'Full asset name'),
        ('asset_type', 'STRING', 'stock/crypto/forex/etf/index/commodity'),
        ('exchange', 'STRING', 'Trading exchange'),
        ('country', 'STRING', 'Country code'),
        ('sector', 'STRING', 'Business sector'),
        ('industry', 'STRING', 'Industry classification'),
        ('currency', 'STRING', 'Trading currency'),
        ('mic_code', 'STRING', 'Market Identifier Code'),
        ('type', 'STRING', 'Security type'),
        ('open', 'FLOAT64', 'Opening price'),
        ('high', 'FLOAT64', 'High price'),
        ('low', 'FLOAT64', 'Low price'),
        ('close', 'FLOAT64', 'Closing price'),
        ('previous_close', 'FLOAT64', 'Previous close'),
        ('volume', 'FLOAT64', 'Trading volume'),
        ('average_volume', 'FLOAT64', 'Average volume'),
        ('change', 'FLOAT64', 'Price change'),
        ('percent_change', 'FLOAT64', 'Percentage change'),
        ('hi_lo', 'FLOAT64', 'Daily range'),
        ('pct_hi_lo', 'FLOAT64', 'Percentage range'),
        ('week_52_high', 'FLOAT64', '52-week high'),
        ('week_52_low', 'FLOAT64', '52-week low'),
        ('datetime', 'TIMESTAMP', 'Data timestamp'),
        ('data_source', 'STRING', 'Data provider'),
        ('created_at', 'TIMESTAMP', 'Record creation time'),
        ('updated_at', 'TIMESTAMP', 'Last update time'),
    ],

    # Daily Data Schema (for *_daily_data tables with technical indicators)
    'daily_data': [
        ('symbol', 'STRING', 'Primary ticker symbol'),
        ('name', 'STRING', 'Full asset name'),
        ('asset_type', 'STRING', 'stock/crypto/forex/etf/index/commodity'),
        ('exchange', 'STRING', 'Trading exchange'),
        ('country', 'STRING', 'Country code'),
        ('currency', 'STRING', 'Trading currency'),
        # Price Data
        ('open', 'FLOAT64', 'Opening price'),
        ('high', 'FLOAT64', 'High price'),
        ('low', 'FLOAT64', 'Low price'),
        ('close', 'FLOAT64', 'Closing price'),
        ('previous_close', 'FLOAT64', 'Previous close'),
        # Volume & Change
        ('volume', 'FLOAT64', 'Trading volume'),
        ('average_volume', 'FLOAT64', 'Average volume'),
        ('change', 'FLOAT64', 'Price change'),
        ('percent_change', 'FLOAT64', 'Percentage change'),
        ('hi_lo', 'FLOAT64', 'Daily range'),
        ('pct_hi_lo', 'FLOAT64', 'Percentage range'),
        # Range
        ('week_52_high', 'FLOAT64', '52-week high'),
        ('week_52_low', 'FLOAT64', '52-week low'),
        # Momentum Indicators
        ('rsi', 'FLOAT64', 'Relative Strength Index'),
        ('stoch_k', 'FLOAT64', 'Stochastic %K'),
        ('stoch_d', 'FLOAT64', 'Stochastic %D'),
        ('momentum', 'FLOAT64', 'Momentum'),
        ('roc', 'FLOAT64', 'Rate of Change'),
        ('williams_r', 'FLOAT64', 'Williams %R'),
        # Moving Averages
        ('sma_20', 'FLOAT64', '20-period SMA'),
        ('sma_50', 'FLOAT64', '50-period SMA'),
        ('sma_200', 'FLOAT64', '200-period SMA'),
        ('ema_12', 'FLOAT64', '12-period EMA'),
        ('ema_26', 'FLOAT64', '26-period EMA'),
        ('ema_50', 'FLOAT64', '50-period EMA'),
        # MACD
        ('macd', 'FLOAT64', 'MACD line'),
        ('macd_signal', 'FLOAT64', 'MACD signal line'),
        ('macd_histogram', 'FLOAT64', 'MACD histogram'),
        # Bollinger Bands
        ('bollinger_upper', 'FLOAT64', 'Upper Bollinger Band'),
        ('bollinger_middle', 'FLOAT64', 'Middle Bollinger Band'),
        ('bollinger_lower', 'FLOAT64', 'Lower Bollinger Band'),
        # Volatility & Strength
        ('atr', 'FLOAT64', 'Average True Range'),
        ('adx', 'FLOAT64', 'Average Directional Index'),
        ('plus_di', 'FLOAT64', 'Positive Directional Indicator'),
        ('minus_di', 'FLOAT64', 'Negative Directional Indicator'),
        # Other Indicators
        ('cci', 'FLOAT64', 'Commodity Channel Index'),
        ('obv', 'FLOAT64', 'On-Balance Volume'),
        ('pvo', 'FLOAT64', 'Price Volume Oscillator'),
        ('ppo', 'FLOAT64', 'Price Percentage Oscillator'),
        ('kama', 'FLOAT64', 'Kaufman Adaptive MA'),
        ('trix', 'FLOAT64', 'Triple Exponential Average'),
        ('ultimate_osc', 'FLOAT64', 'Ultimate Oscillator'),
        ('awesome_osc', 'FLOAT64', 'Awesome Oscillator'),
        # Timestamps
        ('datetime', 'TIMESTAMP', 'Data timestamp'),
        ('timestamp', 'INT64', 'Unix timestamp'),
        ('data_source', 'STRING', 'Data provider'),
        ('created_at', 'TIMESTAMP', 'Record creation time'),
    ],

    # Hourly Data Schema
    'hourly_data': [
        ('symbol', 'STRING', 'Primary ticker symbol'),
        ('name', 'STRING', 'Full asset name'),
        ('asset_type', 'STRING', 'stock/crypto/forex/etf/index/commodity'),
        ('exchange', 'STRING', 'Trading exchange'),
        ('currency', 'STRING', 'Trading currency'),
        # Price Data
        ('open', 'FLOAT64', 'Opening price'),
        ('high', 'FLOAT64', 'High price'),
        ('low', 'FLOAT64', 'Low price'),
        ('close', 'FLOAT64', 'Closing price'),
        # Volume & Change
        ('volume', 'FLOAT64', 'Trading volume'),
        ('change', 'FLOAT64', 'Price change'),
        ('percent_change', 'FLOAT64', 'Percentage change'),
        # Technical Indicators
        ('rsi', 'FLOAT64', 'Relative Strength Index'),
        ('sma_20', 'FLOAT64', '20-period SMA'),
        ('sma_50', 'FLOAT64', '50-period SMA'),
        ('ema_12', 'FLOAT64', '12-period EMA'),
        ('ema_26', 'FLOAT64', '26-period EMA'),
        ('macd', 'FLOAT64', 'MACD line'),
        ('macd_signal', 'FLOAT64', 'MACD signal line'),
        ('bollinger_upper', 'FLOAT64', 'Upper Bollinger Band'),
        ('bollinger_middle', 'FLOAT64', 'Middle Bollinger Band'),
        ('bollinger_lower', 'FLOAT64', 'Lower Bollinger Band'),
        ('atr', 'FLOAT64', 'Average True Range'),
        ('adx', 'FLOAT64', 'Average Directional Index'),
        # Timestamps
        ('datetime', 'TIMESTAMP', 'Data timestamp'),
        ('timestamp', 'INT64', 'Unix timestamp'),
        ('data_source', 'STRING', 'Data provider'),
    ],

    # Weekly Summary Schema
    'weekly_summary': [
        ('symbol', 'STRING', 'Primary ticker symbol'),
        ('name', 'STRING', 'Full asset name'),
        ('asset_type', 'STRING', 'stock/crypto/forex/etf/index/commodity'),
        ('exchange', 'STRING', 'Trading exchange'),
        ('country', 'STRING', 'Country code'),
        ('currency', 'STRING', 'Trading currency'),
        # Price Data
        ('week_open', 'FLOAT64', 'Week opening price'),
        ('week_high', 'FLOAT64', 'Week high'),
        ('week_low', 'FLOAT64', 'Week low'),
        ('week_close', 'FLOAT64', 'Week closing price'),
        # Volume & Change
        ('week_volume', 'FLOAT64', 'Week total volume'),
        ('week_change', 'FLOAT64', 'Week price change'),
        ('week_pct_change', 'FLOAT64', 'Week percentage change'),
        # Technical Indicators
        ('rsi', 'FLOAT64', 'RSI'),
        ('sma_20', 'FLOAT64', '20-period SMA'),
        ('sma_50', 'FLOAT64', '50-period SMA'),
        ('macd', 'FLOAT64', 'MACD'),
        ('macd_signal', 'FLOAT64', 'MACD signal'),
        # Timestamps
        ('week_start', 'DATE', 'Week start date'),
        ('week_end', 'DATE', 'Week end date'),
        ('datetime', 'TIMESTAMP', 'Record timestamp'),
        ('data_source', 'STRING', 'Data provider'),
    ],
}

# Table mapping: old table -> (schema type, new table name)
TABLE_MAPPINGS = {
    # HIGH PRIORITY - Stocks
    'stocks_master_list': ('master_list', 'v2_stocks_master'),
    'stocks_daily_data': ('daily_data', 'v2_stocks_daily'),
    'stocks_hourly_data': ('hourly_data', 'v2_stocks_hourly'),
    'stocks_5min_data': ('hourly_data', 'v2_stocks_5min'),
    'stocks_weekly_summary': ('weekly_summary', 'v2_stocks_weekly'),

    # HIGH PRIORITY - Crypto
    'crypto_analysis': ('daily_data', 'v2_crypto_daily'),
    'crypto_hourly_data': ('hourly_data', 'v2_crypto_hourly'),
    'crypto_5min_top10_gainers': ('hourly_data', 'v2_crypto_5min'),

    # MEDIUM PRIORITY - Forex
    'forex_daily_data': ('daily_data', 'v2_forex_daily'),
    'forex_hourly_data': ('hourly_data', 'v2_forex_hourly'),
    'forex_5min_data': ('hourly_data', 'v2_forex_5min'),
    'forex_weekly_summary': ('weekly_summary', 'v2_forex_weekly'),

    # MEDIUM PRIORITY - ETFs
    'etfs_daily_data': ('daily_data', 'v2_etfs_daily'),
    'etfs_hourly_data': ('hourly_data', 'v2_etfs_hourly'),
    'etfs_5min_data': ('hourly_data', 'v2_etfs_5min'),
    'etfs_weekly_summary': ('weekly_summary', 'v2_etfs_weekly'),

    # MEDIUM PRIORITY - Indices
    'indices_daily_data': ('daily_data', 'v2_indices_daily'),
    'indices_hourly_data': ('hourly_data', 'v2_indices_hourly'),
    'indices_5min_data': ('hourly_data', 'v2_indices_5min'),
    'indices_weekly_summary': ('weekly_summary', 'v2_indices_weekly'),

    # MEDIUM PRIORITY - Commodities
    'commodities_daily_data': ('daily_data', 'v2_commodities_daily'),
    'commodities_hourly_data': ('hourly_data', 'v2_commodities_hourly'),
    'commodities_5min_data': ('hourly_data', 'v2_commodities_5min'),
    'commodities_weekly_summary': ('weekly_summary', 'v2_commodities_weekly'),
}


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def create_schema(schema_definition):
    """Create BigQuery schema from definition"""
    return [
        bigquery.SchemaField(name, field_type, description=desc)
        for name, field_type, desc in schema_definition
    ]


def get_source_fields(client, source_table):
    """Get list of fields in source table"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{source_table}"
    try:
        table = client.get_table(table_ref)
        return [f.name for f in table.schema]
    except Exception as e:
        print(f"Error getting schema for {source_table}: {e}")
        return []


def create_new_table(client, table_name, schema_type):
    """Create new v2 table with standardized schema"""
    schema_def = STANDARDIZED_SCHEMAS[schema_type]
    schema = create_schema(schema_def)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    table = bigquery.Table(table_ref, schema=schema)

    try:
        client.create_table(table)
        print(f"  Created table: {table_name}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  Table already exists: {table_name}")
            return True
        print(f"  Error creating {table_name}: {e}")
        return False


def migrate_data(client, source_table, dest_table, schema_type):
    """Migrate data from source to destination with field mapping"""

    # Get source fields
    source_fields = get_source_fields(client, source_table)
    if not source_fields:
        print(f"  No source fields found for {source_table}")
        return False

    # Get destination field names
    dest_fields = [f[0] for f in STANDARDIZED_SCHEMAS[schema_type]]

    # Build SELECT clause - map source fields to destination, use NULL for missing
    select_parts = []
    for dest_field in dest_fields:
        if dest_field in source_fields:
            select_parts.append(f"`{dest_field}`")
        elif dest_field == 'asset_type':
            # Determine asset type from table name
            if 'stock' in source_table.lower():
                select_parts.append("'stock' as asset_type")
            elif 'crypto' in source_table.lower():
                select_parts.append("'crypto' as asset_type")
            elif 'forex' in source_table.lower():
                select_parts.append("'forex' as asset_type")
            elif 'etf' in source_table.lower():
                select_parts.append("'etf' as asset_type")
            elif 'indic' in source_table.lower():
                select_parts.append("'index' as asset_type")
            elif 'commodit' in source_table.lower():
                select_parts.append("'commodity' as asset_type")
            else:
                select_parts.append("'other' as asset_type")
        elif dest_field == 'created_at':
            select_parts.append("CURRENT_TIMESTAMP() as created_at")
        elif dest_field == 'macd_histogram' and 'macd_hist' in source_fields:
            select_parts.append("`macd_hist` as macd_histogram")
        elif dest_field == 'symbol' and 'pair' in source_fields:
            select_parts.append("`pair` as symbol")
        else:
            # Use NULL for missing fields
            field_type = next((f[1] for f in STANDARDIZED_SCHEMAS[schema_type] if f[0] == dest_field), 'STRING')
            if field_type == 'STRING':
                select_parts.append(f"CAST(NULL AS STRING) as `{dest_field}`")
            elif field_type in ('FLOAT64', 'FLOAT'):
                select_parts.append(f"CAST(NULL AS FLOAT64) as `{dest_field}`")
            elif field_type == 'INT64':
                select_parts.append(f"CAST(NULL AS INT64) as `{dest_field}`")
            elif field_type == 'TIMESTAMP':
                select_parts.append(f"CAST(NULL AS TIMESTAMP) as `{dest_field}`")
            elif field_type == 'DATE':
                select_parts.append(f"CAST(NULL AS DATE) as `{dest_field}`")
            else:
                select_parts.append(f"NULL as `{dest_field}`")

    select_clause = ",\n    ".join(select_parts)

    query = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{dest_table}`
    SELECT
    {select_clause}
    FROM `{PROJECT_ID}.{DATASET_ID}.{source_table}`
    """

    try:
        job = client.query(query)
        job.result()  # Wait for completion
        print(f"  Migrated data from {source_table} to {dest_table}")
        return True
    except Exception as e:
        print(f"  Error migrating {source_table}: {e}")
        return False


def get_row_counts(client, tables):
    """Get row counts for multiple tables"""
    counts = {}
    for table in tables:
        try:
            query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.{table}`"
            result = list(client.query(query).result())[0]
            counts[table] = result.cnt
        except:
            counts[table] = 0
    return counts


def main():
    print("=" * 80)
    print("BIGQUERY TABLE SCHEMA MIGRATION")
    print("=" * 80)
    print(f"\nProject: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Tables to migrate: {len(TABLE_MAPPINGS)}")

    client = get_client()

    # Phase 1: Create new tables
    print("\n" + "=" * 80)
    print("PHASE 1: Creating new v2 tables with standardized schemas")
    print("=" * 80)

    created_tables = []
    for source, (schema_type, dest) in TABLE_MAPPINGS.items():
        print(f"\n[{source}] -> [{dest}] (schema: {schema_type})")
        if create_new_table(client, dest, schema_type):
            created_tables.append((source, dest, schema_type))

    # Phase 2: Migrate data
    print("\n" + "=" * 80)
    print("PHASE 2: Migrating data to new tables")
    print("=" * 80)

    migrated = []
    failed = []

    for source, dest, schema_type in created_tables:
        print(f"\n[{source}] -> [{dest}]")
        if migrate_data(client, source, dest, schema_type):
            migrated.append((source, dest))
        else:
            failed.append((source, dest))
        time.sleep(1)  # Rate limiting

    # Phase 3: Verify migration
    print("\n" + "=" * 80)
    print("PHASE 3: Verifying migration")
    print("=" * 80)

    source_tables = [m[0] for m in migrated]
    dest_tables = [m[1] for m in migrated]

    print("\nGetting row counts...")
    source_counts = get_row_counts(client, source_tables)
    dest_counts = get_row_counts(client, dest_tables)

    print("\nMigration Results:")
    print("-" * 60)
    print(f"{'Source Table':<30} {'Dest Table':<25} {'Rows':<10}")
    print("-" * 60)

    for source, dest in migrated:
        src_count = source_counts.get(source, 0)
        dst_count = dest_counts.get(dest, 0)
        status = "OK" if src_count == dst_count else "MISMATCH"
        print(f"{source:<30} {dest:<25} {dst_count:<10} {status}")

    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"Total tables processed: {len(TABLE_MAPPINGS)}")
    print(f"Successfully migrated: {len(migrated)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed migrations:")
        for source, dest in failed:
            print(f"  - {source} -> {dest}")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("""
1. Verify data integrity in new v2_ tables
2. Update API endpoints to use new table names
3. Update frontend queries if needed
4. After verification, archive old tables (optional)
5. Consider renaming v2_ tables to remove prefix (optional)
""")


if __name__ == "__main__":
    main()
