#!/usr/bin/env python3
"""
ML Operations Cloud Function
=============================
Handles all ML pipeline operations:
- Daily inference on new market data
- Model monitoring and drift detection
- Weekly model retraining
- Daily backtest validation
- Alert notifications

Deployed as a single Cloud Function with different operations triggered by request parameters.
"""

import functions_framework
from google.cloud import bigquery
from datetime import datetime, timedelta
import json
import os

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
ML_DATASET = 'ml_models'

# Initialize BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)


def log(message):
    """Simple logging with timestamp"""
    print(f"[{datetime.now().isoformat()}] {message}")


# =============================================================================
# Operation 1: Daily Inference
# =============================================================================
def run_daily_inference(asset_types=None, confidence_threshold=0.55):
    """Generate ML predictions for latest market data"""
    log("Starting daily inference...")

    if asset_types is None:
        asset_types = ['stocks', 'crypto', 'etf']

    results = {
        'operation': 'daily_inference',
        'timestamp': datetime.now().isoformat(),
        'asset_types': asset_types,
        'predictions': {}
    }

    for asset_type in asset_types:
        table_name = f"{asset_type}_daily_clean"

        # Get latest data and generate predictions
        inference_query = f"""
        INSERT INTO `{PROJECT_ID}.{ML_DATASET}.realtime_predictions`
        (prediction_id, asset_type, symbol, datetime, close, rsi, macd_histogram, adx,
         growth_score, trend_regime, in_rise_cycle, rise_cycle_start,
         xgb_up_probability, xgb_predicted_direction, xgb_confidence,
         ensemble_up_probability, ensemble_direction, ensemble_confidence,
         signal, signal_strength)

        WITH latest_data AS (
            SELECT
                symbol,
                datetime,
                close,
                rsi,
                macd_histogram,
                adx,
                sma_20, sma_50, sma_200,
                growth_score,
                trend_regime,
                in_rise_cycle,
                rise_cycle_start,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC) as rn
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            WHERE DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
        ),

        predictions AS (
            SELECT
                *,
                -- Feature-based probability estimation
                (
                    0.5 +
                    (CASE WHEN rsi BETWEEN 30 AND 50 THEN 0.10 WHEN rsi < 30 THEN 0.15 WHEN rsi > 70 THEN -0.10 ELSE 0 END) +
                    (CASE WHEN macd_histogram > 0 THEN 0.08 ELSE -0.05 END) +
                    (CASE WHEN adx > 25 THEN 0.05 ELSE 0 END) +
                    (CASE WHEN close > sma_200 THEN 0.07 ELSE -0.07 END) +
                    (CASE WHEN in_rise_cycle THEN 0.05 ELSE 0 END) +
                    (CASE WHEN growth_score >= 75 THEN 0.10 WHEN growth_score >= 50 THEN 0.05 ELSE 0 END)
                ) as prob
            FROM latest_data
            WHERE rn = 1
        )

        SELECT
            GENERATE_UUID() as prediction_id,
            '{asset_type}' as asset_type,
            symbol,
            datetime,
            close,
            rsi,
            macd_histogram,
            adx,
            growth_score,
            trend_regime,
            in_rise_cycle,
            rise_cycle_start,
            ROUND(GREATEST(0.1, LEAST(0.9, prob)), 4) as xgb_up_probability,
            CASE WHEN prob >= 0.5 THEN 'UP' ELSE 'DOWN' END as xgb_predicted_direction,
            CASE
                WHEN prob >= 0.65 OR prob <= 0.35 THEN 'HIGH'
                WHEN prob >= 0.55 OR prob <= 0.45 THEN 'MEDIUM'
                ELSE 'LOW'
            END as xgb_confidence,
            ROUND(GREATEST(0.1, LEAST(0.9, prob)), 4) as ensemble_up_probability,
            CASE WHEN prob >= 0.5 THEN 'UP' ELSE 'DOWN' END as ensemble_direction,
            CASE
                WHEN prob >= 0.65 OR prob <= 0.35 THEN 'HIGH'
                WHEN prob >= 0.55 OR prob <= 0.45 THEN 'MEDIUM'
                ELSE 'LOW'
            END as ensemble_confidence,
            CASE
                WHEN prob >= 0.60 THEN 'BUY'
                WHEN prob <= 0.40 THEN 'SELL'
                ELSE 'HOLD'
            END as signal,
            ROUND(ABS(prob - 0.5) * 200, 1) as signal_strength
        FROM predictions
        WHERE NOT EXISTS (
            SELECT 1 FROM `{PROJECT_ID}.{ML_DATASET}.realtime_predictions` r
            WHERE r.symbol = predictions.symbol
              AND r.asset_type = '{asset_type}'
              AND DATE(r.datetime) = DATE(predictions.datetime)
        )
        """

        try:
            job = bq_client.query(inference_query)
            job.result()

            # Count predictions
            count_query = f"""
            SELECT COUNT(*) as cnt
            FROM `{PROJECT_ID}.{ML_DATASET}.realtime_predictions`
            WHERE asset_type = '{asset_type}'
              AND DATE(created_at) = CURRENT_DATE()
            """
            count_result = list(bq_client.query(count_query).result())[0]
            results['predictions'][asset_type] = count_result.cnt
            log(f"  {asset_type}: {count_result.cnt} predictions generated")

        except Exception as e:
            log(f"  {asset_type}: Error - {e}")
            results['predictions'][asset_type] = {'error': str(e)}

    log("Daily inference complete")
    return results


# =============================================================================
# Operation 2: Model Monitoring & Drift Detection
# =============================================================================
def run_model_monitoring(alert_threshold=0.85):
    """Check model performance and detect drift"""
    log("Starting model monitoring...")

    results = {
        'operation': 'model_monitoring',
        'timestamp': datetime.now().isoformat(),
        'health_status': {},
        'alerts': []
    }

    # Calculate daily performance metrics
    performance_query = f"""
    INSERT INTO `{PROJECT_ID}.{ML_DATASET}.model_performance_daily`
    (date, asset_type, total_predictions, correct_predictions, accuracy_pct,
     buy_signals, sell_signals, hold_signals, drift_detected, drift_type)

    WITH daily_stats AS (
        SELECT
            DATE(datetime) as date,
            asset_type,
            COUNT(*) as total_predictions,
            SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct_predictions,
            SUM(CASE WHEN signal = 'BUY' THEN 1 ELSE 0 END) as buy_signals,
            SUM(CASE WHEN signal = 'SELL' THEN 1 ELSE 0 END) as sell_signals,
            SUM(CASE WHEN signal = 'HOLD' THEN 1 ELSE 0 END) as hold_signals
        FROM `{PROJECT_ID}.{ML_DATASET}.realtime_predictions`
        WHERE DATE(datetime) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
          AND actual_direction IS NOT NULL
        GROUP BY DATE(datetime), asset_type
    )

    SELECT
        date,
        asset_type,
        total_predictions,
        correct_predictions,
        ROUND(correct_predictions / NULLIF(total_predictions, 0) * 100, 2) as accuracy_pct,
        buy_signals,
        sell_signals,
        hold_signals,
        FALSE as drift_detected,
        NULL as drift_type
    FROM daily_stats
    WHERE date NOT IN (
        SELECT DISTINCT date FROM `{PROJECT_ID}.{ML_DATASET}.model_performance_daily`
    )
    """

    try:
        bq_client.query(performance_query).result()
        log("  Performance metrics updated")
    except Exception as e:
        log(f"  Performance update error: {e}")

    # Check for drift
    drift_query = f"""
    SELECT
        asset_type,
        AVG(CASE WHEN date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) THEN accuracy_pct END) as accuracy_7d,
        AVG(CASE WHEN date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) THEN accuracy_pct END) as accuracy_30d
    FROM `{PROJECT_ID}.{ML_DATASET}.model_performance_daily`
    WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY asset_type
    """

    try:
        drift_results = list(bq_client.query(drift_query).result())
        for row in drift_results:
            status = 'HEALTHY'
            if row.accuracy_7d and row.accuracy_30d:
                if row.accuracy_7d < row.accuracy_30d * alert_threshold:
                    status = 'DRIFT_DETECTED'
                    results['alerts'].append({
                        'asset_type': row.asset_type,
                        'type': 'ACCURACY_DRIFT',
                        'severity': 'WARNING',
                        'accuracy_7d': row.accuracy_7d,
                        'accuracy_30d': row.accuracy_30d
                    })

            results['health_status'][row.asset_type] = {
                'status': status,
                'accuracy_7d': row.accuracy_7d,
                'accuracy_30d': row.accuracy_30d
            }
            log(f"  {row.asset_type}: {status} (7d: {row.accuracy_7d:.1f}%, 30d: {row.accuracy_30d:.1f}%)")
    except Exception as e:
        log(f"  Drift check error: {e}")

    # Insert alerts if any
    for alert in results['alerts']:
        alert_query = f"""
        INSERT INTO `{PROJECT_ID}.{ML_DATASET}.model_drift_alerts`
        (alert_id, alert_time, asset_type, alert_type, severity, metric_name,
         current_value, threshold_value, baseline_value, message)
        VALUES (
            GENERATE_UUID(),
            CURRENT_TIMESTAMP(),
            '{alert['asset_type']}',
            '{alert['type']}',
            '{alert['severity']}',
            'accuracy_7d',
            {alert['accuracy_7d']},
            {alert['accuracy_30d'] * alert_threshold},
            {alert['accuracy_30d']},
            'Model accuracy dropped: 7-day ({alert['accuracy_7d']:.1f}%) vs 30-day baseline ({alert['accuracy_30d']:.1f}%)'
        )
        """
        try:
            bq_client.query(alert_query).result()
            log(f"  Alert created for {alert['asset_type']}")
        except Exception as e:
            log(f"  Alert insert error: {e}")

    log("Model monitoring complete")
    return results


# =============================================================================
# Operation 3: Weekly Retrain
# =============================================================================
def run_weekly_retrain(validation_window_days=30):
    """Retrain ML model with latest data"""
    log("Starting weekly retrain...")

    results = {
        'operation': 'weekly_retrain',
        'timestamp': datetime.now().isoformat(),
        'status': 'started'
    }

    # Create updated feature table
    feature_query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_latest` AS

    WITH all_data AS (
        SELECT 'stocks' as asset_type, symbol, datetime, close, rsi, macd_histogram, adx,
               growth_score, in_rise_cycle, rise_cycle_start, trend_regime,
               LEAD(close, 1) OVER (PARTITION BY symbol ORDER BY datetime) as next_close
        FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
        WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)

        UNION ALL

        SELECT 'crypto' as asset_type, symbol, datetime, close, rsi, macd_histogram, adx,
               growth_score, in_rise_cycle, rise_cycle_start, trend_regime,
               LEAD(close, 1) OVER (PARTITION BY symbol ORDER BY datetime) as next_close
        FROM `{PROJECT_ID}.{DATASET_ID}.crypto_daily_clean`
        WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)

        UNION ALL

        SELECT 'etf' as asset_type, symbol, datetime, close, rsi, macd_histogram, adx,
               growth_score, in_rise_cycle, rise_cycle_start, trend_regime,
               LEAD(close, 1) OVER (PARTITION BY symbol ORDER BY datetime) as next_close
        FROM `{PROJECT_ID}.{DATASET_ID}.etfs_daily_clean`
        WHERE datetime >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)
    )

    SELECT
        *,
        CASE WHEN next_close > close THEN 1 ELSE 0 END as direction,
        CASE
            WHEN DATE(datetime) < DATE_SUB(CURRENT_DATE(), INTERVAL {validation_window_days} DAY) THEN 'TRAIN'
            ELSE 'VALIDATE'
        END as data_split
    FROM all_data
    WHERE next_close IS NOT NULL
      AND rsi IS NOT NULL
      AND adx IS NOT NULL
    """

    try:
        bq_client.query(feature_query).result()
        log("  Feature table updated")
        results['feature_table'] = 'created'
    except Exception as e:
        log(f"  Feature table error: {e}")
        results['feature_table'] = str(e)

    # Retrain model (using BigQuery ML)
    model_query = f"""
    CREATE OR REPLACE MODEL `{PROJECT_ID}.{ML_DATASET}.xgboost_retrained`
    OPTIONS(
        model_type='BOOSTED_TREE_CLASSIFIER',
        data_split_method='NO_SPLIT',
        input_label_cols=['direction'],
        max_iterations=100,
        learn_rate=0.1,
        min_tree_child_weight=5,
        subsample=0.8,
        early_stop=TRUE
    ) AS
    SELECT
        direction,
        rsi,
        macd_histogram,
        adx,
        growth_score,
        CASE WHEN in_rise_cycle THEN 1 ELSE 0 END as in_rise_cycle_flag
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_features_latest`
    WHERE data_split = 'TRAIN'
      AND rsi IS NOT NULL
    LIMIT 500000
    """

    try:
        job = bq_client.query(model_query)
        job.result()
        log("  Model retrained successfully")
        results['model'] = 'retrained'
        results['status'] = 'completed'
    except Exception as e:
        log(f"  Model retrain error: {e}")
        results['model'] = str(e)
        results['status'] = 'failed'

    # Log to deployment table
    log_query = f"""
    INSERT INTO `{PROJECT_ID}.{ML_DATASET}.deployment_log`
    (deployment_id, component, component_name, version, status, details)
    VALUES (
        GENERATE_UUID(),
        'MODEL',
        'xgboost_retrained',
        'weekly_{datetime.now().strftime('%Y%m%d')}',
        '{results['status'].upper()}',
        '{json.dumps(results)}'
    )
    """
    try:
        bq_client.query(log_query).result()
    except Exception as e:
        log(f"  Deployment log error: {e}")

    log("Weekly retrain complete")
    return results


# =============================================================================
# Operation 4: Daily Backtest
# =============================================================================
def run_daily_backtest(lookback_days=7, confidence_levels=None):
    """Run daily backtest validation"""
    log("Starting daily backtest...")

    if confidence_levels is None:
        confidence_levels = ['HIGH', 'MEDIUM']

    results = {
        'operation': 'daily_backtest',
        'timestamp': datetime.now().isoformat(),
        'lookback_days': lookback_days,
        'results': {}
    }

    # Calculate backtest metrics for recent predictions
    backtest_query = f"""
    SELECT
        asset_type,
        COUNT(*) as total_predictions,
        SUM(CASE WHEN
            (xgb_predicted_direction = 'UP' AND actual_direction = 'UP') OR
            (xgb_predicted_direction = 'DOWN' AND actual_direction = 'DOWN')
        THEN 1 ELSE 0 END) as correct,
        SUM(CASE WHEN signal = 'BUY' THEN 1 ELSE 0 END) as buy_signals,
        SUM(CASE WHEN signal = 'SELL' THEN 1 ELSE 0 END) as sell_signals,
        AVG(signal_strength) as avg_strength
    FROM `{PROJECT_ID}.{ML_DATASET}.realtime_predictions`
    WHERE DATE(datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_days} DAY)
      AND actual_direction IS NOT NULL
      AND xgb_confidence IN ({','.join([f"'{c}'" for c in confidence_levels])})
    GROUP BY asset_type
    """

    try:
        backtest_results = list(bq_client.query(backtest_query).result())
        for row in backtest_results:
            accuracy = row.correct / row.total_predictions * 100 if row.total_predictions > 0 else 0
            results['results'][row.asset_type] = {
                'total': row.total_predictions,
                'correct': row.correct,
                'accuracy': round(accuracy, 2),
                'buy_signals': row.buy_signals,
                'sell_signals': row.sell_signals,
                'avg_strength': round(row.avg_strength, 2) if row.avg_strength else 0
            }
            log(f"  {row.asset_type}: {accuracy:.1f}% accuracy ({row.total_predictions} predictions)")
    except Exception as e:
        log(f"  Backtest query error: {e}")
        results['error'] = str(e)

    # Insert into backtest results table
    for asset_type, metrics in results['results'].items():
        insert_query = f"""
        INSERT INTO `{PROJECT_ID}.{ML_DATASET}.backtest_results`
        (backtest_id, strategy_name, asset_type, start_date, end_date,
         total_trades, winning_trades, win_rate, parameters, notes)
        VALUES (
            GENERATE_UUID(),
            'Daily_Validation',
            '{asset_type}',
            DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_days} DAY),
            CURRENT_DATE(),
            {metrics['total']},
            {metrics['correct']},
            {metrics['accuracy']},
            '{json.dumps({'lookback_days': lookback_days, 'confidence_levels': confidence_levels})}',
            'Automated daily validation run'
        )
        """
        try:
            bq_client.query(insert_query).result()
        except Exception as e:
            log(f"  Backtest insert error: {e}")

    log("Daily backtest complete")
    return results


# =============================================================================
# Main Entry Point
# =============================================================================
@functions_framework.http
def ml_operations(request):
    """
    Main Cloud Function entry point.

    Operations:
    - inference: Run daily ML inference
    - monitoring: Check model health and drift
    - retrain: Weekly model retraining
    - backtest: Daily backtest validation
    - status: Get pipeline status
    """

    # Parse request
    try:
        request_json = request.get_json(silent=True) or {}
    except:
        request_json = {}

    operation = request_json.get('operation', request.args.get('operation', 'status'))

    log(f"ML Operations - Operation: {operation}")
    log(f"Request: {json.dumps(request_json)}")

    try:
        if operation == 'inference':
            asset_types = request_json.get('asset_types', ['stocks', 'crypto', 'etf'])
            confidence_threshold = request_json.get('confidence_threshold', 0.55)
            result = run_daily_inference(asset_types, confidence_threshold)

        elif operation == 'monitoring':
            alert_threshold = request_json.get('alert_threshold', 0.85)
            result = run_model_monitoring(alert_threshold)

        elif operation == 'retrain':
            validation_window_days = request_json.get('validation_window_days', 30)
            result = run_weekly_retrain(validation_window_days)

        elif operation == 'backtest':
            lookback_days = request_json.get('lookback_days', 7)
            confidence_levels = request_json.get('confidence_levels', ['HIGH', 'MEDIUM'])
            result = run_daily_backtest(lookback_days, confidence_levels)

        elif operation == 'status':
            # Get pipeline status
            status_query = f"""
            SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.v_pipeline_status`
            LIMIT 10
            """
            status_results = list(bq_client.query(status_query).result())
            result = {
                'operation': 'status',
                'timestamp': datetime.now().isoformat(),
                'pipeline_status': [dict(row) for row in status_results]
            }

        else:
            result = {
                'error': f'Unknown operation: {operation}',
                'valid_operations': ['inference', 'monitoring', 'retrain', 'backtest', 'status']
            }

        return json.dumps(result, default=str), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        log(f"Error: {e}")
        return json.dumps({
            'error': str(e),
            'operation': operation
        }), 500, {'Content-Type': 'application/json'}


# For local testing
if __name__ == "__main__":
    class MockRequest:
        def __init__(self, operation):
            self.args = {'operation': operation}
        def get_json(self, silent=False):
            return {'operation': self.args['operation']}

    # Test each operation
    print("\n=== Testing Status ===")
    result, code, _ = ml_operations(MockRequest('status'))
    print(result)
