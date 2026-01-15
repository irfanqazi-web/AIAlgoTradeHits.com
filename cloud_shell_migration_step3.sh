#!/bin/bash
# ============================================================
# STEP 3: COPY BIGQUERY TABLES FROM PERSONAL TO CORPORATE
# Run this in GCP Cloud Shell (project: aialgotradehits)
# ============================================================

SOURCE_PROJECT="cryptobot-462709"
TARGET_PROJECT="aialgotradehits"

echo "Copying BigQuery tables from $SOURCE_PROJECT to $TARGET_PROJECT..."
echo "This may take 10-15 minutes depending on data size..."
echo ""

# First, we need to grant the corporate project access to read from personal project
# This requires running from the personal account or granting cross-project access

echo "NOTE: You need to grant BigQuery Data Viewer access to the corporate service account"
echo "on the personal project first."
echo ""
echo "Option A: Run these commands from your personal account's Cloud Shell:"
echo ""
echo "gcloud projects add-iam-policy-binding cryptobot-462709 \\"
echo "  --member='serviceAccount:$TARGET_PROJECT@appspot.gserviceaccount.com' \\"
echo "  --role='roles/bigquery.dataViewer'"
echo ""
echo "Option B: Use BigQuery Data Transfer or export/import via GCS"
echo ""

# Alternative: Export to GCS and import
# For now, let's try direct copy (requires cross-project access)

echo "Attempting direct table copy..."
echo ""

# Main dataset tables - crypto_trading_data
TABLES=(
  "crypto_analysis"
  "crypto_hourly_data"
  "crypto_5min_top10_gainers"
  "stock_analysis"
  "stock_hourly_data"
  "stock_5min_top10_gainers"
  "cryptos_weekly_summary"
  "scheduler_execution_log"
  "search_history"
)

for table in "${TABLES[@]}"; do
  echo "Copying $table..."
  bq cp --force $SOURCE_PROJECT:crypto_trading_data.$table $TARGET_PROJECT:crypto_trading_data.$table 2>/dev/null || echo "  - Could not copy $table (may need cross-project access)"
done

echo ""
echo "✅ STEP 3 attempted. Check BigQuery console for results."
echo ""
echo "If tables didn't copy, we'll create fresh schemas and let schedulers populate data."
