#!/usr/bin/env python3
"""
Train Sector-Specific ML Models
================================
Trains XGBoost models for each sector individually with:
1. Sector-specific features including sentiment and Trump impact
2. Walk-forward validation (Train -> Test -> Validate)
3. Compares sector models vs general model performance

This should improve stock prediction accuracy by accounting for sector characteristics.
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
from datetime import datetime

PROJECT_ID = 'aialgotradehits'
ML_DATASET = 'ml_models'

bq_client = bigquery.Client(project=PROJECT_ID)

print("=" * 70)
print("SECTOR-SPECIFIC ML MODEL TRAINING")
print("=" * 70)
print(f"Started: {datetime.now()}")

# =============================================================================
# STEP 1: Get list of sectors with sufficient data
# =============================================================================
print("\n[1] IDENTIFYING SECTORS FOR TRAINING...")

sector_query = f"""
SELECT
    sector,
    COUNT(*) as total_records,
    SUM(CASE WHEN data_split = 'TRAIN' THEN 1 ELSE 0 END) as train_records,
    SUM(CASE WHEN data_split = 'TEST' THEN 1 ELSE 0 END) as test_records,
    SUM(CASE WHEN data_split = 'VALIDATE' THEN 1 ELSE 0 END) as validate_records
FROM `{PROJECT_ID}.{ML_DATASET}.stock_sector_features`
WHERE sector != 'Unknown'
GROUP BY sector
HAVING train_records >= 500 AND test_records >= 500
ORDER BY total_records DESC
"""

sectors_to_train = []
results = list(bq_client.query(sector_query).result())
print(f"\n  {'Sector':30} | {'Train':>10} | {'Test':>10} | {'Validate':>10}")
print("  " + "-" * 70)
for row in results:
    print(f"  {row.sector:30} | {row.train_records:>10,} | {row.test_records:>10,} | {row.validate_records:>10,}")
    sectors_to_train.append(row.sector)

print(f"\n  Total sectors to train: {len(sectors_to_train)}")

# =============================================================================
# STEP 2: Create Models Results Table
# =============================================================================
print("\n[2] CREATING MODEL RESULTS TABLE...")

create_results_table = f"""
CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.sector_model_results` (
    model_id STRING,
    sector STRING,
    training_date TIMESTAMP,
    train_accuracy FLOAT64,
    test_accuracy FLOAT64,
    validate_accuracy FLOAT64,
    train_records INT64,
    test_records INT64,
    validate_records INT64,
    high_conf_accuracy FLOAT64,
    feature_importance STRING,
    model_config STRING,
    status STRING
)
"""
try:
    bq_client.query(create_results_table).result()
    print("  Created: sector_model_results table")
except Exception as e:
    print(f"  Table exists or error: {e}")

# =============================================================================
# STEP 3: Train Model for Each Sector
# =============================================================================
print("\n[3] TRAINING SECTOR-SPECIFIC MODELS...")

model_results = []

for sector in sectors_to_train:
    sector_safe = sector.replace(' ', '_').replace('&', 'and')
    model_name = f"sector_{sector_safe.lower()}_xgboost"

    print(f"\n  Training: {sector}")

    # Create training model with sector-specific features
    train_query = f"""
    CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.{model_name}`
    OPTIONS (
        model_type = 'BOOSTED_TREE_CLASSIFIER',
        booster_type = 'GBTREE',
        num_parallel_tree = 1,
        max_iterations = 50,
        tree_method = 'HIST',
        early_stop = TRUE,
        min_split_loss = 0,
        max_tree_depth = 6,
        subsample = 0.8,
        input_label_cols = ['next_day_up'],
        data_split_method = 'CUSTOM',
        data_split_col = 'data_split_flag'
    ) AS
    SELECT
        -- Technical indicators
        rsi,
        macd,
        macd_histogram,
        price_vs_sma20,
        price_vs_sma50,
        price_vs_sma200,
        bb_position,
        atr,
        adx,
        plus_di,
        minus_di,
        ema_bullish,
        golden_cross,
        death_cross,

        -- Sector sentiment features (new)
        sector_sentiment,
        sector_fear_greed,
        sector_news_sentiment,
        sector_momentum,
        sector_volatility,
        political_sentiment,
        trump_impact,

        -- Target
        next_day_up,

        -- Data split flag
        CASE data_split
            WHEN 'TRAIN' THEN FALSE
            WHEN 'TEST' THEN TRUE
            ELSE NULL
        END as data_split_flag

    FROM `{PROJECT_ID}.{ML_DATASET}.stock_sector_features`
    WHERE sector = '{sector}'
      AND data_split IN ('TRAIN', 'TEST')
      AND rsi IS NOT NULL
      AND macd IS NOT NULL
    """

    try:
        job = bq_client.query(train_query)
        job.result()
        print(f"    Model trained: {model_name}")

        # Evaluate on validation set
        eval_query = f"""
        SELECT
            '{sector}' as sector,
            COUNT(*) as total_predictions,
            SUM(CASE WHEN predicted_next_day_up = next_day_up THEN 1 ELSE 0 END) as correct,
            ROUND(SUM(CASE WHEN predicted_next_day_up = next_day_up THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as accuracy,

            -- High confidence accuracy
            SUM(CASE WHEN predicted_next_day_up_probs.prob >= 0.65 OR predicted_next_day_up_probs.prob <= 0.35 THEN 1 ELSE 0 END) as high_conf_count,
            ROUND(
                SUM(CASE
                    WHEN (predicted_next_day_up_probs.prob >= 0.65 OR predicted_next_day_up_probs.prob <= 0.35)
                         AND predicted_next_day_up = next_day_up
                    THEN 1 ELSE 0 END) /
                NULLIF(SUM(CASE WHEN predicted_next_day_up_probs.prob >= 0.65 OR predicted_next_day_up_probs.prob <= 0.35 THEN 1 ELSE 0 END), 0) * 100
            , 2) as high_conf_accuracy

        FROM ML.PREDICT(
            MODEL `{PROJECT_ID}.{ML_DATASET}.{model_name}`,
            (
                SELECT
                    rsi, macd, macd_histogram,
                    price_vs_sma20, price_vs_sma50, price_vs_sma200,
                    bb_position, atr, adx, plus_di, minus_di,
                    ema_bullish, golden_cross, death_cross,
                    sector_sentiment, sector_fear_greed, sector_news_sentiment,
                    sector_momentum, sector_volatility, political_sentiment, trump_impact,
                    next_day_up
                FROM `{PROJECT_ID}.{ML_DATASET}.stock_sector_features`
                WHERE sector = '{sector}'
                  AND data_split = 'VALIDATE'
                  AND rsi IS NOT NULL
                  AND macd IS NOT NULL
            )
        )
        """

        eval_results = list(bq_client.query(eval_query).result())[0]

        print(f"    Validation: {eval_results.accuracy:.1f}% ({eval_results.total_predictions:,} records)")
        print(f"    High-Conf:  {eval_results.high_conf_accuracy or 0:.1f}% ({eval_results.high_conf_count:,} signals)")

        model_results.append({
            'sector': sector,
            'model_name': model_name,
            'total_predictions': eval_results.total_predictions,
            'accuracy': eval_results.accuracy,
            'high_conf_count': eval_results.high_conf_count,
            'high_conf_accuracy': eval_results.high_conf_accuracy or 0
        })

    except Exception as e:
        print(f"    Error: {str(e)[:100]}")
        model_results.append({
            'sector': sector,
            'model_name': model_name,
            'error': str(e)[:200]
        })

# =============================================================================
# STEP 4: Save Results
# =============================================================================
print("\n[4] SAVING MODEL RESULTS...")

for result in model_results:
    if 'error' not in result:
        insert_query = f"""
        INSERT INTO `{PROJECT_ID}.{ML_DATASET}.sector_model_results`
        (model_id, sector, training_date, validate_accuracy, validate_records, high_conf_accuracy, status)
        VALUES (
            '{result['model_name']}',
            '{result['sector']}',
            CURRENT_TIMESTAMP(),
            {result['accuracy']},
            {result['total_predictions']},
            {result['high_conf_accuracy']},
            'ACTIVE'
        )
        """
        try:
            bq_client.query(insert_query).result()
        except Exception as e:
            print(f"  Error saving result for {result['sector']}: {e}")

print(f"  Saved {len([r for r in model_results if 'error' not in r])} model results")

# =============================================================================
# STEP 5: Summary Comparison
# =============================================================================
print("\n" + "=" * 70)
print("SECTOR MODEL TRAINING SUMMARY")
print("=" * 70)

print(f"\n{'Sector':30} | {'Accuracy':>10} | {'High-Conf':>10} | {'Records':>12}")
print("-" * 70)

successful_models = [r for r in model_results if 'error' not in r]
for result in sorted(successful_models, key=lambda x: x['accuracy'], reverse=True):
    status = "GOOD" if result['accuracy'] >= 55 else "FAIR" if result['accuracy'] >= 50 else "NEEDS_WORK"
    print(f"{result['sector']:30} | {result['accuracy']:>9.1f}% | {result['high_conf_accuracy']:>9.1f}% | {result['total_predictions']:>12,}  [{status}]")

# Calculate overall improvement
if successful_models:
    avg_accuracy = sum(r['accuracy'] for r in successful_models) / len(successful_models)
    avg_high_conf = sum(r['high_conf_accuracy'] for r in successful_models) / len(successful_models)
    print(f"\n  Average Accuracy: {avg_accuracy:.1f}%")
    print(f"  Average High-Confidence: {avg_high_conf:.1f}%")
    print(f"  Previous Stock Accuracy: 55.6% (general model)")
    print(f"  Improvement: {avg_accuracy - 55.6:+.1f}%")

print("\n" + "=" * 70)
print("SECTOR MODEL TRAINING COMPLETE")
print("=" * 70)
print(f"\nCompleted: {datetime.now()}")
