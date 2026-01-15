"""
BigQuery ML Training Tables Creation
Per masterquery.md: Multi-timeframe ML Indicator Framework

Creates:
- Daily features table (24 indicators)
- Hourly features table (12 indicators)
- 5-minute features table (8 indicators)
- Direction prediction model with XGBoost

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

client = bigquery.Client(project=PROJECT_ID)

# ============================================
# 1. CREATE ML DATASET IF NOT EXISTS
# ============================================

def create_ml_dataset():
    """Create ml_models dataset"""
    dataset_ref = f"{PROJECT_ID}.{ML_DATASET}"
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"

    try:
        client.create_dataset(dataset, exists_ok=True)
        print(f"Dataset {ML_DATASET} ready")
    except Exception as e:
        print(f"Dataset creation: {e}")

# ============================================
# 2. DAILY FEATURES TABLE (24 Indicators)
# ============================================

DAILY_FEATURES_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.daily_features_24` AS
WITH base_data AS (
    SELECT
        symbol,
        datetime,
        open,
        high,
        low,
        close,
        volume,

        -- Momentum Indicators (6)
        rsi as rsi_14,
        macd,
        macd_signal,
        macd_histogram,
        stoch_k,
        stoch_d,

        -- Moving Averages (8)
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50 as ema_50,

        -- Volatility (4)
        atr,
        bollinger_upper as bb_upper,
        bollinger_middle as bb_middle,
        bollinger_lower as bb_lower,

        -- Trend Strength (3)
        adx,

        -- Volume & Flow (2)
        obv,
        williams_r,

        -- Calculated fields
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num

    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1095 DAY)
)
SELECT
    symbol,
    datetime,
    open, high, low, close, volume,

    -- All 24 Technical Indicators
    rsi_14, macd, macd_signal, macd_histogram, stoch_k, stoch_d,
    sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
    atr, bb_upper, bb_middle, bb_lower,
    adx, obv, williams_r,

    -- EMA-based Cycle Detection per masterquery.md
    CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

    -- Momentum Features
    (close - LAG(close, 1) OVER w) / NULLIF(LAG(close, 1) OVER w, 0) * 100 as momentum_1d,
    (close - LAG(close, 5) OVER w) / NULLIF(LAG(close, 5) OVER w, 0) * 100 as momentum_5d,
    (close - LAG(close, 20) OVER w) / NULLIF(LAG(close, 20) OVER w, 0) * 100 as momentum_20d,

    -- Rise Cycle Start (EMA crossover)
    CASE
        WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w
        THEN 1 ELSE 0
    END as rise_cycle_start,

    -- Fall Cycle Start
    CASE
        WHEN ema_12 < ema_26 AND LAG(ema_12) OVER w >= LAG(ema_26) OVER w
        THEN 1 ELSE 0
    END as fall_cycle_start,

    -- Golden Cross
    CASE
        WHEN sma_50 > sma_200 AND LAG(sma_50) OVER w <= LAG(sma_200) OVER w
        THEN 1 ELSE 0
    END as golden_cross,

    -- Trend Regime
    CASE
        WHEN close > sma_50 AND sma_50 > sma_200 THEN 'STRONG_UPTREND'
        WHEN close < sma_50 AND sma_50 < sma_200 THEN 'STRONG_DOWNTREND'
        WHEN close > sma_200 THEN 'WEAK_UPTREND'
        ELSE 'CONSOLIDATION'
    END as trend_regime,

    -- Growth Score (0-100) per masterquery.md
    (CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
     CASE WHEN adx > 25 THEN 25 ELSE 0 END +
     CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score,

    -- Volatility Features
    atr / NULLIF(close, 0) * 100 as atr_pct,
    (bb_upper - bb_lower) / NULLIF(close, 0) * 100 as bb_width_pct,
    (close - bb_lower) / NULLIF(bb_upper - bb_lower, 0) as bb_position,

    -- Volume Ratio
    volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,

    -- Target Variable (next day direction) for ML training
    CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction,
    (LEAD(close, 1) OVER w - close) / NULLIF(close, 0) * 100 as target_return_pct

FROM base_data
WHERE row_num > 200  -- Ensure enough historical data for indicators
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# 3. HOURLY FEATURES TABLE (12 Indicators)
# ============================================

HOURLY_FEATURES_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.hourly_features_12` AS
SELECT
    symbol,
    datetime,
    close,
    volume,

    -- 12 Indicators per masterquery.md
    -- Cycle Detection (2)
    ema_12 as ema_9,   -- Using ema_12 as proxy for fast EMA
    ema_26 as ema_21,  -- Using ema_26 as proxy for slow EMA

    -- Momentum (3)
    rsi as rsi_14,
    macd,
    macd_histogram,

    -- Volume (2) - volume_ratio calculated, VWAP approximated
    volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,
    (high + low + close) / 3 * volume as vwap_proxy,

    -- Volatility (2)
    atr as atr_14,
    (close - bollinger_lower) / NULLIF(bollinger_upper - bollinger_lower, 0) as bb_percent_b,

    -- Trend Context (2)
    sma_50,
    adx,

    -- Flow (1)
    williams_r as mfi_proxy,

    -- Cycle signals
    CASE
        WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w
        THEN 'RISE_START'
        WHEN ema_12 < ema_26 AND LAG(ema_12) OVER w >= LAG(ema_26) OVER w
        THEN 'FALL_START'
        WHEN ema_12 > ema_26 THEN 'RISE'
        ELSE 'FALL'
    END as cycle_status,

    -- Target for ML
    CASE WHEN LEAD(close, 4) OVER w > close THEN 1 ELSE 0 END as target_direction_4h

FROM `{PROJECT_ID}.{DATASET_ID}.stocks_hourly_clean`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 180 DAY)
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# 4. 5-MINUTE FEATURES TABLE (8 Indicators)
# ============================================

FIVEMIN_FEATURES_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.fivemin_features_8` AS
SELECT
    symbol,
    datetime,
    close,
    volume,

    -- 8 Indicators per masterquery.md
    -- Signal (2)
    ema_12 as ema_9,
    ema_26 as ema_21,

    -- Momentum (2)
    rsi as rsi_14,
    macd_histogram,

    -- Volume (2)
    volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,
    (high + low + close) / 3 as vwap_price,

    -- Risk (2)
    atr as atr_14,
    CASE WHEN close > (high + low + close) / 3 THEN 1 ELSE 0 END as price_vs_vwap,

    -- Trade signals per masterquery.md
    CASE
        WHEN ema_12 > ema_26
             AND macd_histogram > 0
             AND rsi BETWEEN 40 AND 70
             AND volume > LAG(volume) OVER w
        THEN 'STRONG_BUY'
        WHEN ema_12 > ema_26 AND rsi > 50 THEN 'BUY'
        WHEN ema_12 < ema_26 AND rsi < 50 THEN 'SELL'
        ELSE 'HOLD'
    END as trade_signal,

    -- Target for ML
    CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction

FROM `{PROJECT_ID}.{DATASET_ID}.stocks_5min_clean`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# 5. CREATE XGBOOST DIRECTION PREDICTOR
# ============================================

ML_MODEL_SQL = f"""
CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.direction_predictor_xgboost`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['target_direction'],
    max_iterations=100,
    early_stop=TRUE,
    data_split_method='AUTO_SPLIT',
    l2_reg=0.1,
    learn_rate=0.1,
    enable_global_explain=TRUE
) AS
SELECT
    rsi_14,
    macd_histogram,
    adx,
    bb_position,
    volume_ratio,
    in_rise_cycle,
    momentum_5d,
    atr_pct,
    growth_score,
    golden_cross,
    CAST(target_direction AS INT64) as target_direction
FROM `{PROJECT_ID}.{ML_DATASET}.daily_features_24`
WHERE target_direction IS NOT NULL
    AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 730 DAY)
"""

# ============================================
# 6. CREATE PREDICTION VIEW
# ============================================

PREDICTION_VIEW_SQL = f"""
CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_daily_predictions` AS
SELECT
    symbol,
    datetime,
    close,
    predicted_target_direction as predicted_direction,
    predicted_target_direction_probs[OFFSET(1)].prob as up_probability,
    growth_score,
    trend_regime,
    rise_cycle_start,
    golden_cross,
    CASE
        WHEN predicted_target_direction_probs[OFFSET(1)].prob > 0.65 THEN 'STRONG_BUY'
        WHEN predicted_target_direction_probs[OFFSET(1)].prob > 0.55 THEN 'BUY'
        WHEN predicted_target_direction_probs[OFFSET(1)].prob < 0.35 THEN 'SELL'
        ELSE 'HOLD'
    END as trade_recommendation
FROM ML.PREDICT(
    MODEL `{PROJECT_ID}.{ML_DATASET}.direction_predictor_xgboost`,
    (SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.daily_features_24`
     WHERE datetime = (SELECT MAX(datetime) FROM `{PROJECT_ID}.{ML_DATASET}.daily_features_24`))
)
"""

def execute_sql(sql, description):
    """Execute SQL statement"""
    print(f"\n{'='*60}")
    print(f"Executing: {description}")
    print(f"{'='*60}")

    try:
        job = client.query(sql)
        result = job.result()
        print(f"SUCCESS: {description}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Create all ML training infrastructure"""
    print("\n" + "="*60)
    print("BIGQUERY ML TRAINING INFRASTRUCTURE SETUP")
    print("Per masterquery.md Multi-Timeframe Indicator Framework")
    print("="*60)

    # Create ML dataset
    create_ml_dataset()

    # Create feature tables
    tasks = [
        (DAILY_FEATURES_SQL, "Daily Features Table (24 indicators)"),
        (HOURLY_FEATURES_SQL, "Hourly Features Table (12 indicators)"),
        (FIVEMIN_FEATURES_SQL, "5-Minute Features Table (8 indicators)"),
    ]

    for sql, desc in tasks:
        execute_sql(sql, desc)

    # Create ML model (this takes longer)
    print("\nCreating XGBoost Direction Predictor Model...")
    print("This may take 5-10 minutes...")
    execute_sql(ML_MODEL_SQL, "XGBoost Direction Predictor")

    # Create prediction view
    execute_sql(PREDICTION_VIEW_SQL, "Prediction View")

    print("\n" + "="*60)
    print("ML TRAINING INFRASTRUCTURE COMPLETE")
    print("="*60)
    print("""
Next steps:
1. Verify tables: SELECT * FROM `aialgotradehits.ml_models.daily_features_24` LIMIT 10
2. Check model: SELECT * FROM ML.TRAINING_INFO(MODEL `aialgotradehits.ml_models.direction_predictor_xgboost`)
3. Get predictions: SELECT * FROM `aialgotradehits.ml_models.v_daily_predictions` LIMIT 20
""")

if __name__ == '__main__':
    main()
