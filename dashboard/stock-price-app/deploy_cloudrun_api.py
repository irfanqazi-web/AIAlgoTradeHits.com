"""
Deploy stock-price-app to Cloud Run using Cloud Build API
No Docker required - builds in the cloud
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import zipfile
import tempfile
import time
from google.cloud import storage, run_v2
from google.cloud.devtools import cloudbuild_v1
from google.protobuf import duration_pb2

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
SERVICE_NAME = 'crypto-trading-app'

def create_source_archive():
    """Create a zip archive of the source code"""
    print("Creating source code archive...")

    app_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(tempfile.gettempdir(), 'stock-app-source.zip')

    # Files to include
    files_to_include = [
        'package.json',
        'package-lock.json',
        'vite.config.js',
        'index.html',
        'Dockerfile',
        'nginx.conf',
        'eslint.config.js',
    ]

    # Directories to include
    dirs_to_include = [
        'src',
        'public'
    ]

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        os.chdir(app_dir)

        # Add files
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file, file)
                print(f"  + {file}")

        # Add directories
        for dir_name in dirs_to_include:
            if os.path.exists(dir_name):
                for root, dirs, files in os.walk(dir_name):
                    # Skip node_modules
                    if 'node_modules' in root:
                        continue
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, file_path)
                print(f"  + {dir_name}/")

    print(f"✓ Archive created: {zip_path}")
    return zip_path


def upload_source_to_gcs(zip_path):
    """Upload source archive to GCS"""
    print("\nUploading source to Cloud Storage...")

    bucket_name = f'{PROJECT_ID}-cloudrun-source'
    blob_name = f'{SERVICE_NAME}-{int(time.time())}.zip'

    storage_client = storage.Client(project=PROJECT_ID)

    # Create bucket if needed
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except:
        print(f"Creating bucket: {bucket_name}")
        bucket = storage_client.create_bucket(bucket_name, location=REGION)

    # Upload
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(zip_path)

    gcs_uri = f'gs://{bucket_name}/{blob_name}'
    print(f"✓ Uploaded to: {gcs_uri}")

    return gcs_uri


def build_with_cloud_build(source_uri):
    """Build Docker image using Cloud Build"""
    print("\nStarting Cloud Build...")

    image_uri = f'gcr.io/{PROJECT_ID}/{SERVICE_NAME}:latest'

    build_client = cloudbuild_v1.CloudBuildClient()

    # Extract bucket and object from GCS URI
    parts = source_uri.replace('gs://', '').split('/', 1)
    bucket = parts[0]
    source_object = parts[1]

    build = cloudbuild_v1.Build(
        source=cloudbuild_v1.Source(
            storage_source=cloudbuild_v1.StorageSource(
                bucket=bucket,
                object_=source_object
            )
        ),
        steps=[
            cloudbuild_v1.BuildStep(
                name='gcr.io/cloud-builders/docker',
                args=['build', '-t', image_uri, '.']
            )
        ],
        images=[image_uri],
        timeout=duration_pb2.Duration(seconds=1200)  # 20 minutes
    )

    operation = build_client.create_build(project_id=PROJECT_ID, build=build)

    print("⏳ Building Docker image (this may take 5-10 minutes)...")
    print("   Cloud Build is installing dependencies and building the app...")

    result = operation.result(timeout=1200)

    if result.status == cloudbuild_v1.Build.Status.SUCCESS:
        print(f"✓ Build successful!")
        print(f"  Image: {image_uri}")
        return image_uri
    else:
        print(f"✗ Build failed: {result.status}")
        print(f"  Log URL: {result.log_url}")
        return None


def deploy_to_cloud_run(image_uri):
    """Deploy image to Cloud Run"""
    print("\nDeploying to Cloud Run...")

    client = run_v2.ServicesClient()

    service_path = f"projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_NAME}"
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"

    # Check if service exists
    try:
        existing_service = client.get_service(name=service_path)
        service_exists = True
        print("Service already exists, updating...")
    except:
        service_exists = False
        print("Creating new service...")

    service = run_v2.Service(
        template=run_v2.RevisionTemplate(
            containers=[run_v2.Container(
                image=image_uri,
                ports=[run_v2.ContainerPort(container_port=8080)],
                resources=run_v2.ResourceRequirements(
                    limits={'memory': '512Mi', 'cpu': '1'}
                )
            )],
            max_instance_request_concurrency=80
        ),
        traffic=[run_v2.TrafficTarget(
            type_=run_v2.TrafficTargetAllocationType.TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST,
            percent=100
        )]
    )

    if service_exists:
        # For update, include the name
        service.name = service_path
        operation = client.update_service(service=service)
        print("⏳ Updating Cloud Run service...")
    else:
        # For create, name must be empty, use service_id instead
        operation = client.create_service(
            parent=parent,
            service=service,
            service_id=SERVICE_NAME
        )
        print("⏳ Creating Cloud Run service...")

    result = operation.result(timeout=300)

    print("\n" + "="*70)
    print("✓ DEPLOYMENT SUCCESSFUL!")
    print("="*70)
    print(f"Service Name: {SERVICE_NAME}")
    print(f"Region: {REGION}")
    print(f"URL: {result.uri}")
    print("="*70)

    return result.uri


def set_iam_policy(service_url):
    """Make the service publicly accessible"""
    print("\nMaking service publicly accessible...")

    client = run_v2.ServicesClient()
    service_path = f"projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_NAME}"

    policy = {
        "bindings": [
            {
                "role": "roles/run.invoker",
                "members": ["allUsers"]
            }
        ]
    }

    try:
        client.set_iam_policy(resource=service_path, policy=policy)
        print("✓ Service is now publicly accessible")
    except Exception as e:
        print(f"⚠ Warning: Could not set IAM policy: {e}")
        print("  You may need to manually allow unauthenticated access in Cloud Console")


def main():
    print("="*70)
    print("DEPLOYING STOCK-PRICE-APP TO CLOUD RUN")
    print("="*70)
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Service: {SERVICE_NAME}")
    print("="*70)
    print()

    try:
        # Step 1: Create source archive
        zip_path = create_source_archive()

        # Step 2: Upload to GCS
        source_uri = upload_source_to_gcs(zip_path)

        # Step 3: Build with Cloud Build
        image_uri = build_with_cloud_build(source_uri)

        if not image_uri:
            print("\n✗ Build failed")
            sys.exit(1)

        # Step 4: Deploy to Cloud Run
        service_url = deploy_to_cloud_run(image_uri)

        # Step 5: Make it public
        set_iam_policy(service_url)

        # Cleanup
        os.remove(zip_path)

        print("\n" + "="*70)
        print("🎉 TRADING APP IS LIVE!")
        print("="*70)
        print(f"\n📊 Access your app at:")
        print(f"   {service_url}")
        print("\n✓ Application is publicly accessible")
        print("✓ Uses nginx for optimal performance")
        print("✓ Automatically scales based on traffic")
        print("="*70)

    except Exception as e:
        print(f"\n✗ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
