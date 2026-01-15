"""
Deploy stock-price-app to Cloud Run using APIs directly
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import subprocess
from google.cloud import artifactregistry_v1
from google.cloud import run_v2
from google.api_core import operation
import time

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
SERVICE_NAME = 'crypto-trading-app'
REPOSITORY_NAME = 'cloud-run-source-deploy'

def build_with_docker():
    """Build Docker image locally"""
    print("Building Docker image...")

    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

    # Build Docker image
    image_tag = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPOSITORY_NAME}/{SERVICE_NAME}:latest"

    try:
        # Build
        print(f"Building image: {image_tag}")
        subprocess.run(['docker', 'build', '-t', image_tag, '.'], check=True)

        # Configure Docker auth for Artifact Registry
        print("Configuring Docker authentication...")
        subprocess.run(['gcloud', 'auth', 'configure-docker', f'{REGION}-docker.pkg.dev', '--quiet'], check=False)

        # Push
        print(f"Pushing image to Artifact Registry...")
        subprocess.run(['docker', 'push', image_tag], check=True)

        print("✓ Image built and pushed successfully!")
        return image_tag

    except subprocess.CalledProcessError as e:
        print(f"✗ Docker command failed: {e}")
        return None
    except FileNotFoundError:
        print("✗ Docker not found. Please install Docker Desktop.")
        print("  Download from: https://www.docker.com/products/docker-desktop")
        return None


def deploy_to_cloud_run(image):
    """Deploy image to Cloud Run"""
    print(f"\nDeploying to Cloud Run...")

    client = run_v2.ServicesClient()

    service_path = f"projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_NAME}"

    service = run_v2.Service(
        name=service_path,
        template=run_v2.RevisionTemplate(
            containers=[run_v2.Container(
                image=image,
                ports=[run_v2.ContainerPort(container_port=8080)],
            )],
        ),
    )

    parent = f"projects/{PROJECT_ID}/locations/{REGION}"

    try:
        # Try to create service
        operation = client.create_service(
            parent=parent,
            service=service,
            service_id=SERVICE_NAME
        )
        print("⏳ Creating service (this may take 2-3 minutes)...")
    except Exception as e:
        if 'already exists' in str(e):
            print("Service exists, updating...")
            operation = client.update_service(service=service)
            print("⏳ Updating service (this may take 2-3 minutes)...")
        else:
            raise e

    # Wait for operation to complete
    result = operation.result(timeout=300)

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

    # Build and push image
    image = build_with_docker()
    if not image:
        print("\n✗ Failed to build/push image")
        print("\nAlternative: Use Cloud Build (requires working gcloud CLI)")
        print("  gcloud builds submit --tag gcr.io/cryptobot-462709/crypto-trading-app")
        sys.exit(1)

    # Deploy to Cloud Run
    url = deploy_to_cloud_run(image)

    print(f"\n✓ Trading application is live at:")
    print(f"  {url}")


if __name__ == "__main__":
    main()
