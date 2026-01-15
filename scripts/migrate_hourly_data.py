"""
Migrate hourly OHLCV data from v2_stocks_hourly to stocks_hourly_clean
Copies base data fields only - indicators will be calculated separately
"""
from google.cloud import bigquery

client = bigquery.Client(project='aialgotradehits')

print("="*80)
print("MIGRATING HOURLY DATA")
print("="*80)

# SQL to copy base data (OHLCV + metadata)
# Leave all indicator fields NULL - they'll be calculated by calculate_hourly_indicators.py
migration_query = """
INSERT INTO `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
(
    datetime, symbol,
    open, high, low, close, volume,
    percent_change, change,
    name, exchange, currency, asset_type,
    data_source, created_at, updated_at, timestamp
)
SELECT
    datetime,
    symbol,
    open,
    high,
    low,
    close,
    CAST(volume AS INT64) as volume,
    percent_change,
    change,
    name,
    exchange,
    currency,
    asset_type,
    data_source,
    created_at,
    updated_at,
    timestamp
FROM `aialgotradehits.crypto_trading_data.v2_stocks_hourly`
WHERE datetime IS NOT NULL
  AND symbol IS NOT NULL
"""

print("\nStep 1: Checking source table...")
count_query = """
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(datetime) as min_date,
    MAX(datetime) as max_date
FROM `aialgotradehits.crypto_trading_data.v2_stocks_hourly`
"""
result = client.query(count_query).result()
for row in result:
    print(f"Source table: {row.total_rows:,} rows, {row.unique_symbols} symbols")
    print(f"Date range: {row.min_date} to {row.max_date}")

print("\nStep 2: Starting migration (copying OHLCV data)...")
print("This will take a few minutes...")

try:
    job = client.query(migration_query)
    result = job.result()

    print("[OK] Migration completed!")

    # Verify
    print("\nStep 3: Verifying destination table...")
    verify_query = """
    SELECT
        COUNT(*) as total_rows,
        COUNT(DISTINCT symbol) as unique_symbols,
        MIN(datetime) as min_date,
        MAX(datetime) as max_date,
        COUNTIF(close IS NOT NULL) as rows_with_close,
        COUNTIF(volume IS NOT NULL) as rows_with_volume
    FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
    """

    result = client.query(verify_query).result()
    for row in result:
        print(f"Destination table: {row.total_rows:,} rows, {row.unique_symbols} symbols")
        print(f"Date range: {row.min_date} to {row.max_date}")
        print(f"Rows with close: {row.rows_with_close:,} ({row.rows_with_close/row.total_rows*100:.1f}%)")
        print(f"Rows with volume: {row.rows_with_volume:,} ({row.rows_with_volume/row.total_rows*100:.1f}%)")

    print("\n" + "="*80)
    print("MIGRATION COMPLETE!")
    print("="*80)
    print("\nNext step: Run calculate_hourly_indicators.py to add indicators")

except Exception as e:
    print(f"[ERROR] Migration failed: {e}")
