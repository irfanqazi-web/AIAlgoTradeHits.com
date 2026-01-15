"""
Deploy Daily Stock Cloud Function via Google Cloud API
"""

import requests
import json
import zipfile
import io
import os
import sys
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'
FUNCTION_NAME = 'daily-stock-fetcher'
ENTRY_POINT = 'daily_stock_fetch'
RUNTIME = 'python311'
TIMEOUT = 540  # 9 minutes
MEMORY = '2Gi'

def get_access_token():
    """Get access token for Google Cloud API"""

    # Use default credentials
    import google.auth
    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )

    # Refresh the credentials
    auth_req = Request()
    credentials.refresh(auth_req)

    return credentials.token

def create_zip_file():
    """Create a zip file containing main.py and requirements.txt"""

    print("Creating deployment package...")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main.py
        zip_file.write('main.py', 'main.py')
        print("  Added main.py")

        # Add requirements.txt
        zip_file.write('requirements.txt', 'requirements.txt')
        print("  Added requirements.txt")

    zip_buffer.seek(0)
    return base64.b64encode(zip_buffer.read()).decode('utf-8')

def deploy_function():
    """Deploy Cloud Function via REST API"""

    print("="*70)
    print("DEPLOYING DAILY STOCK CLOUD FUNCTION")
    print("="*70)
    print(f"\nProject: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Function: {FUNCTION_NAME}")
    print(f"Runtime: {RUNTIME}")
    print(f"Timeout: {TIMEOUT}s")
    print(f"Memory: {MEMORY}")
    print("")

    # Get access token
    print("Authenticating with Google Cloud...")
    access_token = get_access_token()
    print("✓ Authentication successful")

    # Create zip file
    zip_content = create_zip_file()
    print("✓ Deployment package created")

    # Prepare API request
    url = f"https://cloudfunctions.googleapis.com/v2/projects/{PROJECT_ID}/locations/{REGION}/functions/{FUNCTION_NAME}"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    function_config = {
        "name": f"projects/{PROJECT_ID}/locations/{REGION}/functions/{FUNCTION_NAME}",
        "description": "Daily stock data fetcher with Elliott Wave and Fibonacci analysis",
        "buildConfig": {
            "runtime": RUNTIME,
            "entryPoint": ENTRY_POINT,
            "source": {
                "storageSource": {
                    "bucket": f"{PROJECT_ID}-gcf-source",
                    "object": f"{FUNCTION_NAME}-{int(time.time())}.zip"
                }
            }
        },
        "serviceConfig": {
            "timeoutSeconds": TIMEOUT,
            "availableMemory": MEMORY,
            "maxInstanceCount": 1,
            "ingressSettings": "ALLOW_ALL",
            "allTrafficOnLatestRevision": True
        }
    }

    print("\nDeploying function...")
    print("This may take 2-3 minutes...")

    # Use gcloud command for deployment (simpler)
    import subprocess

    deploy_cmd = [
        'gcloud', 'functions', 'deploy', FUNCTION_NAME,
        '--gen2',
        '--runtime', RUNTIME,
        '--region', REGION,
        '--source', '.',
        '--entry-point', ENTRY_POINT,
        '--trigger-http',
        '--allow-unauthenticated',
        '--timeout', str(TIMEOUT),
        '--memory', MEMORY,
        '--max-instances', '1',
        '--project', PROJECT_ID
    ]

    try:
        result = subprocess.run(deploy_cmd, capture_output=True, text=True, check=True)
        print(result.stdout)

        print("\n" + "="*70)
        print("✓ DEPLOYMENT SUCCESSFUL!")
        print("="*70)
        print(f"\nFunction URL: https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}")
        print("\nNext steps:")
        print(f"  1. Set up Cloud Scheduler to trigger daily at midnight")
        print(f"  2. Test manually: curl https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}")
        print("="*70)

        return True

    except subprocess.CalledProcessError as e:
        print("\n" + "="*70)
        print("✗ DEPLOYMENT FAILED")
        print("="*70)
        print(f"\nError: {e}")
        print(f"\nOutput: {e.output}")
        print(f"\nStderr: {e.stderr}")
        return False

if __name__ == "__main__":
    import time

    # Check if files exist
    if not os.path.exists('main.py'):
        print("ERROR: main.py not found in current directory")
        exit(1)

    if not os.path.exists('requirements.txt'):
        print("ERROR: requirements.txt not found in current directory")
        exit(1)

    deploy_function()
