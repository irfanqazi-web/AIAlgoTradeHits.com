"""
Setup Automated Cloud Schedulers for TwelveData and Interest Rates
Configures all data collection jobs to run automatically
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import subprocess
import json

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
TIMEZONE = 'America/New_York'

# Function URLs
TWELVEDATA_URL = 'https://us-central1-cryptobot-462709.cloudfunctions.net/twelvedata-unified-fetcher'
INTEREST_RATES_URL = 'https://us-central1-cryptobot-462709.cloudfunctions.net/interest-rates-fetcher'

# Scheduler configurations
SCHEDULERS = [
    # Daily data fetches - Run at 6 AM ET (after market opens in Asia, before US market)
    {
        'name': 'twelvedata-stocks-daily',
        'schedule': '0 6 * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=stocks&timeframe=daily',
        'description': 'Fetch daily stock data from TwelveData'
    },
    {
        'name': 'twelvedata-crypto-daily',
        'schedule': '5 6 * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=crypto&timeframe=daily',
        'description': 'Fetch daily crypto data from TwelveData'
    },
    {
        'name': 'twelvedata-forex-daily',
        'schedule': '10 6 * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=forex&timeframe=daily',
        'description': 'Fetch daily forex data from TwelveData'
    },
    {
        'name': 'twelvedata-etfs-daily',
        'schedule': '15 6 * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=etfs&timeframe=daily',
        'description': 'Fetch daily ETF data from TwelveData'
    },
    {
        'name': 'twelvedata-indices-daily',
        'schedule': '20 6 * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=indices&timeframe=daily',
        'description': 'Fetch daily indices data from TwelveData'
    },
    {
        'name': 'twelvedata-commodities-daily',
        'schedule': '25 6 * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=commodities&timeframe=daily',
        'description': 'Fetch daily commodities data from TwelveData'
    },

    # Hourly data fetches - Run every hour at minute 30
    {
        'name': 'twelvedata-stocks-hourly',
        'schedule': '30 * * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=stocks&timeframe=hourly',
        'description': 'Fetch hourly stock data from TwelveData'
    },
    {
        'name': 'twelvedata-crypto-hourly',
        'schedule': '32 * * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=crypto&timeframe=hourly',
        'description': 'Fetch hourly crypto data from TwelveData'
    },
    {
        'name': 'twelvedata-forex-hourly',
        'schedule': '34 * * * *',
        'url': f'{TWELVEDATA_URL}?asset_type=forex&timeframe=hourly',
        'description': 'Fetch hourly forex data from TwelveData'
    },

    # Interest rates - Daily at 7 AM ET and hourly at minute 45
    {
        'name': 'interest-rates-daily',
        'schedule': '0 7 * * *',
        'url': f'{INTEREST_RATES_URL}?timeframe=daily',
        'description': 'Fetch G20 interest rates - daily'
    },
    {
        'name': 'interest-rates-hourly',
        'schedule': '45 * * * *',
        'url': f'{INTEREST_RATES_URL}?timeframe=hourly',
        'description': 'Fetch G20 interest rates - hourly'
    },

    # Weekly data - Run on Sundays at 8 AM ET
    {
        'name': 'twelvedata-all-weekly',
        'schedule': '0 8 * * 0',
        'url': f'{TWELVEDATA_URL}?asset_type=all&timeframe=weekly',
        'description': 'Fetch weekly data for all assets from TwelveData'
    },
]


def run_gcloud_command(cmd):
    """Run a gcloud command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)


def delete_scheduler_if_exists(name):
    """Delete existing scheduler job if it exists"""
    cmd = f'gcloud scheduler jobs delete {name} --location={REGION} --project={PROJECT_ID} --quiet 2>&1'
    success, stdout, stderr = run_gcloud_command(cmd)
    if success:
        print(f"  Deleted existing job: {name}")
    return success


def create_scheduler(config):
    """Create a Cloud Scheduler job"""
    name = config['name']
    schedule = config['schedule']
    url = config['url']
    description = config.get('description', '')

    # Delete if exists
    delete_scheduler_if_exists(name)

    # Create new scheduler
    cmd = f'''gcloud scheduler jobs create http {name} \
        --location={REGION} \
        --project={PROJECT_ID} \
        --schedule="{schedule}" \
        --uri="{url}" \
        --http-method=GET \
        --time-zone="{TIMEZONE}" \
        --description="{description}" \
        --attempt-deadline=540s \
        --quiet 2>&1'''

    success, stdout, stderr = run_gcloud_command(cmd)

    if success or 'already exists' in stderr.lower():
        print(f"  Created: {name} | Schedule: {schedule}")
        return True
    else:
        print(f"  FAILED: {name} | Error: {stderr}")
        return False


def main():
    print("=" * 70)
    print("Setting Up Automated Cloud Schedulers")
    print("=" * 70)
    print(f"\nProject: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Timezone: {TIMEZONE}")
    print(f"\nTotal schedulers to create: {len(SCHEDULERS)}")
    print("-" * 70)

    success_count = 0
    fail_count = 0

    for config in SCHEDULERS:
        result = create_scheduler(config)
        if result:
            success_count += 1
        else:
            fail_count += 1

    print("-" * 70)
    print(f"\nResults: {success_count} successful, {fail_count} failed")

    # List all schedulers
    print("\n" + "=" * 70)
    print("Current Cloud Scheduler Jobs:")
    print("=" * 70)
    cmd = f'gcloud scheduler jobs list --location={REGION} --project={PROJECT_ID} --format="table(name,schedule,state,httpTarget.uri)" 2>&1'
    success, stdout, stderr = run_gcloud_command(cmd)
    if success:
        print(stdout)
    else:
        print(f"Error listing jobs: {stderr}")

    print("\n" + "=" * 70)
    print("Scheduler Setup Complete!")
    print("=" * 70)
    print("\nSchedule Summary:")
    print("  - Daily data: 6:00-6:25 AM ET (all 6 asset types)")
    print("  - Hourly data: :30-:34 past each hour (stocks, crypto, forex)")
    print("  - Interest rates: Daily 7 AM + Hourly :45")
    print("  - Weekly data: Sundays 8 AM ET (all assets)")
    print("\nData will be automatically collected and never stopped.")


if __name__ == "__main__":
    main()
