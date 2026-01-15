"""
Sync V2 Tables to Clean Tables
This migrates data from v2_* tables to *_clean tables for ML system compatibility.

Author: Claude Code
Date: December 2025
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

# Mapping from v2 tables to clean tables
TABLE_MAPPINGS = [
    # Hourly tables (missing data!)
    {
        'source': 'v2_stocks_hourly',
        'target': 'stocks_hourly_clean',
        'asset_type': 'stocks'
    },
    {
        'source': 'v2_crypto_hourly',
        'target': 'crypto_hourly_clean',
        'asset_type': 'crypto'
    },
    # 5-min tables
    {
        'source': 'v2_stocks_5min',
        'target': 'stocks_5min_clean',
        'asset_type': 'stocks'
    },
    {
        'source': 'v2_crypto_5min',
        'target': 'crypto_5min_clean',
        'asset_type': 'crypto'
    },
    # Daily tables (backup sync)
    {
        'source': 'v2_stocks_daily',
        'target': 'stocks_daily_clean',
        'asset_type': 'stocks'
    },
    {
        'source': 'v2_crypto_daily',
        'target': 'crypto_daily_clean',
        'asset_type': 'crypto'
    },
]

def get_target_schema():
    """Return the standard clean table schema"""
    return [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("datetime", "TIMESTAMP"),
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("open", "FLOAT64"),
        bigquery.SchemaField("high", "FLOAT64"),
        bigquery.SchemaField("low", "FLOAT64"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "INT64"),
        # Momentum indicators
        bigquery.SchemaField("rsi", "FLOAT64"),
        bigquery.SchemaField("macd", "FLOAT64"),
        bigquery.SchemaField("macd_signal", "FLOAT64"),
        bigquery.SchemaField("macd_histogram", "FLOAT64"),
        bigquery.SchemaField("stoch_k", "FLOAT64"),
        bigquery.SchemaField("stoch_d", "FLOAT64"),
        bigquery.SchemaField("williams_r", "FLOAT64"),
        bigquery.SchemaField("roc", "FLOAT64"),
        bigquery.SchemaField("momentum", "FLOAT64"),
        # Trend indicators
        bigquery.SchemaField("sma_20", "FLOAT64"),
        bigquery.SchemaField("sma_50", "FLOAT64"),
        bigquery.SchemaField("sma_200", "FLOAT64"),
        bigquery.SchemaField("ema_12", "FLOAT64"),
        bigquery.SchemaField("ema_26", "FLOAT64"),
        bigquery.SchemaField("ema_50", "FLOAT64"),
        bigquery.SchemaField("adx", "FLOAT64"),
        bigquery.SchemaField("plus_di", "FLOAT64"),
        bigquery.SchemaField("minus_di", "FLOAT64"),
        # Volatility
        bigquery.SchemaField("atr", "FLOAT64"),
        bigquery.SchemaField("bollinger_upper", "FLOAT64"),
        bigquery.SchemaField("bollinger_middle", "FLOAT64"),
        bigquery.SchemaField("bollinger_lower", "FLOAT64"),
        # Volume indicators
        bigquery.SchemaField("obv", "FLOAT64"),
        bigquery.SchemaField("mfi", "FLOAT64"),
        bigquery.SchemaField("cci", "FLOAT64"),
        # Metadata
        bigquery.SchemaField("data_source", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
    ]

def create_clean_table_if_not_exists(client, table_id):
    """Create clean table with proper schema if it doesn't exist"""
    try:
        client.get_table(table_id)
        print(f"  Table {table_id} exists")
        return True
    except Exception:
        print(f"  Creating table {table_id}...")
        table = bigquery.Table(table_id, schema=get_target_schema())
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="datetime"
        )
        client.create_table(table)
        print(f"  Created table {table_id}")
        return True

def sync_table(client, source_table, target_table, incremental=True):
    """Sync data from v2 table to clean table"""

    source_id = f"{PROJECT_ID}.{DATASET_ID}.{source_table}"
    target_id = f"{PROJECT_ID}.{DATASET_ID}.{target_table}"

    print(f"\nSyncing {source_table} -> {target_table}")

    # Ensure target table exists
    create_clean_table_if_not_exists(client, target_id)

    # Check source count
    source_count_query = f"SELECT COUNT(*) as cnt FROM `{source_id}`"
    source_count = list(client.query(source_count_query).result())[0].cnt
    print(f"  Source records: {source_count:,}")

    if source_count == 0:
        print(f"  Source table is empty, skipping")
        return 0

    # Check target count
    target_count_query = f"SELECT COUNT(*) as cnt FROM `{target_id}`"
    target_count = list(client.query(target_count_query).result())[0].cnt
    print(f"  Target records: {target_count:,}")

    if incremental and target_count > 0:
        # Get latest timestamp in target
        latest_query = f"SELECT MAX(datetime) as latest FROM `{target_id}`"
        latest = list(client.query(latest_query).result())[0].latest
        print(f"  Latest in target: {latest}")
        where_clause = f"WHERE datetime > '{latest}'"
    else:
        where_clause = ""

    # Build the sync query - map v2 columns to clean columns
    sync_query = f"""
    INSERT INTO `{target_id}` (
        id, symbol, datetime, date, open, high, low, close, volume,
        rsi, macd, macd_signal, macd_histogram, stoch_k, stoch_d,
        williams_r, roc, momentum, sma_20, sma_50, sma_200,
        ema_12, ema_26, ema_50, adx, plus_di, minus_di,
        atr, bollinger_upper, bollinger_middle, bollinger_lower,
        obv, mfi, cci, data_source, created_at, updated_at
    )
    SELECT
        COALESCE(id, GENERATE_UUID()) as id,
        symbol,
        datetime,
        COALESCE(date, DATE(datetime)) as date,
        open, high, low, close,
        CAST(volume AS INT64) as volume,
        COALESCE(rsi, rsi_14) as rsi,
        macd,
        macd_signal,
        macd_histogram,
        stoch_k,
        stoch_d,
        williams_r,
        roc,
        momentum,
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50,
        adx,
        plus_di,
        minus_di,
        COALESCE(atr, atr_14) as atr,
        COALESCE(bollinger_upper, bb_upper) as bollinger_upper,
        COALESCE(bollinger_middle, bb_middle) as bollinger_middle,
        COALESCE(bollinger_lower, bb_lower) as bollinger_lower,
        obv,
        mfi,
        cci,
        COALESCE(data_source, 'twelvedata') as data_source,
        COALESCE(created_at, CURRENT_TIMESTAMP()) as created_at,
        CURRENT_TIMESTAMP() as updated_at
    FROM `{source_id}`
    {where_clause}
    """

    try:
        job = client.query(sync_query)
        job.result()

        # Get new count
        new_count = list(client.query(target_count_query).result())[0].cnt
        added = new_count - target_count
        print(f"  Added {added:,} records (new total: {new_count:,})")
        return added

    except Exception as e:
        print(f"  Error syncing: {e}")
        # Try simpler approach without column mapping
        return sync_table_simple(client, source_table, target_table)

def sync_table_simple(client, source_table, target_table):
    """Simple sync using INSERT SELECT with only matching columns"""

    source_id = f"{PROJECT_ID}.{DATASET_ID}.{source_table}"
    target_id = f"{PROJECT_ID}.{DATASET_ID}.{target_table}"

    print(f"  Trying simple sync...")

    # Get source schema
    source_ref = client.get_table(source_id)
    source_cols = {f.name for f in source_ref.schema}

    # Get target schema
    target_ref = client.get_table(target_id)
    target_cols = {f.name for f in target_ref.schema}

    # Find common columns
    common = source_cols.intersection(target_cols)
    print(f"  Common columns: {len(common)}")

    # Build select for common columns
    select_cols = ', '.join(sorted(common))

    sync_query = f"""
    INSERT INTO `{target_id}` ({select_cols})
    SELECT {select_cols}
    FROM `{source_id}` src
    WHERE NOT EXISTS (
        SELECT 1 FROM `{target_id}` tgt
        WHERE tgt.symbol = src.symbol
        AND tgt.datetime = src.datetime
    )
    """

    try:
        job = client.query(sync_query)
        job.result()

        # Count added
        count_query = f"SELECT COUNT(*) as cnt FROM `{target_id}`"
        new_count = list(client.query(count_query).result())[0].cnt
        print(f"  Sync complete. Target now has {new_count:,} records")
        return new_count

    except Exception as e:
        print(f"  Simple sync also failed: {e}")
        return 0

def main():
    print("=" * 60)
    print("V2 to CLEAN Table Sync")
    print("=" * 60)

    client = bigquery.Client(project=PROJECT_ID)

    total_added = 0

    for mapping in TABLE_MAPPINGS:
        added = sync_table(client, mapping['source'], mapping['target'])
        total_added += added

    print("\n" + "=" * 60)
    print(f"SYNC COMPLETE - Total records added: {total_added:,}")
    print("=" * 60)

    # Show final counts
    print("\nFinal Table Status:")
    print("-" * 50)

    for mapping in TABLE_MAPPINGS:
        target_id = f"{PROJECT_ID}.{DATASET_ID}.{mapping['target']}"
        query = f"""
        SELECT
            COUNT(*) as records,
            COUNT(DISTINCT symbol) as symbols,
            MAX(datetime) as latest
        FROM `{target_id}`
        """
        result = list(client.query(query).result())[0]
        print(f"{mapping['target']}: {result.records:,} records, {result.symbols} symbols, latest: {result.latest}")

if __name__ == '__main__':
    main()
