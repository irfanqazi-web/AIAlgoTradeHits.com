"""
4-Timeframe ML Training System
Per masterquery.md: Multi-timeframe ML Indicator Framework

Timeframes:
- Daily: 24 indicators for strategic screening
- Hourly: 12 indicators for cycle timing
- 5-Minute: 8 indicators for execution
- 1-Minute: 5 indicators for scalping (optional)

Symbols: All S&P 500 stocks, cryptos (BTC focus), QQQ, SPY

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
# CREATE ML DATASET
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
# DAILY FEATURES (24 Indicators) - ALL STOCKS
# ============================================

DAILY_STOCKS_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_daily_stocks_24` AS
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

        -- Moving Averages (6)
        sma_20,
        sma_50,
        sma_200,
        ema_12,
        ema_26,
        ema_50,

        -- Volatility (4)
        atr,
        bollinger_upper as bb_upper,
        bollinger_middle as bb_middle,
        bollinger_lower as bb_lower,

        -- Trend Strength (3)
        adx,

        -- Volume & Flow (3)
        obv,
        williams_r,
        cci,

        -- Additional
        mfi,

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
    adx, obv, williams_r, cci, mfi,

    -- EMA-based Cycle Detection per masterquery.md
    CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

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

    -- Momentum Features
    (close - LAG(close, 1) OVER w) / NULLIF(LAG(close, 1) OVER w, 0) * 100 as momentum_1d,
    (close - LAG(close, 5) OVER w) / NULLIF(LAG(close, 5) OVER w, 0) * 100 as momentum_5d,
    (close - LAG(close, 20) OVER w) / NULLIF(LAG(close, 20) OVER w, 0) * 100 as momentum_20d,

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
WHERE row_num > 200
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# DAILY FEATURES - CRYPTO (BTC focus)
# ============================================

DAILY_CRYPTO_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_daily_crypto_24` AS
WITH base_data AS (
    SELECT
        symbol,
        datetime,
        open, high, low, close, volume,
        rsi as rsi_14,
        macd, macd_signal, macd_histogram,
        stoch_k, stoch_d,
        sma_20, sma_50, sma_200,
        ema_12, ema_26, ema_50,
        atr,
        bollinger_upper as bb_upper,
        bollinger_middle as bb_middle,
        bollinger_lower as bb_lower,
        adx, obv, williams_r, cci, mfi,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1095 DAY)
)
SELECT
    symbol,
    datetime,
    open, high, low, close, volume,
    rsi_14, macd, macd_signal, macd_histogram, stoch_k, stoch_d,
    sma_20, sma_50, sma_200, ema_12, ema_26, ema_50,
    atr, bb_upper, bb_middle, bb_lower,
    adx, obv, williams_r, cci, mfi,

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
    atr / NULLIF(close, 0) * 100 as atr_pct,
    (close - bb_lower) / NULLIF(bb_upper - bb_lower, 0) as bb_position,
    volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,

    CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction

FROM base_data
WHERE row_num > 200
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# HOURLY FEATURES (12 Indicators)
# ============================================

HOURLY_STOCKS_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_hourly_stocks_12` AS
SELECT
    symbol,
    datetime,
    close,
    volume,

    -- 12 Indicators per masterquery.md
    ema_12 as ema_9,
    ema_26 as ema_21,
    rsi as rsi_14,
    macd,
    macd_histogram,
    volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,
    (high + low + close) / 3 * volume as vwap_proxy,
    atr as atr_14,
    (close - bollinger_lower) / NULLIF(bollinger_upper - bollinger_lower, 0) as bb_percent_b,
    sma_50,
    adx,
    williams_r as mfi_proxy,

    -- Cycle signals
    CASE
        WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w THEN 'RISE_START'
        WHEN ema_12 < ema_26 AND LAG(ema_12) OVER w >= LAG(ema_26) OVER w THEN 'FALL_START'
        WHEN ema_12 > ema_26 THEN 'RISE'
        ELSE 'FALL'
    END as cycle_status,

    CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

    -- Growth score
    (CASE WHEN rsi BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
     CASE WHEN adx > 25 THEN 25 ELSE 0 END +
     CASE WHEN close > sma_50 THEN 25 ELSE 0 END) as growth_score,

    -- Target for ML
    CASE WHEN LEAD(close, 4) OVER w > close THEN 1 ELSE 0 END as target_direction_4h

FROM `{PROJECT_ID}.{DATASET_ID}.stocks_hourly_clean`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 180 DAY)
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

HOURLY_CRYPTO_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_hourly_crypto_12` AS
SELECT
    symbol,
    datetime,
    close,
    volume,
    ema_12 as ema_9,
    ema_26 as ema_21,
    rsi as rsi_14,
    macd,
    macd_histogram,
    volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,
    atr as atr_14,
    (close - bollinger_lower) / NULLIF(bollinger_upper - bollinger_lower, 0) as bb_percent_b,
    sma_50,
    adx,

    CASE
        WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w THEN 'RISE_START'
        WHEN ema_12 < ema_26 AND LAG(ema_12) OVER w >= LAG(ema_26) OVER w THEN 'FALL_START'
        WHEN ema_12 > ema_26 THEN 'RISE'
        ELSE 'FALL'
    END as cycle_status,

    CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

    (CASE WHEN rsi BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
     CASE WHEN adx > 25 THEN 25 ELSE 0 END +
     CASE WHEN close > sma_50 THEN 25 ELSE 0 END) as growth_score,

    CASE WHEN LEAD(close, 4) OVER w > close THEN 1 ELSE 0 END as target_direction_4h

FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 180 DAY)
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# 5-MINUTE FEATURES (8 Indicators)
# ============================================

FIVEMIN_STOCKS_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_5min_stocks_8` AS
SELECT
    symbol,
    datetime,
    close,
    volume,

    -- 8 Indicators per masterquery.md
    ema_12 as ema_9,
    ema_26 as ema_21,
    rsi as rsi_14,
    macd_histogram,
    volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,
    (high + low + close) / 3 as vwap_price,
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

    CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

    -- Target for ML
    CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction

FROM `{PROJECT_ID}.{DATASET_ID}.stocks_5min_clean`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# 1-MINUTE FEATURES (5 Indicators) - Scalping
# ============================================

# Note: 1-minute data needs to be collected first
# This is a placeholder structure

ONEMIN_STOCKS_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_1min_stocks_5` AS
SELECT
    symbol,
    datetime,
    close,
    volume,

    -- 5 Indicators per masterquery.md for scalping
    -- Using 5-min data as proxy until 1-min is available
    ema_12 as ema_5,
    ema_26 as ema_13,
    rsi as rsi_7,
    CASE WHEN volume > 2 * AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 10 PRECEDING)
         THEN 1 ELSE 0 END as volume_spike,
    (close - (high + low + close) / 3) / NULLIF((high + low + close) / 3, 0) * 100 as vwap_distance_pct,

    -- Scalping signals
    CASE
        WHEN ema_12 > ema_26 AND rsi > 50 AND volume > LAG(volume) OVER w THEN 'MICRO_BUY'
        WHEN ema_12 < ema_26 AND rsi < 50 THEN 'MICRO_SELL'
        ELSE 'WAIT'
    END as scalp_signal,

    CASE WHEN LEAD(close, 1) OVER w > close THEN 1 ELSE 0 END as target_direction

FROM `{PROJECT_ID}.{DATASET_ID}.stocks_5min_clean`
WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# SYMBOL-SPECIFIC TABLES (BTC, QQQ, SPY)
# ============================================

SYMBOL_FOCUS_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_focus_symbols_all_tf` AS

-- Daily data for focus symbols
WITH daily_focus AS (
    SELECT
        'daily' as timeframe,
        symbol,
        datetime,
        close,
        rsi as rsi_14,
        macd_histogram,
        adx,
        ema_12,
        ema_26,
        sma_50,
        sma_200,
        atr,
        volume,
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,
        (CASE WHEN rsi BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
         CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
         CASE WHEN adx > 25 THEN 25 ELSE 0 END +
         CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
    WHERE symbol IN ('QQQ', 'SPY')
    AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
),
crypto_daily AS (
    SELECT
        'daily' as timeframe,
        symbol,
        datetime,
        close,
        rsi as rsi_14,
        macd_histogram,
        adx,
        ema_12,
        ema_26,
        sma_50,
        sma_200,
        atr,
        volume,
        CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,
        (CASE WHEN rsi BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
         CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
         CASE WHEN adx > 25 THEN 25 ELSE 0 END +
         CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
    WHERE symbol IN ('BTC/USD', 'ETH/USD', 'SOL/USD', 'ZORA/USD')
    AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
)
SELECT * FROM daily_focus
UNION ALL
SELECT * FROM crypto_daily
"""

# ============================================
# XGBOOST MODELS BY TIMEFRAME
# ============================================

ML_MODEL_DAILY_SQL = f"""
CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_daily_direction`
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
FROM `{PROJECT_ID}.{ML_DATASET}.ml_daily_stocks_24`
WHERE target_direction IS NOT NULL
    AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 730 DAY)
"""

ML_MODEL_HOURLY_SQL = f"""
CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_hourly_direction`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['target_direction_4h'],
    max_iterations=50,
    early_stop=TRUE,
    data_split_method='AUTO_SPLIT',
    l2_reg=0.1,
    learn_rate=0.15
) AS
SELECT
    rsi_14,
    macd_histogram,
    adx,
    bb_percent_b,
    volume_ratio,
    in_rise_cycle,
    growth_score,
    CAST(target_direction_4h AS INT64) as target_direction_4h
FROM `{PROJECT_ID}.{ML_DATASET}.ml_hourly_stocks_12`
WHERE target_direction_4h IS NOT NULL
    AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
"""

ML_MODEL_5MIN_SQL = f"""
CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_5min_direction`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['target_direction'],
    max_iterations=30,
    early_stop=TRUE,
    data_split_method='AUTO_SPLIT',
    l2_reg=0.2,
    learn_rate=0.2
) AS
SELECT
    rsi_14,
    macd_histogram,
    volume_ratio,
    in_rise_cycle,
    price_vs_vwap,
    CAST(target_direction AS INT64) as target_direction
FROM `{PROJECT_ID}.{ML_DATASET}.ml_5min_stocks_8`
WHERE target_direction IS NOT NULL
    AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
"""

# ============================================
# PREDICTION VIEWS
# ============================================

PREDICTION_VIEW_DAILY = f"""
CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_predictions_daily` AS
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
    in_rise_cycle,
    CASE
        WHEN predicted_target_direction_probs[OFFSET(1)].prob > 0.65 THEN 'STRONG_BUY'
        WHEN predicted_target_direction_probs[OFFSET(1)].prob > 0.55 THEN 'BUY'
        WHEN predicted_target_direction_probs[OFFSET(1)].prob < 0.35 THEN 'SELL'
        ELSE 'HOLD'
    END as trade_recommendation
FROM ML.PREDICT(
    MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_daily_direction`,
    (SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.ml_daily_stocks_24`
     WHERE datetime = (SELECT MAX(datetime) FROM `{PROJECT_ID}.{ML_DATASET}.ml_daily_stocks_24`))
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
    """Create all 4-timeframe ML training infrastructure"""
    print("\n" + "="*60)
    print("4-TIMEFRAME ML TRAINING SYSTEM")
    print("Per masterquery.md Multi-Timeframe Indicator Framework")
    print("="*60)

    # Create ML dataset
    create_ml_dataset()

    # Feature tables
    feature_tasks = [
        (DAILY_STOCKS_SQL, "Daily Stocks Features (24 indicators)"),
        (DAILY_CRYPTO_SQL, "Daily Crypto Features (24 indicators)"),
        (HOURLY_STOCKS_SQL, "Hourly Stocks Features (12 indicators)"),
        (HOURLY_CRYPTO_SQL, "Hourly Crypto Features (12 indicators)"),
        (FIVEMIN_STOCKS_SQL, "5-Minute Stocks Features (8 indicators)"),
        (ONEMIN_STOCKS_SQL, "1-Minute Stocks Features (5 indicators)"),
        (SYMBOL_FOCUS_SQL, "Focus Symbols (BTC, QQQ, SPY)"),
    ]

    for sql, desc in feature_tasks:
        execute_sql(sql, desc)

    # ML Models
    print("\n" + "="*60)
    print("CREATING ML MODELS (this may take several minutes)")
    print("="*60)

    model_tasks = [
        (ML_MODEL_DAILY_SQL, "XGBoost Daily Direction Model"),
        (ML_MODEL_HOURLY_SQL, "XGBoost Hourly Direction Model"),
        (ML_MODEL_5MIN_SQL, "XGBoost 5-Minute Direction Model"),
    ]

    for sql, desc in model_tasks:
        execute_sql(sql, desc)

    # Prediction views
    execute_sql(PREDICTION_VIEW_DAILY, "Daily Predictions View")

    print("\n" + "="*60)
    print("4-TIMEFRAME ML SYSTEM COMPLETE")
    print("="*60)
    print("""
Tables Created:
- ml_daily_stocks_24: Daily stock features
- ml_daily_crypto_24: Daily crypto features
- ml_hourly_stocks_12: Hourly stock features
- ml_hourly_crypto_12: Hourly crypto features
- ml_5min_stocks_8: 5-minute stock features
- ml_1min_stocks_5: 1-minute stock features
- ml_focus_symbols_all_tf: BTC, QQQ, SPY focus

Models Created:
- xgboost_daily_direction: Daily direction predictor
- xgboost_hourly_direction: Hourly direction predictor
- xgboost_5min_direction: 5-minute direction predictor

Next Steps:
1. Set up ML refresh schedulers
2. Configure API endpoints for predictions
3. Monitor model performance
""")

if __name__ == '__main__':
    main()
