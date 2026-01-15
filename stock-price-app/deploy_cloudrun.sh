#!/bin/bash
# Deploy Trading App to Google Cloud Run
# Project: aialgotradehits

PROJECT_ID="aialgotradehits"
REGION="us-central1"
SERVICE_NAME="trading-app"

echo "========================================"
echo "Deploying Trading App to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "========================================"

# Build and deploy using Cloud Build
echo "Building and deploying..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Deployment successful!"
    echo ""
    # Get the service URL
    URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --project $PROJECT_ID --format 'value(status.url)')
    echo "Service URL: $URL"
    echo "========================================"
else
    echo ""
    echo "Deployment failed. Check the error messages above."
    echo ""
    echo "Common issues:"
    echo "1. Not logged into gcloud: run 'gcloud auth login'"
    echo "2. Project not set: run 'gcloud config set project $PROJECT_ID'"
    echo "3. APIs not enabled: Enable Cloud Run and Cloud Build APIs"
    echo ""
fi
