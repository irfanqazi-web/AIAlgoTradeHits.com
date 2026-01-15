#!/bin/bash
# Deploy Cloud Functions to aialgotradehits
PROJECT=aialgotradehits
REGION=us-central1

echo "Deploying Cloud Functions to $PROJECT..."

# Deploy daily crypto fetcher
echo "Deploying daily-crypto-fetcher..."
cd ~/cloud_function_daily
gcloud functions deploy daily-crypto-fetcher \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=fetch_daily_crypto \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --project=$PROJECT

# Deploy hourly crypto fetcher
echo "Deploying hourly-crypto-fetcher..."
cd ~/cloud_function_hourly
gcloud functions deploy hourly-crypto-fetcher \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=fetch_hourly_crypto \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --project=$PROJECT

# Deploy 5min crypto fetcher
echo "Deploying fivemin-crypto-fetcher..."
cd ~/cloud_function_5min
gcloud functions deploy fivemin-crypto-fetcher \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=fetch_5min_top10 \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --project=$PROJECT

# Deploy daily stock fetcher
echo "Deploying daily-stock-fetcher..."
cd ~/cloud_function_daily_stocks
gcloud functions deploy daily-stock-fetcher \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=fetch_daily_stocks \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --project=$PROJECT

# Deploy trading API
echo "Deploying trading-api..."
cd ~/cloud_function_api
gcloud functions deploy trading-api \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=trading_api \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=300s \
  --memory=512MB \
  --project=$PROJECT

echo "Done! Functions deployed to $PROJECT"
