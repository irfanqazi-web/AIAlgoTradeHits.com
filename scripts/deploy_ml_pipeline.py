#!/usr/bin/env python3
"""
ML Pipeline Complete Deployment Script
=======================================
Deploys:
1. ML Operations Cloud Function
2. Cloud Schedulers for automated operations
3. Updates API endpoints
4. Configures alert notifications

Run this script to complete the ML pipeline deployment.
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import subprocess
import json
from datetime import datetime

PROJECT_ID = 'aialgotradehits'
REGION = 'us-central1'
FUNCTION_NAME = 'ml-operations'

print("=" * 70)
print("ML PIPELINE COMPLETE DEPLOYMENT")
print("=" * 70)
print(f"Started: {datetime.now()}")
print(f"Project: {PROJECT_ID}")
print(f"Region: {REGION}")

# =============================================================================
# Step 1: Deploy ML Operations Cloud Function
# =============================================================================
print("\n" + "=" * 70)
print("[1] DEPLOYING ML OPERATIONS CLOUD FUNCTION")
print("=" * 70)

deploy_function_cmd = f"""
gcloud functions deploy {FUNCTION_NAME} \
  --gen2 \
  --runtime=python312 \
  --region={REGION} \
  --source=cloud_function_ml_ops \
  --entry-point=ml_operations \
  --trigger-http \
  --allow-unauthenticated \
  --memory=2048MB \
  --timeout=540s \
  --project={PROJECT_ID}
"""

print(f"\nCommand:\n{deploy_function_cmd}")
print("\nExecuting deployment...")

try:
    result = subprocess.run(
        deploy_function_cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd='C:/1AITrading/Trading'
    )
    if result.returncode == 0:
        print("  Cloud Function deployed successfully!")
        print(result.stdout)
    else:
        print(f"  Deployment error: {result.stderr}")
except Exception as e:
    print(f"  Deployment failed: {e}")

# Get function URL
FUNCTION_URL = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}"
print(f"\nFunction URL: {FUNCTION_URL}")

# =============================================================================
# Step 2: Create Cloud Schedulers
# =============================================================================
print("\n" + "=" * 70)
print("[2] CREATING CLOUD SCHEDULERS")
print("=" * 70)

schedulers = [
    {
        'name': 'ml-daily-inference',
        'schedule': '30 6 * * *',  # 6:30 AM UTC (1:30 AM ET)
        'operation': 'inference',
        'body': {"operation": "inference", "asset_types": ["stocks", "crypto", "etf"], "confidence_threshold": 0.55},
        'description': 'Run ML inference on daily market data'
    },
    {
        'name': 'ml-model-monitoring',
        'schedule': '0 11 * * *',  # 11 AM UTC (6 AM ET)
        'operation': 'monitoring',
        'body': {"operation": "monitoring", "alert_threshold": 0.85},
        'description': 'Check model performance and detect drift'
    },
    {
        'name': 'ml-weekly-retrain',
        'schedule': '0 7 * * 0',  # Sunday 7 AM UTC (2 AM ET)
        'operation': 'retrain',
        'body': {"operation": "retrain", "validation_window_days": 30},
        'description': 'Weekly model retraining with latest data'
    },
    {
        'name': 'ml-daily-backtest',
        'schedule': '0 12 * * *',  # 12 PM UTC (7 AM ET)
        'operation': 'backtest',
        'body': {"operation": "backtest", "lookback_days": 7, "confidence_levels": ["HIGH", "MEDIUM"]},
        'description': 'Daily backtest validation'
    }
]

for scheduler in schedulers:
    print(f"\n  Creating scheduler: {scheduler['name']}")
    print(f"    Schedule: {scheduler['schedule']}")
    print(f"    Operation: {scheduler['operation']}")

    # Delete existing scheduler if exists
    delete_cmd = f"""
    gcloud scheduler jobs delete {scheduler['name']} \
      --location={REGION} \
      --project={PROJECT_ID} \
      --quiet 2>/dev/null || true
    """

    create_cmd = f"""
    gcloud scheduler jobs create http {scheduler['name']} \
      --location={REGION} \
      --schedule="{scheduler['schedule']}" \
      --uri="{FUNCTION_URL}" \
      --http-method=POST \
      --headers="Content-Type=application/json" \
      --message-body='{json.dumps(scheduler['body'])}' \
      --oidc-service-account-email={PROJECT_ID}@appspot.gserviceaccount.com \
      --project={PROJECT_ID} \
      --description="{scheduler['description']}"
    """

    try:
        # Delete existing
        subprocess.run(delete_cmd, shell=True, capture_output=True)

        # Create new
        result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"    Created successfully")
        else:
            print(f"    Error: {result.stderr[:200] if result.stderr else 'Unknown error'}")
    except Exception as e:
        print(f"    Failed: {e}")

# =============================================================================
# Step 3: Verify Deployment
# =============================================================================
print("\n" + "=" * 70)
print("[3] VERIFYING DEPLOYMENT")
print("=" * 70)

# List schedulers
print("\n  Active Schedulers:")
list_cmd = f"gcloud scheduler jobs list --location={REGION} --project={PROJECT_ID} --format=json"
try:
    result = subprocess.run(list_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        jobs = json.loads(result.stdout)
        for job in jobs:
            name = job.get('name', '').split('/')[-1]
            schedule = job.get('schedule', 'N/A')
            state = job.get('state', 'UNKNOWN')
            print(f"    - {name}: {schedule} ({state})")
except Exception as e:
    print(f"    Error listing schedulers: {e}")

# Test function
print("\n  Testing ML Operations Function...")
test_cmd = f'curl -s -X POST "{FUNCTION_URL}" -H "Content-Type: application/json" -d \'{{"operation": "status"}}\''
try:
    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        response = json.loads(result.stdout)
        print(f"    Function Status: OK")
        if 'pipeline_status' in response:
            print(f"    Pipeline Status: {len(response['pipeline_status'])} entries")
    else:
        print(f"    Function test error: {result.stderr}")
except Exception as e:
    print(f"    Function test failed: {e}")

# =============================================================================
# Step 4: Update Trading API (optional - already has ML endpoints)
# =============================================================================
print("\n" + "=" * 70)
print("[4] TRADING API STATUS")
print("=" * 70)

API_URL = "https://trading-api-1075463475276.us-central1.run.app"
print(f"\n  API URL: {API_URL}")
print("\n  ML Endpoints:")
print("    - GET /api/ml/predictions")
print("    - GET /api/ml/high-confidence-signals")
print("    - GET /api/ml/walk-forward-summary")
print("    - GET /api/ml/symbol-prediction/<symbol>")

# Test API
print("\n  Testing API...")
api_test_cmd = f'curl -s "{API_URL}/health"'
try:
    result = subprocess.run(api_test_cmd, shell=True, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print(f"    API Health: OK")
    else:
        print(f"    API may need redeployment")
except Exception as e:
    print(f"    API test error: {e}")

# =============================================================================
# Step 5: Create Alert Notification View
# =============================================================================
print("\n" + "=" * 70)
print("[5] CONFIGURING ALERT NOTIFICATIONS")
print("=" * 70)

from google.cloud import bigquery
bq_client = bigquery.Client(project=PROJECT_ID)

alert_view_query = f"""
CREATE OR REPLACE VIEW `{PROJECT_ID}.ml_models.v_active_alerts` AS
SELECT
    alert_id,
    alert_time,
    asset_type,
    alert_type,
    severity,
    message,
    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), alert_time, HOUR) as hours_since_alert
FROM `{PROJECT_ID}.ml_models.model_drift_alerts`
WHERE NOT is_resolved
  AND alert_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY alert_time DESC
"""

try:
    bq_client.query(alert_view_query).result()
    print("  Created: v_active_alerts view")
except Exception as e:
    print(f"  Alert view error: {e}")

# Check for active alerts
alerts_query = f"""
SELECT COUNT(*) as alert_count,
       SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical_count
FROM `{PROJECT_ID}.ml_models.model_drift_alerts`
WHERE NOT is_resolved
"""
try:
    result = list(bq_client.query(alerts_query).result())[0]
    print(f"  Active Alerts: {result.alert_count} ({result.critical_count} critical)")
except Exception as e:
    print(f"  Alert check error: {e}")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 70)
print("DEPLOYMENT COMPLETE")
print("=" * 70)

print(f"""
SUMMARY
=======

1. ML Operations Cloud Function
   URL: {FUNCTION_URL}
   Operations: inference, monitoring, retrain, backtest, status

2. Cloud Schedulers
   - ml-daily-inference: 6:30 AM UTC daily
   - ml-model-monitoring: 11:00 AM UTC daily
   - ml-weekly-retrain: Sunday 7:00 AM UTC
   - ml-daily-backtest: 12:00 PM UTC daily

3. Trading API
   URL: {API_URL}
   ML Endpoints: /api/ml/predictions, /api/ml/high-confidence-signals

4. Monitoring
   - Check: v_pipeline_status view
   - Alerts: v_active_alerts view

MANUAL TESTING
==============

# Test ML inference
curl -X POST "{FUNCTION_URL}" -H "Content-Type: application/json" -d '{{"operation": "inference"}}'

# Test model monitoring
curl -X POST "{FUNCTION_URL}" -H "Content-Type: application/json" -d '{{"operation": "monitoring"}}'

# Get pipeline status
curl -X POST "{FUNCTION_URL}" -H "Content-Type: application/json" -d '{{"operation": "status"}}'

# Get predictions from API
curl "{API_URL}/api/ml/high-confidence-signals?asset_type=crypto"

Completed: {datetime.now()}
""")
