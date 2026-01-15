"""
Deploy Weekly Stock and Crypto Functions to GCP
Creates Cloud Functions and Schedulers for weekly data collection
"""

import subprocess
import sys

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"SUCCESS: {description}")
        if result.stdout:
            print(result.stdout[:500])
    else:
        print(f"FAILED: {description}")
        print(f"Error: {result.stderr[:500] if result.stderr else 'Unknown error'}")

    return result.returncode == 0


def deploy_weekly_stock_function():
    """Deploy weekly stock fetcher function"""
    cmd = f"""gcloud functions deploy weekly-stock-fetcher \
        --gen2 \
        --runtime=python312 \
        --region={REGION} \
        --source=cloud_function_weekly_stocks \
        --entry-point=weekly_stock_fetcher \
        --trigger-http \
        --allow-unauthenticated \
        --memory=2048MB \
        --timeout=3600s \
        --max-instances=1 \
        --project={PROJECT_ID}"""

    return run_command(cmd, "Deploy weekly-stock-fetcher function")


def deploy_weekly_crypto_function():
    """Deploy weekly crypto fetcher function"""
    cmd = f"""gcloud functions deploy weekly-crypto-fetcher \
        --gen2 \
        --runtime=python312 \
        --region={REGION} \
        --source=cloud_function_weekly_cryptos \
        --entry-point=weekly_crypto_fetcher \
        --trigger-http \
        --allow-unauthenticated \
        --memory=1024MB \
        --timeout=1800s \
        --max-instances=1 \
        --project={PROJECT_ID}"""

    return run_command(cmd, "Deploy weekly-crypto-fetcher function")


def create_weekly_stock_scheduler():
    """Create scheduler for weekly stock updates - runs Saturday 4 AM ET"""
    # Delete existing scheduler if exists
    delete_cmd = f"""gcloud scheduler jobs delete weekly-stock-fetch-job \
        --location={REGION} \
        --project={PROJECT_ID} \
        --quiet"""
    subprocess.run(delete_cmd, shell=True, capture_output=True)

    # Create new scheduler - Saturday 4 AM ET (cron: minute hour day-of-month month day-of-week)
    # 6 = Saturday
    cmd = f"""gcloud scheduler jobs create http weekly-stock-fetch-job \
        --location={REGION} \
        --schedule="0 4 * * 6" \
        --time-zone="America/New_York" \
        --uri="https://weekly-stock-fetcher-252370699783.{REGION}.run.app" \
        --http-method=GET \
        --attempt-deadline=3600s \
        --project={PROJECT_ID} \
        --description="Weekly US stocks data collection - runs Saturday 4 AM ET" """

    return run_command(cmd, "Create weekly-stock-fetch-job scheduler")


def create_weekly_crypto_scheduler():
    """Create scheduler for weekly crypto updates - runs Saturday 4 AM ET"""
    # Delete existing scheduler if exists
    delete_cmd = f"""gcloud scheduler jobs delete weekly-crypto-fetch-job \
        --location={REGION} \
        --project={PROJECT_ID} \
        --quiet"""
    subprocess.run(delete_cmd, shell=True, capture_output=True)

    # Create new scheduler - Saturday 4 AM ET (runs 30 min after stocks start)
    cmd = f"""gcloud scheduler jobs create http weekly-crypto-fetch-job \
        --location={REGION} \
        --schedule="30 4 * * 6" \
        --time-zone="America/New_York" \
        --uri="https://weekly-crypto-fetcher-252370699783.{REGION}.run.app" \
        --http-method=GET \
        --attempt-deadline=1800s \
        --project={PROJECT_ID} \
        --description="Weekly crypto data collection - runs Saturday 4:30 AM ET" """

    return run_command(cmd, "Create weekly-crypto-fetch-job scheduler")


def list_all_schedulers():
    """List all schedulers"""
    cmd = f"gcloud scheduler jobs list --location={REGION} --project={PROJECT_ID}"
    return run_command(cmd, "List all scheduler jobs")


if __name__ == "__main__":
    print("="*60)
    print("DEPLOYING WEEKLY DATA COLLECTION FUNCTIONS")
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print("="*60)

    # Ask user what to deploy
    print("\nOptions:")
    print("1. Deploy weekly stock function only")
    print("2. Deploy weekly crypto function only")
    print("3. Deploy both functions")
    print("4. Create schedulers only")
    print("5. Deploy everything (functions + schedulers)")
    print("6. List existing schedulers")

    choice = input("\nEnter choice (1-6): ").strip()

    if choice == '1':
        deploy_weekly_stock_function()
    elif choice == '2':
        deploy_weekly_crypto_function()
    elif choice == '3':
        deploy_weekly_stock_function()
        deploy_weekly_crypto_function()
    elif choice == '4':
        create_weekly_stock_scheduler()
        create_weekly_crypto_scheduler()
    elif choice == '5':
        print("\nDeploying all functions and schedulers...")
        deploy_weekly_stock_function()
        deploy_weekly_crypto_function()
        create_weekly_stock_scheduler()
        create_weekly_crypto_scheduler()
        list_all_schedulers()
    elif choice == '6':
        list_all_schedulers()
    else:
        print("Invalid choice")

    print("\n" + "="*60)
    print("DEPLOYMENT COMPLETE")
    print("="*60)
