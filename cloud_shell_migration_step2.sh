#!/bin/bash
# ============================================================
# STEP 2: CREATE BIGQUERY DATASETS
# Run this in GCP Cloud Shell (project: aialgotradehits)
# ============================================================

PROJECT_ID="aialgotradehits"
LOCATION="US"

echo "Creating BigQuery datasets..."

# Main trading data dataset
bq mk --project_id=$PROJECT_ID --location=$LOCATION --dataset crypto_trading_data

# Unified trading data dataset
bq mk --project_id=$PROJECT_ID --location=$LOCATION --dataset trading_data_unified

echo ""
echo "✅ STEP 2 COMPLETE: BigQuery datasets created!"
echo ""
echo "Verify at: https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
echo ""
echo "Run STEP 3 next..."
