"""
Deploy stock-price-app to Cloud Run using Cloud Build and Run APIs
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import tarfile
import tempfile
from google.cloud import storage
from google.cloud.devtools import cloudbuild_v1
from google.cloud import run_v2
import time

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
SERVICE_NAME = 'crypto-trading-app'

def create_source_tarball():
    """Create tarball of source code"""
    print("Creating source tarball...")

    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

    # Create tarball
    tarball_path = os.path.join(tempfile.gettempdir(), 'source.tar.gz')

    with tarfile.open(tarball_path, 'w:gz') as tar:
        # Add all necessary files
        files_to_add = [
            'package.json',
            'Dockerfile',
            'nginx.conf',
            'vite.config.js',
            'index.html',
            'eslint.config.js'
        ]

        # Add files
        for filename in files_to_add:
            if os.path.exists(filename):
                tar.add(filename)

        # Add directories
        if os.path.exists('src'):
            tar.add('src')
        if os.path.exists('public'):
            tar.add('public')

    print(f"✓ Tarball created: {tarball_path}")
    return tarball_path


def upload_source(tarball_path):
    """Upload source to GCS"""
    print("Uploading source to Cloud Storage...")

    bucket_name = f'{PROJECT_ID}-cloudbuild-source'
    blob_name = f'{SERVICE_NAME}-{int(time.time())}.tar.gz'

    storage_client = storage.Client(project=PROJECT_ID)

    try:
        bucket = storage_client.get_bucket(bucket_name)
    except:
        print(f"Creating bucket: {bucket_name}")
        bucket = storage_client.create_bucket(bucket_name, location=REGION)

    blob = bucket.blob(blob_name)
    blob.upload_from_filename(tarball_path)

    gcs_uri = f'gs://{bucket_name}/{blob_name}'
    print(f"✓ Uploaded to: {gcs_uri}")

    return bucket_name, blob_name


def build_image(bucket_name, blob_name):
    """Build Docker image using Cloud Build"""
    print("\nBuilding Docker image...")

    client = cloudbuild_v1.CloudBuildClient()

    image_name = f'gcr.io/{PROJECT_ID}/{SERVICE_NAME}:latest'

    build = cloudbuild_v1.Build(
        source=cloudbuild_v1.Source(
            storage_source=cloudbuild_v1.StorageSource(
                bucket=bucket_name,
                object_=blob_name
            )
        ),
        steps=[
            cloudbuild_v1.BuildStep(
                name='gcr.io/cloud-builders/docker',
                args=['build', '-t', image_name, '.']
            )
        ],
        images=[image_name]
    )

    operation = client.create_build(project_id=PROJECT_ID, build=build)

    print("⏳ Building image (this may take 3-5 minutes)...")

    try:
        result = operation.result(timeout=600)
        print("✓ Image built successfully!")
        return image_name
    except Exception as e:
        print(f"✗ Build failed: {e}")
        return None


def deploy_to_cloudrun(image):
    """Deploy to Cloud Run"""
    print("\nDeploying to Cloud Run...")

    client = run_v2.ServicesClient()

    service_path = f"projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_NAME}"

    service = run_v2.Service(
        name=service_path,
        template=run_v2.RevisionTemplate(
            containers=[run_v2.Container(
                image=image,
                ports=[run_v2.ContainerPort(container_port=8080)],
                resources=run_v2.ResourceRequirements(
                    limits={
                        'memory': '512Mi',
                        'cpu': '1'
                    }
                )
            )],
            max_instance_request_concurrency=80
        ),
    )

    parent = f"projects/{PROJECT_ID}/locations/{REGION}"

    try:
        operation = client.create_service(
            parent=parent,
            service=service,
            service_id=SERVICE_NAME
        )
        print("⏳ Creating service...")
    except Exception as e:
        if 'already exists' in str(e):
            print("Service exists, updating...")
            operation = client.update_service(service=service)
            print("⏳ Updating service...")
        else:
            raise e

    result = operation.result(timeout=300)

    # Make service public
    try:
        policy_client = run_v2.ServicesClient()
        policy = {
            "bindings": [
                {
                    "role": "roles/run.invoker",
                    "members": ["allUsers"]
                }
            ]
        }
        policy_client.set_iam_policy(resource=service_path, policy=policy)
        print("✓ Service made publicly accessible")
    except:
        pass

    print("\n" + "="*70)
    print("✓ CLOUD RUN DEPLOYMENT SUCCESSFUL!")
    print("="*70)
    print(f"\nService: {SERVICE_NAME}")
    print(f"Region: {REGION}")
    print(f"URL: {result.uri}")
    print("="*70)

    return result.uri


def main():
    print("="*70)
    print("DEPLOYING TRADING APP TO CLOUD RUN")
    print("="*70)
    print()

    try:
        # Step 1: Create source tarball
        tarball = create_source_tarball()

        # Step 2: Upload to GCS
        bucket, blob = upload_source(tarball)

        # Step 3: Build with Cloud Build
        image = build_image(bucket, blob)

        if not image:
            print("\n✗ Build failed")
            sys.exit(1)

        # Step 4: Deploy to Cloud Run
        url = deploy_to_cloudrun(image)

        # Clean up
        os.remove(tarball)

        print(f"\n✓ Trading application is live at:")
        print(f"  {url}")

    except Exception as e:
        print(f"\n✗ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
