"""
UP Cycle Prediction Improvement Strategy
Addresses the 10.6% UP accuracy by creating specialized models and features
"""
from google.cloud import bigquery
from datetime import datetime
import json

client = bigquery.Client(project='aialgotradehits')

print("=" * 70)
print("UP CYCLE PREDICTION IMPROVEMENT STRATEGY")
print("=" * 70)
print(f"Started: {datetime.now()}")
print()

# Configuration
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'AVGO', 'INTC',
           'LMT', 'RTX', 'HON', 'CAT', 'JPM', 'V']
symbol_str = "','".join(SYMBOLS)

# ============================================================================
# PHASE 1: Analyze UP Prediction Failures
# ============================================================================
print("PHASE 1: Analyzing UP Prediction Failure Patterns")
print("-" * 70)

# Check class distribution
class_query = f"""
SELECT
    CASE WHEN direction_target = 1 THEN 'UP' ELSE 'DOWN' END as direction,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM `aialgotradehits.ml_models.backtest_features`
WHERE symbol IN ('{symbol_str}')
  AND direction_target IS NOT NULL
GROUP BY direction_target
"""
result = client.query(class_query).result()
print("\nClass Distribution in Training Data:")
for row in result:
    print(f"  {row.direction}: {row.count:,} ({row.percentage}%)")

# Analyze features when UP moves occur
up_features_query = f"""
SELECT
    'UP Days' as category,
    ROUND(AVG(rsi), 2) as avg_rsi,
    ROUND(AVG(macd), 4) as avg_macd,
    ROUND(AVG(macd_histogram), 4) as avg_macd_hist,
    ROUND(AVG(adx), 2) as avg_adx,
    ROUND(AVG(momentum), 4) as avg_momentum,
    ROUND(AVG(mfi), 2) as avg_mfi,
    ROUND(AVG(cci), 2) as avg_cci
FROM `aialgotradehits.ml_models.backtest_features`
WHERE direction_target = 1
  AND symbol IN ('{symbol_str}')

UNION ALL

SELECT
    'DOWN Days' as category,
    ROUND(AVG(rsi), 2) as avg_rsi,
    ROUND(AVG(macd), 4) as avg_macd,
    ROUND(AVG(macd_histogram), 4) as avg_macd_hist,
    ROUND(AVG(adx), 2) as avg_adx,
    ROUND(AVG(momentum), 4) as avg_momentum,
    ROUND(AVG(mfi), 2) as avg_mfi,
    ROUND(AVG(cci), 2) as avg_cci
FROM `aialgotradehits.ml_models.backtest_features`
WHERE direction_target = 0
  AND symbol IN ('{symbol_str}')
"""
result = client.query(up_features_query).result()
print("\nFeature Comparison (UP vs DOWN days):")
print(f"{'Category':<12} {'RSI':>8} {'MACD':>10} {'MACD_H':>10} {'ADX':>8} {'Mom':>10} {'MFI':>8} {'CCI':>8}")
print("-" * 80)
for row in result:
    print(f"{row.category:<12} {row.avg_rsi:>8} {row.avg_macd:>10} {row.avg_macd_hist:>10} {row.avg_adx:>8} {row.avg_momentum:>10} {row.avg_mfi:>8} {row.avg_cci:>8}")

# ============================================================================
# PHASE 2: Create Rise-Cycle Specific Features
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 2: Creating Rise-Cycle Specific Features")
print("-" * 70)

rise_features_query = f"""
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.rise_cycle_features` AS
WITH base_data AS (
    SELECT
        symbol, datetime, close, open, high, low, volume,
        rsi, macd, macd_histogram, mfi, cci, adx, momentum,
        sma_20, sma_50, sma_200, atr, ema_12, ema_26,
        CASE WHEN LEAD(close) OVER (PARTITION BY symbol ORDER BY datetime) > close THEN 1 ELSE 0 END as direction_target
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
    WHERE symbol IN ('{symbol_str}')
      AND datetime >= '2023-01-01'
      AND rsi IS NOT NULL AND macd IS NOT NULL AND ema_12 IS NOT NULL
),
-- Step 1: Compute all LAG values first to avoid nested analytic functions
with_lags AS (
    SELECT *,
        LAG(close) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close,
        LAG(close, 5) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close_5,
        LAG(rsi) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi,
        LAG(rsi, 3) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi_3,
        LAG(rsi, 5) OVER (PARTITION BY symbol ORDER BY datetime) as prev_rsi_5,
        LAG(macd_histogram) OVER (PARTITION BY symbol ORDER BY datetime) as prev_macd_hist,
        LAG(ema_12) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_12,
        LAG(ema_26) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_26,
        LAG(momentum) OVER (PARTITION BY symbol ORDER BY datetime) as prev_momentum,
        LAG(cci) OVER (PARTITION BY symbol ORDER BY datetime) as prev_cci,
        AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as avg_volume_20,
        MAX(high) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) as max_high_20,
        STDDEV(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as stddev_10,
        STDDEV(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 30 PRECEDING AND 11 PRECEDING) as stddev_30_11
    FROM base_data WHERE direction_target IS NOT NULL
),
-- Step 2: Compute up_day flag using the pre-computed LAG
with_up_flags AS (
    SELECT *, CASE WHEN close > prev_close THEN 1 ELSE 0 END as is_up_day
    FROM with_lags
),
-- Step 3: Compute rolling sum on up_day flag
with_up_counts AS (
    SELECT *, SUM(is_up_day) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) as up_days_5
    FROM with_up_flags
)
SELECT
    symbol, datetime, close, direction_target,
    rsi, macd, macd_histogram, mfi, cci, adx, momentum,

    -- RISE CYCLE INDICATORS --
    CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END as ema_bullish,
    CASE WHEN ema_12 > ema_26 AND prev_ema_12 <= prev_ema_26 THEN 1 ELSE 0 END as ema_cross_up,
    rsi - prev_rsi_3 as rsi_momentum_3d,
    CASE WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END as rsi_sweet_spot,
    CASE WHEN macd_histogram > 0 AND prev_macd_hist <= 0 THEN 1 ELSE 0 END as macd_turning_bullish,
    macd_histogram - prev_macd_hist as macd_hist_change,
    CASE WHEN close > sma_20 THEN 1 ELSE 0 END as above_sma20,
    CASE WHEN close > sma_50 THEN 1 ELSE 0 END as above_sma50,
    CASE WHEN close > sma_200 THEN 1 ELSE 0 END as above_sma200,
    CASE WHEN adx > 25 THEN 1 ELSE 0 END as strong_trend,
    CASE WHEN mfi BETWEEN 30 AND 70 THEN 1 ELSE 0 END as mfi_healthy,
    CASE WHEN momentum > 0 THEN 1 ELSE 0 END as positive_momentum,
    momentum - prev_momentum as momentum_change,
    volume / NULLIF(avg_volume_20, 0) as volume_ratio,
    (close - low) / NULLIF(high - low, 0) as daily_range_position,
    up_days_5,
    close / NULLIF(max_high_20, 0) as price_vs_20d_high,
    stddev_10 / NULLIF(stddev_30_11, 0) as volatility_ratio,
    CASE WHEN close < prev_close_5 AND rsi > prev_rsi_5 THEN 1 ELSE 0 END as bullish_divergence,
    CASE WHEN cci > -100 AND prev_cci <= -100 THEN 1 ELSE 0 END as cci_oversold_recovery,

    -- Rise Cycle Score (0-10)
    (CASE WHEN ema_12 > ema_26 THEN 1 ELSE 0 END) +
    (CASE WHEN rsi BETWEEN 40 AND 65 THEN 1 ELSE 0 END) +
    (CASE WHEN macd_histogram > 0 THEN 1 ELSE 0 END) +
    (CASE WHEN close > sma_50 THEN 1 ELSE 0 END) +
    (CASE WHEN close > sma_200 THEN 1 ELSE 0 END) +
    (CASE WHEN adx > 25 THEN 1 ELSE 0 END) +
    (CASE WHEN mfi BETWEEN 30 AND 70 THEN 1 ELSE 0 END) +
    (CASE WHEN momentum > 0 THEN 1 ELSE 0 END) +
    (CASE WHEN macd_histogram > prev_macd_hist THEN 1 ELSE 0 END) +
    (CASE WHEN rsi > prev_rsi THEN 1 ELSE 0 END) as rise_cycle_score
FROM with_up_counts
"""

print("Creating rise cycle features table...")
client.query(rise_features_query).result()

# Count records
count_result = list(client.query("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN direction_target = 1 THEN 1 ELSE 0 END) as up_count,
           ROUND(AVG(rise_cycle_score), 2) as avg_score
    FROM `aialgotradehits.ml_models.rise_cycle_features`
""").result())[0]
print(f"Features table created: {count_result.total:,} records")
print(f"UP days: {count_result.up_count:,} ({count_result.up_count/count_result.total*100:.1f}%)")
print(f"Average rise cycle score: {count_result.avg_score}")

# Analyze rise cycle score effectiveness
score_analysis = """
SELECT
    rise_cycle_score,
    COUNT(*) as total,
    SUM(direction_target) as up_count,
    ROUND(AVG(direction_target) * 100, 2) as up_percentage
FROM `aialgotradehits.ml_models.rise_cycle_features`
GROUP BY rise_cycle_score
ORDER BY rise_cycle_score
"""
print("\nRise Cycle Score Effectiveness:")
print(f"{'Score':<8} {'Total':>10} {'UP Count':>10} {'UP %':>10}")
print("-" * 40)
for row in client.query(score_analysis).result():
    print(f"{row.rise_cycle_score:<8} {row.total:>10,} {row.up_count:>10,} {row.up_percentage:>9.1f}%")

# ============================================================================
# PHASE 3: Create Dedicated UP-Only Model with Class Balancing
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 3: Creating Dedicated UP-Only Model with Class Balancing")
print("-" * 70)

# Create balanced training set (undersample DOWN class)
# First get the UP count to use as LIMIT
up_count_result = list(client.query("""
    SELECT COUNT(*) as up_count FROM `aialgotradehits.ml_models.rise_cycle_features` WHERE direction_target = 1
""").result())[0]
up_count = up_count_result.up_count

balanced_data_query = f"""
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.rise_cycle_balanced` AS
WITH up_samples AS (
    SELECT * FROM `aialgotradehits.ml_models.rise_cycle_features`
    WHERE direction_target = 1
),
down_samples AS (
    SELECT * FROM `aialgotradehits.ml_models.rise_cycle_features`
    WHERE direction_target = 0
    ORDER BY RAND()
    LIMIT {up_count}
)
SELECT * FROM up_samples
UNION ALL
SELECT * FROM down_samples
"""
print(f"Creating balanced training dataset (matching {up_count:,} UP samples)...")
client.query(balanced_data_query).result()

balanced_count = list(client.query("""
    SELECT COUNT(*) as total,
           SUM(direction_target) as up_count,
           ROUND(AVG(direction_target) * 100, 1) as up_pct
    FROM `aialgotradehits.ml_models.rise_cycle_balanced`
""").result())[0]
print(f"Balanced dataset: {balanced_count.total:,} records ({balanced_count.up_pct}% UP)")

# Train UP-focused model
print("\nTraining UP-focused XGBoost model...")
up_model_query = """
CREATE OR REPLACE MODEL `aialgotradehits.ml_models.rise_cycle_predictor_v1`
OPTIONS(
    model_type = 'BOOSTED_TREE_CLASSIFIER',
    input_label_cols = ['direction_target'],
    max_iterations = 100,
    learn_rate = 0.05,
    early_stop = TRUE,
    min_split_loss = 0.01,
    l1_reg = 0.1,
    l2_reg = 0.1,
    data_split_method = 'AUTO_SPLIT',
    enable_global_explain = TRUE
) AS
SELECT
    -- Core indicators
    rsi,
    macd,
    macd_histogram,
    mfi,
    cci,
    adx,
    momentum,

    -- Rise cycle specific features
    ema_bullish,
    ema_cross_up,
    rsi_momentum_3d,
    rsi_sweet_spot,
    macd_turning_bullish,
    macd_hist_change,
    above_sma20,
    above_sma50,
    above_sma200,
    strong_trend,
    mfi_healthy,
    positive_momentum,
    momentum_change,
    volume_ratio,
    daily_range_position,
    up_days_5,
    price_vs_20d_high,
    bullish_divergence,
    cci_oversold_recovery,
    rise_cycle_score,

    -- Target
    direction_target
FROM `aialgotradehits.ml_models.rise_cycle_balanced`
WHERE datetime < '2025-06-01'
"""

try:
    client.query(up_model_query).result()
    print("Model trained successfully!")
except Exception as e:
    print(f"Training error: {e}")

# ============================================================================
# PHASE 4: Evaluate UP Model Performance
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 4: Evaluating UP Model Performance")
print("-" * 70)

# Evaluate on test set
eval_query = """
SELECT *
FROM ML.EVALUATE(MODEL `aialgotradehits.ml_models.rise_cycle_predictor_v1`,
    (SELECT
        rsi, macd, macd_histogram, mfi, cci, adx, momentum,
        ema_bullish, ema_cross_up, rsi_momentum_3d, rsi_sweet_spot,
        macd_turning_bullish, macd_hist_change, above_sma20, above_sma50,
        above_sma200, strong_trend, mfi_healthy, positive_momentum,
        momentum_change, volume_ratio, daily_range_position, up_days_5,
        price_vs_20d_high, bullish_divergence, cci_oversold_recovery,
        rise_cycle_score, direction_target
     FROM `aialgotradehits.ml_models.rise_cycle_features`
     WHERE datetime >= '2025-06-01'))
"""

try:
    eval_result = list(client.query(eval_query).result())[0]
    print(f"\nModel Evaluation (Test Set: 2025-06 onwards):")
    print(f"  Accuracy: {eval_result.accuracy * 100:.1f}%")
    print(f"  Precision: {eval_result.precision * 100:.1f}%")
    print(f"  Recall: {eval_result.recall * 100:.1f}%")
    print(f"  F1 Score: {eval_result.f1_score * 100:.1f}%")
    print(f"  ROC AUC: {eval_result.roc_auc:.3f}")
except Exception as e:
    print(f"Evaluation error: {e}")

# Detailed UP/DOWN accuracy
detailed_eval_query = """
WITH predictions AS (
    SELECT
        direction_target as actual,
        predicted_direction_target as predicted,
        predicted_direction_target_probs[OFFSET(1)].prob as prob_up
    FROM ML.PREDICT(MODEL `aialgotradehits.ml_models.rise_cycle_predictor_v1`,
        (SELECT
            rsi, macd, macd_histogram, mfi, cci, adx, momentum,
            ema_bullish, ema_cross_up, rsi_momentum_3d, rsi_sweet_spot,
            macd_turning_bullish, macd_hist_change, above_sma20, above_sma50,
            above_sma200, strong_trend, mfi_healthy, positive_momentum,
            momentum_change, volume_ratio, daily_range_position, up_days_5,
            price_vs_20d_high, bullish_divergence, cci_oversold_recovery,
            rise_cycle_score, direction_target
         FROM `aialgotradehits.ml_models.rise_cycle_features`
         WHERE datetime >= '2025-06-01'))
)
SELECT
    'Overall' as category,
    COUNT(*) as total,
    SUM(CASE WHEN predicted = actual THEN 1 ELSE 0 END) as correct,
    ROUND(AVG(CASE WHEN predicted = actual THEN 1.0 ELSE 0.0 END) * 100, 2) as accuracy
FROM predictions

UNION ALL

SELECT
    'UP Predictions' as category,
    SUM(CASE WHEN actual = 1 THEN 1 ELSE 0 END) as total,
    SUM(CASE WHEN predicted = 1 AND actual = 1 THEN 1 ELSE 0 END) as correct,
    ROUND(SUM(CASE WHEN predicted = 1 AND actual = 1 THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN actual = 1 THEN 1 ELSE 0 END), 0), 2) as accuracy
FROM predictions

UNION ALL

SELECT
    'DOWN Predictions' as category,
    SUM(CASE WHEN actual = 0 THEN 1 ELSE 0 END) as total,
    SUM(CASE WHEN predicted = 0 AND actual = 0 THEN 1 ELSE 0 END) as correct,
    ROUND(SUM(CASE WHEN predicted = 0 AND actual = 0 THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN actual = 0 THEN 1 ELSE 0 END), 0), 2) as accuracy
FROM predictions

UNION ALL

SELECT
    'High Conf UP (>70%)' as category,
    SUM(CASE WHEN prob_up >= 0.70 THEN 1 ELSE 0 END) as total,
    SUM(CASE WHEN prob_up >= 0.70 AND actual = 1 THEN 1 ELSE 0 END) as correct,
    ROUND(SUM(CASE WHEN prob_up >= 0.70 AND actual = 1 THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN prob_up >= 0.70 THEN 1 ELSE 0 END), 0), 2) as accuracy
FROM predictions

UNION ALL

SELECT
    'High Conf UP (>80%)' as category,
    SUM(CASE WHEN prob_up >= 0.80 THEN 1 ELSE 0 END) as total,
    SUM(CASE WHEN prob_up >= 0.80 AND actual = 1 THEN 1 ELSE 0 END) as correct,
    ROUND(SUM(CASE WHEN prob_up >= 0.80 AND actual = 1 THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN prob_up >= 0.80 THEN 1 ELSE 0 END), 0), 2) as accuracy
FROM predictions
"""

print("\nDetailed Performance by Category:")
print(f"{'Category':<22} {'Total':>10} {'Correct':>10} {'Accuracy':>10}")
print("-" * 55)
for row in client.query(detailed_eval_query).result():
    acc_str = f"{row.accuracy:.1f}%" if row.accuracy else "N/A"
    print(f"{row.category:<22} {row.total:>10,} {row.correct:>10,} {acc_str:>10}")

# Feature importance
print("\nTop 10 Features for UP Prediction:")
importance_query = """
SELECT
    feature,
    ROUND(importance_weight * 100, 2) as importance_pct
FROM ML.FEATURE_IMPORTANCE(MODEL `aialgotradehits.ml_models.rise_cycle_predictor_v1`)
ORDER BY importance_weight DESC
LIMIT 10
"""
for row in client.query(importance_query).result():
    print(f"  {row.feature}: {row.importance_pct}%")

# ============================================================================
# PHASE 5: Create High-Confidence UP Signal View
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 5: Creating High-Confidence UP Signal View")
print("-" * 70)

signal_view_query = """
CREATE OR REPLACE VIEW `aialgotradehits.ml_models.v_high_confidence_up_signals` AS
WITH predictions AS (
    SELECT
        symbol,
        DATE(datetime) as signal_date,
        close as current_price,
        rise_cycle_score,
        predicted_direction_target as predicted,
        predicted_direction_target_probs[OFFSET(1)].prob as prob_up,
        rsi,
        macd_histogram,
        ema_bullish,
        above_sma50,
        above_sma200
    FROM ML.PREDICT(MODEL `aialgotradehits.ml_models.rise_cycle_predictor_v1`,
        (SELECT *
         FROM `aialgotradehits.ml_models.rise_cycle_features`
         WHERE DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)))
)
SELECT
    symbol,
    signal_date,
    current_price,
    rise_cycle_score,
    prob_up,
    CASE
        WHEN prob_up >= 0.80 THEN 'STRONG_BUY'
        WHEN prob_up >= 0.70 THEN 'BUY'
        WHEN prob_up >= 0.60 THEN 'WEAK_BUY'
        ELSE 'NO_SIGNAL'
    END as signal,
    CASE
        WHEN prob_up >= 0.80 THEN 'VERY_HIGH'
        WHEN prob_up >= 0.70 THEN 'HIGH'
        WHEN prob_up >= 0.60 THEN 'MEDIUM'
        ELSE 'LOW'
    END as confidence,
    rsi,
    macd_histogram,
    ema_bullish,
    above_sma50,
    above_sma200
FROM predictions
WHERE prob_up >= 0.60  -- Only show signals with 60%+ confidence
ORDER BY prob_up DESC
"""

try:
    client.query(signal_view_query).result()
    print("High-confidence UP signal view created!")
except Exception as e:
    print(f"View error: {e}")

# Get current high-confidence signals
print("\nCurrent High-Confidence UP Signals:")
signals_query = """
SELECT * FROM `aialgotradehits.ml_models.v_high_confidence_up_signals`
WHERE signal IN ('STRONG_BUY', 'BUY')
ORDER BY prob_up DESC
LIMIT 15
"""
try:
    result = client.query(signals_query).result()
    signals = list(result)
    if signals:
        print(f"{'Symbol':<8} {'Date':<12} {'Price':>10} {'Score':>6} {'Prob':>8} {'Signal':<12}")
        print("-" * 60)
        for s in signals:
            print(f"{s.symbol:<8} {str(s.signal_date):<12} ${s.current_price:>8.2f} {s.rise_cycle_score:>6} {s.prob_up*100:>7.1f}% {s.signal:<12}")
    else:
        print("  No high-confidence UP signals currently")
except Exception as e:
    print(f"  Signals query error: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("UP CYCLE PREDICTION IMPROVEMENT - SUMMARY")
print("=" * 70)

summary = {
    'model_name': 'rise_cycle_predictor_v1',
    'features_used': 27,
    'class_balancing': 'Undersampling (50/50 split)',
    'confidence_thresholds': {
        'STRONG_BUY': '80%+',
        'BUY': '70-80%',
        'WEAK_BUY': '60-70%'
    },
    'key_features': [
        'rise_cycle_score',
        'ema_bullish',
        'macd_hist_change',
        'rsi_momentum_3d',
        'volume_ratio'
    ]
}

print(f"""
Model: {summary['model_name']}
Features: {summary['features_used']} rise-cycle specific features
Balancing: {summary['class_balancing']}

Confidence Thresholds:
  STRONG_BUY: {summary['confidence_thresholds']['STRONG_BUY']}
  BUY: {summary['confidence_thresholds']['BUY']}
  WEAK_BUY: {summary['confidence_thresholds']['WEAK_BUY']}

Key Rise Cycle Indicators:
  1. EMA 12/26 Crossover (bullish alignment)
  2. RSI Momentum (3-day change)
  3. MACD Histogram Change (momentum shift)
  4. Rise Cycle Score (composite 0-10)
  5. Volume Confirmation (above average)
""")

with open('up_prediction_improvement_results.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\nCompleted: {datetime.now()}")
print("=" * 70)
