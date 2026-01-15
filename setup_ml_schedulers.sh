#!/bin/bash
# ML Pipeline Cloud Schedulers Setup
# Run this script to create/update ML schedulers in GCP

PROJECT_ID="aialgotradehits"
REGION="us-central1"
API_URL="https://trading-api-1075463475276.us-central1.run.app"

echo "Setting up ML Cloud Schedulers..."

# 1. Daily Feature Refresh - 4:00 AM ET
echo "Creating ml-feature-refresh-daily..."
gcloud scheduler jobs create http ml-feature-refresh-daily \
    --location=$REGION \
    --schedule="0 4 * * *" \
    --uri="$API_URL/api/ml/refresh-features" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --description="Daily ML feature table refresh at 4 AM ET" \
    --project=$PROJECT_ID 2>/dev/null \
    || gcloud scheduler jobs update http ml-feature-refresh-daily \
    --location=$REGION \
    --schedule="0 4 * * *" \
    --uri="$API_URL/api/ml/refresh-features" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --project=$PROJECT_ID

# 2. Weekly Model Retrain - Sunday 2:00 AM ET
echo "Creating ml-model-retrain-weekly..."
gcloud scheduler jobs create http ml-model-retrain-weekly \
    --location=$REGION \
    --schedule="0 2 * * 0" \
    --uri="$API_URL/api/ml/retrain" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --description="Weekly ML model retraining on Sunday 2 AM ET" \
    --project=$PROJECT_ID 2>/dev/null \
    || gcloud scheduler jobs update http ml-model-retrain-weekly \
    --location=$REGION \
    --schedule="0 2 * * 0" \
    --uri="$API_URL/api/ml/retrain" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --project=$PROJECT_ID

# 3. Daily Predictions - 4:30 AM ET
echo "Creating ml-predictions-daily..."
gcloud scheduler jobs create http ml-predictions-daily \
    --location=$REGION \
    --schedule="30 4 * * *" \
    --uri="$API_URL/api/ml/generate-predictions" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --description="Daily ML predictions at 4:30 AM ET" \
    --project=$PROJECT_ID 2>/dev/null \
    || gcloud scheduler jobs update http ml-predictions-daily \
    --location=$REGION \
    --schedule="30 4 * * *" \
    --uri="$API_URL/api/ml/generate-predictions" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --project=$PROJECT_ID

# 4. Drift Detection - Every 6 hours
echo "Creating ml-drift-detection..."
gcloud scheduler jobs create http ml-drift-detection \
    --location=$REGION \
    --schedule="0 */6 * * *" \
    --uri="$API_URL/api/ml/drift-check" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --description="Data drift detection every 6 hours" \
    --project=$PROJECT_ID 2>/dev/null \
    || gcloud scheduler jobs update http ml-drift-detection \
    --location=$REGION \
    --schedule="0 */6 * * *" \
    --uri="$API_URL/api/ml/drift-check" \
    --http-method=POST \
    --time-zone="America/New_York" \
    --project=$PROJECT_ID

echo ""
echo "Scheduler setup complete. Verify with:"
echo "gcloud scheduler jobs list --project=$PROJECT_ID --location=$REGION"
