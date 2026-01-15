#!/bin/bash

# Deploy Cloud Function for Hourly Crypto Data Fetcher
# This script deploys the function to Google Cloud

gcloud functions deploy hourly-crypto-fetcher \
  --gen2 \
  --runtime=python313 \
  --region=us-central1 \
  --source=. \
  --entry-point=hourly_crypto_fetch \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --project=molten-optics-310919

echo "Cloud Function deployed successfully!"
echo "Function URL will be shown above"
