"""
Model Performance Monitoring and Drift Detection for AIAlgoTradeHits.com
Based on: llm-model-development-process-aialgotradehits.html

This module provides:
1. Real-time prediction tracking
2. Accuracy monitoring over rolling windows
3. Data drift detection using KL divergence
4. Concept drift detection using model performance decay
5. Alert system for performance degradation
"""

from google.cloud import bigquery
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime, timedelta
import json
import pickle
import os
from typing import Dict, List, Optional

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
MODEL_DIR = 'C:/1AITrading/Trading/models'
METRICS_DIR = 'C:/1AITrading/Trading/metrics'

os.makedirs(METRICS_DIR, exist_ok=True)

bq_client = bigquery.Client(project=PROJECT_ID)


class ModelPerformanceMonitor:
    """Monitor model performance and detect drift"""

    def __init__(self, model_name: str = 'hybrid_model'):
        self.model_name = model_name
        self.predictions_log = []
        self.baseline_stats = {}
        self.alert_thresholds = {
            'accuracy_drop': 0.05,  # Alert if accuracy drops by 5%
            'kl_divergence': 0.5,   # Alert if KL divergence exceeds 0.5
            'performance_window': 30,  # Days to calculate rolling performance
            'min_samples': 20       # Minimum samples for reliable metrics
        }

    def log_prediction(self, symbol: str, asset_type: str, prediction: Dict,
                       actual_direction: Optional[str] = None):
        """Log a model prediction for future evaluation"""

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'asset_type': asset_type,
            'predicted_direction': prediction.get('direction'),
            'confidence': prediction.get('confidence'),
            'ensemble_score': prediction.get('ensemble_score'),
            'xgb_prediction': prediction.get('xgb_prediction', {}).get('direction'),
            'gemini_prediction': prediction.get('gemini_prediction', {}).get('direction'),
            'actual_direction': actual_direction,
            'is_correct': None if actual_direction is None else (
                prediction.get('direction') == actual_direction
            )
        }

        self.predictions_log.append(log_entry)
        return log_entry

    def evaluate_past_predictions(self, asset_type: str = 'stocks', lookback_days: int = 30):
        """Evaluate past predictions against actual outcomes"""

        table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'

        # Load predictions log
        log_path = os.path.join(METRICS_DIR, f'{self.model_name}_{asset_type}_predictions.json')
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                self.predictions_log = json.load(f)

        # Get actual price movements from BigQuery
        query = f"""
        SELECT
            symbol,
            DATE(datetime) as date,
            close,
            LAG(close) OVER (PARTITION BY symbol ORDER BY datetime) as prev_close
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_days} DAY))
        ORDER BY symbol, datetime
        """

        df = bq_client.query(query).to_dataframe()
        df['actual_direction'] = np.where(df['close'] > df['prev_close'], 'UP',
                                          np.where(df['close'] < df['prev_close'], 'DOWN', 'NEUTRAL'))

        # Match predictions with actuals
        updated_log = []
        for pred in self.predictions_log:
            pred_date = pd.to_datetime(pred['timestamp']).date()
            symbol = pred['symbol']

            # Find next day's actual direction
            actual = df[(df['symbol'] == symbol) &
                        (df['date'] == pred_date + timedelta(days=1))]

            if not actual.empty:
                pred['actual_direction'] = actual.iloc[0]['actual_direction']
                pred['is_correct'] = pred['predicted_direction'] == pred['actual_direction']

            updated_log.append(pred)

        self.predictions_log = updated_log

        # Save updated log
        with open(log_path, 'w') as f:
            json.dump(self.predictions_log, f, indent=2)

        return self.predictions_log

    def calculate_performance_metrics(self, asset_type: str = 'stocks',
                                       window_days: int = None) -> Dict:
        """Calculate model performance metrics"""

        if window_days is None:
            window_days = self.alert_thresholds['performance_window']

        # Filter predictions with outcomes
        evaluated = [p for p in self.predictions_log
                     if p.get('actual_direction') is not None
                     and p.get('asset_type') == asset_type]

        if len(evaluated) < self.alert_thresholds['min_samples']:
            return {
                'status': 'insufficient_data',
                'sample_count': len(evaluated),
                'required': self.alert_thresholds['min_samples']
            }

        # Filter by time window
        cutoff = datetime.now() - timedelta(days=window_days)
        recent = [p for p in evaluated
                  if pd.to_datetime(p['timestamp']) >= cutoff]

        if len(recent) < self.alert_thresholds['min_samples']:
            recent = evaluated  # Use all data if not enough recent

        # Calculate metrics
        y_true = [p['actual_direction'] for p in recent]
        y_pred = [p['predicted_direction'] for p in recent]

        # Convert to binary for metrics
        y_true_binary = [1 if d == 'UP' else 0 for d in y_true]
        y_pred_binary = [1 if d == 'UP' else 0 for d in y_pred]

        metrics = {
            'asset_type': asset_type,
            'window_days': window_days,
            'sample_count': len(recent),
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true_binary, y_pred_binary, zero_division=0),
            'recall': recall_score(y_true_binary, y_pred_binary, zero_division=0),
            'f1_score': f1_score(y_true_binary, y_pred_binary, zero_division=0),
            'direction_distribution': {
                'predicted': {
                    'UP': y_pred.count('UP') / len(y_pred),
                    'DOWN': y_pred.count('DOWN') / len(y_pred),
                    'NEUTRAL': y_pred.count('NEUTRAL') / len(y_pred)
                },
                'actual': {
                    'UP': y_true.count('UP') / len(y_true),
                    'DOWN': y_true.count('DOWN') / len(y_true),
                    'NEUTRAL': y_true.count('NEUTRAL') / len(y_true)
                }
            },
            'calculated_at': datetime.now().isoformat()
        }

        # By confidence level
        for conf in ['HIGH', 'MEDIUM', 'LOW']:
            conf_preds = [p for p in recent if p.get('confidence') == conf]
            if conf_preds:
                conf_correct = sum(1 for p in conf_preds if p.get('is_correct'))
                metrics[f'accuracy_{conf.lower()}_confidence'] = conf_correct / len(conf_preds)

        return metrics

    def detect_data_drift(self, asset_type: str = 'stocks',
                          reference_days: int = 90,
                          current_days: int = 7) -> Dict:
        """Detect data drift using statistical tests"""

        table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'

        # Fetch reference data (older)
        reference_query = f"""
        SELECT rsi, macd, adx, atr, volume, close
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE datetime BETWEEN
            TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL {reference_days} DAY))
            AND TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL {current_days + 7} DAY))
        AND rsi IS NOT NULL
        """

        # Fetch current data (recent)
        current_query = f"""
        SELECT rsi, macd, adx, atr, volume, close
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL {current_days} DAY))
        AND rsi IS NOT NULL
        """

        df_ref = bq_client.query(reference_query).to_dataframe()
        df_cur = bq_client.query(current_query).to_dataframe()

        if df_ref.empty or df_cur.empty:
            return {'status': 'insufficient_data'}

        drift_results = {
            'asset_type': asset_type,
            'reference_period': f'{reference_days} days',
            'current_period': f'{current_days} days',
            'reference_samples': len(df_ref),
            'current_samples': len(df_cur),
            'features': {},
            'drift_detected': False,
            'calculated_at': datetime.now().isoformat()
        }

        # Check each feature for drift
        features = ['rsi', 'macd', 'adx', 'atr', 'volume', 'close']

        for feature in features:
            ref_data = df_ref[feature].dropna()
            cur_data = df_cur[feature].dropna()

            if len(ref_data) < 10 or len(cur_data) < 10:
                continue

            # KS test for distribution difference
            ks_stat, ks_pvalue = stats.ks_2samp(ref_data, cur_data)

            # Calculate KL divergence (approximate)
            # Normalize and bin the data
            ref_hist, bins = np.histogram(ref_data, bins=20, density=True)
            cur_hist, _ = np.histogram(cur_data, bins=bins, density=True)

            # Add small epsilon to avoid division by zero
            ref_hist = ref_hist + 1e-10
            cur_hist = cur_hist + 1e-10

            kl_div = stats.entropy(cur_hist, ref_hist)

            # Mean and std comparison
            ref_mean, ref_std = ref_data.mean(), ref_data.std()
            cur_mean, cur_std = cur_data.mean(), cur_data.std()
            mean_shift = abs(cur_mean - ref_mean) / (ref_std + 1e-10)

            drift_results['features'][feature] = {
                'ks_statistic': float(ks_stat),
                'ks_pvalue': float(ks_pvalue),
                'kl_divergence': float(kl_div),
                'reference_mean': float(ref_mean),
                'current_mean': float(cur_mean),
                'mean_shift_std': float(mean_shift),
                'drift_detected': kl_div > self.alert_thresholds['kl_divergence'] or ks_pvalue < 0.05
            }

            if drift_results['features'][feature]['drift_detected']:
                drift_results['drift_detected'] = True

        return drift_results

    def detect_concept_drift(self, asset_type: str = 'stocks') -> Dict:
        """Detect concept drift by comparing model performance over time windows"""

        # Calculate performance for different time windows
        windows = [7, 14, 30, 60]
        window_metrics = {}

        for window in windows:
            metrics = self.calculate_performance_metrics(asset_type, window)
            if metrics.get('status') != 'insufficient_data':
                window_metrics[f'{window}d'] = metrics.get('accuracy', 0)

        if len(window_metrics) < 2:
            return {'status': 'insufficient_data', 'window_metrics': window_metrics}

        # Check for performance degradation
        values = list(window_metrics.values())
        if len(values) >= 2:
            recent_acc = values[0]  # Most recent window
            older_acc = values[-1]  # Oldest window

            performance_drop = older_acc - recent_acc

            concept_drift = {
                'asset_type': asset_type,
                'window_metrics': window_metrics,
                'performance_drop': float(performance_drop),
                'drift_detected': performance_drop > self.alert_thresholds['accuracy_drop'],
                'severity': 'HIGH' if performance_drop > 0.1 else 'MEDIUM' if performance_drop > 0.05 else 'LOW',
                'calculated_at': datetime.now().isoformat()
            }

            return concept_drift

        return {'status': 'insufficient_data', 'window_metrics': window_metrics}

    def generate_monitoring_report(self, asset_type: str = 'stocks') -> Dict:
        """Generate comprehensive monitoring report"""

        report = {
            'model_name': self.model_name,
            'asset_type': asset_type,
            'generated_at': datetime.now().isoformat(),
            'sections': {}
        }

        # Performance metrics
        print(f"Calculating performance metrics for {asset_type}...")
        report['sections']['performance'] = self.calculate_performance_metrics(asset_type)

        # Data drift
        print(f"Detecting data drift for {asset_type}...")
        report['sections']['data_drift'] = self.detect_data_drift(asset_type)

        # Concept drift
        print(f"Detecting concept drift for {asset_type}...")
        report['sections']['concept_drift'] = self.detect_concept_drift(asset_type)

        # Generate alerts
        alerts = []

        # Performance alerts
        perf = report['sections']['performance']
        if perf.get('accuracy') and perf['accuracy'] < 0.5:
            alerts.append({
                'type': 'PERFORMANCE',
                'severity': 'HIGH',
                'message': f"Model accuracy ({perf['accuracy']:.2%}) is below random baseline"
            })

        # Data drift alerts
        data_drift = report['sections']['data_drift']
        if data_drift.get('drift_detected'):
            drifted_features = [f for f, v in data_drift.get('features', {}).items()
                                if v.get('drift_detected')]
            alerts.append({
                'type': 'DATA_DRIFT',
                'severity': 'MEDIUM',
                'message': f"Data drift detected in features: {', '.join(drifted_features)}"
            })

        # Concept drift alerts
        concept_drift = report['sections']['concept_drift']
        if concept_drift.get('drift_detected'):
            alerts.append({
                'type': 'CONCEPT_DRIFT',
                'severity': concept_drift.get('severity', 'MEDIUM'),
                'message': f"Model performance dropping by {concept_drift.get('performance_drop', 0):.2%}"
            })

        report['alerts'] = alerts
        report['alert_count'] = len(alerts)

        # Convert numpy types to native Python types
        def convert_types(obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            return obj

        report = convert_types(report)

        # Save report
        report_path = os.path.join(METRICS_DIR, f'{self.model_name}_{asset_type}_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Report saved to: {report_path}")

        return report

    def set_baseline_stats(self, asset_type: str = 'stocks'):
        """Set baseline statistics for drift detection"""

        table = 'stocks_daily_clean' if asset_type == 'stocks' else 'crypto_daily_clean'

        query = f"""
        SELECT
            AVG(rsi) as avg_rsi,
            STDDEV(rsi) as std_rsi,
            AVG(macd) as avg_macd,
            STDDEV(macd) as std_macd,
            AVG(adx) as avg_adx,
            STDDEV(adx) as std_adx,
            AVG(atr) as avg_atr,
            STDDEV(atr) as std_atr
        FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
        WHERE datetime >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY))
        """

        df = bq_client.query(query).to_dataframe()

        if not df.empty:
            self.baseline_stats[asset_type] = df.iloc[0].to_dict()

            # Save baseline
            baseline_path = os.path.join(METRICS_DIR, f'{self.model_name}_{asset_type}_baseline.json')
            with open(baseline_path, 'w') as f:
                json.dump(self.baseline_stats[asset_type], f, indent=2)

            print(f"Baseline stats saved for {asset_type}")

        return self.baseline_stats.get(asset_type)


def create_monitoring_tables():
    """Create BigQuery tables for storing model metrics"""

    # Predictions log table
    predictions_schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("model_name", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("predicted_direction", "STRING"),
        bigquery.SchemaField("confidence", "STRING"),
        bigquery.SchemaField("ensemble_score", "FLOAT"),
        bigquery.SchemaField("actual_direction", "STRING"),
        bigquery.SchemaField("is_correct", "BOOLEAN"),
    ]

    # Performance metrics table
    metrics_schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("model_name", "STRING"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("window_days", "INT64"),
        bigquery.SchemaField("accuracy", "FLOAT"),
        bigquery.SchemaField("precision", "FLOAT"),
        bigquery.SchemaField("recall", "FLOAT"),
        bigquery.SchemaField("f1_score", "FLOAT"),
        bigquery.SchemaField("sample_count", "INT64"),
    ]

    # Drift detection table
    drift_schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("model_name", "STRING"),
        bigquery.SchemaField("asset_type", "STRING"),
        bigquery.SchemaField("drift_type", "STRING"),
        bigquery.SchemaField("drift_detected", "BOOLEAN"),
        bigquery.SchemaField("severity", "STRING"),
        bigquery.SchemaField("details", "JSON"),
    ]

    tables = {
        'model_predictions_log': predictions_schema,
        'model_performance_metrics': metrics_schema,
        'model_drift_detection': drift_schema
    }

    for table_name, schema in tables.items():
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)

        try:
            bq_client.create_table(table)
            print(f"Created table: {table_id}")
        except Exception as e:
            if 'Already Exists' in str(e):
                print(f"Table already exists: {table_id}")
            else:
                print(f"Error creating table {table_id}: {e}")


def main():
    """Main function to run monitoring"""

    print("=" * 80)
    print("MODEL PERFORMANCE MONITORING AND DRIFT DETECTION")
    print("=" * 80)
    print(f"Started: {datetime.now()}")

    # Create monitoring tables
    print("\n--- CREATING MONITORING TABLES ---")
    create_monitoring_tables()

    # Initialize monitor
    monitor = ModelPerformanceMonitor('hybrid_model')

    # Set baselines
    print("\n--- SETTING BASELINE STATISTICS ---")
    monitor.set_baseline_stats('stocks')
    monitor.set_baseline_stats('crypto')

    # Generate reports
    print("\n--- GENERATING MONITORING REPORTS ---")

    stock_report = monitor.generate_monitoring_report('stocks')
    print(f"\nStock Report Summary:")
    print(f"  Alerts: {stock_report['alert_count']}")
    if stock_report['alerts']:
        for alert in stock_report['alerts']:
            print(f"  - [{alert['severity']}] {alert['type']}: {alert['message']}")

    crypto_report = monitor.generate_monitoring_report('crypto')
    print(f"\nCrypto Report Summary:")
    print(f"  Alerts: {crypto_report['alert_count']}")
    if crypto_report['alerts']:
        for alert in crypto_report['alerts']:
            print(f"  - [{alert['severity']}] {alert['type']}: {alert['message']}")

    print("\n" + "=" * 80)
    print("MONITORING COMPLETE")
    print("=" * 80)
    print(f"Reports saved in: {METRICS_DIR}")
    print(f"Completed: {datetime.now()}")


if __name__ == "__main__":
    main()
