"""
Deployment script for Trading Agent Cloud Run service
AIAlgoTradeHits.com
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

# Configuration
PROJECT_ID = "aialgotradehits"
SERVICE_NAME = "trading-agent"
REGION = "us-central1"
MEMORY = "1Gi"
CPU = "1"
TIMEOUT = "300"

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {description}")
    print(f"Command: {cmd}")
    print('='*60)

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
        return False

    print(f"[SUCCESS] {description}")
    return True


def prepare_deployment_package():
    """Prepare files for deployment"""
    print("\n" + "="*60)
    print("Preparing deployment package...")
    print("="*60)

    deploy_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(deploy_dir)
    shared_modules_src = os.path.join(parent_dir, "shared_ai_modules")
    shared_modules_dst = os.path.join(deploy_dir, "shared_ai_modules")

    # Copy shared_ai_modules to deployment directory
    if os.path.exists(shared_modules_dst):
        shutil.rmtree(shared_modules_dst)

    if os.path.exists(shared_modules_src):
        shutil.copytree(shared_modules_src, shared_modules_dst)
        print(f"Copied shared_ai_modules to {shared_modules_dst}")
    else:
        print(f"[WARNING] shared_ai_modules not found at {shared_modules_src}")

    return True


def update_dockerfile():
    """Update Dockerfile for local shared_ai_modules"""
    dockerfile_content = '''# AIAlgoTradeHits Trading Agent - Cloud Run Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared AI modules
COPY shared_ai_modules /app/shared_ai_modules

# Copy application code
COPY main.py .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV GCP_PROJECT_ID=aialgotradehits

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
'''

    deploy_dir = os.path.dirname(os.path.abspath(__file__))
    dockerfile_path = os.path.join(deploy_dir, "Dockerfile")

    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)

    print(f"Updated Dockerfile at {dockerfile_path}")
    return True


def deploy_to_cloud_run():
    """Deploy to Google Cloud Run"""

    # Get Anthropic API key from environment
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not anthropic_key:
        print("[WARNING] ANTHROPIC_API_KEY not set. Agent chat functionality will be limited.")

    deploy_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(deploy_dir)

    # Step 1: Build container using Cloud Build
    success = run_command(
        f"gcloud builds submit --project={PROJECT_ID} --tag=gcr.io/{PROJECT_ID}/{SERVICE_NAME}:latest",
        "Building container with Cloud Build"
    )

    if not success:
        return False

    # Step 2: Deploy to Cloud Run
    env_vars = f"GCP_PROJECT_ID={PROJECT_ID}"
    if anthropic_key:
        env_vars += f",ANTHROPIC_API_KEY={anthropic_key}"

    success = run_command(
        f"gcloud run deploy {SERVICE_NAME} "
        f"--image=gcr.io/{PROJECT_ID}/{SERVICE_NAME}:latest "
        f"--platform=managed "
        f"--region={REGION} "
        f"--allow-unauthenticated "
        f"--memory={MEMORY} "
        f"--cpu={CPU} "
        f"--timeout={TIMEOUT} "
        f"--set-env-vars={env_vars} "
        f"--project={PROJECT_ID}",
        "Deploying to Cloud Run"
    )

    return success


def get_service_url():
    """Get the deployed service URL"""
    result = subprocess.run(
        f"gcloud run services describe {SERVICE_NAME} --region={REGION} --project={PROJECT_ID} --format='value(status.url)'",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def test_deployment(service_url):
    """Test the deployed service"""
    print("\n" + "="*60)
    print("Testing deployed service...")
    print("="*60)

    import requests

    try:
        # Test health endpoint
        response = requests.get(f"{service_url}/health", timeout=30)
        print(f"\nHealth check: {response.status_code}")
        print(response.json())

        # Test tools endpoint
        response = requests.get(f"{service_url}/tools", timeout=30)
        print(f"\nTools endpoint: {response.status_code}")
        tools = response.json()
        print(f"Available tools: {len(tools['tools'])}")

        # Test workflows endpoint
        response = requests.get(f"{service_url}/workflows", timeout=30)
        print(f"\nWorkflows endpoint: {response.status_code}")
        print(response.json())

        print("\n[SUCCESS] All deployment tests passed!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Deployment test failed: {e}")
        return False


def main():
    """Main deployment function"""
    print("="*60)
    print("AIAlgoTradeHits Trading Agent Deployment")
    print(f"Project: {PROJECT_ID}")
    print(f"Service: {SERVICE_NAME}")
    print(f"Region: {REGION}")
    print(f"Time: {datetime.now().isoformat()}")
    print("="*60)

    # Step 1: Prepare deployment package
    if not prepare_deployment_package():
        print("[FAILED] Package preparation failed")
        return False

    # Step 2: Update Dockerfile
    if not update_dockerfile():
        print("[FAILED] Dockerfile update failed")
        return False

    # Step 3: Deploy to Cloud Run
    if not deploy_to_cloud_run():
        print("[FAILED] Deployment failed")
        return False

    # Step 4: Get service URL
    service_url = get_service_url()
    if service_url:
        print(f"\n{'='*60}")
        print("DEPLOYMENT SUCCESSFUL!")
        print(f"Service URL: {service_url}")
        print("="*60)

        # Step 5: Test deployment
        test_deployment(service_url)

        print(f"\nEndpoints available:")
        print(f"  - {service_url}/health - Health check")
        print(f"  - {service_url}/chat - Chat with Trading Agent")
        print(f"  - {service_url}/growth-score - Calculate Growth Score")
        print(f"  - {service_url}/rise-cycle - Detect rise/fall cycle")
        print(f"  - {service_url}/market-data - Get market data")
        print(f"  - {service_url}/rise-cycle-candidates - Get rise cycle candidates")
        print(f"  - {service_url}/top-growth-scores - Get top Growth Scores")
        print(f"  - {service_url}/workflows - List available workflows")
        print(f"  - {service_url}/metrics - Agent performance metrics")
        print(f"  - {service_url}/tools - Available tool definitions")

    else:
        print("[WARNING] Could not retrieve service URL")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
