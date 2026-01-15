"""
Refresh ML Feature Tables from V2 Source Tables
Updates ML tables to use v2_* tables directly with proper type conversion.

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
ML_DATASET = 'ml_models'

def refresh_daily_features_24(client):
    """Refresh daily_features_24 from stocks_daily_clean"""
    print("\n1. Refreshing daily_features_24...")

    query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.daily_features_24` AS
    WITH base_data AS (
        SELECT
            symbol, datetime, open, high, low, close, volume,
            rsi as rsi_14, macd, macd_signal, macd_histogram, stoch_k, stoch_d,
            sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
            atr, bollinger_upper as bb_upper, bollinger_middle as bb_middle,
            bollinger_lower as bb_lower, adx, obv, williams_r, cci, mfi,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1095 DAY)
    )
    SELECT
        symbol, datetime, open, high, low, close, volume,
        rsi_14, macd, macd_signal, macd_histogram, stoch_k, stoch_d,
        sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
        atr, bb_upper, bb_middle, bb_lower, adx, obv, williams_r, cci, mfi,
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,
        CASE WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w THEN 1 ELSE 0 END as rise_cycle_start,
        CASE WHEN ema_12 < ema_26 AND LAG(ema_12) OVER w >= LAG(ema_26) OVER w THEN 1 ELSE 0 END as fall_cycle_start,
        CASE WHEN sma_50 > sma_200 AND LAG(sma_50) OVER w <= LAG(sma_200) OVER w THEN 1 ELSE 0 END as golden_cross,
        CASE
            WHEN close > sma_50 AND sma_50 > sma_200 THEN 'STRONG_UPTREND'
            WHEN close < sma_50 AND sma_50 < sma_200 THEN 'STRONG_DOWNTREND'
            WHEN close > sma_200 THEN 'WEAK_UPTREND'
            ELSE 'CONSOLIDATION'
        END as trend_regime,
        (CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
         CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
         CASE WHEN adx > 25 THEN 25 ELSE 0 END +
         CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score,
        (close - LAG(close, 1) OVER w) / NULLIF(LAG(close, 1) OVER w, 0) * 100 as momentum_1d,
        (close - LAG(close, 5) OVER w) / NULLIF(LAG(close, 5) OVER w, 0) * 100 as momentum_5d,
        atr / NULLIF(close, 0) * 100 as atr_pct,
        (close - bb_lower) / NULLIF(bb_upper - bb_lower, 0) as bb_position,
        volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,
        CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction
    FROM base_data
    WHERE row_num > 200
    WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
    """

    job = client.query(query)
    job.result()
    count = list(client.query(f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{ML_DATASET}.daily_features_24`").result())[0].cnt
    print(f"   Created daily_features_24 with {count:,} records")
    return count


def refresh_hourly_features_12(client):
    """Refresh hourly_features_12 from v2_stocks_hourly"""
    print("\n2. Refreshing hourly_features_12 from v2_stocks_hourly...")

    # v2_stocks_hourly has: ema_12, ema_26 (not ema_9, ema_21), rsi (not rsi_14), no mfi
    query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.hourly_features_12` AS
    WITH base_data AS (
        SELECT
            symbol,
            TIMESTAMP(datetime) as datetime,
            open, high, low, close, volume,
            rsi as rsi_14,
            macd, macd_signal, macd_histogram,
            bollinger_upper as bb_upper,
            bollinger_middle as bb_middle,
            bollinger_lower as bb_lower,
            adx,
            sma_20,
            sma_50,
            ema_12,
            ema_26,
            atr,
            stoch_k,
            cci,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num
        FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_hourly`
        WHERE datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 180 DAY)
    )
    SELECT
        symbol, datetime, open, high, low, close, volume,
        -- 12 Indicators for Hourly (adapted to available columns)
        ema_12,  -- Cycle detection (faster EMA)
        ema_26,  -- Cycle detection (slower EMA)
        rsi_14,  -- Momentum
        macd,    -- Momentum
        macd_histogram, -- Momentum
        SAFE_DIVIDE(volume, AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING)) as volume_ratio,
        atr,     -- Volatility
        SAFE_DIVIDE(close - bb_lower, bb_upper - bb_lower) as bb_percent_b,
        sma_50,  -- Trend context
        adx,     -- Trend strength
        stoch_k, -- Flow substitute
        SAFE_DIVIDE(close * volume, SUM(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING)) as vwap_approx,
        -- Cycle signals (using ema_12/ema_26 crossover)
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,
        CASE WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w THEN 1 ELSE 0 END as rise_cycle_start,
        -- Target
        CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction
    FROM base_data
    WHERE row_num > 50
    WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
    """

    job = client.query(query)
    job.result()
    count = list(client.query(f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{ML_DATASET}.hourly_features_12`").result())[0].cnt
    print(f"   Created hourly_features_12 with {count:,} records")
    return count


def refresh_5min_features_8(client):
    """Refresh 5min_features_8 from v2_stocks_5min"""
    print("\n3. Refreshing fivemin_features_8 from v2_stocks_5min...")

    # v2_stocks_5min has ema_12, ema_26 (not ema_9, ema_21)
    query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.fivemin_features_8` AS
    WITH base_data AS (
        SELECT
            symbol,
            TIMESTAMP(datetime) as datetime,
            open, high, low, close, volume,
            rsi as rsi_14,
            macd_histogram,
            ema_12,
            ema_26,
            atr,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num
        FROM `{PROJECT_ID}.{DATASET_ID}.v2_stocks_5min`
        WHERE datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
    )
    SELECT
        symbol, datetime, open, high, low, close, volume,
        -- 8 Indicators for 5min (adapted to available columns)
        ema_12,          -- Signal (fast)
        ema_26,          -- Signal (slow)
        rsi_14,          -- Momentum
        macd_histogram,  -- Momentum
        SAFE_DIVIDE(volume, AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING)) as volume_ratio,
        SAFE_DIVIDE(close * volume, SUM(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING)) as vwap_approx,
        atr,             -- Risk
        SAFE_DIVIDE(close - AVG(close * volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING) / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0), close) * 100 as price_vs_vwap,
        -- Cycle signal
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,
        -- Target
        CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction
    FROM base_data
    WHERE row_num > 20
    WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
    """

    job = client.query(query)
    job.result()
    count = list(client.query(f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{ML_DATASET}.fivemin_features_8`").result())[0].cnt
    print(f"   Created fivemin_features_8 with {count:,} records")
    return count


def refresh_crypto_hourly_12(client):
    """Refresh crypto hourly features from v2_crypto_hourly"""
    print("\n4. Refreshing crypto_hourly_features_12 from v2_crypto_hourly...")

    # v2_crypto_hourly has no volume, uses ema_12/ema_26
    query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.crypto_hourly_features_12` AS
    WITH base_data AS (
        SELECT
            symbol,
            TIMESTAMP(datetime) as datetime,
            open, high, low, close,
            rsi as rsi_14,
            macd, macd_signal, macd_histogram,
            bollinger_upper as bb_upper,
            bollinger_middle as bb_middle,
            bollinger_lower as bb_lower,
            adx,
            sma_50,
            ema_12,
            ema_26,
            stoch_k,
            atr,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num
        FROM `{PROJECT_ID}.{DATASET_ID}.v2_crypto_hourly`
        WHERE datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 180 DAY)
    )
    SELECT
        symbol, datetime, open, high, low, close,
        ema_12, ema_26, rsi_14, macd, macd_histogram,
        atr,
        SAFE_DIVIDE(close - bb_lower, bb_upper - bb_lower) as bb_percent_b,
        sma_50, adx, stoch_k,
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,
        CASE WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w THEN 1 ELSE 0 END as rise_cycle_start,
        CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction
    FROM base_data
    WHERE row_num > 50
    WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
    """

    job = client.query(query)
    job.result()
    count = list(client.query(f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{ML_DATASET}.crypto_hourly_features_12`").result())[0].cnt
    print(f"   Created crypto_hourly_features_12 with {count:,} records")
    return count


def refresh_crypto_5min_8(client):
    """Refresh crypto 5min features from v2_crypto_5min"""
    print("\n5. Refreshing crypto_5min_features_8 from v2_crypto_5min...")

    # v2_crypto_5min uses ema_12/ema_26
    query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.crypto_5min_features_8` AS
    WITH base_data AS (
        SELECT
            symbol,
            TIMESTAMP(datetime) as datetime,
            open, high, low, close,
            rsi as rsi_14,
            macd_histogram,
            ema_12,
            ema_26,
            atr,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num
        FROM `{PROJECT_ID}.{DATASET_ID}.v2_crypto_5min`
        WHERE datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
    )
    SELECT
        symbol, datetime, open, high, low, close,
        ema_12, ema_26, rsi_14, macd_histogram,
        atr,
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,
        CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction
    FROM base_data
    WHERE row_num > 20
    WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
    """

    job = client.query(query)
    job.result()
    count = list(client.query(f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{ML_DATASET}.crypto_5min_features_8`").result())[0].cnt
    print(f"   Created crypto_5min_features_8 with {count:,} records")
    return count


def show_summary(client):
    """Display summary of all ML feature tables"""
    print("\n" + "=" * 60)
    print("ML FEATURE TABLES SUMMARY")
    print("=" * 60)

    tables = [
        ('daily_features_24', 'Daily stocks (24 indicators)'),
        ('hourly_features_12', 'Hourly stocks (12 indicators)'),
        ('fivemin_features_8', '5-min stocks (8 indicators)'),
        ('crypto_hourly_features_12', 'Hourly crypto (12 indicators)'),
        ('crypto_5min_features_8', '5-min crypto (8 indicators)'),
    ]

    for table_name, desc in tables:
        try:
            query = f"""
            SELECT
                COUNT(*) as records,
                COUNT(DISTINCT symbol) as symbols,
                MAX(datetime) as latest
            FROM `{PROJECT_ID}.{ML_DATASET}.{table_name}`
            """
            result = list(client.query(query).result())[0]
            print(f"\n{desc}:")
            print(f"   Table: {table_name}")
            print(f"   Records: {result.records:,}")
            print(f"   Symbols: {result.symbols}")
            print(f"   Latest: {result.latest}")
        except Exception as e:
            print(f"\n{desc}: ERROR - {e}")


def main():
    print("=" * 60)
    print("ML FEATURE TABLE REFRESH")
    print("Using v2_* tables as source for fresh data")
    print("=" * 60)

    client = bigquery.Client(project=PROJECT_ID)

    # Refresh all feature tables
    refresh_daily_features_24(client)
    refresh_hourly_features_12(client)
    refresh_5min_features_8(client)
    refresh_crypto_hourly_12(client)
    refresh_crypto_5min_8(client)

    # Show summary
    show_summary(client)

    print("\n" + "=" * 60)
    print("REFRESH COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
