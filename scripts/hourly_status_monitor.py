#!/usr/bin/env python3
"""
Hourly Status Monitor for Stock Data Backfill
Reports daily stock record counts and backfill progress
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
from datetime import datetime
from google.cloud import bigquery

# Configuration
PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'crypto_trading_data'
PROGRESS_FILE = 'index_backfill_progress.json'
STATUS_FILE = 'hourly_status_report.txt'

client = bigquery.Client(project=PROJECT_ID)


def get_daily_stock_stats():
    """Get current daily stock data statistics"""
    query = f"""
    SELECT
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as unique_symbols,
        CAST(MIN(datetime) AS DATE) as earliest_date,
        CAST(MAX(datetime) AS DATE) as latest_date
    FROM `{PROJECT_ID}.{DATASET_ID}.stocks_daily_clean`
    """
    result = list(client.query(query).result())[0]
    return {
        'total_records': result.total_records,
        'unique_symbols': result.unique_symbols,
        'earliest_date': str(result.earliest_date),
        'latest_date': str(result.latest_date)
    }


def get_backfill_progress():
    """Get backfill progress from JSON file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return None


def generate_status_report():
    """Generate comprehensive status report"""
    now = datetime.now()

    # Get BigQuery stats
    print("Fetching BigQuery statistics...")
    bq_stats = get_daily_stock_stats()

    # Get backfill progress
    progress = get_backfill_progress()

    report = f"""
================================================================================
HOURLY STATUS REPORT - {now.strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

BIGQUERY DATA STATUS (stocks_daily_clean)
-----------------------------------------
Total Records:    {bq_stats['total_records']:,}
Unique Symbols:   {bq_stats['unique_symbols']}
Date Range:       {bq_stats['earliest_date']} to {bq_stats['latest_date']}

"""

    if progress:
        completed = len(progress.get('completed', []))
        failed = len(progress.get('failed', []))
        total = completed + failed + len([s for s in progress.get('completed', []) if s not in progress.get('completed', [])])
        total_records = progress.get('total_records', 0)

        # Calculate rate if start time available
        if progress.get('start_time'):
            start = datetime.fromisoformat(progress['start_time'])
            elapsed_hours = (now - start).total_seconds() / 3600
            rate = completed / elapsed_hours if elapsed_hours > 0 else 0
            eta = (647 - completed) / rate if rate > 0 else 0
        else:
            elapsed_hours = 0
            rate = 0
            eta = 0

        report += f"""BACKFILL PROGRESS
-----------------
Completed:        {completed}/647 symbols ({completed/647*100:.1f}%)
Failed:           {failed}
Records Added:    {total_records:,}
Elapsed Time:     {elapsed_hours:.2f} hours
Rate:             {rate:.1f} symbols/hour
ETA:              {eta:.1f} hours remaining

Last Completed:   {', '.join(progress.get('completed', [])[-5:])}
"""
        if failed > 0:
            report += f"Failed Symbols:   {', '.join(progress.get('failed', [])[:10])}\n"
    else:
        report += """BACKFILL PROGRESS
-----------------
No backfill progress file found.
"""

    report += """
================================================================================
TwelveData $229 Plan Optimization:
- 1,597 API credits/minute
- Time series = 1 credit per symbol
- Current rate optimizes API usage while ensuring data quality
================================================================================
"""

    print(report)

    # Save to file
    with open(STATUS_FILE, 'w') as f:
        f.write(report)

    print(f"Report saved to {STATUS_FILE}")
    return report


if __name__ == "__main__":
    generate_status_report()
