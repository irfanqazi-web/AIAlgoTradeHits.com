"""
Deploy Smart Search Cloud Function to GCP
"""

import subprocess
import sys

PROJECT_ID = "aialgotradehits"
REGION = "us-central1"
FUNCTION_NAME = "smart-search"

def deploy():
    print("=" * 60)
    print("DEPLOYING AI SMART SEARCH FUNCTION")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Function: {FUNCTION_NAME}")
    print("=" * 60)

    # Deploy command
    cmd = [
        "gcloud", "functions", "deploy", FUNCTION_NAME,
        "--gen2",
        "--runtime", "python311",
        "--region", REGION,
        "--source", ".",
        "--entry-point", "smart_search",
        "--trigger-http",
        "--allow-unauthenticated",
        "--memory", "512MB",
        "--timeout", "120s",
        "--min-instances", "0",
        "--max-instances", "10",
        "--project", PROJECT_ID,
    ]

    print("\nRunning deployment command...")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)

        # Get the URL
        url_cmd = [
            "gcloud", "functions", "describe", FUNCTION_NAME,
            "--gen2",
            "--region", REGION,
            "--project", PROJECT_ID,
            "--format", "value(serviceConfig.uri)"
        ]

        url_result = subprocess.run(url_cmd, capture_output=True, text=True)
        if url_result.returncode == 0:
            url = url_result.stdout.strip()
            print(f"\nFunction URL: {url}")
            print(f"\nTest with:")
            print(f'curl -X POST {url} -H "Content-Type: application/json" -d \'{{"query": "show me oversold stocks"}}\'')
    else:
        print("\n" + "=" * 60)
        print("DEPLOYMENT FAILED!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    deploy()
