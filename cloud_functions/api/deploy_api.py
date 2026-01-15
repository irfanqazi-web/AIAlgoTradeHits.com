"""
Deploy Trading Data API to Cloud Run
This script deploys the Flask API that serves BigQuery data to the React frontend
"""

import subprocess
import sys
import time
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
PROJECT_ID = 'aialgotradehits'
SERVICE_NAME = 'trading-api'
REGION = 'us-central1'
MEMORY = '512Mi'
CPU = '1'
TIMEOUT = '300'
MAX_INSTANCES = '10'
MIN_INSTANCES = '0'

def run_command(command, description):
    """Execute a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}\n")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Deploy the API to Cloud Run"""

    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Trading Data API - Cloud Run Deployment           ║
    ║                                                            ║
    ║  This will deploy the Flask API that serves BigQuery      ║
    ║  data to the React frontend application.                  ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Set the project
    if not run_command(
        f'gcloud config set project {PROJECT_ID}',
        'Setting active GCP project'
    ):
        print("❌ Failed to set project")
        return False

    # Step 2: Enable required APIs
    apis = [
        'run.googleapis.com',
        'cloudbuild.googleapis.com',
        'bigquery.googleapis.com'
    ]

    for api in apis:
        if not run_command(
            f'gcloud services enable {api} --project={PROJECT_ID}',
            f'Enabling {api}'
        ):
            print(f"⚠️  Warning: Failed to enable {api}, might already be enabled")

    # Step 3: Deploy to Cloud Run
    deploy_command = f"""gcloud run deploy {SERVICE_NAME} \
        --source . \
        --platform managed \
        --region {REGION} \
        --allow-unauthenticated \
        --memory {MEMORY} \
        --cpu {CPU} \
        --timeout {TIMEOUT} \
        --max-instances {MAX_INSTANCES} \
        --min-instances {MIN_INSTANCES} \
        --port 8080 \
        --project {PROJECT_ID} \
        --set-env-vars PROJECT_ID={PROJECT_ID},JWT_SECRET=crypto-trading-jwt-secret-2025-secure-key"""

    if not run_command(
        deploy_command,
        'Deploying API to Cloud Run'
    ):
        print("❌ Deployment failed")
        return False

    # Step 4: Get the service URL
    print("\n" + "="*60)
    print("📋 Getting service URL...")
    print("="*60)

    try:
        result = subprocess.run(
            f'gcloud run services describe {SERVICE_NAME} --region={REGION} --project={PROJECT_ID} --format="value(status.url)"',
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        service_url = result.stdout.strip()

        print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║              🎉 DEPLOYMENT SUCCESSFUL! 🎉                  ║
    ╚════════════════════════════════════════════════════════════╝

    📍 Service URL: {service_url}

    🔗 API Endpoints:
       • Health Check:  {service_url}/health
       • Crypto Daily:  {service_url}/api/crypto/daily?limit=10
       • Crypto Hourly: {service_url}/api/crypto/hourly?limit=10
       • Crypto 5-Min:  {service_url}/api/crypto/5min?limit=10
       • Stock Data:    {service_url}/api/stocks?limit=10
       • Crypto Summary: {service_url}/api/summary/crypto
       • Stock Summary:  {service_url}/api/summary/stock
       • Users:         {service_url}/api/users

    📝 Next Steps:
       1. Test the health endpoint: curl {service_url}/health
       2. Update frontend API_BASE_URL in src/services/api.js to: {service_url}
       3. Deploy the frontend app

    🔧 Management Commands:
       • View logs: gcloud run services logs read {SERVICE_NAME} --project={PROJECT_ID}
       • Update service: Run this script again
       • Delete service: gcloud run services delete {SERVICE_NAME} --region={REGION} --project={PROJECT_ID}
        """)

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get service URL: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
