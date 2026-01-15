from google.cloud import bigquery
import sys
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = bigquery.Client(project='aialgotradehits')

print("=" * 80)
print("RE-MIGRATING HOURLY DATA WITH DEDUPLICATION")
print("=" * 80)

# Step 1: Truncate the corrupted table
print("\n[Step 1] Truncating stocks_hourly_clean...")
truncate_query = """
TRUNCATE TABLE `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
"""

try:
    job = client.query(truncate_query)
    job.result()
    print("✓ Table truncated")
except Exception as e:
    print(f"✗ Error truncating table: {str(e)}")
    sys.exit(1)

# Step 2: Re-migrate data with deduplication
print("\n[Step 2] Migrating deduplicated data from v2_stocks_hourly...")
print("This will insert unique (symbol, datetime) rows only, keeping the one with highest close/volume")

migration_query = """
INSERT INTO `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
SELECT * EXCEPT(row_num)
FROM (
    SELECT
        symbol,
        datetime,
        open,
        high,
        low,
        close,
        volume,
        trades,
        market_cap,
        volume_24h,
        exchange,
        mic_code,
        currency,
        sector,
        industry,
        average_volume,
        ROW_NUMBER() OVER (
            PARTITION BY symbol, datetime
            ORDER BY close DESC, volume DESC
        ) as row_num
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_hourly`
)
WHERE row_num = 1
"""

try:
    job = client.query(migration_query)
    result = job.result()
    rows_inserted = result.num_dml_affected_rows if hasattr(result, 'num_dml_affected_rows') else 0
    print(f"✓ Inserted {rows_inserted:,} unique rows")
except Exception as e:
    print(f"✗ Error migrating data: {str(e)}")
    sys.exit(1)

# Step 3: Verify the migration
print("\n[Step 3] Verifying migration...")

verify_query = """
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(datetime) as min_date,
    MAX(datetime) as max_date
FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
"""

try:
    result = client.query(verify_query).to_dataframe()
    print(f"✓ Total rows: {result['total_rows'].values[0]:,}")
    print(f"✓ Unique symbols: {result['unique_symbols'].values[0]}")
    print(f"✓ Date range: {result['min_date'].values[0]} to {result['max_date'].values[0]}")
except Exception as e:
    print(f"✗ Error verifying: {str(e)}")
    sys.exit(1)

# Step 4: Check for duplicates
print("\n[Step 4] Checking for duplicates...")

dup_check_query = """
SELECT COUNT(*) as total_dups
FROM (
    SELECT symbol, datetime, COUNT(*) as dup_count
    FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
    GROUP BY symbol, datetime
    HAVING COUNT(*) > 1
)
"""

try:
    result = client.query(dup_check_query).to_dataframe()
    dup_count = result['total_dups'].values[0]
    if dup_count == 0:
        print(f"✓ No duplicates found!")
    else:
        print(f"⚠ WARNING: {dup_count} duplicate (symbol, datetime) pairs found!")
except Exception as e:
    print(f"✗ Error checking duplicates: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ HOURLY DATA RE-MIGRATION COMPLETE!")
print("=" * 80)
