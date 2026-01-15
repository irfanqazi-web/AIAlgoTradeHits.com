"""
Deploy 5-minute top-10 gainers function and scheduler
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import functions_v2, scheduler_v1, storage
from google.cloud.functions_v2 import types
from google.protobuf import duration_pb2
import os, zipfile, tempfile, time

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
FUNCTION_NAME = 'fivemin-top10-fetcher'
RUNTIME = 'python313'
ENTRY_POINT = 'fivemin_top10_fetch'
MEMORY_MB = 256
TIMEOUT_SECONDS = 600  # 10 minutes - fetches only 10 pairs but calculates indicators
JOB_NAME = 'fivemin-top10-fetch-job'
SCHEDULE = '*/5 * * * *'  # Every 5 minutes
TIMEZONE = 'America/New_York'

def deploy_function():
    print("="*70)
    print("DEPLOYING 5-MINUTE TOP-10 GAINERS CLOUD FUNCTION")
    print("="*70)

    # Create zip
    zip_path = os.path.join(tempfile.gettempdir(), f'{FUNCTION_NAME}_source.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('main.py', 'main.py')
        zipf.write('requirements.txt', 'requirements.txt')
    print(f"✓ Created archive")

    # Upload to GCS
    bucket_name = f'{PROJECT_ID}-gcf-sources'
    blob_name = f'{FUNCTION_NAME}-{int(time.time())}.zip'
    storage_client = storage.Client(project=PROJECT_ID)
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except:
        bucket = storage_client.create_bucket(bucket_name, location=REGION)
    bucket.blob(blob_name).upload_from_filename(zip_path)
    gcs_uri = f'gs://{bucket_name}/{blob_name}'
    print(f"✓ Uploaded to GCS")

    # Deploy function
    client = functions_v2.FunctionServiceClient()
    function_path = f"projects/{PROJECT_ID}/locations/{REGION}/functions/{FUNCTION_NAME}"

    function = types.Function(
        name=function_path,
        description="5-minute OHLC data for top 10 hourly gainers",
        build_config=types.BuildConfig(
            runtime=RUNTIME,
            entry_point=ENTRY_POINT,
            source=types.Source(
                storage_source=types.StorageSource(
                    bucket=bucket_name,
                    object_=blob_name
                )
            )
        ),
        service_config=types.ServiceConfig(
            max_instance_count=5,
            available_memory=f"{MEMORY_MB}M",
            timeout_seconds=TIMEOUT_SECONDS,
            ingress_settings=types.ServiceConfig.IngressSettings.ALLOW_ALL,
        )
    )

    try:
        operation = client.create_function(
            parent=f"projects/{PROJECT_ID}/locations/{REGION}",
            function=function,
            function_id=FUNCTION_NAME
        )
    except Exception as e:
        if 'already exists' in str(e):
            operation = client.update_function(function=function)
        else:
            raise e

    print("⏳ Deploying...")
    result = operation.result(timeout=300)
    function_url = result.service_config.uri

    print("✓ Function deployed!")
    print(f"URL: {function_url}")

    os.remove(zip_path)
    return function_url

def setup_scheduler(function_url):
    print("\n" + "="*70)
    print("SETTING UP 5-MINUTE SCHEDULER")
    print("="*70)

    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"
    job_path = f"{parent}/jobs/{JOB_NAME}"

    job = scheduler_v1.Job(
        name=job_path,
        description="5-minute top-10 gainers data fetch",
        schedule=SCHEDULE,
        time_zone=TIMEZONE,
        http_target=scheduler_v1.HttpTarget(
            uri=function_url,
            http_method=scheduler_v1.HttpMethod.GET,
        ),
        attempt_deadline=duration_pb2.Duration(seconds=600),  # 10 minutes
        retry_config=scheduler_v1.RetryConfig(
            retry_count=2,
            max_retry_duration=duration_pb2.Duration(seconds=600),
        ),
    )

    try:
        client.create_job(parent=parent, job=job)
        print("✓ Scheduler created!")
    except Exception as e:
        if 'already exists' in str(e):
            client.update_job(job=job)
            print("✓ Scheduler updated!")
        else:
            raise e

    print(f"Schedule: Every 5 minutes ({TIMEZONE})")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    url = deploy_function()
    setup_scheduler(url)
    print("\n" + "="*70)
    print("✓ ALL DEPLOYMENTS COMPLETE!")
    print("="*70)
