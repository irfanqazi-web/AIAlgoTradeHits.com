"""
Deploy stock-price-app to Cloud Run using Docker and Cloud Build
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import subprocess
import os

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
SERVICE_NAME = 'crypto-trading-app'
IMAGE_NAME = f'gcr.io/{PROJECT_ID}/{SERVICE_NAME}'

def main():
    print("="*70)
    print("DEPLOYING TRADING APP TO CLOUD RUN")
    print("="*70)
    print()

    # Change to app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

    print("Step 1: Building Docker image with Cloud Build...")
    build_cmd = [
        'gcloud', 'builds', 'submit',
        '--tag', IMAGE_NAME,
        '--project', PROJECT_ID,
        '.'
    ]

    result = subprocess.run(build_cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print("✗ Build failed!")
        sys.exit(1)

    print("\n✓ Docker image built successfully!")

    print("\nStep 2: Deploying to Cloud Run...")
    deploy_cmd = [
        'gcloud', 'run', 'deploy', SERVICE_NAME,
        '--image', IMAGE_NAME,
        '--platform', 'managed',
        '--region', REGION,
        '--allow-unauthenticated',
        '--project', PROJECT_ID,
        '--port', '8080'
    ]

    result = subprocess.run(deploy_cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print("✗ Deployment failed!")
        sys.exit(1)

    print("\n" + "="*70)
    print("✓ TRADING APP DEPLOYED SUCCESSFULLY!")
    print("="*70)
    print(f"\nService: {SERVICE_NAME}")
    print(f"Region: {REGION}")
    print(f"Project: {PROJECT_ID}")


if __name__ == "__main__":
    main()
