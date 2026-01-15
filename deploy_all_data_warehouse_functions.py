"""
Deploy All Data Warehouse Cloud Functions
Deploys all new fetchers for the expanded Fintech data warehouse
"""

import subprocess
import os
import sys
import io

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ID = "aialgotradehits"
REGION = "us-central1"

FUNCTIONS = [
    {
        "name": "fundamentals-fetcher",
        "source": "cloud_function_fundamentals",
        "entry_point": "fundamentals_fetcher",
        "memory": "512MB",
        "timeout": "540s",
        "schedule": "0 7 * * 0"  # Sundays 7 AM
    },
    {
        "name": "analyst-fetcher",
        "source": "cloud_function_analyst",
        "entry_point": "analyst_fetcher",
        "memory": "512MB",
        "timeout": "540s",
        "schedule": "0 8 * * *"  # Daily 8 AM
    },
    {
        "name": "earnings-calendar-fetcher",
        "source": "cloud_function_earnings",
        "entry_point": "earnings_fetcher",
        "memory": "256MB",
        "timeout": "300s",
        "schedule": "0 6 * * *"  # Daily 6 AM
    },
    {
        "name": "market-movers-fetcher",
        "source": "cloud_function_market_movers",
        "entry_point": "market_movers_fetcher",
        "memory": "256MB",
        "timeout": "300s",
        "schedule": "0,30 9-16 * * 1-5"  # Every 30 min during market hours
    },
    {
        "name": "etf-analytics-fetcher",
        "source": "cloud_function_etf_analytics",
        "entry_point": "etf_analytics_fetcher",
        "memory": "512MB",
        "timeout": "540s",
        "schedule": "0 7 * * *"  # Daily 7 AM
    }
]

def deploy_function(func):
    """Deploy a single cloud function"""
    print(f"\n{'='*60}")
    print(f"Deploying: {func['name']}")
    print(f"{'='*60}")

    source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), func['source'])

    cmd = f"""gcloud functions deploy {func['name']} \
        --gen2 \
        --runtime=python311 \
        --region={REGION} \
        --source={source_path} \
        --entry-point={func['entry_point']} \
        --trigger-http \
        --allow-unauthenticated \
        --memory={func['memory']} \
        --timeout={func['timeout']} \
        --project={PROJECT_ID}"""

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"SUCCESS: {func['name']} deployed")
        return True
    else:
        print(f"ERROR deploying {func['name']}: {result.stderr}")
        return False


def setup_scheduler(func):
    """Setup Cloud Scheduler for a function"""
    if 'schedule' not in func:
        return True

    job_name = f"{func['name']}-scheduler"
    function_url = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{func['name']}"

    # Delete existing job if exists
    delete_cmd = f"gcloud scheduler jobs delete {job_name} --location={REGION} --project={PROJECT_ID} --quiet"
    subprocess.run(delete_cmd, shell=True, capture_output=True)

    # Create new job
    cmd = f"""gcloud scheduler jobs create http {job_name} \
        --location={REGION} \
        --schedule="{func['schedule']}" \
        --uri="{function_url}" \
        --http-method=POST \
        --project={PROJECT_ID} \
        --time-zone="America/New_York" \
        --attempt-deadline=600s"""

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Scheduler created: {job_name}")
        return True
    else:
        print(f"Warning: Scheduler setup for {job_name}: {result.stderr}")
        return False


def main():
    print("=" * 60)
    print("FINTECH DATA WAREHOUSE - FUNCTION DEPLOYMENT")
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Total Functions: {len(FUNCTIONS)}")
    print("=" * 60)

    successful = 0
    failed = 0

    for func in FUNCTIONS:
        if deploy_function(func):
            successful += 1
            setup_scheduler(func)
        else:
            failed += 1

    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(FUNCTIONS)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
