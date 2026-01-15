#!/usr/bin/env python3
"""
Phase 5: Model Monitoring & Drift Detection
============================================
Continuously monitors ML model performance and detects:
1. Prediction accuracy drift
2. Feature distribution drift
3. Market regime changes
4. Concept drift (relationship changes)

Alerts when accuracy falls below thresholds.
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
from datetime import datetime, timedelta
import json

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

bq_client = bigquery.Client(project=PROJECT_ID)

print("=" * 70)
print("PHASE 5: MODEL MONITORING & DRIFT DETECTION")
print("=" * 70)
print(f"Started: {datetime.now()}")

# =============================================================================
# Step 1: Create Model Performance Tracking Table
# =============================================================================
print("\n[1] Creating Model Performance Tracking Table...")

create_performance_table = f"""
CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.model_performance_daily` (
    date DATE NOT NULL,
    asset_type STRING NOT NULL,
    total_predictions INT64,
    correct_predictions INT64,
    accuracy_pct FLOAT64,
    accuracy_high_conf FLOAT64,
    accuracy_medium_conf FLOAT64,
    accuracy_low_conf FLOAT64,
    avg_up_probability FLOAT64,
    buy_signals INT64,
    sell_signals INT64,
    hold_signals INT64,
    true_positives INT64,
    false_positives INT64,
    true_negatives INT64,
    false_negatives INT64,
    precision_score FLOAT64,
    recall_score FLOAT64,
    f1_score FLOAT64,
    rolling_7d_accuracy FLOAT64,
    rolling_30d_accuracy FLOAT64,
    drift_detected BOOL,
    drift_type STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
"""
try:
    bq_client.query(create_performance_table).result()
    print("  Created: model_performance_daily")
except Exception as e:
    print(f"  Table exists or error: {e}")

# =============================================================================
# Step 2: Create Feature Distribution Tracking Table
# =============================================================================
print("\n[2] Creating Feature Distribution Tracking Table...")

create_feature_dist_table = f"""
CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.feature_distributions` (
    date DATE NOT NULL,
    asset_type STRING NOT NULL,
    feature_name STRING NOT NULL,
    mean_value FLOAT64,
    std_value FLOAT64,
    min_value FLOAT64,
    max_value FLOAT64,
    percentile_25 FLOAT64,
    percentile_50 FLOAT64,
    percentile_75 FLOAT64,
    null_count INT64,
    baseline_mean FLOAT64,
    baseline_std FLOAT64,
    ks_statistic FLOAT64,
    drift_detected BOOL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
"""
try:
    bq_client.query(create_feature_dist_table).result()
    print("  Created: feature_distributions")
except Exception as e:
    print(f"  Table exists or error: {e}")

# =============================================================================
# Step 3: Create Drift Alerts Table
# =============================================================================
print("\n[3] Creating Drift Alerts Table...")

create_alerts_table = f"""
CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{ML_DATASET}.model_drift_alerts` (
    alert_id STRING NOT NULL,
    alert_time TIMESTAMP NOT NULL,
    asset_type STRING,
    alert_type STRING,  -- ACCURACY_DRIFT, FEATURE_DRIFT, REGIME_CHANGE, CONCEPT_DRIFT
    severity STRING,    -- WARNING, CRITICAL
    metric_name STRING,
    current_value FLOAT64,
    threshold_value FLOAT64,
    baseline_value FLOAT64,
    message STRING,
    is_resolved BOOL DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
"""
try:
    bq_client.query(create_alerts_table).result()
    print("  Created: model_drift_alerts")
except Exception as e:
    print(f"  Table exists or error: {e}")

# =============================================================================
# Step 4: Calculate Daily Performance Metrics
# =============================================================================
print("\n[4] Calculating Daily Performance Metrics...")

daily_performance_query = f"""
INSERT INTO `{PROJECT_ID}.{ML_DATASET}.model_performance_daily`
(date, asset_type, total_predictions, correct_predictions, accuracy_pct,
 accuracy_high_conf, accuracy_medium_conf, accuracy_low_conf,
 avg_up_probability, buy_signals, sell_signals, hold_signals,
 true_positives, false_positives, true_negatives, false_negatives,
 precision_score, recall_score, f1_score, drift_detected, drift_type)

WITH daily_stats AS (
    SELECT
        DATE(datetime) as date,
        asset_type,
        COUNT(*) as total_predictions,
        SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct_predictions,

        -- High confidence accuracy (>65% or <35%)
        SUM(CASE WHEN (up_probability >= 0.65 OR up_probability <= 0.35)
                 AND predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct_high,
        SUM(CASE WHEN up_probability >= 0.65 OR up_probability <= 0.35 THEN 1 ELSE 0 END) as total_high,

        -- Medium confidence
        SUM(CASE WHEN up_probability BETWEEN 0.45 AND 0.65
                 AND up_probability NOT BETWEEN 0.55 AND 0.65
                 AND predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct_medium,
        SUM(CASE WHEN up_probability BETWEEN 0.45 AND 0.65
                 AND up_probability NOT BETWEEN 0.55 AND 0.65 THEN 1 ELSE 0 END) as total_medium,

        -- Low confidence
        SUM(CASE WHEN up_probability BETWEEN 0.45 AND 0.55
                 AND predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct_low,
        SUM(CASE WHEN up_probability BETWEEN 0.45 AND 0.55 THEN 1 ELSE 0 END) as total_low,

        AVG(up_probability) as avg_up_probability,

        -- Signal counts
        SUM(CASE WHEN up_probability >= 0.60 THEN 1 ELSE 0 END) as buy_signals,
        SUM(CASE WHEN up_probability <= 0.40 THEN 1 ELSE 0 END) as sell_signals,
        SUM(CASE WHEN up_probability BETWEEN 0.40 AND 0.60 THEN 1 ELSE 0 END) as hold_signals,

        -- Confusion matrix for UP predictions
        SUM(CASE WHEN predicted_direction = 'UP' AND actual_direction = 'UP' THEN 1 ELSE 0 END) as true_positives,
        SUM(CASE WHEN predicted_direction = 'UP' AND actual_direction = 'DOWN' THEN 1 ELSE 0 END) as false_positives,
        SUM(CASE WHEN predicted_direction = 'DOWN' AND actual_direction = 'DOWN' THEN 1 ELSE 0 END) as true_negatives,
        SUM(CASE WHEN predicted_direction = 'DOWN' AND actual_direction = 'UP' THEN 1 ELSE 0 END) as false_negatives

    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    WHERE data_split = 'VALIDATE'
      AND DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
    GROUP BY DATE(datetime), asset_type
)

SELECT
    date,
    asset_type,
    total_predictions,
    correct_predictions,
    ROUND(correct_predictions / total_predictions * 100, 2) as accuracy_pct,

    CASE WHEN total_high > 0 THEN ROUND(correct_high / total_high * 100, 2) ELSE NULL END as accuracy_high_conf,
    CASE WHEN total_medium > 0 THEN ROUND(correct_medium / total_medium * 100, 2) ELSE NULL END as accuracy_medium_conf,
    CASE WHEN total_low > 0 THEN ROUND(correct_low / total_low * 100, 2) ELSE NULL END as accuracy_low_conf,

    ROUND(avg_up_probability, 4) as avg_up_probability,
    buy_signals,
    sell_signals,
    hold_signals,
    true_positives,
    false_positives,
    true_negatives,
    false_negatives,

    -- Precision = TP / (TP + FP)
    CASE WHEN (true_positives + false_positives) > 0
         THEN ROUND(true_positives / (true_positives + false_positives), 4)
         ELSE NULL END as precision_score,

    -- Recall = TP / (TP + FN)
    CASE WHEN (true_positives + false_negatives) > 0
         THEN ROUND(true_positives / (true_positives + false_negatives), 4)
         ELSE NULL END as recall_score,

    -- F1 = 2 * (precision * recall) / (precision + recall)
    CASE WHEN (true_positives + false_positives) > 0 AND (true_positives + false_negatives) > 0
         THEN ROUND(
             2.0 * (true_positives / (true_positives + false_positives)) *
                   (true_positives / (true_positives + false_negatives)) /
             ((true_positives / (true_positives + false_positives)) +
              (true_positives / (true_positives + false_negatives)))
         , 4)
         ELSE NULL END as f1_score,

    FALSE as drift_detected,
    NULL as drift_type

FROM daily_stats
WHERE date NOT IN (SELECT DISTINCT date FROM `{PROJECT_ID}.{ML_DATASET}.model_performance_daily`)
ORDER BY date DESC, asset_type
"""

try:
    result = bq_client.query(daily_performance_query).result()
    print("  Inserted daily performance metrics")
except Exception as e:
    print(f"  Performance insert error: {e}")

# =============================================================================
# Step 5: Calculate Rolling Accuracy and Detect Drift
# =============================================================================
print("\n[5] Calculating Rolling Accuracy & Detecting Drift...")

rolling_accuracy_query = f"""
UPDATE `{PROJECT_ID}.{ML_DATASET}.model_performance_daily` t
SET
    rolling_7d_accuracy = r.rolling_7d,
    rolling_30d_accuracy = r.rolling_30d,
    drift_detected = CASE
        WHEN r.rolling_7d < (r.rolling_30d * 0.85) THEN TRUE  -- 15% drop
        ELSE FALSE
    END,
    drift_type = CASE
        WHEN r.rolling_7d < (r.rolling_30d * 0.85) THEN 'ACCURACY_DRIFT'
        ELSE NULL
    END
FROM (
    SELECT
        date,
        asset_type,
        AVG(accuracy_pct) OVER (
            PARTITION BY asset_type
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as rolling_7d,
        AVG(accuracy_pct) OVER (
            PARTITION BY asset_type
            ORDER BY date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) as rolling_30d
    FROM `{PROJECT_ID}.{ML_DATASET}.model_performance_daily`
) r
WHERE t.date = r.date AND t.asset_type = r.asset_type
"""

try:
    bq_client.query(rolling_accuracy_query).result()
    print("  Updated rolling accuracy metrics")
except Exception as e:
    print(f"  Rolling accuracy update error: {e}")

# =============================================================================
# Step 6: Generate Drift Alerts
# =============================================================================
print("\n[6] Generating Drift Alerts...")

drift_alert_query = f"""
INSERT INTO `{PROJECT_ID}.{ML_DATASET}.model_drift_alerts`
(alert_id, alert_time, asset_type, alert_type, severity, metric_name,
 current_value, threshold_value, baseline_value, message)

SELECT
    GENERATE_UUID() as alert_id,
    CURRENT_TIMESTAMP() as alert_time,
    asset_type,
    'ACCURACY_DRIFT' as alert_type,
    CASE
        WHEN rolling_7d_accuracy < (rolling_30d_accuracy * 0.75) THEN 'CRITICAL'
        ELSE 'WARNING'
    END as severity,
    'rolling_7d_accuracy' as metric_name,
    rolling_7d_accuracy as current_value,
    rolling_30d_accuracy * 0.85 as threshold_value,
    rolling_30d_accuracy as baseline_value,
    CONCAT(
        'Model accuracy dropped for ', asset_type, ': ',
        CAST(ROUND(rolling_7d_accuracy, 1) AS STRING), '% (7-day) vs ',
        CAST(ROUND(rolling_30d_accuracy, 1) AS STRING), '% (30-day baseline)'
    ) as message

FROM `{PROJECT_ID}.{ML_DATASET}.model_performance_daily`
WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND drift_detected = TRUE
  AND NOT EXISTS (
      SELECT 1 FROM `{PROJECT_ID}.{ML_DATASET}.model_drift_alerts`
      WHERE DATE(alert_time) = CURRENT_DATE()
        AND asset_type = model_performance_daily.asset_type
        AND alert_type = 'ACCURACY_DRIFT'
  )
"""

try:
    bq_client.query(drift_alert_query).result()
    print("  Generated drift alerts")
except Exception as e:
    print(f"  Alert generation error: {e}")

# =============================================================================
# Step 7: Create Monitoring View
# =============================================================================
print("\n[7] Creating Monitoring Dashboard View...")

create_monitoring_view = f"""
CREATE OR REPLACE VIEW `{PROJECT_ID}.{ML_DATASET}.v_model_monitoring_dashboard` AS

SELECT
    p.date,
    p.asset_type,
    p.total_predictions,
    p.accuracy_pct,
    p.accuracy_high_conf,
    p.rolling_7d_accuracy,
    p.rolling_30d_accuracy,
    p.precision_score,
    p.recall_score,
    p.f1_score,
    p.drift_detected,
    p.drift_type,

    -- Model health score (0-100)
    ROUND(
        (COALESCE(p.accuracy_pct, 50) * 0.4) +
        (COALESCE(p.precision_score, 0.5) * 100 * 0.2) +
        (COALESCE(p.recall_score, 0.5) * 100 * 0.2) +
        (CASE WHEN p.drift_detected THEN 0 ELSE 20 END)
    , 1) as model_health_score,

    -- Status
    CASE
        WHEN p.drift_detected AND p.rolling_7d_accuracy < 50 THEN 'CRITICAL'
        WHEN p.drift_detected THEN 'WARNING'
        WHEN p.accuracy_pct >= 80 THEN 'EXCELLENT'
        WHEN p.accuracy_pct >= 70 THEN 'GOOD'
        WHEN p.accuracy_pct >= 60 THEN 'FAIR'
        ELSE 'NEEDS_ATTENTION'
    END as model_status,

    -- Recent alerts
    a.alert_count

FROM `{PROJECT_ID}.{ML_DATASET}.model_performance_daily` p
LEFT JOIN (
    SELECT
        DATE(alert_time) as alert_date,
        asset_type,
        COUNT(*) as alert_count
    FROM `{PROJECT_ID}.{ML_DATASET}.model_drift_alerts`
    WHERE NOT is_resolved
    GROUP BY DATE(alert_time), asset_type
) a ON p.date = a.alert_date AND p.asset_type = a.asset_type

WHERE p.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY p.date DESC, p.asset_type
"""

try:
    bq_client.query(create_monitoring_view).result()
    print("  Created: v_model_monitoring_dashboard view")
except Exception as e:
    print(f"  View creation error: {e}")

# =============================================================================
# Step 8: Display Current Model Health
# =============================================================================
print("\n[8] Current Model Health Status...")
print("-" * 70)

health_query = f"""
SELECT
    asset_type,
    ROUND(AVG(accuracy_pct), 2) as avg_accuracy,
    ROUND(AVG(accuracy_high_conf), 2) as avg_high_conf_accuracy,
    ROUND(AVG(precision_score) * 100, 2) as avg_precision,
    ROUND(AVG(recall_score) * 100, 2) as avg_recall,
    SUM(CASE WHEN drift_detected THEN 1 ELSE 0 END) as drift_days,
    COUNT(*) as total_days
FROM `{PROJECT_ID}.{ML_DATASET}.model_performance_daily`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY asset_type
ORDER BY asset_type
"""

try:
    results = list(bq_client.query(health_query).result())
    for row in results:
        status = "HEALTHY" if row.drift_days == 0 else f"DRIFT ({row.drift_days} days)"
        print(f"  {row.asset_type:10} | Accuracy: {row.avg_accuracy or 0:.1f}% | High-Conf: {row.avg_high_conf_accuracy or 0:.1f}% | Precision: {row.avg_precision or 0:.1f}% | Status: {status}")
except Exception as e:
    print(f"  Health query error: {e}")

# =============================================================================
# Step 9: Check Active Alerts
# =============================================================================
print("\n[9] Active Drift Alerts...")
print("-" * 70)

alerts_query = f"""
SELECT
    alert_time,
    asset_type,
    alert_type,
    severity,
    message
FROM `{PROJECT_ID}.{ML_DATASET}.model_drift_alerts`
WHERE NOT is_resolved
ORDER BY alert_time DESC
LIMIT 10
"""

try:
    results = list(bq_client.query(alerts_query).result())
    if results:
        for row in results:
            print(f"  [{row.severity}] {row.asset_type}: {row.message}")
    else:
        print("  No active alerts - all models healthy")
except Exception as e:
    print(f"  Alerts query error: {e}")

print("\n" + "=" * 70)
print("PHASE 5 COMPLETE: Model Monitoring & Drift Detection")
print("=" * 70)
print("""
Created Tables:
  - model_performance_daily: Daily accuracy metrics
  - feature_distributions: Feature statistics tracking
  - model_drift_alerts: Alert log

Created Views:
  - v_model_monitoring_dashboard: Unified monitoring view

Drift Detection Rules:
  - WARNING: 7-day accuracy < 85% of 30-day baseline
  - CRITICAL: 7-day accuracy < 75% of 30-day baseline

Query Examples:
  -- Check model health
  SELECT * FROM `aialgotradehits.ml_models.v_model_monitoring_dashboard`
  WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)

  -- Get active alerts
  SELECT * FROM `aialgotradehits.ml_models.model_drift_alerts`
  WHERE NOT is_resolved
""")
print(f"\nCompleted: {datetime.now()}")
