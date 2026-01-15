"""
Setup Cloud Schedulers for cryptobot-462709 project
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

# Function URLs
DAILY_URL = 'https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app'
HOURLY_URL = 'https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app'


def create_daily_scheduler():
    """Create daily scheduler job"""
    print("\n" + "="*70)
    print("CREATING DAILY SCHEDULER")
    print("="*70)

    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"
    job_name = "daily-crypto-fetch-job"
    job_path = f"{parent}/jobs/{job_name}"

    job = scheduler_v1.Job(
        name=job_path,
        description="Daily cryptocurrency data fetch from Kraken Pro API",
        schedule="0 0 * * *",  # Midnight ET
        time_zone=TIMEZONE,
        http_target=scheduler_v1.HttpTarget(
            uri=DAILY_URL,
            http_method=scheduler_v1.HttpMethod.GET,
        ),
        attempt_deadline=duration_pb2.Duration(seconds=1200),  # 20 minutes
        retry_config=scheduler_v1.RetryConfig(
            retry_count=2,
            max_retry_duration=duration_pb2.Duration(seconds=1200),
        ),
    )

    try:
        client.create_job(parent=parent, job=job)
        print("✓ Daily scheduler created!")
    except Exception as e:
        if 'already exists' in str(e):
            client.update_job(job=job)
            print("✓ Daily scheduler updated!")
        else:
            raise e

    print(f"Schedule: Midnight ET (0 0 * * *)")
    print(f"URL: {DAILY_URL}")


def create_hourly_scheduler():
    """Create hourly scheduler job"""
    print("\n" + "="*70)
    print("CREATING HOURLY SCHEDULER")
    print("="*70)

    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"
    job_name = "hourly-crypto-fetch-job"
    job_path = f"{parent}/jobs/{job_name}"

    job = scheduler_v1.Job(
        name=job_path,
        description="Hourly cryptocurrency data fetch from Kraken Pro API",
        schedule="0 * * * *",  # Every hour
        time_zone=TIMEZONE,
        http_target=scheduler_v1.HttpTarget(
            uri=HOURLY_URL,
            http_method=scheduler_v1.HttpMethod.GET,
        ),
        attempt_deadline=duration_pb2.Duration(seconds=1200),  # 20 minutes
        retry_config=scheduler_v1.RetryConfig(
            retry_count=2,
            max_retry_duration=duration_pb2.Duration(seconds=1200),
        ),
    )

    try:
        client.create_job(parent=parent, job=job)
        print("✓ Hourly scheduler created!")
    except Exception as e:
        if 'already exists' in str(e):
            client.update_job(job=job)
            print("✓ Hourly scheduler updated!")
        else:
            raise e

    print(f"Schedule: Every hour (0 * * * *)")
    print(f"URL: {HOURLY_URL}")


def main():
    print("="*70)
    print("SETTING UP CLOUD SCHEDULERS FOR CRYPTOBOT-462709")
    print("="*70)

    create_daily_scheduler()
    create_hourly_scheduler()

    print("\n" + "="*70)
    print("✓ ALL SCHEDULERS SET UP!")
    print("="*70)
    print("\nScheduler Summary:")
    print("  1. Daily: Midnight ET (0 0 * * *)")
    print("  2. Hourly: Every hour (0 * * * *)")
    print("  3. 5-Minute: Every 5 minutes (*/5 * * * *) [Already created]")


if __name__ == "__main__":
    main()
