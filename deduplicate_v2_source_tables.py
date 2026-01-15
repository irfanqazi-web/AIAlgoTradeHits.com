from google.cloud import bigquery
import sys
import io

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = bigquery.Client(project='aialgotradehits')

print("=" * 80)
print("DEDUPLICATING SOURCE TABLES (v2_stocks_hourly, v2_stocks_daily)")
print("=" * 80)

# ============================================================
# DEDUPLICATE v2_stocks_hourly
# ============================================================
print("\n[1/2] Deduplicating v2_stocks_hourly...")
print("Strategy: Keep the row with MAX(close, volume) for each (symbol, datetime)")

# Use DELETE with a subquery to remove duplicates
dedupe_hourly_query = """
DELETE FROM `aialgotradehits.crypto_trading_data.v2_stocks_hourly`
WHERE CONCAT(CAST(symbol AS STRING), '|', CAST(datetime AS STRING)) IN (
    SELECT CONCAT(CAST(symbol AS STRING), '|', CAST(datetime AS STRING))
    FROM (
        SELECT symbol, datetime,
               ROW_NUMBER() OVER (
                   PARTITION BY symbol, datetime
                   ORDER BY close DESC, volume DESC
               ) as row_num
        FROM `aialgotradehits.crypto_trading_data.v2_stocks_hourly`
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

    # Count remaining rows
    count_query = """
    SELECT COUNT(*) as total_rows,
           COUNT(DISTINCT symbol) as unique_symbols
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_hourly`
    """
    count_result = client.query(count_query).to_dataframe()
    print(f"  Total rows: {count_result['total_rows'].values[0]:,}")
    print(f"  Unique symbols: {count_result['unique_symbols'].values[0]}")
    print(f"✓ Hourly source table deduplicated!")

except Exception as e:
    print(f"✗ Error deduplicating hourly table: {str(e)}")
    sys.exit(1)

# ============================================================
# DEDUPLICATE v2_stocks_daily
# ============================================================
print("\n[2/2] Checking v2_stocks_daily for duplicates...")

# First check if there are duplicates
check_daily_query = """
SELECT COUNT(*) as total_dups
FROM (
    SELECT symbol, datetime, COUNT(*) as dup_count
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
    GROUP BY symbol, datetime
    HAVING COUNT(*) > 1
)
"""

try:
    result = client.query(check_daily_query).to_dataframe()
    dup_count = result['total_dups'].values[0]

    if dup_count > 0:
        print(f"Found {dup_count:,} duplicate pairs, deduplicating...")

        dedupe_daily_query = """
        DELETE FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
        WHERE CONCAT(CAST(symbol AS STRING), '|', CAST(datetime AS STRING)) IN (
            SELECT CONCAT(CAST(symbol AS STRING), '|', CAST(datetime AS STRING))
            FROM (
                SELECT symbol, datetime,
                       ROW_NUMBER() OVER (
                           PARTITION BY symbol, datetime
                           ORDER BY close DESC, volume DESC
                       ) as row_num
                FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
            )
            WHERE row_num > 1
        )
        """

        job = client.query(dedupe_daily_query)
        result = job.result()
        rows_deleted = result.num_dml_affected_rows if hasattr(result, 'num_dml_affected_rows') else 0
        print(f"✓ Deleted {rows_deleted:,} duplicate rows")

        # Count remaining rows
        count_query = """
        SELECT COUNT(*) as total_rows,
               COUNT(DISTINCT symbol) as unique_symbols
        FROM `aialgotradehits.crypto_trading_data.v2_stocks_daily`
        """
        count_result = client.query(count_query).to_dataframe()
        print(f"  Total rows: {count_result['total_rows'].values[0]:,}")
        print(f"  Unique symbols: {count_result['unique_symbols'].values[0]}")
        print(f"✓ Daily source table deduplicated!")
    else:
        print("✓ No duplicates found in v2_stocks_daily!")

except Exception as e:
    print(f"✗ Error with daily table: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ SOURCE TABLES DEDUPLICATED!")
print("=" * 80)
print("\nNext steps:")
print("1. Re-run hourly indicator calculations: python calculate_hourly_indicators.py")
print("2. Re-run daily indicator calculations: python calculate_all_indicators_FIXED.py")
