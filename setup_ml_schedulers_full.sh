#!/bin/bash
# ML Pipeline Cloud Scheduler Setup
# Run this script in Google Cloud Shell

PROJECT_ID="aialgotradehits"
REGION="us-central1"


# Run ML inference on daily data
gcloud scheduler jobs create http ml-daily-inference \
  --location=us-central1 \
  --schedule="30 1 * * *" \
  --uri="https://us-central1-aialgotradehits.cloudfunctions.net/ml-inference" \
  --http-method=POST \
  --message-body='{"asset_types": ["stocks", "crypto", "etf"], "confidence_threshold": 0.55}' \
  --oidc-service-account-email=aialgotradehits@appspot.gserviceaccount.com \
  --project=aialgotradehits \
  2>/dev/null || echo "Job ml-daily-inference already exists"

# Check model performance and detect drift
gcloud scheduler jobs create http ml-model-monitoring \
  --location=us-central1 \
  --schedule="0 6 * * *" \
  --uri="https://us-central1-aialgotradehits.cloudfunctions.net/ml-monitoring" \
  --http-method=POST \
  --message-body='{"check_drift": true, "alert_threshold": 0.85}' \
  --oidc-service-account-email=aialgotradehits@appspot.gserviceaccount.com \
  --project=aialgotradehits \
  2>/dev/null || echo "Job ml-model-monitoring already exists"

# Retrain models weekly with new data
gcloud scheduler jobs create http ml-weekly-retrain \
  --location=us-central1 \
  --schedule="0 2 * * 0" \
  --uri="https://us-central1-aialgotradehits.cloudfunctions.net/ml-retrain" \
  --http-method=POST \
  --message-body='{"models": ["xgboost_walk_forward"], "validation_window_days": 30}' \
  --oidc-service-account-email=aialgotradehits@appspot.gserviceaccount.com \
  --project=aialgotradehits \
  2>/dev/null || echo "Job ml-weekly-retrain already exists"

# Daily backtest validation
gcloud scheduler jobs create http ml-backtest-daily \
  --location=us-central1 \
  --schedule="0 7 * * *" \
  --uri="https://us-central1-aialgotradehits.cloudfunctions.net/ml-backtest" \
  --http-method=POST \
  --message-body='{"lookback_days": 7, "confidence_levels": ["HIGH", "MEDIUM"]}' \
  --oidc-service-account-email=aialgotradehits@appspot.gserviceaccount.com \
  --project=aialgotradehits \
  2>/dev/null || echo "Job ml-backtest-daily already exists"
