#!/usr/bin/env python3
"""
Setup Weekly Capacity Scheduler
================================
Creates Cloud Scheduler jobs for weekly capacity increases

Schedule:
- Week 1 (Dec 17, 2025): 50% capacity
- Week 2 (Dec 24, 2025): 60% capacity
- Week 3 (Dec 31, 2025): 70% capacity
- Week 4 (Jan 7, 2026): 80% capacity
- Week 5 (Jan 14, 2026): 90% capacity

The scheduler runs every Sunday at midnight to fetch data
at the appropriate capacity level.
"""

import subprocess
import sys

PROJECT_ID = "aialgotradehits"
REGION = "us-central1"

# Capacity schedule
CAPACITY_SCHEDULE = """
================================================================================
TWELVEDATA CAPACITY INCREASE SCHEDULE
================================================================================

Week 1 (Dec 17, 2025): 50% = 576,000 credits/day
  - S&P 500 Top 50 stocks
  - Top 20 ETFs
  - 5 years daily data
  - Basic fundamentals (earnings, dividends)

Week 2 (Dec 24, 2025): 60% = 691,200 credits/day
  - S&P 500 Top 150 stocks (+100)
  - Top 40 ETFs (+20)
  - Extended fundamentals (statistics, profile)

Week 3 (Dec 31, 2025): 70% = 806,400 credits/day
  - Full S&P 500 (500 stocks)
  - Top 60 ETFs (+20)
  - Financial statements (balance sheet, income)

Week 4 (Jan 7, 2026): 80% = 921,600 credits/day
  - S&P 500 + additional stocks (600 total)
  - Full 100 ETFs
  - Hourly data for top 100

Week 5 (Jan 14, 2026): 90% = 1,036,800 credits/day
  - All available stocks (800+)
  - All ETFs + International
  - 5-minute data for top 50
  - Full fundamentals suite

================================================================================
"""

def run_command(cmd):
    """Run a gcloud command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  Success")
        return True
    else:
        print(f"  Error: {result.stderr}")
        return False


def deploy_weekly_function():
    """Deploy the weekly capacity function"""
    print("\n--- Deploying Weekly Capacity Function ---")

    cmd = f"""gcloud functions deploy weekly-capacity-fetch \
        --gen2 \
        --runtime=python311 \
        --region={REGION} \
        --source=cloud_function_weekly_capacity \
        --entry-point=weekly_capacity_fetch \
        --trigger-http \
        --allow-unauthenticated \
        --memory=1024MB \
        --timeout=540s \
        --project={PROJECT_ID}"""

    return run_command(cmd)


def create_weekly_scheduler():
    """Create the weekly scheduler job"""
    print("\n--- Creating Weekly Scheduler ---")

    # Get function URL
    get_url_cmd = f"gcloud functions describe weekly-capacity-fetch --region={REGION} --project={PROJECT_ID} --format='value(url)'"
    result = subprocess.run(get_url_cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print("Could not get function URL")
        function_url = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/weekly-capacity-fetch"
    else:
        function_url = result.stdout.strip()

    print(f"Function URL: {function_url}")

    # Delete existing scheduler if exists
    delete_cmd = f"gcloud scheduler jobs delete weekly-capacity-increase --location={REGION} --project={PROJECT_ID} --quiet 2>nul"
    subprocess.run(delete_cmd, shell=True, capture_output=True)

    # Create scheduler - runs every Sunday at midnight EST
    create_cmd = f"""gcloud scheduler jobs create http weekly-capacity-increase \
        --location={REGION} \
        --project={PROJECT_ID} \
        --schedule="0 0 * * 0" \
        --time-zone="America/New_York" \
        --uri="{function_url}" \
        --http-method=GET \
        --description="Weekly capacity increase for TwelveData fetching" """

    return run_command(create_cmd)


def create_capacity_tracking_table():
    """Create BigQuery table for tracking capacity usage"""
    print("\n--- Creating Capacity Tracking Table ---")

    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID)

    schema = [
        bigquery.SchemaField("week", "INT64"),
        bigquery.SchemaField("capacity_percent", "INT64"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("stocks_count", "INT64"),
        bigquery.SchemaField("etfs_count", "INT64"),
        bigquery.SchemaField("records_fetched", "INT64"),
        bigquery.SchemaField("api_calls_made", "INT64"),
        bigquery.SchemaField("errors_count", "INT64"),
        bigquery.SchemaField("status", "STRING"),
    ]

    table_id = f"{PROJECT_ID}.crypto_trading_data.capacity_tracking"

    try:
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)
        print(f"  Created table: {table_id}")
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  Table already exists: {table_id}")
        else:
            print(f"  Error: {e}")


def main():
    print(CAPACITY_SCHEDULE)

    print("="*60)
    print("SETTING UP WEEKLY CAPACITY SCHEDULER")
    print("="*60)

    # Create tracking table
    create_capacity_tracking_table()

    # Deploy function
    if deploy_weekly_function():
        # Create scheduler
        create_weekly_scheduler()

    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    print("""
Next Steps:
1. The comprehensive_50pct_fetcher.py is running now (Week 1 - 50%)
2. Cloud Scheduler will trigger weekly increases automatically
3. Monitor progress in BigQuery: capacity_tracking table
4. Use /ml-test-data in the app to download ML datasets

To manually trigger next week's capacity:
  gcloud scheduler jobs run weekly-capacity-increase --location=us-central1

To check scheduler status:
  gcloud scheduler jobs list --location=us-central1 --project=aialgotradehits
""")


if __name__ == "__main__":
    main()
