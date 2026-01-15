"""
Deploy Cloud Function using Google Cloud API directly
Bypasses gcloud CLI issues
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import functions_v2
from google.cloud.functions_v2 import types
import os
import zipfile
import tempfile
from google.cloud import storage
import time

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
FUNCTION_NAME = 'daily-crypto-fetcher'
RUNTIME = 'python313'
ENTRY_POINT = 'daily_crypto_fetch'
MEMORY_MB = 512
TIMEOUT_SECONDS = 1200  # 20 minutes - enough for ~675 pairs with 1.5s rate limiting

def create_source_zip():
    """Create a zip file with the function source code"""
    print("Creating source code archive...")

    # Create temporary zip file
    zip_path = os.path.join(tempfile.gettempdir(), 'function_source.zip')

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main.py
        zipf.write('main.py', 'main.py')
        # Add requirements.txt
        zipf.write('requirements.txt', 'requirements.txt')

    print(f"✓ Created archive: {zip_path}")
    return zip_path

def upload_to_gcs(zip_path):
    """Upload source code to Google Cloud Storage"""
    print("Uploading source code to Cloud Storage...")

    # Create bucket name
    bucket_name = f'{PROJECT_ID}-gcf-sources'
    blob_name = f'{FUNCTION_NAME}-{int(time.time())}.zip'

    # Initialize storage client
    storage_client = storage.Client(project=PROJECT_ID)

    # Create bucket if it doesn't exist
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except:
        print(f"Creating bucket: {bucket_name}")
        bucket = storage_client.create_bucket(bucket_name, location=REGION)

    # Upload file
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(zip_path)

    gcs_uri = f'gs://{bucket_name}/{blob_name}'
    print(f"✓ Uploaded to: {gcs_uri}")

    return gcs_uri

def deploy_function(source_uri):
    """Deploy the Cloud Function"""
    print(f"Deploying function: {FUNCTION_NAME}...")

    # Initialize Cloud Functions client
    client = functions_v2.FunctionServiceClient()

    # Define function configuration
    function_path = f"projects/{PROJECT_ID}/locations/{REGION}/functions/{FUNCTION_NAME}"

    function = types.Function(
        name=function_path,
        description="Daily cryptocurrency data fetcher from Kraken Pro API",
        build_config=types.BuildConfig(
            runtime=RUNTIME,
            entry_point=ENTRY_POINT,
            source=types.Source(
                storage_source=types.StorageSource(
                    bucket=source_uri.split('/')[2],
                    object_=source_uri.split('/')[-1]
                )
            )
        ),
        service_config=types.ServiceConfig(
            max_instance_count=10,
            available_memory=f"{MEMORY_MB}M",
            timeout_seconds=TIMEOUT_SECONDS,
            ingress_settings=types.ServiceConfig.IngressSettings.ALLOW_ALL,
        )
    )

    # Create or update function
    try:
        operation = client.create_function(
            parent=f"projects/{PROJECT_ID}/locations/{REGION}",
            function=function,
            function_id=FUNCTION_NAME
        )
    except Exception as e:
        if 'already exists' in str(e):
            print("Function exists, updating...")
            operation = client.update_function(
                function=function
            )
        else:
            raise e

    print("⏳ Waiting for deployment to complete (this may take 2-3 minutes)...")
    result = operation.result(timeout=300)

    print("\n" + "="*70)
    print("✓ DEPLOYMENT SUCCESSFUL!")
    print("="*70)
    print(f"\nFunction Name: {FUNCTION_NAME}")
    print(f"Region: {REGION}")
    print(f"URL: {result.service_config.uri}")
    print("\n⚠ IMPORTANT: Copy the URL above for Cloud Scheduler setup!")
    print("="*70)

    return result.service_config.uri

def main():
    try:
        print("="*70)
        print("DEPLOYING CLOUD FUNCTION VIA API")
        print("="*70)
        print()

        # Step 1: Create source archive
        zip_path = create_source_zip()

        # Step 2: Upload to Cloud Storage
        source_uri = upload_to_gcs(zip_path)

        # Step 3: Deploy function
        function_url = deploy_function(source_uri)

        # Clean up
        os.remove(zip_path)

        print("\n✓ Deployment complete!")
        print(f"\nNext step: Set up Cloud Scheduler with this URL:")
        print(f"  {function_url}")

        # Save URL to file
        with open('function_url.txt', 'w') as f:
            f.write(function_url)
        print("\n✓ URL saved to: function_url.txt")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
