#!/bin/bash
cd ~/cloud_function_daily
gcloud functions deploy daily-crypto-fetcher --gen2 --runtime=python311 --region=us-central1 --source=. --entry-point=daily_crypto_fetch --trigger-http --allow-unauthenticated --timeout=540s --memory=512MB --project=aialgotradehits
