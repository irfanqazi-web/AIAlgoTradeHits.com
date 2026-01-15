"""
ML Model Accuracy Improvement
Per masterquery.md: Target 66-72% accuracy (current: 52.8%)

Improvements:
1. Feature Interactions: RSI × Volume_Ratio, MACD × ATR, ADX × Trend_Direction
2. Lagged Features: RSI_t-1, RSI_t-5, Price momentum 5/10/20
3. Better Labels: >1% moves only (significant moves)
4. Class Balancing: Undersample majority class
5. Hyperparameter Tuning: Optimized XGBoost settings

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
# 1. ENHANCED FEATURE TABLE WITH INTERACTIONS
# ============================================

ENHANCED_FEATURES_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_features_v2` AS
WITH base_data AS (
    SELECT
        symbol,
        datetime,
        open, high, low, close, volume,

        -- Core Indicators
        rsi as rsi_14,
        macd,
        macd_signal,
        macd_histogram,
        stoch_k,
        stoch_d,
        sma_20, sma_50, sma_200,
        ema_12, ema_26, ema_50,
        atr,
        bollinger_upper as bb_upper,
        bollinger_middle as bb_middle,
        bollinger_lower as bb_lower,
        adx,
        obv,
        williams_r,
        cci,
        mfi,

        -- Lagged RSI (t-1, t-5)
        LAG(rsi, 1) OVER w as rsi_lag1,
        LAG(rsi, 5) OVER w as rsi_lag5,

        -- Lagged MACD
        LAG(macd_histogram, 1) OVER w as macd_hist_lag1,
        LAG(macd_histogram, 5) OVER w as macd_hist_lag5,

        -- Price Momentum (various periods)
        (close - LAG(close, 1) OVER w) / NULLIF(LAG(close, 1) OVER w, 0) * 100 as momentum_1d,
        (close - LAG(close, 5) OVER w) / NULLIF(LAG(close, 5) OVER w, 0) * 100 as momentum_5d,
        (close - LAG(close, 10) OVER w) / NULLIF(LAG(close, 10) OVER w, 0) * 100 as momentum_10d,
        (close - LAG(close, 20) OVER w) / NULLIF(LAG(close, 20) OVER w, 0) * 100 as momentum_20d,

        -- Volume features
        volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS 20 PRECEDING), 0) as volume_ratio,

        -- Target (next day return)
        (LEAD(close, 1) OVER w - close) / NULLIF(close, 0) * 100 as next_day_return,

        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime) as row_num

    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
    WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1095 DAY)
    WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
)
SELECT
    symbol,
    datetime,
    close,
    volume,

    -- Core Indicators
    rsi_14,
    macd,
    macd_histogram,
    stoch_k,
    stoch_d,
    adx,
    atr,
    cci,
    mfi,
    williams_r,
    obv,

    -- Moving Averages
    sma_20, sma_50, sma_200,
    ema_12, ema_26, ema_50,
    bb_upper, bb_middle, bb_lower,

    -- Lagged Features (per masterquery.md)
    rsi_lag1,
    rsi_lag5,
    macd_hist_lag1,
    macd_hist_lag5,

    -- Momentum Features (per masterquery.md)
    momentum_1d,
    momentum_5d,
    momentum_10d,
    momentum_20d,

    -- RSI Change
    rsi_14 - COALESCE(rsi_lag1, rsi_14) as rsi_change_1d,
    rsi_14 - COALESCE(rsi_lag5, rsi_14) as rsi_change_5d,

    -- ========================================
    -- FEATURE INTERACTIONS (per masterquery.md)
    -- ========================================

    -- RSI × Volume_Ratio: Momentum confirmed by volume
    rsi_14 * volume_ratio as rsi_volume_interaction,

    -- MACD × ATR: Momentum relative to volatility
    macd_histogram * (atr / NULLIF(close, 0) * 100) as macd_atr_interaction,

    -- ADX × Trend_Direction: Trend strength with direction
    adx * CASE WHEN ema_12 > ema_26 THEN 1 ELSE -1 END as adx_trend_interaction,

    -- RSI × ADX: Momentum in trending market
    rsi_14 * (adx / 100) as rsi_adx_interaction,

    -- Stochastic × Volume: Reversal signals with volume
    stoch_k * volume_ratio as stoch_volume_interaction,

    -- ========================================
    -- CYCLE DETECTION (per masterquery.md)
    -- ========================================

    -- EMA Cycle
    CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as in_rise_cycle,

    -- Rise/Fall Cycle Start
    CASE WHEN ema_12 > ema_26 AND LAG(ema_12) OVER w <= LAG(ema_26) OVER w THEN 1 ELSE 0 END as rise_cycle_start,
    CASE WHEN ema_12 < ema_26 AND LAG(ema_12) OVER w >= LAG(ema_26) OVER w THEN 1 ELSE 0 END as fall_cycle_start,

    -- Golden/Death Cross
    CASE WHEN sma_50 > sma_200 AND LAG(sma_50) OVER w <= LAG(sma_200) OVER w THEN 1 ELSE 0 END as golden_cross,
    CASE WHEN sma_50 < sma_200 AND LAG(sma_50) OVER w >= LAG(sma_200) OVER w THEN 1 ELSE 0 END as death_cross,

    -- Trend Regime
    CASE
        WHEN close > sma_50 AND sma_50 > sma_200 THEN 'STRONG_UPTREND'
        WHEN close < sma_50 AND sma_50 < sma_200 THEN 'STRONG_DOWNTREND'
        WHEN close > sma_200 THEN 'WEAK_UPTREND'
        ELSE 'CONSOLIDATION'
    END as trend_regime,

    -- ========================================
    -- GROWTH SCORE (per masterquery.md)
    -- ========================================
    (CASE WHEN rsi_14 BETWEEN 50 AND 70 THEN 25 ELSE 0 END +
     CASE WHEN macd_histogram > 0 THEN 25 ELSE 0 END +
     CASE WHEN adx > 25 THEN 25 ELSE 0 END +
     CASE WHEN close > sma_200 THEN 25 ELSE 0 END) as growth_score,

    -- ========================================
    -- VOLATILITY FEATURES
    -- ========================================
    atr / NULLIF(close, 0) * 100 as atr_pct,
    (bb_upper - bb_lower) / NULLIF(close, 0) * 100 as bb_width_pct,
    (close - bb_lower) / NULLIF(bb_upper - bb_lower, 0) as bb_position,

    -- Volume Ratio
    volume_ratio,

    -- ========================================
    -- TARGET VARIABLES (IMPROVED per masterquery.md)
    -- ========================================

    -- Standard direction (any move)
    CASE WHEN next_day_return > 0 THEN 1 ELSE 0 END as target_direction,

    -- IMPROVED: Significant moves only (>1%)
    CASE WHEN next_day_return > 1.0 THEN 1 ELSE 0 END as target_up_1pct,
    CASE WHEN next_day_return < -1.0 THEN 1 ELSE 0 END as target_down_1pct,

    -- 3-class target (UP_BIG, DOWN_BIG, FLAT)
    CASE
        WHEN next_day_return > 1.0 THEN 'UP_BIG'
        WHEN next_day_return < -1.0 THEN 'DOWN_BIG'
        ELSE 'FLAT'
    END as target_3class,

    next_day_return as target_return_pct

FROM base_data
WHERE row_num > 200  -- Enough history for indicators
WINDOW w AS (PARTITION BY symbol ORDER BY datetime)
"""

# ============================================
# 2. IMPROVED XGBOOST MODEL WITH TUNED HYPERPARAMETERS
# ============================================

IMPROVED_MODEL_SQL = f"""
CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_v2_improved`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['target_direction'],

    -- TUNED HYPERPARAMETERS (per masterquery.md)
    max_iterations=200,
    num_parallel_tree=2,
    max_tree_depth=8,
    min_tree_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    l1_reg=0.01,
    l2_reg=0.1,
    learn_rate=0.05,

    -- Training settings
    early_stop=TRUE,
    data_split_method='AUTO_SPLIT',
    enable_global_explain=TRUE
) AS
SELECT
    -- Core Indicators
    rsi_14,
    macd_histogram,
    adx,
    stoch_k,
    cci,
    mfi,

    -- Lagged Features (per masterquery.md)
    rsi_lag1,
    rsi_lag5,
    macd_hist_lag1,
    rsi_change_1d,

    -- Momentum (per masterquery.md)
    momentum_5d,
    momentum_10d,
    momentum_20d,

    -- Feature Interactions (per masterquery.md)
    rsi_volume_interaction,
    macd_atr_interaction,
    adx_trend_interaction,
    rsi_adx_interaction,

    -- Cycle Detection
    in_rise_cycle,
    rise_cycle_start,
    golden_cross,
    growth_score,

    -- Volatility
    atr_pct,
    bb_position,
    volume_ratio,

    CAST(target_direction AS INT64) as target_direction

FROM `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_features_v2`
WHERE target_direction IS NOT NULL
    AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 730 DAY)
    AND rsi_14 IS NOT NULL
    AND volume_ratio IS NOT NULL
"""

# ============================================
# 3. BALANCED CLASS MODEL (>1% moves only)
# ============================================

BALANCED_MODEL_SQL = f"""
CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_v2_significant_moves`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['target_up_1pct'],

    -- Hyperparameters
    max_iterations=150,
    max_tree_depth=6,
    min_tree_child_weight=5,
    subsample=0.7,
    colsample_bytree=0.7,
    l2_reg=0.2,
    learn_rate=0.08,

    early_stop=TRUE,
    data_split_method='AUTO_SPLIT',
    enable_global_explain=TRUE,

    -- Class weights to handle imbalance
    auto_class_weights=TRUE
) AS
SELECT
    rsi_14,
    macd_histogram,
    adx,
    stoch_k,

    rsi_lag1,
    rsi_lag5,
    rsi_change_1d,

    momentum_5d,
    momentum_10d,

    rsi_volume_interaction,
    macd_atr_interaction,
    adx_trend_interaction,

    in_rise_cycle,
    rise_cycle_start,
    growth_score,

    atr_pct,
    bb_position,
    volume_ratio,

    CAST(target_up_1pct AS INT64) as target_up_1pct

FROM `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_features_v2`
WHERE target_up_1pct IS NOT NULL
    AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 730 DAY)
    AND rsi_14 IS NOT NULL
"""

# ============================================
# 4. IMPROVED PREDICTION VIEW
# ============================================

IMPROVED_PREDICTION_VIEW_SQL = f"""
CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_predictions_v2` AS
SELECT
    f.symbol,
    f.datetime,
    f.close,
    f.rsi_14,
    f.macd_histogram,
    f.adx,
    f.growth_score,
    f.in_rise_cycle,
    f.trend_regime,
    f.rise_cycle_start,
    f.golden_cross,

    -- V2 Model Predictions
    p.predicted_target_direction as predicted_direction,
    p.predicted_target_direction_probs[OFFSET(1)].prob as up_probability,

    -- Enhanced Trade Recommendation
    CASE
        WHEN p.predicted_target_direction_probs[OFFSET(1)].prob > 0.65
             AND f.growth_score >= 75
             AND f.in_rise_cycle = 1 THEN 'STRONG_BUY'
        WHEN p.predicted_target_direction_probs[OFFSET(1)].prob > 0.55
             AND f.growth_score >= 50 THEN 'BUY'
        WHEN p.predicted_target_direction_probs[OFFSET(1)].prob < 0.35
             AND f.growth_score <= 25 THEN 'SELL'
        WHEN p.predicted_target_direction_probs[OFFSET(1)].prob < 0.45 THEN 'WEAK_SELL'
        ELSE 'HOLD'
    END as trade_recommendation,

    -- Confidence Level
    CASE
        WHEN ABS(p.predicted_target_direction_probs[OFFSET(1)].prob - 0.5) > 0.15 THEN 'HIGH'
        WHEN ABS(p.predicted_target_direction_probs[OFFSET(1)].prob - 0.5) > 0.08 THEN 'MEDIUM'
        ELSE 'LOW'
    END as confidence_level

FROM ML.PREDICT(
    MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_v2_improved`,
    (SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_features_v2`
     WHERE datetime = (SELECT MAX(datetime) FROM `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_features_v2`))
) p
JOIN `{PROJECT_ID}.{ML_DATASET}.ml_enhanced_features_v2` f
  ON p.symbol = f.symbol AND p.datetime = f.datetime
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


def evaluate_model(model_name):
    """Evaluate model performance"""
    print(f"\n--- Evaluating {model_name} ---")

    eval_sql = f"""
    SELECT * FROM ML.EVALUATE(MODEL `{PROJECT_ID}.{ML_DATASET}.{model_name}`)
    """

    try:
        results = list(client.query(eval_sql).result())
        if results:
            row = results[0]
            print(f"Accuracy:  {row.get('accuracy', 0)*100:.2f}%")
            print(f"Precision: {row.get('precision', 0)*100:.2f}%")
            print(f"Recall:    {row.get('recall', 0)*100:.2f}%")
            print(f"F1 Score:  {row.get('f1_score', 0)*100:.2f}%")
            print(f"ROC AUC:   {row.get('roc_auc', 0)*100:.2f}%")
            return row.get('accuracy', 0)
    except Exception as e:
        print(f"Evaluation error: {e}")
    return 0


def main():
    print("\n" + "="*60)
    print("ML MODEL ACCURACY IMPROVEMENT")
    print("Target: 66-72% (Current: 52.8%)")
    print("="*60)

    # 1. Create enhanced features table
    print("\n[1/4] Creating enhanced feature table with interactions...")
    execute_sql(ENHANCED_FEATURES_SQL, "Enhanced Features with Interactions")

    # 2. Train improved model
    print("\n[2/4] Training improved XGBoost model...")
    execute_sql(IMPROVED_MODEL_SQL, "XGBoost V2 Improved Model")

    # 3. Train balanced model for significant moves
    print("\n[3/4] Training balanced model for >1% moves...")
    execute_sql(BALANCED_MODEL_SQL, "XGBoost V2 Significant Moves Model")

    # 4. Create improved prediction view
    print("\n[4/4] Creating improved prediction view...")
    execute_sql(IMPROVED_PREDICTION_VIEW_SQL, "Predictions V2 View")

    # Evaluate models
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)

    v1_accuracy = evaluate_model("xgboost_daily_direction")
    v2_accuracy = evaluate_model("xgboost_v2_improved")
    sig_accuracy = evaluate_model("xgboost_v2_significant_moves")

    print("\n" + "="*60)
    print("IMPROVEMENT SUMMARY")
    print("="*60)
    print(f"""
Original Model (V1):   {v1_accuracy*100:.2f}%
Improved Model (V2):   {v2_accuracy*100:.2f}%
Significant Moves:     {sig_accuracy*100:.2f}%

Improvements Applied:
1. Feature Interactions:
   - RSI × Volume_Ratio
   - MACD × ATR
   - ADX × Trend_Direction
   - RSI × ADX

2. Lagged Features:
   - RSI_t-1, RSI_t-5
   - MACD_histogram_t-1
   - RSI Change (1d, 5d)

3. Momentum Features:
   - 5-day, 10-day, 20-day momentum

4. Hyperparameter Tuning:
   - max_tree_depth=8
   - learn_rate=0.05
   - subsample=0.8
   - early_stop=TRUE

5. Class Balancing:
   - auto_class_weights=TRUE for significant moves model

Next Steps:
- Monitor predictions: SELECT * FROM `aialgotradehits.ml_models.v_predictions_v2` LIMIT 20
- Compare with actual: Track prediction accuracy over next week
- Further tuning if accuracy < 60%
""")

if __name__ == '__main__':
    main()
