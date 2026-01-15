"""
Set up Cloud Schedulers for Stock Data Collection
Creates hourly and 5-minute schedulers for stock data fetchers
"""

import subprocess
import sys

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
TIMEZONE = 'America/New_York'

# Function URLs (will be set after deployment)
HOURLY_FUNCTION_URL = f'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/stock-hourly-fetcher'
FIVEMIN_FUNCTION_URL = f'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/stock-5min-fetcher'


def create_scheduler(job_name, schedule, function_url, description):
    """Create a Cloud Scheduler job"""

    print(f"\n{'='*70}")
    print(f"Creating scheduler: {job_name}")
    print(f"{'='*70}")
    print(f"Schedule: {schedule}")
    print(f"URL: {function_url}")
    print(f"Description: {description}")

    # Check if job already exists
    check_cmd = [
        'gcloud', 'scheduler', 'jobs', 'describe', job_name,
        '--location', REGION,
        '--project', PROJECT_ID
    ]

    try:
        subprocess.run(check_cmd, check=True, capture_output=True)
        print(f"⚠ Job {job_name} already exists. Updating...")

        # Update existing job
        update_cmd = [
            'gcloud', 'scheduler', 'jobs', 'update', 'http', job_name,
            '--location', REGION,
            '--schedule', schedule,
            '--uri', function_url,
            '--http-method', 'GET',
            '--time-zone', TIMEZONE,
            '--project', PROJECT_ID
        ]

        subprocess.run(update_cmd, check=True)
        print(f"✓ Updated scheduler: {job_name}")
        return True

    except subprocess.CalledProcessError:
        # Job doesn't exist, create it
        print(f"Creating new scheduler job...")

        create_cmd = [
            'gcloud', 'scheduler', 'jobs', 'create', 'http', job_name,
            '--location', REGION,
            '--schedule', schedule,
            '--uri', function_url,
            '--http-method', 'GET',
            '--time-zone', TIMEZONE,
            '--description', description,
            '--project', PROJECT_ID
        ]

        try:
            subprocess.run(create_cmd, check=True)
            print(f"✓ Created scheduler: {job_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create scheduler: {e}")
            return False


def main():
    """Set up all stock schedulers"""

    print("=" * 70)
    print("STOCK DATA COLLECTION - CLOUD SCHEDULER SETUP")
    print("=" * 70)
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Timezone: {TIMEZONE}")
    print("=" * 70)

    success_count = 0

    # 1. Stock Hourly Scheduler
    if create_scheduler(
        job_name='stock-hourly-fetch-job',
        schedule='0 * * * *',  # Every hour at minute 0
        function_url=HOURLY_FUNCTION_URL,
        description='Fetch hourly stock data with technical indicators'
    ):
        success_count += 1

    # 2. Stock 5-Minute Scheduler
    if create_scheduler(
        job_name='stock-5min-fetch-job',
        schedule='*/5 * * * *',  # Every 5 minutes
        function_url=FIVEMIN_FUNCTION_URL,
        description='Fetch 5-minute data for top 10 stock gainers'
    ):
        success_count += 1

    print("\n" + "=" * 70)
    print("SCHEDULER SETUP COMPLETE")
    print("=" * 70)
    print(f"✓ Created/Updated: {success_count}/2 schedulers")

    if success_count == 2:
        print("\n📅 Scheduler Summary:")
        print("  1. stock-hourly-fetch-job  - Runs every hour")
        print("  2. stock-5min-fetch-job    - Runs every 5 minutes")
        print("\n⏰ Both schedulers use America/New_York timezone")
        print("   (Stock market hours: 9:30 AM - 4:00 PM ET)")

        print("\n🔧 Management Commands:")
        print(f"  List all jobs:")
        print(f"    gcloud scheduler jobs list --location={REGION} --project={PROJECT_ID}")
        print(f"\n  Manually trigger hourly job:")
        print(f"    gcloud scheduler jobs run stock-hourly-fetch-job --location={REGION} --project={PROJECT_ID}")
        print(f"\n  Manually trigger 5-min job:")
        print(f"    gcloud scheduler jobs run stock-5min-fetch-job --location={REGION} --project={PROJECT_ID}")
        print(f"\n  Pause a job:")
        print(f"    gcloud scheduler jobs pause stock-hourly-fetch-job --location={REGION} --project={PROJECT_ID}")
        print(f"\n  Resume a job:")
        print(f"    gcloud scheduler jobs resume stock-hourly-fetch-job --location={REGION} --project={PROJECT_ID}")

        print("\n" + "=" * 70)
        print("✓ ALL SCHEDULERS SET UP SUCCESSFULLY!")
        print("=" * 70)
    else:
        print("\n✗ Some schedulers failed to set up")

    print()


if __name__ == "__main__":
    main()
