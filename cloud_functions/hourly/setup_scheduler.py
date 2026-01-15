"""
Setup hourly Cloud Scheduler
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
JOB_NAME = 'hourly-crypto-fetch-job'
SCHEDULE = '0 * * * *'  # Every hour
TIMEZONE = 'America/New_York'

def create_scheduler_job():
    url_file = 'function_url.txt'
    with open(url_file, 'r') as f:
        function_url = f.read().strip()

    print(f"Setting up hourly scheduler for: {function_url}")

    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    job_path = f"{parent}/jobs/{JOB_NAME}"

    http_target = scheduler_v1.HttpTarget(
        uri=function_url,
        http_method=scheduler_v1.HttpMethod.GET,
    )

    retry_config = scheduler_v1.RetryConfig(
        retry_count=3,
        max_retry_duration=duration_pb2.Duration(seconds=600),
    )

    job = scheduler_v1.Job(
        name=job_path,
        description="Hourly cryptocurrency data fetch from Kraken Pro API",
        schedule=SCHEDULE,
        time_zone=TIMEZONE,
        http_target=http_target,
        retry_config=retry_config,
    )

    try:
        response = client.create_job(parent=parent, job=job)
        print("✓ Hourly scheduler created!")
    except Exception as e:
        if 'already exists' in str(e):
            response = client.update_job(job=job)
            print("✓ Hourly scheduler updated!")
        else:
            raise e

    print(f"Schedule: Every hour ({TIMEZONE})")
    return response

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_scheduler_job()
