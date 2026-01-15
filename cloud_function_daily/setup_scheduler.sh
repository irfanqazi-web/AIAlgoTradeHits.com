#!/bin/bash

# Setup Google Cloud Scheduler to trigger the Cloud Function daily at midnight
# Run this AFTER deploying the Cloud Function

# Configuration
PROJECT_ID="molten-optics-310919"
REGION="us-central1"
JOB_NAME="daily-crypto-fetch-job"
FUNCTION_URL="YOUR_CLOUD_FUNCTION_URL"  # Replace with actual URL from deployment

echo "Setting up Cloud Scheduler for daily midnight runs..."

# Create the Cloud Scheduler job
gcloud scheduler jobs create http $JOB_NAME \
  --location=$REGION \
  --schedule="0 0 * * *" \
  --uri=$FUNCTION_URL \
  --http-method=GET \
  --time-zone="America/New_York" \
  --project=$PROJECT_ID

echo "Cloud Scheduler job created successfully!"
echo "Job will run daily at midnight (00:00) Eastern Time"
echo ""
echo "To manually trigger the job, run:"
echo "gcloud scheduler jobs run $JOB_NAME --location=$REGION"
echo ""
echo "To view job details:"
echo "gcloud scheduler jobs describe $JOB_NAME --location=$REGION"
echo ""
echo "To view job execution history:"
echo "gcloud scheduler jobs describe $JOB_NAME --location=$REGION"
