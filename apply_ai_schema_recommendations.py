"""
Apply Gemini AI recommended field ordering to all v2 tables
Field Order:
  TIER 1: symbol, name, asset_type (Identity)
  TIER 2: exchange, country, sector, industry, currency (Classification)
  TIER 3: open, high, low, close, previous_close (Price)
  TIER 4: volume, average_volume, change, percent_change, hi_lo, pct_hi_lo (Volume/Change)
  TIER 5: week_52_high, week_52_low (Range)
  TIER 6: Technical Indicators (grouped logically)
  TIER 7: datetime, timestamp, data_source, created_at (Timestamps)
"""
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
import time

PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'

# AI-Recommended Schema Definitions with proper field ordering
AI_RECOMMENDED_SCHEMAS = {
    'v2_stocks_master': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_stocks_master` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        name,
        'stock' as asset_type,
        -- TIER 2: Classification
        exchange,
        country,
        CAST(NULL AS STRING) as sector,
        CAST(NULL AS STRING) as industry,
        currency,
        mic_code,
        type,
        -- TIER 3: Price
        open,
        high,
        low,
        close,
        previous_close,
        -- TIER 4: Volume & Change
        volume,
        average_volume,
        change,
        percent_change,
        (high - low) as hi_lo,
        SAFE_DIVIDE((high - low), low) * 100 as pct_hi_lo,
        -- TIER 5: Range
        week_52_high,
        week_52_low,
        -- TIER 7: Timestamps (Last)
        CURRENT_TIMESTAMP() as datetime,
        'twelvedata' as data_source,
        CURRENT_TIMESTAMP() as created_at,
        CURRENT_TIMESTAMP() as updated_at
    FROM `{PROJECT}.{DATASET}.stocks_master_list`
    """,

    'v2_stocks_daily': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_stocks_daily` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        CAST(NULL AS STRING) as name,
        'stock' as asset_type,
        -- TIER 2: Classification
        CAST(NULL AS STRING) as exchange,
        CAST(NULL AS STRING) as country,
        currency,
        -- TIER 3: Price
        open,
        high,
        low,
        close,
        previous_close,
        -- TIER 4: Volume & Change
        volume,
        average_volume,
        change,
        percent_change,
        (high - low) as hi_lo,
        SAFE_DIVIDE((high - low), NULLIF(low, 0)) * 100 as pct_hi_lo,
        -- TIER 5: Range
        week_52_high,
        week_52_low,
        -- TIER 6: Technical Indicators (Momentum)
        rsi,
        stoch_k,
        stoch_d,
        momentum,
        roc,
        williams_r,
        -- TIER 6: Technical Indicators (Moving Averages)
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50,
        -- TIER 6: Technical Indicators (MACD)
        macd,
        macd_signal,
        macd_hist as macd_histogram,
        -- TIER 6: Technical Indicators (Bollinger)
        bb_upper as bollinger_upper,
        bb_middle as bollinger_middle,
        bb_lower as bollinger_lower,
        -- TIER 6: Technical Indicators (Volatility & Strength)
        atr,
        adx,
        plus_di,
        minus_di,
        -- TIER 6: Technical Indicators (Other)
        cci,
        obv,
        pvo,
        ppo,
        kama,
        trix,
        ultimate_osc,
        awesome_osc,
        -- TIER 7: Timestamps
        CAST(datetime AS TIMESTAMP) as datetime,
        timestamp,
        data_source,
        CURRENT_TIMESTAMP() as created_at
    FROM `{PROJECT}.{DATASET}.stocks_daily`
    """,

    'v2_stocks_hourly': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_stocks_hourly` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        CAST(NULL AS STRING) as name,
        'stock' as asset_type,
        -- TIER 2: Classification
        CAST(NULL AS STRING) as exchange,
        currency,
        -- TIER 3: Price
        open,
        high,
        low,
        close,
        -- TIER 4: Volume & Change
        volume,
        change,
        percent_change,
        -- TIER 6: Technical Indicators
        rsi,
        sma_20,
        sma_50,
        ema_12,
        ema_26,
        macd,
        macd_signal,
        bb_upper as bollinger_upper,
        bb_middle as bollinger_middle,
        bb_lower as bollinger_lower,
        atr,
        adx,
        -- TIER 7: Timestamps
        CAST(datetime AS TIMESTAMP) as datetime,
        timestamp,
        data_source
    FROM `{PROJECT}.{DATASET}.stocks_hourly`
    """,

    'v2_crypto_daily': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_crypto_daily` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        CAST(NULL AS STRING) as name,
        'crypto' as asset_type,
        -- TIER 2: Classification
        CAST(NULL AS STRING) as exchange,
        CAST(NULL AS STRING) as country,
        'USD' as currency,
        -- TIER 3: Price
        open,
        high,
        low,
        close,
        CAST(NULL AS FLOAT64) as previous_close,
        -- TIER 4: Volume & Change
        volume,
        CAST(NULL AS FLOAT64) as average_volume,
        (close - open) as change,
        SAFE_DIVIDE((close - open), NULLIF(open, 0)) * 100 as percent_change,
        (high - low) as hi_lo,
        SAFE_DIVIDE((high - low), NULLIF(low, 0)) * 100 as pct_hi_lo,
        -- TIER 5: Range
        CAST(NULL AS FLOAT64) as week_52_high,
        CAST(NULL AS FLOAT64) as week_52_low,
        -- TIER 6: Technical Indicators (Momentum)
        rsi,
        stoch_k,
        stoch_d,
        momentum,
        roc,
        williams_r,
        -- TIER 6: Technical Indicators (Moving Averages)
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50,
        -- TIER 6: Technical Indicators (MACD)
        macd,
        macd_signal,
        macd_hist as macd_histogram,
        -- TIER 6: Technical Indicators (Bollinger)
        bb_upper as bollinger_upper,
        bb_middle as bollinger_middle,
        bb_lower as bollinger_lower,
        -- TIER 6: Technical Indicators (Volatility & Strength)
        atr,
        adx,
        plus_di,
        minus_di,
        -- TIER 6: Technical Indicators (Other)
        cci,
        obv,
        pvo,
        ppo,
        kama,
        trix,
        ultimate_osc,
        awesome_osc,
        -- TIER 7: Timestamps
        datetime,
        timestamp,
        data_source,
        CURRENT_TIMESTAMP() as created_at
    FROM `{PROJECT}.{DATASET}.crypto_daily`
    """,

    'v2_crypto_hourly': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_crypto_hourly` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        CAST(NULL AS STRING) as name,
        'crypto' as asset_type,
        -- TIER 2: Classification
        CAST(NULL AS STRING) as exchange,
        'USD' as currency,
        -- TIER 3: Price
        open,
        high,
        low,
        close,
        -- TIER 4: Volume & Change
        volume,
        (close - open) as change,
        SAFE_DIVIDE((close - open), NULLIF(open, 0)) * 100 as percent_change,
        -- TIER 6: Technical Indicators
        rsi,
        sma_20,
        sma_50,
        ema_12,
        ema_26,
        macd,
        macd_signal,
        bb_upper as bollinger_upper,
        bb_middle as bollinger_middle,
        bb_lower as bollinger_lower,
        atr,
        adx,
        -- TIER 7: Timestamps
        CAST(datetime AS TIMESTAMP) as datetime,
        timestamp,
        data_source
    FROM `{PROJECT}.{DATASET}.crypto_hourly`
    """,

    'v2_forex_daily': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_forex_daily` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        CAST(NULL AS STRING) as name,
        'forex' as asset_type,
        -- TIER 2: Classification
        CAST(NULL AS STRING) as exchange,
        CAST(NULL AS STRING) as country,
        currency,
        -- TIER 3: Price
        open,
        high,
        low,
        close,
        previous_close,
        -- TIER 4: Volume & Change
        CAST(NULL AS FLOAT64) as volume,
        CAST(NULL AS FLOAT64) as average_volume,
        change,
        percent_change,
        (high - low) as hi_lo,
        SAFE_DIVIDE((high - low), NULLIF(low, 0)) * 100 as pct_hi_lo,
        -- TIER 5: Range
        week_52_high,
        week_52_low,
        -- TIER 6: Technical Indicators
        rsi, stoch_k, stoch_d, momentum, roc, williams_r,
        sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
        macd, macd_signal, macd_hist as macd_histogram,
        bb_upper as bollinger_upper, bb_middle as bollinger_middle, bb_lower as bollinger_lower,
        atr, adx, plus_di, minus_di,
        cci, obv, pvo, ppo, kama, trix, ultimate_osc, awesome_osc,
        -- TIER 7: Timestamps
        CAST(datetime AS TIMESTAMP) as datetime,
        timestamp,
        data_source,
        CURRENT_TIMESTAMP() as created_at
    FROM `{PROJECT}.{DATASET}.forex_daily`
    """,

    'v2_etfs_daily': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_etfs_daily` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        CAST(NULL AS STRING) as name,
        'etf' as asset_type,
        -- TIER 2: Classification
        CAST(NULL AS STRING) as exchange,
        CAST(NULL AS STRING) as country,
        currency,
        -- TIER 3: Price
        open, high, low, close, previous_close,
        -- TIER 4: Volume & Change
        volume, average_volume, change, percent_change,
        (high - low) as hi_lo, SAFE_DIVIDE((high - low), NULLIF(low, 0)) * 100 as pct_hi_lo,
        -- TIER 5: Range
        week_52_high, week_52_low,
        -- TIER 6: Technical Indicators
        rsi, stoch_k, stoch_d, momentum, roc, williams_r,
        sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
        macd, macd_signal, macd_hist as macd_histogram,
        bb_upper as bollinger_upper, bb_middle as bollinger_middle, bb_lower as bollinger_lower,
        atr, adx, plus_di, minus_di,
        cci, obv, pvo, ppo, kama, trix, ultimate_osc, awesome_osc,
        -- TIER 7: Timestamps
        CAST(datetime AS TIMESTAMP) as datetime, timestamp, data_source,
        CURRENT_TIMESTAMP() as created_at
    FROM `{PROJECT}.{DATASET}.etfs_daily`
    """,

    'v2_indices_daily': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_indices_daily` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        CAST(NULL AS STRING) as name,
        'index' as asset_type,
        -- TIER 2: Classification
        CAST(NULL AS STRING) as exchange,
        CAST(NULL AS STRING) as country,
        currency,
        -- TIER 3: Price
        open, high, low, close, previous_close,
        -- TIER 4: Volume & Change
        volume, average_volume, change, percent_change,
        (high - low) as hi_lo, SAFE_DIVIDE((high - low), NULLIF(low, 0)) * 100 as pct_hi_lo,
        -- TIER 5: Range
        week_52_high, week_52_low,
        -- TIER 6: Technical Indicators
        rsi, stoch_k, stoch_d, momentum, roc, williams_r,
        sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
        macd, macd_signal, macd_hist as macd_histogram,
        bb_upper as bollinger_upper, bb_middle as bollinger_middle, bb_lower as bollinger_lower,
        atr, adx, plus_di, minus_di,
        cci, obv, pvo, ppo, kama, trix, ultimate_osc, awesome_osc,
        -- TIER 7: Timestamps
        CAST(datetime AS TIMESTAMP) as datetime, timestamp, data_source,
        CURRENT_TIMESTAMP() as created_at
    FROM `{PROJECT}.{DATASET}.indices_daily`
    """,

    'v2_commodities_daily': """
    CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.v2_commodities_daily` AS
    SELECT
        -- TIER 1: Identity
        symbol,
        CAST(NULL AS STRING) as name,
        'commodity' as asset_type,
        -- TIER 2: Classification
        CAST(NULL AS STRING) as exchange,
        CAST(NULL AS STRING) as country,
        currency,
        -- TIER 3: Price
        open, high, low, close, previous_close,
        -- TIER 4: Volume & Change
        volume, average_volume, change, percent_change,
        (high - low) as hi_lo, SAFE_DIVIDE((high - low), NULLIF(low, 0)) * 100 as pct_hi_lo,
        -- TIER 5: Range
        week_52_high, week_52_low,
        -- TIER 6: Technical Indicators
        rsi, stoch_k, stoch_d, momentum, roc, williams_r,
        sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
        macd, macd_signal, macd_hist as macd_histogram,
        bb_upper as bollinger_upper, bb_middle as bollinger_middle, bb_lower as bollinger_lower,
        atr, adx, plus_di, minus_di,
        cci, obv, pvo, ppo, kama, trix, ultimate_osc, awesome_osc,
        -- TIER 7: Timestamps
        CAST(datetime AS TIMESTAMP) as datetime, timestamp, data_source,
        CURRENT_TIMESTAMP() as created_at
    FROM `{PROJECT}.{DATASET}.commodities_daily`
    """
}


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def apply_schema(client, table_name, query):
    """Apply the AI-recommended schema to a table"""
    formatted_query = query.format(PROJECT=PROJECT_ID, DATASET=DATASET_ID)

    try:
        job = client.query(formatted_query)
        job.result()
        print(f"  SUCCESS: {table_name} recreated with AI-recommended field order")
        return True
    except Exception as e:
        print(f"  ERROR: {table_name} - {str(e)[:100]}")
        return False


def main():
    print("=" * 80)
    print("APPLYING GEMINI AI RECOMMENDED FIELD ORDER TO V2 TABLES")
    print("=" * 80)
    print("""
Field Order (7 Tiers):
  1. IDENTITY: symbol, name, asset_type
  2. CLASSIFICATION: exchange, country, sector, industry, currency
  3. PRICE: open, high, low, close, previous_close
  4. VOLUME/CHANGE: volume, average_volume, change, percent_change, hi_lo, pct_hi_lo
  5. RANGE: week_52_high, week_52_low
  6. INDICATORS: rsi, macd, sma_*, ema_*, bollinger_*, atr, adx, etc.
  7. TIMESTAMPS: datetime, timestamp, data_source, created_at
    """)

    client = get_client()
    success = []
    failed = []

    for table_name, query in AI_RECOMMENDED_SCHEMAS.items():
        print(f"\n[{table_name}]")
        if apply_schema(client, table_name, query):
            success.append(table_name)
        else:
            failed.append(table_name)
        time.sleep(1)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"\nTables Updated: {len(success)}")
    for t in success:
        count_query = f"SELECT COUNT(*) as c FROM `{PROJECT_ID}.{DATASET_ID}.{t}`"
        try:
            count = list(client.query(count_query).result())[0].c
            print(f"  {t}: {count:,} rows")
        except:
            print(f"  {t}: (count unavailable)")

    if failed:
        print(f"\nFailed: {len(failed)}")
        for t in failed:
            print(f"  - {t}")

    print("\n" + "=" * 80)
    print("VERIFICATION - Check field order in first table:")
    print("=" * 80)

    if success:
        first_table = success[0]
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{first_table}"
        table = client.get_table(table_ref)
        print(f"\n{first_table} fields in order:")
        for i, field in enumerate(table.schema, 1):
            print(f"  {i:2}. {field.name:<25} ({field.field_type})")


if __name__ == "__main__":
    main()
