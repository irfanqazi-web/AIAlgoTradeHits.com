#!/usr/bin/env python3
"""
Deploy Robust Stock Data Fetcher to Cloud Run
With automatic retry policies and self-healing schedulers
"""

import subprocess
import os
import sys

PROJECT_ID = "aialgotradehits"
REGION = "us-central1"
FUNCTION_NAME = "twelvedata-daily-robust"

def run_cmd(cmd, capture=False):
    """Run shell command"""
    print(f"\n>>> {cmd}")
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    else:
        subprocess.run(cmd, shell=True)
        return None

def main():
    print("="*60)
    print("Deploying Robust TwelveData Fetcher")
    print("="*60)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Copy main_robust.py to main.py for deployment
    print("\n1. Preparing deployment files...")
    import shutil
    shutil.copy(
        os.path.join(script_dir, "main_robust.py"),
        os.path.join(script_dir, "main.py")
    )
    print("   Copied main_robust.py -> main.py")

    # Deploy to Cloud Run
    print("\n2. Deploying to Cloud Run...")
    deploy_cmd = f"""gcloud run deploy {FUNCTION_NAME} \
        --source {script_dir} \
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
    print("\n3. Getting service URL...")
    url = run_cmd(
        f"gcloud run services describe {FUNCTION_NAME} --region {REGION} --project {PROJECT_ID} --format 'value(status.url)'",
        capture=True
    )
    print(f"   Service URL: {url}")

    # Create/Update scheduler for stocks (daily at midnight ET)
    print("\n4. Setting up Stock scheduler (daily at midnight ET)...")
    run_cmd(f"""gcloud scheduler jobs delete twelvedata-daily-stocks-robust \
        --location {REGION} --project {PROJECT_ID} --quiet 2>/dev/null || true""")

    run_cmd(f"""gcloud scheduler jobs create http twelvedata-daily-stocks-robust \
        --location {REGION} \
        --project {PROJECT_ID} \
        --schedule "0 0 * * 1-5" \
        --time-zone "America/New_York" \
        --uri "{url}" \
        --http-method POST \
        --headers "Content-Type=application/json" \
        --message-body '{{"asset_type": "stocks"}}' \
        --attempt-deadline 900s \
        --max-retry-attempts 3 \
        --min-backoff 60s \
        --max-backoff 600s
    """)

    # Create/Update scheduler for crypto (daily at 1am ET)
    print("\n5. Setting up Crypto scheduler (daily at 1am ET)...")
    run_cmd(f"""gcloud scheduler jobs delete twelvedata-daily-crypto-robust \
        --location {REGION} --project {PROJECT_ID} --quiet 2>/dev/null || true""")

    run_cmd(f"""gcloud scheduler jobs create http twelvedata-daily-crypto-robust \
        --location {REGION} \
        --project {PROJECT_ID} \
        --schedule "0 1 * * *" \
        --time-zone "America/New_York" \
        --uri "{url}" \
        --http-method POST \
        --headers "Content-Type=application/json" \
        --message-body '{{"asset_type": "crypto"}}' \
        --attempt-deadline 900s \
        --max-retry-attempts 3 \
        --min-backoff 60s \
        --max-backoff 600s
    """)

    # Create backfill scheduler (runs at 6am ET to catch any missed data)
    print("\n6. Setting up Backfill scheduler (6am ET daily)...")
    run_cmd(f"""gcloud scheduler jobs delete twelvedata-daily-backfill \
        --location {REGION} --project {PROJECT_ID} --quiet 2>/dev/null || true""")

    run_cmd(f"""gcloud scheduler jobs create http twelvedata-daily-backfill \
        --location {REGION} \
        --project {PROJECT_ID} \
        --schedule "0 6 * * 1-5" \
        --time-zone "America/New_York" \
        --uri "{url}" \
        --http-method POST \
        --headers "Content-Type=application/json" \
        --message-body '{{"asset_type": "all", "backfill": true}}' \
        --attempt-deadline 900s \
        --max-retry-attempts 3 \
        --min-backoff 60s \
        --max-backoff 600s
    """)

    print("\n" + "="*60)
    print("DEPLOYMENT COMPLETE!")
    print("="*60)
    print(f"\nService URL: {url}")
    print("\nSchedulers configured:")
    print("  - twelvedata-daily-stocks-robust: 12:00 AM ET (Mon-Fri)")
    print("  - twelvedata-daily-crypto-robust: 1:00 AM ET (Daily)")
    print("  - twelvedata-daily-backfill: 6:00 AM ET (Mon-Fri)")
    print("\nAll schedulers have:")
    print("  - 3 automatic retry attempts")
    print("  - 15-minute timeout")
    print("  - Exponential backoff (60s-600s)")
    print("\nTo trigger manually:")
    print(f"  curl -X POST {url} -H 'Content-Type: application/json' -d '{{\"asset_type\": \"all\"}}'")


if __name__ == "__main__":
    main()
