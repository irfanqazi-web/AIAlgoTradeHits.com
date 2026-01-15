"""
Setup Cloud Scheduler using Google Cloud API
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import scheduler_v1
from google.protobuf import duration_pb2
import os

PROJECT_ID = 'molten-optics-310919'
LOCATION = 'us-central1'
JOB_NAME = 'daily-crypto-fetch-job'
SCHEDULE = '0 0 * * *'  # Midnight daily
TIMEZONE = 'America/New_York'

def create_scheduler_job():
    """Create Cloud Scheduler job"""

    # Read function URL from file
    url_file = 'function_url.txt'
    if not os.path.exists(url_file):
        print(f"✗ Error: {url_file} not found!")
        print("Please deploy the Cloud Function first.")
        return

    with open(url_file, 'r') as f:
        function_url = f.read().strip()

    print("="*70)
    print("SETTING UP CLOUD SCHEDULER")
    print("="*70)
    print(f"\nFunction URL: {function_url}")
    print(f"Schedule: {SCHEDULE} ({TIMEZONE})")
    print()

    # Initialize scheduler client
    client = scheduler_v1.CloudSchedulerClient()

    # Define job path
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    job_path = f"{parent}/jobs/{JOB_NAME}"

    # Create HTTP target
    http_target = scheduler_v1.HttpTarget(
        uri=function_url,
        http_method=scheduler_v1.HttpMethod.GET,
    )

    # Create retry config
    retry_config = scheduler_v1.RetryConfig(
        retry_count=3,
        max_retry_duration=duration_pb2.Duration(seconds=600),
        min_backoff_duration=duration_pb2.Duration(seconds=5),
        max_backoff_duration=duration_pb2.Duration(seconds=300),
    )

    # Create job
    job = scheduler_v1.Job(
        name=job_path,
        description="Daily cryptocurrency data fetch from Kraken Pro API",
        schedule=SCHEDULE,
        time_zone=TIMEZONE,
        http_target=http_target,
        retry_config=retry_config,
    )

    try:
        # Try to create new job
        print("Creating scheduler job...")
        response = client.create_job(
            parent=parent,
            job=job
        )
        print("\n✓ Scheduler job created successfully!")

    except Exception as e:
        if 'already exists' in str(e):
            print("Job already exists, updating...")
            # Update existing job
            response = client.update_job(job=job)
            print("\n✓ Scheduler job updated successfully!")
        else:
            raise e

    print("\n" + "="*70)
    print("✓ CLOUD SCHEDULER CONFIGURED")
    print("="*70)
    print(f"\nJob Name: {JOB_NAME}")
    print(f"Schedule: {SCHEDULE}")
    print(f"Next run: Daily at midnight {TIMEZONE}")
    print(f"Function URL: {function_url}")
    print("\nTo manually test:")
    print(f"  gcloud scheduler jobs run {JOB_NAME} --location={LOCATION}")
    print("\nOr via API:")
    print(f"  Visit: https://console.cloud.google.com/cloudscheduler?project={PROJECT_ID}")
    print("="*70)

    return response

def main():
    try:
        result = create_scheduler_job()
        print("\n✓ Setup complete!")
        print("\nYour daily crypto data fetcher is now active!")
        print("It will run automatically every night at midnight Eastern Time.")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
