from google.cloud import bigquery
import sys
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = bigquery.Client(project='aialgotradehits')

print("=" * 80)
print("DEDUPLICATING STOCKS TABLES")
print("=" * 80)

# ============================================================
# DEDUPLICATE HOURLY TABLE
# ============================================================
print("\n[1/2] Deduplicating stocks_hourly_clean...")
print("Strategy: Keep the row with MAX(close, volume) for each (symbol, datetime)")

# Use DELETE with a subquery to remove duplicates
dedupe_hourly_query = """
DELETE FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
WHERE CONCAT(CAST(symbol AS STRING), '|', CAST(datetime AS STRING)) IN (
    SELECT CONCAT(CAST(symbol AS STRING), '|', CAST(datetime AS STRING))
    FROM (
        SELECT symbol, datetime,
               ROW_NUMBER() OVER (
                   PARTITION BY symbol, datetime
                   ORDER BY close DESC, volume DESC
               ) as row_num
        FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
    )
    WHERE row_num > 1
)
"""

try:
    print("Running deduplication query...")
    job = client.query(dedupe_hourly_query)
    result = job.result()
    rows_deleted = result.num_dml_affected_rows if hasattr(result, 'num_dml_affected_rows') else 0
    print(f"✓ Deleted {rows_deleted:,} duplicate rows")
    print(f"✓ Hourly table deduplicated successfully!")

    # Count remaining rows
    count_query = """
    SELECT COUNT(*) as total_rows,
           COUNT(DISTINCT symbol) as unique_symbols
    FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
    """
    count_result = client.query(count_query).to_dataframe()
    print(f"  Total rows: {count_result['total_rows'].values[0]:,}")
    print(f"  Unique symbols: {count_result['unique_symbols'].values[0]}")

except Exception as e:
    print(f"✗ Error deduplicating hourly table: {str(e)}")
    sys.exit(1)

# ============================================================
# DEDUPLICATE DAILY TABLE
# ============================================================
print("\n[2/2] Deduplicating stocks_daily_clean...")
print("Strategy: Keep the row with MAX(close, volume) for each (symbol, datetime)")

# Use DELETE with a subquery to remove duplicates
dedupe_daily_query = """
DELETE FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE CONCAT(CAST(symbol AS STRING), '|', CAST(datetime AS STRING)) IN (
    SELECT CONCAT(CAST(symbol AS STRING), '|', CAST(datetime AS STRING))
    FROM (
        SELECT symbol, datetime,
               ROW_NUMBER() OVER (
                   PARTITION BY symbol, datetime
                   ORDER BY close DESC, volume DESC
               ) as row_num
        FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    )
    WHERE row_num > 1
)
"""

try:
    print("Running deduplication query...")
    job = client.query(dedupe_daily_query)
    result = job.result()
    rows_deleted = result.num_dml_affected_rows if hasattr(result, 'num_dml_affected_rows') else 0
    print(f"✓ Deleted {rows_deleted:,} duplicate rows")
    print(f"✓ Daily table deduplicated successfully!")

    # Count remaining rows
    count_query = """
    SELECT COUNT(*) as total_rows,
           COUNT(DISTINCT symbol) as unique_symbols
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    """
    count_result = client.query(count_query).to_dataframe()
    print(f"  Total rows: {count_result['total_rows'].values[0]:,}")
    print(f"  Unique symbols: {count_result['unique_symbols'].values[0]}")

except Exception as e:
    print(f"✗ Error deduplicating daily table: {str(e)}")
    sys.exit(1)

# ============================================================
# VERIFY NO DUPLICATES REMAIN
# ============================================================
print("\n" + "=" * 80)
print("VERIFICATION: Checking for remaining duplicates...")
print("=" * 80)

# Check hourly
verify_hourly = """
SELECT COUNT(*) as total_dups
FROM (
    SELECT symbol, datetime, COUNT(*) as dup_count
    FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
    GROUP BY symbol, datetime
    HAVING COUNT(*) > 1
)
"""
hourly_dups = client.query(verify_hourly).to_dataframe()
hourly_dup_count = hourly_dups['total_dups'].values[0]
print(f"\n✓ Hourly duplicates remaining: {hourly_dup_count}")

# Check daily
verify_daily = """
SELECT COUNT(*) as total_dups
FROM (
    SELECT symbol, datetime, COUNT(*) as dup_count
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    GROUP BY symbol, datetime
    HAVING COUNT(*) > 1
)
"""
daily_dups = client.query(verify_daily).to_dataframe()
daily_dup_count = daily_dups['total_dups'].values[0]
print(f"✓ Daily duplicates remaining: {daily_dup_count}")

if hourly_dup_count == 0 and daily_dup_count == 0:
    print("\n" + "=" * 80)
    print("✓ SUCCESS! All duplicates removed from both tables.")
    print("=" * 80)
else:
    print("\n" + "=" * 80)
    print("⚠ WARNING: Some duplicates still remain!")
    print("=" * 80)

print("\nDeduplication complete!")
