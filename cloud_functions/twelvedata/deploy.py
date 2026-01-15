"""
Deploy TwelveData Fetcher Cloud Function to GCP
"""
import subprocess
import sys

PROJECT_ID = "aialgotradehits"
REGION = "us-central1"
FUNCTION_NAME = "twelvedata-fetcher"

def deploy():
    print("=" * 60)
    print("DEPLOYING TWELVEDATA FETCHER CLOUD FUNCTION")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Function: {FUNCTION_NAME}")
    print()

    # Deploy command
    cmd = [
        "gcloud", "functions", "deploy", FUNCTION_NAME,
        "--gen2",
        "--runtime", "python311",
        "--region", REGION,
        "--source", ".",
        "--entry-point", "fetch_twelvedata",
        "--trigger-http",
        "--allow-unauthenticated",
        "--timeout", "540s",
        "--memory", "512MB",
        "--project", PROJECT_ID
    ]

    print("Running command:")
    print(" ".join(cmd))
    print()

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print()
        print("=" * 60)
        print("DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        print()
        print("Function URL:")
        print(f"  https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}")
        print()
        print("Test commands:")
        print(f"  # Fetch stocks daily data:")
        print(f"  curl 'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}?asset_type=stocks&timeframe=daily'")
        print()
        print(f"  # Fetch all crypto hourly:")
        print(f"  curl 'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}?asset_type=crypto&timeframe=hourly'")
        print()
        print(f"  # Fetch everything (daily):")
        print(f"  curl 'https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}?asset_type=all&timeframe=daily'")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e}")
        return False


if __name__ == "__main__":
    deploy()
