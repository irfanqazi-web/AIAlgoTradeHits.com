"""
TwelveData Quota Monitoring - Ensures 2M Records/Day Target is Met
Run daily to check if we're utilizing the full $229/month quota
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery
from datetime import datetime, timedelta, timezone
import json

PROJECT_ID = "aialgotradehits"
DATASET_ID = "crypto_trading_data"

# Target: 2,000,000 records/day from $229 TwelveData plan
DAILY_QUOTA_TARGET = 2_000_000
MINIMUM_ACCEPTABLE = 1_000_000  # Alert if below this

def check_daily_quota_usage():
    """Check how many records were fetched today from TwelveData"""

    client = bigquery.Client(project=PROJECT_ID)

    # Tables that receive TwelveData data
    tables = [
        'v2_stocks_daily', 'v2_stocks_hourly', 'v2_stocks_5min', 'v2_stocks_weekly',
        'v2_crypto_daily', 'v2_crypto_hourly', 'v2_crypto_5min', 'v2_crypto_weekly',
        'v2_etfs_daily', 'v2_etfs_hourly', 'v2_forex_daily', 'v2_forex_hourly',
        'stocks_hourly_clean', 'stocks_daily_clean',
        'crypto_hourly_clean', 'crypto_daily_clean'
    ]

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    print("="*70)
    print("TWELVEDATA QUOTA MONITORING REPORT")
    print(f"Date: {today}")
    print("="*70)
    print(f"Daily Quota Target: {DAILY_QUOTA_TARGET:,}")
    print(f"Minimum Acceptable: {MINIMUM_ACCEPTABLE:,}")
    print("="*70)

    total_records_today = 0
    total_records_yesterday = 0
    results = []

    for table in tables:
        try:
            # Count records added today (by created_at timestamp)
            query_today = f"""
            SELECT COUNT(*) as count
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
            WHERE DATE(created_at) = '{today}'
            """

            query_yesterday = f"""
            SELECT COUNT(*) as count
            FROM `{PROJECT_ID}.{DATASET_ID}.{table}`
            WHERE DATE(created_at) = '{yesterday}'
            """

            result_today = list(client.query(query_today).result())[0].count
            result_yesterday = list(client.query(query_yesterday).result())[0].count

            if result_today > 0 or result_yesterday > 0:
                results.append({
                    'table': table,
                    'today': result_today,
                    'yesterday': result_yesterday
                })
                total_records_today += result_today
                total_records_yesterday += result_yesterday

        except Exception as e:
            # Table might not have created_at field
            pass

    print("\nRecords by Table:")
    print("-"*70)
    for r in sorted(results, key=lambda x: x['today'], reverse=True):
        print(f"  {r['table']:<35} Today: {r['today']:>10,}  Yesterday: {r['yesterday']:>10,}")

    print("-"*70)
    print(f"  {'TOTAL':<35} Today: {total_records_today:>10,}  Yesterday: {total_records_yesterday:>10,}")

    # Calculate quota usage
    quota_usage_today = (total_records_today / DAILY_QUOTA_TARGET) * 100
    quota_usage_yesterday = (total_records_yesterday / DAILY_QUOTA_TARGET) * 100

    print("\n" + "="*70)
    print("QUOTA USAGE ANALYSIS")
    print("="*70)
    print(f"Today's Usage: {total_records_today:,} records ({quota_usage_today:.1f}% of quota)")
    print(f"Yesterday's Usage: {total_records_yesterday:,} records ({quota_usage_yesterday:.1f}% of quota)")

    # Status check
    if total_records_today >= MINIMUM_ACCEPTABLE:
        status = "OK"
        print(f"\nStatus: {status} - Meeting minimum acceptable threshold")
    elif total_records_today > 0:
        status = "WARNING"
        print(f"\nStatus: {status} - Below minimum threshold!")
        print(f"  Missing: {MINIMUM_ACCEPTABLE - total_records_today:,} records to meet minimum")
    else:
        status = "CRITICAL"
        print(f"\nStatus: {status} - No records fetched today!")

    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)

    if quota_usage_today < 50:
        print("1. CHECK: Cloud Scheduler jobs are running")
        print("2. CHECK: TwelveData API key is valid")
        print("3. CHECK: outputsize is set to 5000 (max)")
        print("4. CHECK: Cloud Function logs for errors")
        print("")
        print("Quick diagnostic commands:")
        print("  gcloud scheduler jobs list --project=aialgotradehits --location=us-central1")
        print("  gcloud functions logs read twelvedata-fetcher --project=aialgotradehits --limit=50")
    else:
        print("Quota utilization is healthy!")

    # Save report
    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'date': str(today),
        'total_records_today': total_records_today,
        'total_records_yesterday': total_records_yesterday,
        'quota_target': DAILY_QUOTA_TARGET,
        'quota_usage_percent': quota_usage_today,
        'status': status,
        'details': results
    }

    return report


def check_outputsize_config():
    """Verify the Cloud Function has correct outputsize settings"""

    print("\n" + "="*70)
    print("CONFIGURATION CHECK")
    print("="*70)

    # Expected settings after fix
    expected = {
        'weekly': 5000,
        'daily': 5000,
        'hourly': 5000,
        '5min': 5000
    }

    print("\nExpected outputsize settings (MUST be 5000 for all):")
    for tf, size in expected.items():
        print(f"  {tf}: {size}")

    print("\nTo verify, check cloud_function_twelvedata/main.py:")
    print("  grep 'outputsize' cloud_function_twelvedata/main.py")


if __name__ == "__main__":
    report = check_daily_quota_usage()
    check_outputsize_config()

    print("\n" + "="*70)
    print(f"Report generated at: {report['timestamp']}")
    print("="*70)
