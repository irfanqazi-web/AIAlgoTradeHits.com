"""
Merge v2_stocks_daily and v2_stocks_historical_daily into a unified table
This eliminates confusion and provides complete historical data in one place
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'

client = bigquery.Client(project=PROJECT_ID)

print("="*80)
print("MERGING STOCK TABLES INTO UNIFIED TABLE")
print("="*80)
print(f"Project: {PROJECT_ID}")
print(f"Dataset: {DATASET_ID}")
print()

# Step 1: Create the unified table with all fields from both tables
print("Step 1: Creating unified table schema...")
create_table_query = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.stocks_unified_daily` AS
WITH historical_data AS (
    SELECT
        symbol,
        name,
        datetime,
        open,
        high,
        low,
        close,
        volume,
        exchange,
        currency,
        percent_change,
        data_source,
        created_at,
        NULL as rsi,
        NULL as macd,
        NULL as macd_signal,
        NULL as macd_histogram,
        NULL as bollinger_upper,
        NULL as bollinger_middle,
        NULL as bollinger_lower,
        NULL as sma_20,
        NULL as sma_50,
        NULL as sma_200,
        NULL as ema_12,
        NULL as ema_26,
        NULL as ema_50,
        NULL as adx,
        NULL as atr,
        NULL as stoch_k,
        NULL as stoch_d,
        NULL as cci,
        NULL as williams_r,
        NULL as obv,
        NULL as momentum,
        NULL as roc,
        'historical' as source_table
    FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_historical_daily`
),
current_data AS (
    SELECT
        symbol,
        name,
        datetime,
        open,
        high,
        low,
        close,
        volume,
        exchange,
        currency,
        percent_change,
        'twelvedata' as data_source,
        CURRENT_TIMESTAMP() as created_at,
        rsi,
        macd,
        macd_signal,
        macd_histogram,
        bollinger_upper,
        bollinger_middle,
        bollinger_lower,
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50,
        adx,
        atr,
        stoch_k,
        stoch_d,
        cci,
        williams_r,
        obv,
        momentum,
        roc,
        'current' as source_table
    FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_daily`
)
SELECT * FROM historical_data
UNION ALL
SELECT * FROM current_data
ORDER BY symbol, datetime DESC
"""

try:
    print("Executing query...")
    query_job = client.query(create_table_query)
    query_job.result()  # Wait for completion
    print("✓ Unified table created successfully!")
except Exception as e:
    print(f"✗ Error creating unified table: {e}")
    sys.exit(1)

# Step 2: Get statistics
print("\nStep 2: Getting statistics...")
stats_query = f"""
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(DATE(datetime)) as earliest_date,
    MAX(DATE(datetime)) as latest_date,
    COUNTIF(source_table = 'historical') as historical_records,
    COUNTIF(source_table = 'current') as current_records,
    COUNTIF(rsi IS NOT NULL) as records_with_indicators
FROM `{PROJECT_ID}.{DATASET_ID}.stocks_unified_daily`
"""

try:
    query_job = client.query(stats_query)
    results = list(query_job.result())

    for row in results:
        print(f"\n{'='*60}")
        print("UNIFIED TABLE STATISTICS")
        print(f"{'='*60}")
        print(f"Total Records:           {row.total_records:,}")
        print(f"Unique Symbols:          {row.unique_symbols}")
        print(f"Earliest Date:           {row.earliest_date}")
        print(f"Latest Date:             {row.latest_date}")
        print(f"Historical Records:      {row.historical_records:,}")
        print(f"Current Records:         {row.current_records:,}")
        print(f"Records with Indicators: {row.records_with_indicators:,}")
        print(f"{'='*60}")

except Exception as e:
    print(f"✗ Error getting statistics: {e}")

# Step 3: Show sample of stocks with most historical data
print("\nStep 3: Top stocks by data range...")
sample_query = f"""
SELECT
    symbol,
    MIN(DATE(datetime)) as earliest_date,
    MAX(DATE(datetime)) as latest_date,
    DATE_DIFF(MAX(DATE(datetime)), MIN(DATE(datetime)), DAY) as days_of_data,
    ROUND(DATE_DIFF(MAX(DATE(datetime)), MIN(DATE(datetime)), DAY) / 365.25, 1) as years_of_data,
    COUNT(*) as total_records,
    COUNTIF(rsi IS NOT NULL) as records_with_indicators
FROM `{PROJECT_ID}.{DATASET_ID}.stocks_unified_daily`
GROUP BY symbol
ORDER BY years_of_data DESC
LIMIT 10
"""

try:
    query_job = client.query(sample_query)
    results = list(query_job.result())

    print(f"\n{'Symbol':<10} {'Earliest':<12} {'Latest':<12} {'Years':<8} {'Records':<10} {'w/ Indicators'}")
    print("-" * 70)
    for row in results:
        print(f"{row.symbol:<10} {str(row.earliest_date):<12} {str(row.latest_date):<12} {row.years_of_data:<8.1f} {row.total_records:<10,} {row.records_with_indicators:,}")

except Exception as e:
    print(f"✗ Error getting sample data: {e}")

print("\n" + "="*80)
print("✓ MERGE COMPLETE!")
print("="*80)
print("\nNext Steps:")
print("1. Update API to use 'stocks_unified_daily' instead of 'v2_stocks_daily'")
print("2. Optionally delete old tables to save storage:")
print(f"   bq rm -f {PROJECT_ID}:{DATASET_ID}.v2_stocks_daily")
print(f"   bq rm -f {PROJECT_ID}:{DATASET_ID}.v2_stocks_historical_daily")
print()
