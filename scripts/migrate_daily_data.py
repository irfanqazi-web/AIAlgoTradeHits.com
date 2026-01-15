"""
Migrate daily OHLCV data from v2_stocks_daily to stocks_daily_clean
Copies base data fields only - indicators will be calculated separately
"""
from google.cloud import bigquery

client = bigquery.Client(project='aialgotradehits')

print("="*80)
print("MIGRATING DAILY DATA")
print("="*80)

# SQL to copy base data (OHLCV + metadata)
# Leave all indicator fields NULL - they'll be calculated by calculate_all_indicators_FIXED.py
migration_query = """
INSERT INTO `aialgotradehits.crypto_trading_data.stocks_daily_clean`
(
    datetime, symbol,
    open, high, low, close, previous_close, volume,
    average_volume, change, percent_change,
    high_low, pct_high_low, week_52_high, week_52_low,
    name, exchange, currency, asset_type,
    data_source, created_at, updated_at
)
SELECT
    datetime,
    symbol,
    open,
    high,
    low,
    close,
    previous_close,
    CAST(volume AS INT64) as volume,
    CAST(average_volume AS INT64) as average_volume,
    change,
    percent_change,
    hi_lo as high_low,
    pct_hi_lo as pct_high_low,
    week_52_high,
    week_52_low,
    name,
    exchange,
    currency,
    asset_type,
    data_source,
    created_at,
    updated_at
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
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
FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
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
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
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
    print("\nNext step: Run calculate_all_indicators_FIXED.py to add indicators")

except Exception as e:
    print(f"[ERROR] Migration failed: {e}")
