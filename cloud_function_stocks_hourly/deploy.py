"""
Deploy Stock Hourly Fetcher to Google Cloud Functions
"""

import subprocess
import sys

PROJECT_ID = 'cryptobot-462709'
FUNCTION_NAME = 'stock-hourly-fetcher'
REGION = 'us-central1'
RUNTIME = 'python311'
ENTRY_POINT = 'main'
MEMORY = '512MB'
TIMEOUT = '540s'

def deploy():
    """Deploy the Cloud Function"""

    print("=" * 70)
    print(f"DEPLOYING {FUNCTION_NAME.upper()}")
    print("=" * 70)
    print(f"Project: {PROJECT_ID}")
    print(f"Function: {FUNCTION_NAME}")
    print(f"Region: {REGION}")
    print(f"Runtime: {RUNTIME}")
    print(f"Memory: {MEMORY}")
    print(f"Timeout: {TIMEOUT}")
    print("=" * 70)

    cmd = [
        'gcloud', 'functions', 'deploy', FUNCTION_NAME,
        '--gen2',
        '--runtime', RUNTIME,
        '--region', REGION,
        '--source', '.',
        '--entry-point', ENTRY_POINT,
        '--trigger-http',
        '--allow-unauthenticated',
        '--memory', MEMORY,
        '--timeout', TIMEOUT,
        '--set-env-vars', f'PROJECT_ID={PROJECT_ID}',
        '--project', PROJECT_ID
    ]

    print(f"\nExecuting: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout)

        print("\n" + "=" * 70)
        print("✓ DEPLOYMENT SUCCESSFUL!")
        print("=" * 70)
        print(f"\nFunction URL will be displayed above.")
        print(f"\nTo test the function:")
        print(f"  curl https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}")
        print(f"\nTo view logs:")
        print(f"  gcloud functions logs read {FUNCTION_NAME} --region={REGION} --project={PROJECT_ID} --limit=50")
        print("=" * 70)

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ DEPLOYMENT FAILED!")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)
