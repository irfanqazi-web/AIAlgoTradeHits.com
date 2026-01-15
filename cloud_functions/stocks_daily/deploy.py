"""
Deploy Daily Stock Fetcher Cloud Function
"""
import subprocess
import sys

PROJECT_ID = "cryptobot-462709"
FUNCTION_NAME = "daily-stocks-fetcher"
REGION = "us-central1"
RUNTIME = "python311"
ENTRY_POINT = "main"
MEMORY = "1GB"
TIMEOUT = "540s"

def deploy_function():
    """Deploy the Cloud Function"""
    print("=" * 80)
    print(f"Deploying {FUNCTION_NAME} to {PROJECT_ID}")
    print("=" * 80)

    cmd = [
        "gcloud", "functions", "deploy", FUNCTION_NAME,
        f"--gen2",
        f"--runtime={RUNTIME}",
        f"--region={REGION}",
        f"--source=.",
        f"--entry-point={ENTRY_POINT}",
        f"--trigger-http",
        f"--memory={MEMORY}",
        f"--timeout={TIMEOUT}",
        f"--project={PROJECT_ID}",
        "--allow-unauthenticated"
    ]

    print(f"\nRunning command:")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode == 0:
        print("\n" + "=" * 80)
        print(f"✅ SUCCESS! {FUNCTION_NAME} deployed")
        print("=" * 80)
        print(f"\nFunction URL: https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}")
    else:
        print("\n" + "=" * 80)
        print(f"❌ FAILED to deploy {FUNCTION_NAME}")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    deploy_function()
