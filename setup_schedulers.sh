#!/bin/bash
# Setup TwelveData Cloud Schedulers for aialgotradehits
# Run this in Google Cloud Shell

PROJECT_ID="aialgotradehits"
REGION="us-central1"
FUNCTION_URL="https://${REGION}-${PROJECT_ID}.cloudfunctions.net/twelvedata-fetcher"

echo "============================================================"
echo "SETTING UP TWELVEDATA CLOUD SCHEDULERS"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Function URL: $FUNCTION_URL"
echo "============================================================"

# Helper function to create scheduler
create_scheduler() {
    local name=$1
    local schedule=$2
    local description=$3
    local params=$4

    echo ""
    echo "Creating scheduler: $name"
    echo "  Schedule: $schedule"

    # Delete if exists
    gcloud scheduler jobs delete $name \
        --location=$REGION \
        --project=$PROJECT_ID \
        --quiet 2>/dev/null

    # Create scheduler
    gcloud scheduler jobs create http $name \
        --location=$REGION \
        --schedule="$schedule" \
        --uri="${FUNCTION_URL}?${params}" \
        --http-method=GET \
        --time-zone="America/New_York" \
        --description="$description" \
        --project=$PROJECT_ID \
        --attempt-deadline=540s \
        --quiet

    if [ $? -eq 0 ]; then
        echo "  SUCCESS: $name created"
    else
        echo "  FAILED: $name"
    fi
}

# Weekly data - Sunday at midnight
create_scheduler "twelvedata-weekly-all" \
    "0 0 * * 0" \
    "Fetch weekly data for all asset types" \
    "asset_type=all&timeframe=weekly"

# Daily data - Every day at midnight ET (staggered by 5 minutes)
create_scheduler "twelvedata-daily-stocks" \
    "0 0 * * *" \
    "Fetch daily stocks data" \
    "asset_type=stocks&timeframe=daily"

create_scheduler "twelvedata-daily-crypto" \
    "5 0 * * *" \
    "Fetch daily crypto data" \
    "asset_type=crypto&timeframe=daily"

create_scheduler "twelvedata-daily-forex" \
    "10 0 * * *" \
    "Fetch daily forex data" \
    "asset_type=forex&timeframe=daily"

create_scheduler "twelvedata-daily-etfs" \
    "15 0 * * *" \
    "Fetch daily ETFs data" \
    "asset_type=etfs&timeframe=daily"

create_scheduler "twelvedata-daily-indices" \
    "20 0 * * *" \
    "Fetch daily indices data" \
    "asset_type=indices&timeframe=daily"

create_scheduler "twelvedata-daily-commodities" \
    "25 0 * * *" \
    "Fetch daily commodities data" \
    "asset_type=commodities&timeframe=daily"

# Hourly data - Every hour for stocks and crypto
create_scheduler "twelvedata-hourly-stocks" \
    "0 * * * *" \
    "Fetch hourly stocks data" \
    "asset_type=stocks&timeframe=hourly"

create_scheduler "twelvedata-hourly-crypto" \
    "5 * * * *" \
    "Fetch hourly crypto data" \
    "asset_type=crypto&timeframe=hourly"

# 5-minute data during market hours
create_scheduler "twelvedata-5min-stocks" \
    "*/5 9-16 * * 1-5" \
    "Fetch 5-minute stocks data during market hours" \
    "asset_type=stocks&timeframe=5min"

create_scheduler "twelvedata-5min-crypto" \
    "*/5 * * * *" \
    "Fetch 5-minute crypto data 24/7" \
    "asset_type=crypto&timeframe=5min"

echo ""
echo "============================================================"
echo "SCHEDULER SETUP COMPLETE"
echo "============================================================"

# List all schedulers
echo ""
echo "All schedulers:"
gcloud scheduler jobs list --location=$REGION --project=$PROJECT_ID

echo ""
echo "To manually trigger a scheduler, run:"
echo "gcloud scheduler jobs run [JOB_NAME] --location=$REGION --project=$PROJECT_ID"
