#!/usr/bin/env python3
"""
Deploy Error-Tolerant Asset Fetcher and Set Up All Schedulers
Creates robust schedulers for all 7 asset types with automatic retry
"""

import subprocess
import os
import sys

PROJECT_ID = "aialgotradehits"
REGION = "us-central1"
FUNCTION_NAME = "twelvedata-all-assets"

# Scheduler configurations for all 7 asset types
SCHEDULERS = [
    {
        'name': 'daily-stocks-robust',
        'schedule': '0 0 * * 1-5',  # Weekdays at midnight ET
        'timezone': 'America/New_York',
        'body': '{"asset_type": "stocks"}',
        'description': 'Daily stock data fetch (Mon-Fri)'
    },
    {
        'name': 'daily-crypto-robust',
        'schedule': '0 1 * * *',  # Daily at 1am ET
        'timezone': 'America/New_York',
        'body': '{"asset_type": "crypto"}',
        'description': 'Daily crypto data fetch'
    },
    {
        'name': 'daily-etfs-robust',
        'schedule': '15 0 * * 1-5',  # Weekdays at 00:15 ET
        'timezone': 'America/New_York',
        'body': '{"asset_type": "etfs"}',
        'description': 'Daily ETF data fetch (Mon-Fri)'
    },
    {
        'name': 'daily-forex-robust',
        'schedule': '30 0 * * 1-5',  # Weekdays at 00:30 ET
        'timezone': 'America/New_York',
        'body': '{"asset_type": "forex"}',
        'description': 'Daily forex data fetch (Mon-Fri)'
    },
    {
        'name': 'daily-indices-robust',
        'schedule': '45 0 * * 1-5',  # Weekdays at 00:45 ET
        'timezone': 'America/New_York',
        'body': '{"asset_type": "indices"}',
        'description': 'Daily indices data fetch (Mon-Fri)'
    },
    {
        'name': 'daily-commodities-robust',
        'schedule': '0 2 * * *',  # Daily at 2am ET
        'timezone': 'America/New_York',
        'body': '{"asset_type": "commodities"}',
        'description': 'Daily commodities data fetch'
    },
    {
        'name': 'daily-all-backfill',
        'schedule': '0 6 * * 0',  # Sundays at 6am ET
        'timezone': 'America/New_York',
        'body': '{"asset_type": "all", "backfill": true}',
        'description': 'Weekly full backfill all assets'
    }
]


def run_cmd(cmd, capture=False):
    """Run shell command"""
    print(f"\n>>> {cmd[:100]}...")
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    else:
        subprocess.run(cmd, shell=True)
        return None


def main():
    print("=" * 70)
    print("Deploying Error-Tolerant TwelveData Fetcher")
    print("All 7 Asset Types with Robust Schedulers")
    print("=" * 70)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Deploy to Cloud Run
    print("\n1. Deploying Cloud Function to Cloud Run...")
    deploy_cmd = f"""gcloud run deploy {FUNCTION_NAME} \
        --source "{script_dir}" \
        --project {PROJECT_ID} \
        --region {REGION} \
        --platform managed \
        --allow-unauthenticated \
        --memory 4Gi \
        --cpu 2 \
        --timeout 900 \
        --min-instances 0 \
        --max-instances 5 \
        --set-env-vars "GCP_PROJECT={PROJECT_ID}"
    """
    run_cmd(deploy_cmd)

    # Get the service URL
    print("\n2. Getting service URL...")
    url = run_cmd(
        f'gcloud run services describe {FUNCTION_NAME} --region {REGION} --project {PROJECT_ID} --format "value(status.url)"',
        capture=True
    )
    print(f"   Service URL: {url}")

    if not url:
        print("ERROR: Could not get service URL. Deployment may have failed.")
        return

    # Create/Update schedulers
    print("\n3. Setting up schedulers...")

    for i, sched in enumerate(SCHEDULERS):
        print(f"\n   {i+1}/{len(SCHEDULERS)}: {sched['name']}")

        # Delete existing scheduler if exists
        run_cmd(f"""gcloud scheduler jobs delete {sched['name']} \
            --location {REGION} --project {PROJECT_ID} --quiet 2>/dev/null || true""")

        # Create new scheduler with retry policies
        create_cmd = f"""gcloud scheduler jobs create http {sched['name']} \
            --location {REGION} \
            --project {PROJECT_ID} \
            --schedule "{sched['schedule']}" \
            --time-zone "{sched['timezone']}" \
            --uri "{url}" \
            --http-method POST \
            --headers "Content-Type=application/json" \
            --message-body '{sched['body']}' \
            --attempt-deadline 900s \
            --max-retry-attempts 3 \
            --min-backoff 60s \
            --max-backoff 600s \
            --description "{sched['description']}"
        """
        run_cmd(create_cmd)

    # Summary
    print("\n" + "=" * 70)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 70)
    print(f"\nService URL: {url}")
    print("\nSchedulers configured:")
    for sched in SCHEDULERS:
        print(f"  - {sched['name']}: {sched['schedule']} ({sched['description']})")

    print("\nAll schedulers have:")
    print("  - 3 automatic retry attempts")
    print("  - 15-minute timeout")
    print("  - Exponential backoff (60s-600s)")

    print("\nManual triggers:")
    print(f"  # All assets:")
    print(f"  curl -X POST {url} -H 'Content-Type: application/json' -d '{{\"asset_type\": \"all\"}}'")
    print(f"\n  # Specific asset:")
    print(f"  curl -X POST {url} -H 'Content-Type: application/json' -d '{{\"asset_type\": \"stocks\"}}'")
    print(f"\n  # Backfill mode:")
    print(f"  curl -X POST {url} -H 'Content-Type: application/json' -d '{{\"asset_type\": \"all\", \"backfill\": true}}'")


if __name__ == "__main__":
    main()
