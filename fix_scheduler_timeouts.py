"""
Fix Cloud Scheduler timeouts to match Cloud Function timeouts
This prevents DEADLINE_EXCEEDED errors
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import scheduler_v1
from google.protobuf import duration_pb2

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
TIMEZONE = 'America/New_York'

# Function URLs (from deployment)
DAILY_URL = 'https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app'
HOURLY_URL = 'https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app'
FIVEMIN_URL = 'https://fivemin-top10-fetcher-cnyn5l4u2a-uc.a.run.app'

def update_scheduler(job_name, schedule, url, timeout_seconds, description):
    """Update a Cloud Scheduler job with new timeout"""
    print(f"\n{'='*70}")
    print(f"Updating: {job_name}")
    print('='*70)

    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"
    job_path = f"{parent}/jobs/{job_name}"

    job = scheduler_v1.Job(
        name=job_path,
        description=description,
        schedule=schedule,
        time_zone=TIMEZONE,
        http_target=scheduler_v1.HttpTarget(
            uri=url,
            http_method=scheduler_v1.HttpMethod.GET,
        ),
        attempt_deadline=duration_pb2.Duration(seconds=timeout_seconds),
        retry_config=scheduler_v1.RetryConfig(
            retry_count=2,
            max_retry_duration=duration_pb2.Duration(seconds=timeout_seconds),
        ),
    )

    try:
        client.update_job(job=job)
        print(f"✓ Updated successfully!")
        print(f"  Schedule: {schedule}")
        print(f"  Timeout: {timeout_seconds}s ({timeout_seconds//60} minutes)")
        print(f"  URL: {url}")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


def main():
    print("="*70)
    print("FIXING CLOUD SCHEDULER TIMEOUTS")
    print("="*70)
    print("\nThis will update all schedulers to prevent timeout errors")
    print()

    try:
        # Daily scheduler - 20 minutes
        update_scheduler(
            job_name='daily-crypto-fetch-job',
            schedule='0 0 * * *',  # Midnight ET
            url=DAILY_URL,
            timeout_seconds=1200,  # 20 minutes
            description='Daily cryptocurrency data fetch from Kraken Pro API'
        )

        # Hourly scheduler - 20 minutes
        update_scheduler(
            job_name='hourly-crypto-fetch-job',
            schedule='0 * * * *',  # Every hour
            url=HOURLY_URL,
            timeout_seconds=1200,  # 20 minutes
            description='Hourly cryptocurrency data fetch from Kraken Pro API'
        )

        # 5-minute scheduler - 10 minutes
        update_scheduler(
            job_name='fivemin-top10-fetch-job',
            schedule='*/5 * * * *',  # Every 5 minutes
            url=FIVEMIN_URL,
            timeout_seconds=600,  # 10 minutes
            description='5-minute OHLC data for top 10 hourly gainers'
        )

        print("\n" + "="*70)
        print("✓ ALL SCHEDULERS UPDATED SUCCESSFULLY!")
        print("="*70)
        print("\nTimeout Summary:")
        print("  Daily Function:   1200s (20 minutes)")
        print("  Hourly Function:  1200s (20 minutes)")
        print("  5-Minute Function: 600s (10 minutes)")
        print("\nThese timeouts allow functions to complete without errors.")

    except Exception as e:
        print(f"\n✗ Failed to update schedulers: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
