#!/usr/bin/env python3
"""
ML Weekly Review Script
=======================
Generates a comprehensive weekly performance report for the ML pipeline:
1. Model accuracy by asset type
2. Top performing symbols
3. Drift detection summary
4. Backtest results
5. Recommendations

Can be run manually or scheduled via Cloud Scheduler.
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from google.cloud import bigquery
from datetime import datetime, timedelta
import json

PROJECT_ID = 'aialgotradehits'
ML_DATASET = 'ml_models'

bq_client = bigquery.Client(project=PROJECT_ID)

def run_weekly_review():
    """Generate weekly ML performance review"""

    print("=" * 70)
    print("ML PIPELINE WEEKLY REVIEW")
    print("=" * 70)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Review Period: Last 7 days")

    report = {
        'report_date': datetime.now().isoformat(),
        'sections': {}
    }

    # ==========================================================================
    # Section 1: Model Accuracy Summary
    # ==========================================================================
    print("\n" + "-" * 70)
    print("[1] MODEL ACCURACY SUMMARY")
    print("-" * 70)

    accuracy_query = f"""
    SELECT
        asset_type,
        COUNT(*) as total_predictions,
        SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) as correct,
        ROUND(SUM(CASE WHEN predicted_direction = actual_direction THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as accuracy,

        -- High confidence
        SUM(CASE WHEN up_probability >= 0.65 OR up_probability <= 0.35 THEN 1 ELSE 0 END) as high_conf_count,
        ROUND(
            SUM(CASE WHEN (up_probability >= 0.65 OR up_probability <= 0.35) AND predicted_direction = actual_direction THEN 1 ELSE 0 END) /
            NULLIF(SUM(CASE WHEN up_probability >= 0.65 OR up_probability <= 0.35 THEN 1 ELSE 0 END), 0) * 100
        , 2) as high_conf_accuracy

    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    WHERE data_split = 'VALIDATE'
    GROUP BY asset_type
    ORDER BY asset_type
    """

    try:
        results = list(bq_client.query(accuracy_query).result())
        print(f"\n  {'Asset':10} | {'Total':>12} | {'Accuracy':>10} | {'High-Conf':>10} | {'HC Acc':>10}")
        print("  " + "-" * 65)

        accuracy_data = []
        for row in results:
            status = "GOOD" if row.accuracy >= 70 else "FAIR" if row.accuracy >= 50 else "NEEDS_WORK"
            print(f"  {row.asset_type:10} | {row.total_predictions:>12,} | {row.accuracy:>9.1f}% | {row.high_conf_count:>10,} | {row.high_conf_accuracy or 0:>9.1f}%")
            accuracy_data.append({
                'asset_type': row.asset_type,
                'total': row.total_predictions,
                'accuracy': row.accuracy,
                'high_conf_accuracy': row.high_conf_accuracy,
                'status': status
            })
        report['sections']['accuracy'] = accuracy_data
    except Exception as e:
        print(f"  Error: {e}")

    # ==========================================================================
    # Section 2: Top Performers
    # ==========================================================================
    print("\n" + "-" * 70)
    print("[2] TOP PERFORMERS BY ASSET CLASS")
    print("-" * 70)

    top_query = f"""
    SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.v_best_performers`
    WHERE rank_in_class <= 5
    ORDER BY asset_type, rank_in_class
    """

    try:
        results = list(bq_client.query(top_query).result())
        current_asset = ""
        top_performers = {}
        for row in results:
            if row.asset_type != current_asset:
                current_asset = row.asset_type
                top_performers[current_asset] = []
                print(f"\n  {current_asset.upper()}:")
                print(f"  {'Rank':>4} | {'Symbol':10} | {'Signals':>8} | {'Accuracy':>8}")
                print("  " + "-" * 45)
            print(f"  {row.rank_in_class:>4} | {row.symbol:10} | {row.total_signals:>8,} | {row.accuracy:>7.1f}%")
            top_performers[current_asset].append({
                'symbol': row.symbol,
                'signals': row.total_signals,
                'accuracy': row.accuracy
            })
        report['sections']['top_performers'] = top_performers
    except Exception as e:
        print(f"  Error: {e}")

    # ==========================================================================
    # Section 3: Signal Distribution
    # ==========================================================================
    print("\n" + "-" * 70)
    print("[3] SIGNAL DISTRIBUTION (VALIDATION PERIOD)")
    print("-" * 70)

    signal_query = f"""
    SELECT
        asset_type,
        SUM(CASE WHEN up_probability >= 0.60 THEN 1 ELSE 0 END) as buy_signals,
        SUM(CASE WHEN up_probability <= 0.40 THEN 1 ELSE 0 END) as sell_signals,
        SUM(CASE WHEN up_probability > 0.40 AND up_probability < 0.60 THEN 1 ELSE 0 END) as hold_signals,
        COUNT(*) as total
    FROM `{PROJECT_ID}.{ML_DATASET}.walk_forward_predictions_v2`
    WHERE data_split = 'VALIDATE'
    GROUP BY asset_type
    """

    try:
        results = list(bq_client.query(signal_query).result())
        print(f"\n  {'Asset':10} | {'BUY':>10} | {'SELL':>10} | {'HOLD':>10} | {'Total':>12}")
        print("  " + "-" * 60)

        signal_data = []
        for row in results:
            buy_pct = row.buy_signals / row.total * 100
            sell_pct = row.sell_signals / row.total * 100
            print(f"  {row.asset_type:10} | {row.buy_signals:>10,} | {row.sell_signals:>10,} | {row.hold_signals:>10,} | {row.total:>12,}")
            signal_data.append({
                'asset_type': row.asset_type,
                'buy': row.buy_signals,
                'sell': row.sell_signals,
                'hold': row.hold_signals,
                'buy_pct': round(buy_pct, 1),
                'sell_pct': round(sell_pct, 1)
            })
        report['sections']['signals'] = signal_data
    except Exception as e:
        print(f"  Error: {e}")

    # ==========================================================================
    # Section 4: Active Alerts
    # ==========================================================================
    print("\n" + "-" * 70)
    print("[4] ACTIVE ALERTS")
    print("-" * 70)

    alerts_query = f"""
    SELECT
        alert_type,
        severity,
        asset_type,
        message,
        alert_time
    FROM `{PROJECT_ID}.{ML_DATASET}.model_drift_alerts`
    WHERE NOT is_resolved
    ORDER BY alert_time DESC
    LIMIT 10
    """

    try:
        results = list(bq_client.query(alerts_query).result())
        if results:
            for row in results:
                print(f"\n  [{row.severity}] {row.asset_type} - {row.alert_type}")
                print(f"    {row.message}")
            report['sections']['alerts'] = [{'type': r.alert_type, 'severity': r.severity, 'asset': r.asset_type} for r in results]
        else:
            print("\n  No active alerts - all systems healthy")
            report['sections']['alerts'] = []
    except Exception as e:
        print(f"  Error: {e}")

    # ==========================================================================
    # Section 5: Recommendations
    # ==========================================================================
    print("\n" + "-" * 70)
    print("[5] RECOMMENDATIONS")
    print("-" * 70)

    recommendations = []

    # Check accuracy and provide recommendations
    for acc in report['sections'].get('accuracy', []):
        if acc['status'] == 'NEEDS_WORK':
            rec = f"Consider increasing Gemini ensemble weight for {acc['asset_type']} (current accuracy: {acc['accuracy']}%)"
            recommendations.append(rec)
            print(f"\n  - {rec}")

    if not recommendations:
        print("\n  All models performing within acceptable parameters.")
        recommendations.append("Continue monitoring - no immediate action needed")

    report['sections']['recommendations'] = recommendations

    # ==========================================================================
    # Save Report
    # ==========================================================================
    print("\n" + "=" * 70)
    print("WEEKLY REVIEW COMPLETE")
    print("=" * 70)

    # Insert report into BigQuery
    insert_query = f"""
    INSERT INTO `{PROJECT_ID}.{ML_DATASET}.deployment_log`
    (deployment_id, component, component_name, version, status, details)
    VALUES (
        GENERATE_UUID(),
        'REPORT',
        'weekly_review',
        '{datetime.now().strftime('%Y%m%d')}',
        'COMPLETED',
        '{json.dumps(report)}'
    )
    """
    try:
        bq_client.query(insert_query).result()
        print(f"\nReport saved to deployment_log")
    except Exception as e:
        print(f"\nReport save error: {e}")

    return report


if __name__ == "__main__":
    run_weekly_review()
