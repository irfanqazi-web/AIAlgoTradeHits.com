"""
Multi-Timeframe Ensemble ML System
Combines daily and hourly predictions for higher confidence signals
"""
from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client(project='aialgotradehits')

print("=" * 60)
print("MULTI-TIMEFRAME ENSEMBLE ML SYSTEM")
print("=" * 60)
print(f"Started: {datetime.now()}")
print()

# Top performing symbols for ensemble
ENSEMBLE_SYMBOLS = [
    # Space/Robotics (98% accuracy)
    'HON', 'ROK', 'ISRG',
    # Semiconductors (81-88%)
    'NVDA', 'AMD', 'AVGO', 'INTC',
    # Defense (80%)
    'LMT', 'RTX', 'GD',
    # Dividend Champions (84%)
    'AAPL', 'MSFT', 'CAT'
]

symbol_str = "','".join(ENSEMBLE_SYMBOLS)

# Step 1: Create hourly features table
print("Step 1: Creating hourly features for ensemble...")

hourly_features_query = f"""
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.ensemble_hourly_features` AS
SELECT
    symbol,
    datetime,
    close,
    rsi,
    macd,
    macd_histogram,
    cci,
    adx,
    momentum,
    volume,
    COALESCE(atr, 0) as atr,
    -- Hourly-specific features
    STDDEV(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 24 PRECEDING AND CURRENT ROW) as hourly_volatility,
    AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 24 PRECEDING AND CURRENT ROW) as avg_hourly_volume,
    volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 24 PRECEDING AND CURRENT ROW), 0) as volume_spike,
    -- Direction target (next hour)
    CASE
        WHEN LEAD(close) OVER (PARTITION BY symbol ORDER BY datetime) > close THEN 1
        ELSE 0
    END as direction_target
FROM `aialgotradehits.crypto_trading_data.stocks_hourly_clean`
WHERE symbol IN ('{symbol_str}')
  AND datetime >= '2024-01-01'
  AND rsi IS NOT NULL
  AND macd IS NOT NULL
"""

try:
    client.query(hourly_features_query).result()
    print("Hourly features table created.")
except Exception as e:
    print(f"Hourly features error: {e}")

# Step 2: Train hourly model
print("\nStep 2: Training hourly XGBoost model...")

hourly_model_query = """
CREATE OR REPLACE MODEL `aialgotradehits.ml_models.ensemble_hourly_xgboost`
OPTIONS(
    model_type = 'BOOSTED_TREE_CLASSIFIER',
    input_label_cols = ['direction_target'],
    max_iterations = 30,
    learn_rate = 0.1,
    early_stop = TRUE,
    data_split_method = 'AUTO_SPLIT'
) AS
SELECT
    rsi, macd, macd_histogram, cci, adx, momentum, atr,
    hourly_volatility, volume_spike,
    direction_target
FROM `aialgotradehits.ml_models.ensemble_hourly_features`
WHERE datetime < '2025-10-01'
  AND direction_target IS NOT NULL
"""

try:
    client.query(hourly_model_query).result()
    print("Hourly model trained successfully!")
except Exception as e:
    print(f"Hourly model error: {e}")

# Step 3: Create daily features table
print("\nStep 3: Creating daily features for ensemble...")

daily_features_query = f"""
CREATE OR REPLACE TABLE `aialgotradehits.ml_models.ensemble_daily_features` AS
SELECT
    symbol,
    datetime,
    close,
    rsi,
    macd,
    macd_histogram,
    mfi,
    cci,
    adx,
    momentum,
    volume,
    sma_20,
    sma_50,
    sma_200,
    -- Daily-specific features
    close / NULLIF(sma_50, 0) as price_sma50_ratio,
    close / NULLIF(sma_200, 0) as price_sma200_ratio,
    STDDEV(close) OVER (PARTITION BY symbol ORDER BY datetime ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as daily_volatility,
    -- Direction target (next day)
    CASE
        WHEN LEAD(close) OVER (PARTITION BY symbol ORDER BY datetime) > close THEN 1
        ELSE 0
    END as direction_target
FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
WHERE symbol IN ('{symbol_str}')
  AND datetime >= '2020-01-01'
  AND rsi IS NOT NULL
  AND macd IS NOT NULL
"""

try:
    client.query(daily_features_query).result()
    print("Daily features table created.")
except Exception as e:
    print(f"Daily features error: {e}")

# Step 4: Train daily model
print("\nStep 4: Training daily XGBoost model...")

daily_model_query = """
CREATE OR REPLACE MODEL `aialgotradehits.ml_models.ensemble_daily_xgboost`
OPTIONS(
    model_type = 'BOOSTED_TREE_CLASSIFIER',
    input_label_cols = ['direction_target'],
    max_iterations = 50,
    learn_rate = 0.1,
    early_stop = TRUE,
    data_split_method = 'AUTO_SPLIT'
) AS
SELECT
    rsi, macd, macd_histogram, mfi, cci, adx, momentum,
    price_sma50_ratio, price_sma200_ratio, daily_volatility,
    direction_target
FROM `aialgotradehits.ml_models.ensemble_daily_features`
WHERE datetime < '2025-06-01'
  AND direction_target IS NOT NULL
"""

try:
    client.query(daily_model_query).result()
    print("Daily model trained successfully!")
except Exception as e:
    print(f"Daily model error: {e}")

# Step 5: Evaluate both models
print("\nStep 5: Evaluating models...")

# Hourly model evaluation
hourly_eval_query = """
SELECT 'Hourly' as timeframe, *
FROM ML.EVALUATE(MODEL `aialgotradehits.ml_models.ensemble_hourly_xgboost`,
    (SELECT rsi, macd, macd_histogram, cci, adx, momentum, atr,
            hourly_volatility, volume_spike, direction_target
     FROM `aialgotradehits.ml_models.ensemble_hourly_features`
     WHERE datetime >= '2025-10-01' AND direction_target IS NOT NULL))
"""

try:
    hourly_eval = list(client.query(hourly_eval_query).result())[0]
    print(f"\nHourly Model Results:")
    print(f"  Accuracy: {hourly_eval.accuracy * 100:.1f}%")
    print(f"  ROC AUC: {hourly_eval.roc_auc:.3f}")
except Exception as e:
    print(f"Hourly eval error: {e}")

# Daily model evaluation
daily_eval_query = """
SELECT 'Daily' as timeframe, *
FROM ML.EVALUATE(MODEL `aialgotradehits.ml_models.ensemble_daily_xgboost`,
    (SELECT rsi, macd, macd_histogram, mfi, cci, adx, momentum,
            price_sma50_ratio, price_sma200_ratio, daily_volatility, direction_target
     FROM `aialgotradehits.ml_models.ensemble_daily_features`
     WHERE datetime >= '2025-06-01' AND direction_target IS NOT NULL))
"""

try:
    daily_eval = list(client.query(daily_eval_query).result())[0]
    print(f"\nDaily Model Results:")
    print(f"  Accuracy: {daily_eval.accuracy * 100:.1f}%")
    print(f"  ROC AUC: {daily_eval.roc_auc:.3f}")
except Exception as e:
    print(f"Daily eval error: {e}")

# Step 6: Create ensemble predictions view
print("\nStep 6: Creating ensemble predictions view...")

ensemble_view_query = """
CREATE OR REPLACE VIEW `aialgotradehits.ml_models.v_ensemble_predictions` AS
WITH hourly_predictions AS (
    SELECT
        symbol,
        TIMESTAMP_TRUNC(datetime, DAY) as trade_date,
        AVG(CASE WHEN predicted_direction_target = 1 THEN 1.0 ELSE 0.0 END) as hourly_bullish_pct,
        COUNT(*) as hourly_signals
    FROM ML.PREDICT(MODEL `aialgotradehits.ml_models.ensemble_hourly_xgboost`,
        (SELECT symbol, datetime,
                rsi, macd, macd_histogram, cci, adx, momentum, atr,
                hourly_volatility, volume_spike
         FROM `aialgotradehits.ml_models.ensemble_hourly_features`
         WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)))
    GROUP BY symbol, TIMESTAMP_TRUNC(datetime, DAY)
),
daily_predictions AS (
    SELECT
        symbol,
        DATE(datetime) as trade_date,
        predicted_direction_target as daily_direction,
        predicted_direction_target_probs[OFFSET(1)].prob as daily_prob_up
    FROM ML.PREDICT(MODEL `aialgotradehits.ml_models.ensemble_daily_xgboost`,
        (SELECT symbol, datetime,
                rsi, macd, macd_histogram, mfi, cci, adx, momentum,
                price_sma50_ratio, price_sma200_ratio, daily_volatility
         FROM `aialgotradehits.ml_models.ensemble_daily_features`
         WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)))
)
SELECT
    d.symbol,
    d.trade_date,
    d.daily_direction,
    d.daily_prob_up,
    h.hourly_bullish_pct,
    h.hourly_signals,
    -- Ensemble signal: requires alignment between daily and hourly
    CASE
        WHEN d.daily_direction = 1 AND h.hourly_bullish_pct >= 0.6 THEN 'STRONG_BUY'
        WHEN d.daily_direction = 1 AND h.hourly_bullish_pct >= 0.4 THEN 'BUY'
        WHEN d.daily_direction = 0 AND h.hourly_bullish_pct <= 0.4 THEN 'STRONG_SELL'
        WHEN d.daily_direction = 0 AND h.hourly_bullish_pct <= 0.6 THEN 'SELL'
        ELSE 'HOLD'
    END as ensemble_signal,
    -- Confidence based on alignment
    CASE
        WHEN (d.daily_direction = 1 AND h.hourly_bullish_pct >= 0.6) OR
             (d.daily_direction = 0 AND h.hourly_bullish_pct <= 0.4)
        THEN 'HIGH'
        WHEN (d.daily_direction = 1 AND h.hourly_bullish_pct >= 0.5) OR
             (d.daily_direction = 0 AND h.hourly_bullish_pct <= 0.5)
        THEN 'MEDIUM'
        ELSE 'LOW'
    END as confidence
FROM daily_predictions d
LEFT JOIN hourly_predictions h ON d.symbol = h.symbol AND d.trade_date = DATE(h.trade_date)
"""

try:
    client.query(ensemble_view_query).result()
    print("Ensemble predictions view created!")
except Exception as e:
    print(f"View creation error: {e}")

# Step 7: Get current ensemble signals
print("\nStep 7: Current Ensemble Signals...")

signals_query = """
SELECT *
FROM `aialgotradehits.ml_models.v_ensemble_predictions`
WHERE confidence IN ('HIGH', 'MEDIUM')
ORDER BY trade_date DESC, confidence, symbol
LIMIT 20
"""

try:
    signals = client.query(signals_query).result()
    print("\nCurrent High-Confidence Ensemble Signals:")
    for row in signals:
        print(f"  {row.symbol} ({row.trade_date}): {row.ensemble_signal} [{row.confidence}]")
        print(f"    Daily: {'UP' if row.daily_direction == 1 else 'DOWN'} ({row.daily_prob_up*100:.1f}%)")
        print(f"    Hourly: {row.hourly_bullish_pct*100:.1f}% bullish ({row.hourly_signals} signals)")
except Exception as e:
    print(f"Signals error: {e}")

print("\n" + "=" * 60)
print("MULTI-TIMEFRAME ENSEMBLE COMPLETE")
print("=" * 60)
print(f"Completed: {datetime.now()}")
