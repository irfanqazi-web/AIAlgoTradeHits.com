"""
Setup Cloud Schedulers for TwelveData Fetchers
Schedules data fetching for all 6 asset types at 4 timeframes
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import subprocess

PROJECT_ID = 'aialgotradehits'
REGION = 'us-central1'
FUNCTION_URL = f'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/twelvedata-fetcher'

# Scheduler configurations
SCHEDULERS = [
    # Weekly data - Sunday at midnight
    {
        'name': 'twelvedata-weekly-all',
        'schedule': '0 0 * * 0',
        'description': 'Fetch weekly data for all asset types',
        'params': 'asset_type=all&timeframe=weekly'
    },

    # Daily data - Every day at midnight ET
    {
        'name': 'twelvedata-daily-stocks',
        'schedule': '0 0 * * *',
        'description': 'Fetch daily stocks data',
        'params': 'asset_type=stocks&timeframe=daily'
    },
    {
        'name': 'twelvedata-daily-crypto',
        'schedule': '5 0 * * *',
        'description': 'Fetch daily crypto data',
        'params': 'asset_type=crypto&timeframe=daily'
    },
    {
        'name': 'twelvedata-daily-forex',
        'schedule': '10 0 * * *',
        'description': 'Fetch daily forex data',
        'params': 'asset_type=forex&timeframe=daily'
    },
    {
        'name': 'twelvedata-daily-etfs',
        'schedule': '15 0 * * *',
        'description': 'Fetch daily ETFs data',
        'params': 'asset_type=etfs&timeframe=daily'
    },
    {
        'name': 'twelvedata-daily-indices',
        'schedule': '20 0 * * *',
        'description': 'Fetch daily indices data',
        'params': 'asset_type=indices&timeframe=daily'
    },
    {
        'name': 'twelvedata-daily-commodities',
        'schedule': '25 0 * * *',
        'description': 'Fetch daily commodities data',
        'params': 'asset_type=commodities&timeframe=daily'
    },

    # Hourly data - Every hour for stocks and crypto only
    {
        'name': 'twelvedata-hourly-stocks',
        'schedule': '0 * * * *',
        'description': 'Fetch hourly stocks data',
        'params': 'asset_type=stocks&timeframe=hourly'
    },
    {
        'name': 'twelvedata-hourly-crypto',
        'schedule': '5 * * * *',
        'description': 'Fetch hourly crypto data',
        'params': 'asset_type=crypto&timeframe=hourly'
    },

    # 5-minute data - Every 5 minutes during market hours (9:30 AM - 4:00 PM ET)
    # For stocks only (crypto runs 24/7)
    {
        'name': 'twelvedata-5min-stocks',
        'schedule': '*/5 9-16 * * 1-5',
        'description': 'Fetch 5-minute stocks data during market hours',
        'params': 'asset_type=stocks&timeframe=5min'
    },
    {
        'name': 'twelvedata-5min-crypto',
        'schedule': '*/5 * * * *',
        'description': 'Fetch 5-minute crypto data (24/7)',
        'params': 'asset_type=crypto&timeframe=5min'
    },
]


def create_scheduler(scheduler):
    """Create a Cloud Scheduler job"""
    name = scheduler['name']
    schedule = scheduler['schedule']
    description = scheduler['description']
    params = scheduler['params']

    # Build the URL with query parameters
    url = f"{FUNCTION_URL}?{params}"

    # Build the gcloud command
    cmd = [
        'gcloud', 'scheduler', 'jobs', 'create', 'http',
        name,
        f'--location={REGION}',
        f'--schedule={schedule}',
        f'--uri={url}',
        '--http-method=GET',
        '--time-zone=America/New_York',
        f'--description={description}',
        f'--project={PROJECT_ID}',
        '--attempt-deadline=540s',
        '--quiet'
    ]

    print(f"\nCreating scheduler: {name}")
    print(f"  Schedule: {schedule}")
    print(f"  URL: {url}")

    try:
        # First try to delete if exists
        delete_cmd = [
            'gcloud', 'scheduler', 'jobs', 'delete', name,
            f'--location={REGION}',
            f'--project={PROJECT_ID}',
            '--quiet'
        ]
        subprocess.run(delete_cmd, capture_output=True)

        # Create the scheduler
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  Created {name}")
            return True
        else:
            print(f"  Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"  Exception: {e}")
        return False


def main():
    print("=" * 60)
    print("SETTING UP TWELVEDATA CLOUD SCHEDULERS")
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Function URL: {FUNCTION_URL}")
    print("=" * 60)

    success = 0
    failed = 0

    for scheduler in SCHEDULERS:
        if create_scheduler(scheduler):
            success += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"SCHEDULERS SETUP COMPLETE")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print("=" * 60)

    # List all schedulers
    print("\nListing all schedulers:")
    subprocess.run([
        'gcloud', 'scheduler', 'jobs', 'list',
        f'--location={REGION}',
        f'--project={PROJECT_ID}'
    ])


if __name__ == "__main__":
    main()
