"""
Nested Multi-Timeframe ML Model Implementation
==============================================
Implements hierarchical Daily > Hourly > 5-Minute signal cascade

Theory: True rise cycle signals occur ONLY when all timeframes align
"""

from google.cloud import bigquery
from datetime import datetime, timedelta
import time

client = bigquery.Client(project='aialgotradehits')

print("=" * 80)
print("NESTED MULTI-TIMEFRAME ML MODEL")
print("Daily > Hourly > 5-Minute Signal Cascade")
print("=" * 80)

# ============================================================================
# STEP 1: CREATE HOURLY FEATURES TABLE WITH RISE CYCLE SCORE
# ============================================================================
print("\n" + "=" * 80)
print("STEP 1: CREATE HOURLY FEATURES TABLE")
print("=" * 80)

hourly_features_sql = """
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.hourly_features_16` AS

WITH base_hourly AS (
    SELECT
        datetime,
        symbol,
        open,
        high,
        low,
        close,
        volume,
        -- Indicators from source
        COALESCE(ema_12, 0) as ema_12,
        COALESCE(ema_26, 0) as ema_26,
        COALESCE(sma_20, 0) as sma_20,
        COALESCE(sma_50, 0) as sma_50,
        COALESCE(sma_200, 0) as sma_200,
        COALESCE(rsi, 50) as rsi,
        COALESCE(macd, 0) as macd,
        COALESCE(macd_signal, 0) as macd_signal,
        COALESCE(macd_histogram, 0) as macd_histogram,
        COALESCE(adx, 0) as adx,
        COALESCE(atr, 0) as atr,
        COALESCE(stoch_k, 50) as stoch_k,
        COALESCE(stoch_d, 50) as stoch_d
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_hourly`
    WHERE datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 30 DAY)
      AND close > 0
      AND volume > 0
),

with_prev AS (
    SELECT
        *,
        LAG(ema_12) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_12,
        LAG(ema_26) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_26,
        LAG(macd_histogram) OVER (PARTITION BY symbol ORDER BY datetime) as prev_macd_histogram,
        LAG(rsi) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi,
        LAG(close) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close,
        AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as avg_volume_20
    FROM base_hourly
),

with_features AS (
    SELECT
        datetime,
        symbol,
        open, high, low, close, volume,
        ema_12, ema_26, sma_20, sma_50, sma_200,
        rsi, macd, macd_signal, macd_histogram, adx, atr, stoch_k, stoch_d,

        -- Rise Cycle Core Features
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as ema_bullish,
        CASE WHEN ema_12 > ema_26 AND COALESCE(prev_ema_12, 0) <= COALESCE(prev_ema_26, 0) THEN 1 ELSE 0 END as ema_cross_up,
        CASE WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END as rsi_sweet_spot,
        CASE WHEN macd_histogram > 0 THEN 1 ELSE 0 END as macd_bullish,
        CASE WHEN macd_histogram > COALESCE(prev_macd_histogram, 0) THEN 1 ELSE 0 END as macd_turning_up,
        CASE WHEN adx > 25 THEN 1 ELSE 0 END as strong_trend,
        CASE WHEN close > sma_50 THEN 1 ELSE 0 END as price_above_sma50,
        CASE WHEN close > sma_200 THEN 1 ELSE 0 END as price_above_sma200,
        CASE WHEN stoch_k > stoch_d THEN 1 ELSE 0 END as stoch_bullish,
        CASE WHEN volume > COALESCE(avg_volume_20, volume) * 1.2 THEN 1 ELSE 0 END as volume_surge,
        CASE WHEN rsi > COALESCE(prev_rsi, rsi) THEN 1 ELSE 0 END as rsi_increasing,
        CASE WHEN close > COALESCE(prev_close, close) THEN 1 ELSE 0 END as price_up,

        SAFE_DIVIDE(volume, NULLIF(avg_volume_20, 0)) as volume_ratio
    FROM with_prev
    WHERE prev_close IS NOT NULL
)

SELECT
    *,
    -- Hourly Rise Cycle Score (0-10)
    (ema_bullish + rsi_sweet_spot + macd_bullish + macd_turning_up + strong_trend +
     price_above_sma50 + price_above_sma200 + stoch_bullish + volume_surge + rsi_increasing) as hourly_score,

    -- Hourly Signal
    CASE
        WHEN (ema_bullish + rsi_sweet_spot + macd_bullish + macd_turning_up + strong_trend +
              price_above_sma50 + price_above_sma200 + stoch_bullish + volume_surge + rsi_increasing) >= 7 THEN 'STRONG_BUY'
        WHEN (ema_bullish + rsi_sweet_spot + macd_bullish + macd_turning_up + strong_trend +
              price_above_sma50 + price_above_sma200 + stoch_bullish + volume_surge + rsi_increasing) >= 5 THEN 'BUY'
        WHEN (ema_bullish + rsi_sweet_spot + macd_bullish + macd_turning_up + strong_trend +
              price_above_sma50 + price_above_sma200 + stoch_bullish + volume_surge + rsi_increasing) >= 3 THEN 'WEAK_BUY'
        ELSE 'HOLD'
    END as hourly_signal,

    -- Target: Next hour direction
    CASE
        WHEN LEAD(close) OVER (PARTITION BY symbol ORDER BY datetime) > close THEN 'UP'
        ELSE 'DOWN'
    END as next_hour_direction
FROM with_features
"""

print("Creating hourly_features_16 table...")
try:
    client.query(hourly_features_sql).result()

    # Get count
    count = list(client.query("SELECT COUNT(*) as cnt FROM `aialgotradehits.ml_models.hourly_features_16`").result())[0].cnt
    print(f"  Created hourly_features_16 with {count:,} records")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================================
# STEP 2: CREATE 5-MINUTE FEATURES TABLE WITH RISE CYCLE SCORE
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: CREATE 5-MINUTE FEATURES TABLE")
print("=" * 80)

fivemin_features_sql = """
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.fivemin_features_16` AS

WITH base_5min AS (
    SELECT
        datetime,
        symbol,
        open,
        high,
        low,
        close,
        volume,
        COALESCE(ema_12, 0) as ema_12,
        COALESCE(ema_26, 0) as ema_26,
        COALESCE(sma_20, 0) as sma_20,
        COALESCE(sma_50, 0) as sma_50,
        COALESCE(rsi, 50) as rsi,
        COALESCE(macd, 0) as macd,
        COALESCE(macd_signal, 0) as macd_signal,
        COALESCE(macd_histogram, 0) as macd_histogram,
        COALESCE(adx, 0) as adx,
        COALESCE(atr, 0) as atr,
        COALESCE(stoch_k, 50) as stoch_k,
        COALESCE(stoch_d, 50) as stoch_d
    FROM `aialgotradehits.crypto_trading_data.v2_stocks_5min`
    WHERE datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 14 DAY)
      AND close > 0
      AND volume > 0
),

with_prev AS (
    SELECT
        *,
        LAG(ema_12) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_12,
        LAG(ema_26) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_26,
        LAG(macd_histogram) OVER (PARTITION BY symbol ORDER BY datetime) as prev_macd_histogram,
        LAG(rsi) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi,
        LAG(close) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close,
        AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as avg_volume_20
    FROM base_5min
),

with_features AS (
    SELECT
        datetime,
        symbol,
        open, high, low, close, volume,
        ema_12, ema_26, sma_20, sma_50,
        rsi, macd, macd_signal, macd_histogram, adx, atr, stoch_k, stoch_d,

        -- Rise Cycle Core Features
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as ema_bullish,
        CASE WHEN ema_12 > ema_26 AND COALESCE(prev_ema_12, 0) <= COALESCE(prev_ema_26, 0) THEN 1 ELSE 0 END as ema_cross_up,
        CASE WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END as rsi_sweet_spot,
        CASE WHEN macd_histogram > 0 THEN 1 ELSE 0 END as macd_bullish,
        CASE WHEN macd_histogram > COALESCE(prev_macd_histogram, 0) THEN 1 ELSE 0 END as macd_turning_up,
        CASE WHEN adx > 25 THEN 1 ELSE 0 END as strong_trend,
        CASE WHEN close > sma_50 THEN 1 ELSE 0 END as price_above_sma50,
        CASE WHEN stoch_k > stoch_d THEN 1 ELSE 0 END as stoch_bullish,
        CASE WHEN volume > COALESCE(avg_volume_20, volume) * 1.2 THEN 1 ELSE 0 END as volume_surge,
        CASE WHEN rsi > COALESCE(prev_rsi, rsi) THEN 1 ELSE 0 END as rsi_increasing,
        CASE WHEN close > COALESCE(prev_close, close) THEN 1 ELSE 0 END as price_up,

        SAFE_DIVIDE(volume, NULLIF(avg_volume_20, 0)) as volume_ratio
    FROM with_prev
    WHERE prev_close IS NOT NULL
)

SELECT
    *,
    -- 5-Min Rise Cycle Score (0-10)
    (ema_bullish + rsi_sweet_spot + macd_bullish + macd_turning_up + strong_trend +
     price_above_sma50 + stoch_bullish + volume_surge + rsi_increasing + price_up) as fivemin_score,

    -- 5-Min Signal
    CASE
        WHEN (ema_bullish + rsi_sweet_spot + macd_bullish + macd_turning_up + strong_trend +
              price_above_sma50 + stoch_bullish + volume_surge + rsi_increasing + price_up) >= 7 THEN 'STRONG_BUY'
        WHEN (ema_bullish + rsi_sweet_spot + macd_bullish + macd_turning_up + strong_trend +
              price_above_sma50 + stoch_bullish + volume_surge + rsi_increasing + price_up) >= 5 THEN 'BUY'
        WHEN (ema_bullish + rsi_sweet_spot + macd_bullish + macd_turning_up + strong_trend +
              price_above_sma50 + stoch_bullish + volume_surge + rsi_increasing + price_up) >= 3 THEN 'WEAK_BUY'
        ELSE 'HOLD'
    END as fivemin_signal,

    -- Target: Next 5-min direction
    CASE
        WHEN LEAD(close) OVER (PARTITION BY symbol ORDER BY datetime) > close THEN 'UP'
        ELSE 'DOWN'
    END as next_5min_direction
FROM with_features
"""

print("Creating fivemin_features_16 table...")
try:
    client.query(fivemin_features_sql).result()

    count = list(client.query("SELECT COUNT(*) as cnt FROM `aialgotradehits.ml_models.fivemin_features_16`").result())[0].cnt
    print(f"  Created fivemin_features_16 with {count:,} records")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================================
# STEP 3: CREATE NESTED ALIGNMENT TABLE
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: CREATE NESTED ALIGNMENT TABLE")
print("=" * 80)

# First, let's verify we have daily features
print("Checking daily features...")
daily_count_query = """
SELECT COUNT(*) as cnt FROM `aialgotradehits.ml_models.rise_cycle_features`
WHERE DATE(signal_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)
"""
try:
    daily_count = list(client.query(daily_count_query).result())[0].cnt
    print(f"  Daily features available: {daily_count:,}")
except:
    print("  Daily features table not found, creating from daily data...")
    # Create from stocks_daily_clean
    daily_features_sql = """
    CREATE OR REPLACE TABLE `aialgotradehits.ml_models.rise_cycle_features` AS
    SELECT
        DATE(datetime) as signal_date,
        symbol,
        close as current_price,
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as ema_bullish,
        CASE WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END as rsi_sweet_spot,
        CASE WHEN macd_histogram > 0 THEN 1 ELSE 0 END as macd_bullish,
        CASE WHEN adx > 25 THEN 1 ELSE 0 END as strong_trend,
        CASE WHEN close > sma_50 THEN 1 ELSE 0 END as price_above_sma50,
        CASE WHEN close > sma_200 THEN 1 ELSE 0 END as price_above_sma200,
        -- Simple rise_cycle_score
        (CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END +
         CASE WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END +
         CASE WHEN macd_histogram > 0 THEN 1 ELSE 0 END +
         CASE WHEN adx > 25 THEN 1 ELSE 0 END +
         CASE WHEN close > sma_50 THEN 1 ELSE 0 END +
         CASE WHEN close > sma_200 THEN 1 ELSE 0 END) as rise_cycle_score
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    """
    client.query(daily_features_sql).result()
    daily_count = list(client.query("SELECT COUNT(*) as cnt FROM `aialgotradehits.ml_models.rise_cycle_features`").result())[0].cnt
    print(f"  Created daily features: {daily_count:,}")

nested_alignment_sql = """
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.nested_alignment_features` AS

WITH daily_signals AS (
    SELECT
        signal_date,
        symbol,
        rise_cycle_score as daily_score,
        ema_bullish as daily_ema_bullish,
        CASE
            WHEN rise_cycle_score >= 5 AND ema_bullish = 1 THEN 'BULLISH'
            WHEN rise_cycle_score <= 2 THEN 'BEARISH'
            ELSE 'NEUTRAL'
        END as daily_trend
    FROM `aialgotradehits.ml_models.rise_cycle_features`
    WHERE signal_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)
),

hourly_signals AS (
    SELECT
        DATE(datetime) as trade_date,
        EXTRACT(HOUR FROM datetime) as trade_hour,
        datetime,
        symbol,
        hourly_score,
        ema_bullish as hourly_ema_bullish,
        macd_bullish as hourly_macd_bullish,
        strong_trend as hourly_strong_trend,
        hourly_signal,
        next_hour_direction
    FROM `aialgotradehits.ml_models.hourly_features_16`
),

fivemin_signals AS (
    SELECT
        DATE(datetime) as trade_date,
        EXTRACT(HOUR FROM datetime) as trade_hour,
        datetime,
        symbol,
        fivemin_score,
        ema_bullish as fivemin_ema_bullish,
        macd_bullish as fivemin_macd_bullish,
        fivemin_signal,
        next_5min_direction
    FROM `aialgotradehits.ml_models.fivemin_features_16`
)

SELECT
    f.datetime,
    f.symbol,
    f.trade_date,
    f.trade_hour,

    -- Daily Features
    COALESCE(d.daily_score, 0) as daily_score,
    COALESCE(d.daily_ema_bullish, 0) as daily_ema_bullish,
    d.daily_trend,

    -- Hourly Features
    COALESCE(h.hourly_score, 0) as hourly_score,
    COALESCE(h.hourly_ema_bullish, 0) as hourly_ema_bullish,
    COALESCE(h.hourly_macd_bullish, 0) as hourly_macd_bullish,
    COALESCE(h.hourly_strong_trend, 0) as hourly_strong_trend,
    h.hourly_signal,

    -- 5-Min Features
    f.fivemin_score,
    f.fivemin_ema_bullish,
    f.fivemin_macd_bullish,
    f.fivemin_signal,

    -- Cross-Timeframe Alignment
    CASE WHEN d.daily_ema_bullish = 1 AND h.hourly_ema_bullish = 1 THEN 1 ELSE 0 END as daily_hourly_ema_aligned,
    CASE WHEN h.hourly_ema_bullish = 1 AND f.fivemin_ema_bullish = 1 THEN 1 ELSE 0 END as hourly_5min_ema_aligned,
    CASE WHEN d.daily_ema_bullish = 1 AND h.hourly_ema_bullish = 1 AND f.fivemin_ema_bullish = 1 THEN 1 ELSE 0 END as all_tf_ema_aligned,

    -- Momentum Cascade
    CASE WHEN h.hourly_macd_bullish = 1 AND f.fivemin_macd_bullish = 1 THEN 1 ELSE 0 END as momentum_cascade,

    -- Nested Score (0-30 + bonuses)
    COALESCE(d.daily_score, 0) + COALESCE(h.hourly_score, 0) + f.fivemin_score as raw_nested_score,

    COALESCE(d.daily_score, 0) + COALESCE(h.hourly_score, 0) + f.fivemin_score +
        (CASE WHEN d.daily_ema_bullish = 1 AND h.hourly_ema_bullish = 1 AND f.fivemin_ema_bullish = 1 THEN 3 ELSE 0 END) +
        (CASE WHEN h.hourly_macd_bullish = 1 AND f.fivemin_macd_bullish = 1 THEN 2 ELSE 0 END) as enhanced_nested_score,

    -- Nested Signal Classification
    CASE
        WHEN d.daily_ema_bullish = 1 AND h.hourly_ema_bullish = 1 AND f.fivemin_ema_bullish = 1
             AND d.daily_score >= 5 AND h.hourly_score >= 5 AND f.fivemin_score >= 5 THEN 'ULTRA_BUY'
        WHEN d.daily_ema_bullish = 1 AND h.hourly_ema_bullish = 1 AND f.fivemin_ema_bullish = 1
             AND d.daily_score >= 4 AND h.hourly_score >= 4 AND f.fivemin_score >= 4 THEN 'STRONG_BUY'
        WHEN d.daily_ema_bullish = 1 AND h.hourly_ema_bullish = 1
             AND d.daily_score >= 4 AND h.hourly_score >= 3 THEN 'BUY'
        WHEN d.daily_ema_bullish = 1 AND d.daily_score >= 4 THEN 'WEAK_BUY'
        ELSE 'HOLD'
    END as nested_signal,

    -- Target (5-min direction since that's the entry timeframe)
    f.next_5min_direction as target_direction

FROM fivemin_signals f
LEFT JOIN hourly_signals h ON f.symbol = h.symbol
    AND f.trade_date = h.trade_date
    AND f.trade_hour = h.trade_hour
LEFT JOIN daily_signals d ON f.symbol = d.symbol
    AND f.trade_date = d.signal_date

WHERE f.next_5min_direction IS NOT NULL
"""

print("Creating nested_alignment_features table...")
try:
    client.query(nested_alignment_sql).result()

    count = list(client.query("SELECT COUNT(*) as cnt FROM `aialgotradehits.ml_models.nested_alignment_features`").result())[0].cnt
    print(f"  Created nested_alignment_features with {count:,} records")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================================
# STEP 4: ANALYZE NESTED SIGNAL EFFECTIVENESS
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: ANALYZE NESTED SIGNAL EFFECTIVENESS")
print("=" * 80)

analysis_sql = """
SELECT
    nested_signal,
    COUNT(*) as total,
    COUNTIF(target_direction = 'UP') as up_count,
    ROUND(100.0 * COUNTIF(target_direction = 'UP') / COUNT(*), 2) as up_pct,
    ROUND(AVG(daily_score), 2) as avg_daily_score,
    ROUND(AVG(hourly_score), 2) as avg_hourly_score,
    ROUND(AVG(fivemin_score), 2) as avg_5min_score,
    ROUND(AVG(enhanced_nested_score), 2) as avg_nested_score
FROM `aialgotradehits.ml_models.nested_alignment_features`
GROUP BY nested_signal
ORDER BY
    CASE nested_signal
        WHEN 'ULTRA_BUY' THEN 1
        WHEN 'STRONG_BUY' THEN 2
        WHEN 'BUY' THEN 3
        WHEN 'WEAK_BUY' THEN 4
        ELSE 5
    END
"""

print("\nNested Signal Effectiveness:")
print("-" * 100)
print(f"{'Signal':<12} {'Total':>10} {'UP Count':>10} {'UP %':>8} {'Daily':>8} {'Hourly':>8} {'5-Min':>8} {'Nested':>8}")
print("-" * 100)

try:
    for row in client.query(analysis_sql).result():
        print(f"{row.nested_signal:<12} {row.total:>10,} {row.up_count:>10,} {row.up_pct:>7.1f}% {row.avg_daily_score:>8.1f} {row.avg_hourly_score:>8.1f} {row.avg_5min_score:>8.1f} {row.avg_nested_score:>8.1f}")
except Exception as e:
    print(f"Error: {e}")

# Analyze by alignment
print("\n\nAlignment Analysis:")
print("-" * 80)

alignment_sql = """
SELECT
    all_tf_ema_aligned,
    momentum_cascade,
    COUNT(*) as total,
    COUNTIF(target_direction = 'UP') as up_count,
    ROUND(100.0 * COUNTIF(target_direction = 'UP') / COUNT(*), 2) as up_pct
FROM `aialgotradehits.ml_models.nested_alignment_features`
GROUP BY all_tf_ema_aligned, momentum_cascade
ORDER BY all_tf_ema_aligned DESC, momentum_cascade DESC
"""

print(f"{'All TF Aligned':>15} {'Momentum Cascade':>18} {'Total':>10} {'UP Count':>10} {'UP %':>8}")
print("-" * 70)

try:
    for row in client.query(alignment_sql).result():
        aligned = "YES" if row.all_tf_ema_aligned == 1 else "NO"
        momentum = "YES" if row.momentum_cascade == 1 else "NO"
        print(f"{aligned:>15} {momentum:>18} {row.total:>10,} {row.up_count:>10,} {row.up_pct:>7.1f}%")
except Exception as e:
    print(f"Error: {e}")

# ============================================================================
# STEP 5: CREATE BALANCED TRAINING DATASET
# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: CREATE BALANCED TRAINING DATASET")
print("=" * 80)

# First, check class distribution
class_dist = list(client.query("""
    SELECT target_direction, COUNT(*) as cnt
    FROM `aialgotradehits.ml_models.nested_alignment_features`
    GROUP BY target_direction
""").result())

for row in class_dist:
    print(f"  {row.target_direction}: {row.cnt:,}")

# Get minority class count
up_count = next((r.cnt for r in class_dist if r.target_direction == 'UP'), 0)
down_count = next((r.cnt for r in class_dist if r.target_direction == 'DOWN'), 0)
minority_count = min(up_count, down_count)

print(f"\n  Balancing to {minority_count:,} samples per class...")

balanced_sql = f"""
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.nested_training_balanced` AS

WITH up_samples AS (
    SELECT * FROM `aialgotradehits.ml_models.nested_alignment_features`
    WHERE target_direction = 'UP'
    ORDER BY RAND()
    LIMIT {minority_count}
),
down_samples AS (
    SELECT * FROM `aialgotradehits.ml_models.nested_alignment_features`
    WHERE target_direction = 'DOWN'
    ORDER BY RAND()
    LIMIT {minority_count}
)

SELECT * FROM up_samples
UNION ALL
SELECT * FROM down_samples
"""

try:
    client.query(balanced_sql).result()
    balanced_count = list(client.query("SELECT COUNT(*) as cnt FROM `aialgotradehits.ml_models.nested_training_balanced`").result())[0].cnt
    print(f"  Created balanced training set: {balanced_count:,} records")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================================
# STEP 6: TRAIN NESTED ML MODEL
# ============================================================================
print("\n" + "=" * 80)
print("STEP 6: TRAIN NESTED ML MODEL (XGBoost)")
print("=" * 80)

model_sql = """
CREATE OR REPLACE MODEL `aialgotradehits.ml_models.nested_predictor_v1`
OPTIONS(
    model_type = 'BOOSTED_TREE_CLASSIFIER',
    input_label_cols = ['target_direction'],
    num_parallel_tree = 5,
    max_iterations = 50,
    learn_rate = 0.1,
    subsample = 0.8,
    min_split_loss = 0.1,
    max_tree_depth = 6,
    data_split_method = 'RANDOM',
    data_split_eval_fraction = 0.2,
    enable_global_explain = TRUE
) AS

SELECT
    -- Timeframe Scores
    daily_score,
    hourly_score,
    fivemin_score,
    enhanced_nested_score,

    -- EMA Alignment
    daily_ema_bullish,
    hourly_ema_bullish,
    fivemin_ema_bullish,
    all_tf_ema_aligned,
    daily_hourly_ema_aligned,
    hourly_5min_ema_aligned,

    -- Momentum
    hourly_macd_bullish,
    fivemin_macd_bullish,
    momentum_cascade,

    -- Trend
    hourly_strong_trend,

    -- Target
    target_direction

FROM `aialgotradehits.ml_models.nested_training_balanced`
"""

print("Training nested XGBoost model...")
print("  (This may take a few minutes)")

try:
    start_time = time.time()
    client.query(model_sql).result()
    elapsed = time.time() - start_time
    print(f"  Model trained successfully in {elapsed:.1f} seconds")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================================
# STEP 7: EVALUATE MODEL
# ============================================================================
print("\n" + "=" * 80)
print("STEP 7: EVALUATE NESTED MODEL")
print("=" * 80)

eval_sql = """
SELECT
    *
FROM ML.EVALUATE(MODEL `aialgotradehits.ml_models.nested_predictor_v1`)
"""

try:
    eval_result = list(client.query(eval_sql).result())[0]
    print(f"\nModel Evaluation Metrics:")
    print(f"  Precision: {eval_result.precision:.4f}")
    print(f"  Recall: {eval_result.recall:.4f}")
    print(f"  Accuracy: {eval_result.accuracy:.4f}")
    print(f"  F1 Score: {eval_result.f1_score:.4f}")
    print(f"  Log Loss: {eval_result.log_loss:.4f}")
    print(f"  ROC AUC: {eval_result.roc_auc:.4f}")
except Exception as e:
    print(f"  Error: {e}")

# Confusion matrix
confusion_sql = """
SELECT
    *
FROM ML.CONFUSION_MATRIX(MODEL `aialgotradehits.ml_models.nested_predictor_v1`)
"""

print("\nConfusion Matrix:")
try:
    for row in client.query(confusion_sql).result():
        print(f"  Actual: {row.expected_label}, Predicted: {dict(row)}")
except Exception as e:
    print(f"  Error: {e}")

# Feature importance
print("\nFeature Importance:")
try:
    importance_sql = """
    SELECT
        *
    FROM ML.GLOBAL_EXPLAIN(MODEL `aialgotradehits.ml_models.nested_predictor_v1`)
    ORDER BY attribution DESC
    LIMIT 10
    """
    for row in client.query(importance_sql).result():
        print(f"  {row.feature:<30} {row.attribution:.4f}")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================================
# STEP 8: CREATE PREDICTION VIEW
# ============================================================================
print("\n" + "=" * 80)
print("STEP 8: CREATE PREDICTION VIEW")
print("=" * 80)

prediction_view_sql = """
CREATE OR REPLACE VIEW `aialgotradehits.ml_models.v_nested_predictions` AS

SELECT
    n.datetime,
    n.symbol,
    n.daily_score,
    n.hourly_score,
    n.fivemin_score,
    n.enhanced_nested_score,
    n.all_tf_ema_aligned,
    n.momentum_cascade,
    n.nested_signal,
    p.predicted_target_direction,
    p.predicted_target_direction_probs[OFFSET(0)].prob as down_prob,
    p.predicted_target_direction_probs[OFFSET(1)].prob as up_prob,
    CASE
        WHEN p.predicted_target_direction_probs[OFFSET(1)].prob >= 0.6 THEN 'HIGH_CONFIDENCE_UP'
        WHEN p.predicted_target_direction_probs[OFFSET(1)].prob >= 0.55 THEN 'MODERATE_UP'
        WHEN p.predicted_target_direction_probs[OFFSET(1)].prob <= 0.4 THEN 'HIGH_CONFIDENCE_DOWN'
        ELSE 'UNCERTAIN'
    END as prediction_confidence
FROM `aialgotradehits.ml_models.nested_alignment_features` n
CROSS JOIN ML.PREDICT(
    MODEL `aialgotradehits.ml_models.nested_predictor_v1`,
    (SELECT * FROM `aialgotradehits.ml_models.nested_alignment_features` WHERE symbol = n.symbol AND datetime = n.datetime LIMIT 1)
) p
WHERE n.datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 3 DAY)
"""

# Simpler prediction view
simple_pred_view = """
CREATE OR REPLACE VIEW `aialgotradehits.ml_models.v_nested_signals_live` AS

WITH latest_signals AS (
    SELECT
        datetime,
        symbol,
        daily_score,
        hourly_score,
        fivemin_score,
        enhanced_nested_score,
        all_tf_ema_aligned,
        momentum_cascade,
        nested_signal
    FROM `aialgotradehits.ml_models.nested_alignment_features`
    WHERE datetime >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 3 DAY)
)
SELECT
    *,
    CASE
        WHEN nested_signal = 'ULTRA_BUY' AND all_tf_ema_aligned = 1 AND momentum_cascade = 1 THEN 'EXECUTE'
        WHEN nested_signal = 'STRONG_BUY' AND all_tf_ema_aligned = 1 THEN 'READY'
        WHEN nested_signal = 'BUY' THEN 'WATCH'
        ELSE 'WAIT'
    END as action_status
FROM latest_signals
ORDER BY enhanced_nested_score DESC
"""

try:
    client.query(simple_pred_view).result()
    print("  Created v_nested_signals_live view")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================================
# STEP 9: FINAL VALIDATION
# ============================================================================
print("\n" + "=" * 80)
print("STEP 9: FINAL VALIDATION - COMPARING APPROACHES")
print("=" * 80)

validation_sql = """
SELECT
    'Daily Only (Baseline)' as approach,
    COUNT(*) as total,
    COUNTIF(target_direction = 'UP') as up_count,
    ROUND(100.0 * COUNTIF(target_direction = 'UP') / COUNT(*), 2) as up_pct
FROM `aialgotradehits.ml_models.nested_alignment_features`
WHERE daily_score >= 5

UNION ALL

SELECT
    'Daily + Hourly Aligned' as approach,
    COUNT(*) as total,
    COUNTIF(target_direction = 'UP') as up_count,
    ROUND(100.0 * COUNTIF(target_direction = 'UP') / COUNT(*), 2) as up_pct
FROM `aialgotradehits.ml_models.nested_alignment_features`
WHERE daily_score >= 5 AND hourly_score >= 4 AND daily_hourly_ema_aligned = 1

UNION ALL

SELECT
    'All 3 Timeframes Aligned' as approach,
    COUNT(*) as total,
    COUNTIF(target_direction = 'UP') as up_count,
    ROUND(100.0 * COUNTIF(target_direction = 'UP') / COUNT(*), 2) as up_pct
FROM `aialgotradehits.ml_models.nested_alignment_features`
WHERE daily_score >= 5 AND hourly_score >= 4 AND fivemin_score >= 4
  AND all_tf_ema_aligned = 1

UNION ALL

SELECT
    'Nested ULTRA_BUY Signal' as approach,
    COUNT(*) as total,
    COUNTIF(target_direction = 'UP') as up_count,
    ROUND(100.0 * COUNTIF(target_direction = 'UP') / COUNT(*), 2) as up_pct
FROM `aialgotradehits.ml_models.nested_alignment_features`
WHERE nested_signal = 'ULTRA_BUY'

UNION ALL

SELECT
    'Nested + Momentum Cascade' as approach,
    COUNT(*) as total,
    COUNTIF(target_direction = 'UP') as up_count,
    ROUND(100.0 * COUNTIF(target_direction = 'UP') / COUNT(*), 2) as up_pct
FROM `aialgotradehits.ml_models.nested_alignment_features`
WHERE nested_signal IN ('ULTRA_BUY', 'STRONG_BUY')
  AND all_tf_ema_aligned = 1
  AND momentum_cascade = 1
"""

print("\nApproach Comparison:")
print("-" * 80)
print(f"{'Approach':<30} {'Total':>12} {'UP Count':>12} {'UP %':>10}")
print("-" * 80)

try:
    for row in client.query(validation_sql).result():
        print(f"{row.approach:<30} {row.total:>12,} {row.up_count:>12,} {row.up_pct:>9.1f}%")
except Exception as e:
    print(f"Error: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("NESTED MULTI-TIMEFRAME ML MODEL - COMPLETE")
print("=" * 80)

print("""
OBJECTS CREATED:
----------------
Tables:
  - aialgotradehits.ml_models.hourly_features_16
  - aialgotradehits.ml_models.fivemin_features_16
  - aialgotradehits.ml_models.nested_alignment_features
  - aialgotradehits.ml_models.nested_training_balanced

Models:
  - aialgotradehits.ml_models.nested_predictor_v1

Views:
  - aialgotradehits.ml_models.v_nested_signals_live

NESTED SIGNAL HIERARCHY:
------------------------
ULTRA_BUY:  All 3 TFs aligned, all scores >= 5
STRONG_BUY: All 3 TFs aligned, all scores >= 4
BUY:        Daily + Hourly aligned, scores >= 4/3
WEAK_BUY:   Daily bullish only, score >= 4
HOLD:       No alignment

EXPECTED IMPROVEMENTS:
---------------------
- Daily Only: ~19% UP rate (baseline)
- Daily + Hourly: ~25-30% UP rate
- All 3 Aligned: ~35-45% UP rate
- Nested + Momentum: ~45-55% UP rate
""")
