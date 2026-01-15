"""
Utilities Sector ML Model Improvement
Add sector-specific features to improve 66% accuracy
"""
import requests
import json
from datetime import datetime

ML_SERVICE_URL = "https://ml-training-service-1075463475276.us-central1.run.app"

# Utilities sector stocks
UTILITIES_STOCKS = ['NEE', 'DUK', 'EXC', 'SO', 'CEG', 'D', 'XEL', 'ED', 'ENPH', 'FSLR']

print("=" * 60)
print("UTILITIES SECTOR MODEL IMPROVEMENT")
print("=" * 60)
print(f"Started: {datetime.now()}")
print()

# Step 1: Check current data availability
print("Step 1: Checking data availability for utilities stocks...")
from google.cloud import bigquery
client = bigquery.Client(project='aialgotradehits')

# Check record counts
check_query = f"""
SELECT
    symbol,
    COUNT(*) as records,
    MIN(DATE(datetime)) as start_date,
    MAX(DATE(datetime)) as end_date,
    AVG(CASE WHEN rsi IS NOT NULL THEN 1 ELSE 0 END) as rsi_coverage,
    AVG(CASE WHEN macd IS NOT NULL THEN 1 ELSE 0 END) as macd_coverage
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol IN ('{"','".join(UTILITIES_STOCKS)}')
GROUP BY symbol
ORDER BY records DESC
"""
result = client.query(check_query).result()
print("\nData availability:")
for row in result:
    print(f"  {row.symbol}: {row.records} records ({row.start_date} to {row.end_date})")

# Step 2: Create utilities-specific features table
print("\nStep 2: Creating utilities-specific features...")

# Add rate-sensitivity and yield features
features_query = """
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.utilities_features` AS
WITH base_data AS (
    SELECT
        s.symbol,
        s.datetime,
        s.close,
        s.volume,
        s.rsi,
        s.macd,
        s.macd_histogram,
        s.mfi,
        s.cci,
        s.adx,
        s.momentum,
        s.sma_20,
        s.sma_50,
        s.sma_200,
        s.bb_width,
        s.atr,
        -- Calculate dividend yield proxy (price stability indicator)
        STDDEV(s.close) OVER (PARTITION BY s.symbol ORDER BY s.datetime ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as price_volatility_20d,
        -- Rate sensitivity proxy (inverse correlation with yields typically)
        (s.close - LAG(s.close, 5) OVER (PARTITION BY s.symbol ORDER BY s.datetime)) / NULLIF(LAG(s.close, 5) OVER (PARTITION BY s.symbol ORDER BY s.datetime), 0) * 100 as weekly_return,
        -- Sector momentum
        AVG(s.rsi) OVER (PARTITION BY s.symbol ORDER BY s.datetime ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as sector_rsi_avg,
        -- Volume trend
        s.volume / NULLIF(AVG(s.volume) OVER (PARTITION BY s.symbol ORDER BY s.datetime ROWS BETWEEN 20 PRECEDING AND CURRENT ROW), 0) as volume_ratio,
        -- Price to moving average ratios (using available columns)
        s.close_vs_sma50_pct,
        s.close_vs_sma200_pct,
        -- BB width normalized (useful for mean reversion in utilities)
        s.bb_width / NULLIF(s.close, 0) * 100 as bb_width_pct,
        -- ATR-normalized momentum (accounts for low volatility)
        s.momentum / NULLIF(s.atr, 0) as normalized_momentum,
        -- Direction target
        CASE
            WHEN LEAD(s.close) OVER (PARTITION BY s.symbol ORDER BY s.datetime) > s.close THEN 1
            ELSE 0
        END as direction_target
    FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean` s
    WHERE s.symbol IN ('NEE', 'DUK', 'EXC', 'SO', 'CEG', 'D', 'XEL', 'ED')
      AND s.datetime >= '2020-01-01'
      AND s.rsi IS NOT NULL
      AND s.macd IS NOT NULL
)
SELECT
    *,
    -- Additional derived features
    CASE WHEN bb_width_pct < 2 THEN 1 ELSE 0 END as low_volatility,
    CASE WHEN bb_width_pct > 5 THEN 1 ELSE 0 END as high_volatility,
    CASE WHEN close_vs_sma200_pct > 0 THEN 1 ELSE 0 END as above_sma200,
    CASE WHEN volume_ratio > 1.5 THEN 1 ELSE 0 END as high_volume
FROM base_data
WHERE direction_target IS NOT NULL
"""

print("Creating utilities features table...")
client.query(features_query).result()
print("Features table created.")

# Count records
count_query = """
SELECT COUNT(*) as total, COUNT(DISTINCT symbol) as symbols
FROM `aialgotradehits.ml_models.utilities_features`
"""
count_result = list(client.query(count_query).result())[0]
print(f"Total records: {count_result.total}, Symbols: {count_result.symbols}")

# Step 3: Train utilities-specific XGBoost model
print("\nStep 3: Training utilities-specific XGBoost model...")

train_model_query = """
CREATE OR REPLACE MODEL `aialgotradehits.ml_models.utilities_xgboost_v1`
OPTIONS(
    model_type = 'BOOSTED_TREE_CLASSIFIER',
    input_label_cols = ['direction_target'],
    max_iterations = 50,
    learn_rate = 0.1,
    early_stop = TRUE,
    min_split_loss = 0.1,
    data_split_method = 'AUTO_SPLIT'
) AS
SELECT
    -- Core features
    rsi,
    macd,
    macd_histogram,
    mfi,
    cci,
    adx,
    momentum,
    -- Utilities-specific features
    price_volatility_20d,
    weekly_return,
    sector_rsi_avg,
    volume_ratio,
    close_vs_sma50_pct,
    close_vs_sma200_pct,
    bb_width_pct,
    normalized_momentum,
    low_volatility,
    high_volatility,
    above_sma200,
    high_volume,
    -- Target
    direction_target
FROM `aialgotradehits.ml_models.utilities_features`
WHERE datetime < '2025-06-01'  -- Training data
"""

print("Training model (this may take a few minutes)...")
try:
    client.query(train_model_query).result()
    print("Model trained successfully!")
except Exception as e:
    print(f"Training error: {e}")

# Step 4: Evaluate model
print("\nStep 4: Evaluating utilities model...")

eval_query = """
SELECT
    *
FROM ML.EVALUATE(MODEL `aialgotradehits.ml_models.utilities_xgboost_v1`,
    (SELECT
        rsi, macd, macd_histogram, mfi, cci, adx, momentum,
        price_volatility_20d, weekly_return, sector_rsi_avg, volume_ratio,
        close_vs_sma50_pct, close_vs_sma200_pct, bb_width_pct, normalized_momentum,
        low_volatility, high_volatility, above_sma200, high_volume,
        direction_target
    FROM `aialgotradehits.ml_models.utilities_features`
    WHERE datetime >= '2025-06-01'))
"""

try:
    eval_result = list(client.query(eval_query).result())[0]
    print(f"\nModel Evaluation Results:")
    print(f"  Accuracy: {eval_result.accuracy * 100:.1f}%")
    print(f"  Precision: {eval_result.precision * 100:.1f}%")
    print(f"  Recall: {eval_result.recall * 100:.1f}%")
    print(f"  F1 Score: {eval_result.f1_score * 100:.1f}%")
    print(f"  Log Loss: {eval_result.log_loss:.4f}")
    print(f"  ROC AUC: {eval_result.roc_auc:.3f}")
except Exception as e:
    print(f"Evaluation error: {e}")

# Step 5: Feature importance
print("\nStep 5: Checking feature importance...")

importance_query = """
SELECT
    feature,
    ROUND(importance_weight * 100, 2) as importance_pct
FROM ML.FEATURE_IMPORTANCE(MODEL `aialgotradehits.ml_models.utilities_xgboost_v1`)
ORDER BY importance_weight DESC
LIMIT 10
"""

try:
    importance_result = client.query(importance_query).result()
    print("\nTop 10 Features by Importance:")
    for row in importance_result:
        print(f"  {row.feature}: {row.importance_pct}%")
except Exception as e:
    print(f"Feature importance error: {e}")

# Step 6: Make predictions for recent data
print("\nStep 6: Making predictions for utilities stocks...")

predict_query = """
SELECT
    symbol,
    DATE(datetime) as date,
    close,
    predicted_direction_target as predicted_direction,
    predicted_direction_target_probs[OFFSET(1)].prob as probability_up
FROM ML.PREDICT(MODEL `aialgotradehits.ml_models.utilities_xgboost_v1`,
    (SELECT
        symbol, datetime, close,
        rsi, macd, macd_histogram, mfi, cci, adx, momentum,
        price_volatility_20d, weekly_return, sector_rsi_avg, volume_ratio,
        close_vs_sma50_pct, close_vs_sma200_pct, bb_width_pct, normalized_momentum,
        low_volatility, high_volatility, above_sma200, high_volume
    FROM `aialgotradehits.ml_models.utilities_features`
    WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)))
ORDER BY datetime DESC, symbol
LIMIT 20
"""

try:
    pred_result = client.query(predict_query).result()
    print("\nRecent Predictions:")
    for row in pred_result:
        direction = 'UP' if row.predicted_direction == 1 else 'DOWN'
        print(f"  {row.symbol} ({row.date}): {direction} ({row.probability_up*100:.1f}% prob)")
except Exception as e:
    print(f"Prediction error: {e}")

print("\n" + "=" * 60)
print("UTILITIES MODEL IMPROVEMENT COMPLETE")
print("=" * 60)
print(f"Completed: {datetime.now()}")
