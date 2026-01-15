"""
Verify and Add the 16 Validated Features for Walk-Forward Validation
"""

from google.cloud import bigquery
from datetime import datetime

def verify_and_add_features():
    """Verify all 16 features exist and create feature table if needed"""

    client = bigquery.Client(project='aialgotradehits')

    print("=" * 60)
    print("VERIFYING 16 VALIDATED FEATURES")
    print("=" * 60)

    # The 16 validated features from the spec
    REQUIRED_FEATURES = [
        'pivot_low_flag',
        'pivot_high_flag',
        'rsi',
        'rsi_slope',
        'rsi_zscore',
        'rsi_overbought',
        'rsi_oversold',
        'macd',
        'macd_signal',
        'macd_histogram',
        'macd_cross',
        'momentum',
        'mfi',
        'cci',
        'awesome_osc',
        'vwap_daily'
    ]

    print("\nRequired 16 Features:")
    for i, f in enumerate(REQUIRED_FEATURES, 1):
        print(f"  {i:2d}. {f}")

    # Check what columns exist in stocks_daily_clean
    print("\n[1] Checking stocks_daily_clean schema...")
    query = """
    SELECT column_name
    FROM `aialgotradehits.crypto_trading_data.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = 'stocks_daily_clean'
    """
    result = client.query(query).result()
    existing_columns = [row.column_name for row in result]

    print(f"    Found {len(existing_columns)} columns")

    # Check which features exist
    print("\n[2] Feature Status:")
    missing = []
    found = []
    for feature in REQUIRED_FEATURES:
        if feature in existing_columns:
            found.append(feature)
            print(f"    [OK] {feature}")
        else:
            missing.append(feature)
            print(f"    [MISSING] {feature}")

    print(f"\n    Found: {len(found)}/16")
    print(f"    Missing: {len(missing)}/16")

    # Create a view that calculates all 16 features
    print("\n[3] Creating walk_forward_features_16 view with all features...")

    view_sql = """
    CREATE OR REPLACE VIEW `aialgotradehits.ml_models.walk_forward_features_16` AS
    WITH base_data AS (
        SELECT
            symbol,
            DATE(datetime) as trade_date,
            datetime,
            open,
            high,
            low,
            close,
            volume,
            -- Existing indicators
            rsi,
            macd,
            macd_signal,
            macd_histogram,
            mfi,
            cci,
            sma_20,
            sma_50,
            ema_12,
            ema_26,
            atr,
            -- Calculate pivot points (simplified: compare to neighbors)
            LAG(low, 2) OVER (PARTITION BY symbol ORDER BY datetime) as low_2back,
            LAG(low, 1) OVER (PARTITION BY symbol ORDER BY datetime) as low_1back,
            LEAD(low, 1) OVER (PARTITION BY symbol ORDER BY datetime) as low_1fwd,
            LEAD(low, 2) OVER (PARTITION BY symbol ORDER BY datetime) as low_2fwd,
            LAG(high, 2) OVER (PARTITION BY symbol ORDER BY datetime) as high_2back,
            LAG(high, 1) OVER (PARTITION BY symbol ORDER BY datetime) as high_1back,
            LEAD(high, 1) OVER (PARTITION BY symbol ORDER BY datetime) as high_1fwd,
            LEAD(high, 2) OVER (PARTITION BY symbol ORDER BY datetime) as high_2fwd,
            -- RSI slope (change over 5 periods)
            LAG(rsi, 5) OVER (PARTITION BY symbol ORDER BY datetime) as rsi_5back,
            -- RSI stats for zscore
            AVG(rsi) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as rsi_avg_20,
            STDDEV(rsi) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as rsi_std_20,
            -- MACD cross detection
            LAG(macd) OVER (PARTITION BY symbol ORDER BY datetime) as macd_prev,
            LAG(macd_signal) OVER (PARTITION BY symbol ORDER BY datetime) as macd_signal_prev,
            -- Momentum (rate of change)
            LAG(close, 10) OVER (PARTITION BY symbol ORDER BY datetime) as close_10back,
            -- Awesome Oscillator components
            AVG((high + low) / 2) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) as ao_fast,
            AVG((high + low) / 2) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 33 PRECEDING AND CURRENT ROW) as ao_slow,
            -- VWAP components
            SUM(close * volume) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime) as cum_vol_price,
            SUM(volume) OVER (PARTITION BY symbol, DATE(datetime) ORDER BY datetime) as cum_volume
        FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
        WHERE datetime >= '2020-01-01'
    )
    SELECT
        symbol,
        trade_date,
        datetime,
        open,
        high,
        low,
        close,
        volume,

        -- Feature 1: pivot_low_flag (local minimum)
        CASE
            WHEN low < low_2back AND low < low_1back AND low < low_1fwd AND low < low_2fwd THEN 1
            ELSE 0
        END as pivot_low_flag,

        -- Feature 2: pivot_high_flag (local maximum)
        CASE
            WHEN high > high_2back AND high > high_1back AND high > high_1fwd AND high > high_2fwd THEN 1
            ELSE 0
        END as pivot_high_flag,

        -- Feature 3: rsi (already exists)
        rsi,

        -- Feature 4: rsi_slope (5-period change)
        CASE
            WHEN rsi_5back IS NOT NULL THEN (rsi - rsi_5back) / 5
            ELSE 0
        END as rsi_slope,

        -- Feature 5: rsi_zscore (standardized RSI)
        CASE
            WHEN rsi_std_20 > 0 THEN (rsi - rsi_avg_20) / rsi_std_20
            ELSE 0
        END as rsi_zscore,

        -- Feature 6: rsi_overbought (RSI > 70)
        CASE WHEN rsi > 70 THEN 1 ELSE 0 END as rsi_overbought,

        -- Feature 7: rsi_oversold (RSI < 30)
        CASE WHEN rsi < 30 THEN 1 ELSE 0 END as rsi_oversold,

        -- Feature 8: macd (already exists)
        macd,

        -- Feature 9: macd_signal (already exists)
        macd_signal,

        -- Feature 10: macd_histogram (already exists)
        macd_histogram,

        -- Feature 11: macd_cross (1 = bullish cross, -1 = bearish cross, 0 = no cross)
        CASE
            WHEN macd > macd_signal AND macd_prev <= macd_signal_prev THEN 1  -- Bullish cross
            WHEN macd < macd_signal AND macd_prev >= macd_signal_prev THEN -1  -- Bearish cross
            ELSE 0
        END as macd_cross,

        -- Feature 12: momentum (10-period rate of change)
        CASE
            WHEN close_10back > 0 THEN ((close - close_10back) / close_10back) * 100
            ELSE 0
        END as momentum,

        -- Feature 13: mfi (already exists)
        mfi,

        -- Feature 14: cci (already exists)
        cci,

        -- Feature 15: awesome_osc (5-period SMA of HL/2 minus 34-period SMA of HL/2)
        COALESCE(ao_fast - ao_slow, 0) as awesome_osc,

        -- Feature 16: vwap_daily (Volume Weighted Average Price)
        CASE
            WHEN cum_volume > 0 THEN cum_vol_price / cum_volume
            ELSE close
        END as vwap_daily,

        -- Additional useful fields for ML
        sma_20,
        sma_50,
        ema_12,
        ema_26,
        atr,

        -- Direction target for ML (next day direction)
        CASE
            WHEN LEAD(close, 1) OVER (PARTITION BY symbol ORDER BY datetime) > close THEN 1
            ELSE 0
        END as direction_target

    FROM base_data
    WHERE rsi IS NOT NULL
    """

    try:
        client.query(view_sql).result()
        print("    View created: ml_models.walk_forward_features_16")
    except Exception as e:
        print(f"    Error creating view: {e}")

    # Test the view
    print("\n[4] Testing feature view...")
    test_query = """
    SELECT
        symbol,
        trade_date,
        pivot_low_flag,
        pivot_high_flag,
        rsi,
        rsi_slope,
        rsi_zscore,
        rsi_overbought,
        rsi_oversold,
        macd,
        macd_signal,
        macd_histogram,
        macd_cross,
        momentum,
        mfi,
        cci,
        awesome_osc,
        vwap_daily,
        direction_target
    FROM `aialgotradehits.ml_models.walk_forward_features_16`
    WHERE symbol = 'AAPL'
    ORDER BY trade_date DESC
    LIMIT 5
    """

    result = client.query(test_query).result()
    rows = list(result)

    if rows:
        print(f"    Sample data for AAPL (latest 5 days):")
        for row in rows:
            print(f"      {row.trade_date}: RSI={row.rsi:.1f}, MACD_cross={row.macd_cross}, momentum={row.momentum:.2f}")
    else:
        print("    No data returned")

    # Count total records
    count_query = """
    SELECT COUNT(*) as total, COUNT(DISTINCT symbol) as symbols
    FROM `aialgotradehits.ml_models.walk_forward_features_16`
    """
    result = client.query(count_query).result()
    row = list(result)[0]
    print(f"\n    Total records: {row.total:,}")
    print(f"    Unique symbols: {row.symbols}")

    # Create a materialized table for faster queries
    print("\n[5] Creating materialized feature table for ML training...")

    materialize_sql = """
    CREATE OR REPLACE TABLE `aialgotradehits.ml_models.walk_forward_features_16_mat` AS
    SELECT * FROM `aialgotradehits.ml_models.walk_forward_features_16`
    """

    try:
        client.query(materialize_sql).result()
        print("    Materialized table created: ml_models.walk_forward_features_16_mat")
    except Exception as e:
        print(f"    Error creating materialized table: {e}")

    print("\n" + "=" * 60)
    print("16 VALIDATED FEATURES VERIFICATION COMPLETE")
    print("=" * 60)

    return True

if __name__ == "__main__":
    verify_and_add_features()
